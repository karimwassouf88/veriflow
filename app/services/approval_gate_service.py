import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document import Document
from app.models.document_extraction import DocumentExtraction
from app.models.validation_result import ValidationResult
from app.models.compliance_result import ComplianceResult
from app.models.approval import Approval, ApprovalDecision
from app.models.audit_log import ActorType
from app.services import audit_service
from app.core.logging_config import log

AUTO_APPROVE_AMOUNT_THRESHOLD = 1000.00
MIN_FIELD_CONFIDENCE = 0.6

def _latest(db: Session, model, document_id):
    return db.scalars(
        select(model).where(model.document_id == document_id).order_by(model.created_at.desc())
    ).first()

def run_approval_gate(db: Session, document: Document, actor_id: uuid.UUID) -> Approval:
    log.info("approval_gate_started", document_id=str(document.id))
    try:
        validation = _latest(db, ValidationResult, document.id)
        compliance = _latest(db, ComplianceResult, document.id)
        extraction = {
            row.field_name: row
            for row in db.scalars(select(DocumentExtraction).where(DocumentExtraction.document_id == document.id)).all()
        }

        if validation is None or compliance is None:
            raise ValueError("Document must complete validation and compliance checks before the approval gate can run")

        reasons = []
        route_to_human = False

        if not validation.passed:
            route_to_human = True
            reasons.append(f"Validation issue: {validation.summary}")

        if not compliance.compliant:
            route_to_human = True
            reasons.append(f"Compliance check flagged this invoice: {compliance.reasoning}")

        for field_name in ("vendor_name", "total_amount"):
            field = extraction.get(field_name)
            if field is None or field.confidence_score < MIN_FIELD_CONFIDENCE:
                route_to_human = True
                reasons.append(f"Low confidence on '{field_name}' ({field.confidence_score if field else 'missing'})")

        amount_field = extraction.get("total_amount")
        amount = None
        if amount_field and amount_field.extracted_value:
            try:
                amount = float(amount_field.extracted_value)
            except ValueError:
                amount = None

        if amount is None:
            route_to_human = True
            reasons.append("Could not determine invoice amount")
        elif amount > AUTO_APPROVE_AMOUNT_THRESHOLD:
            route_to_human = True
            reasons.append(
                f"Amount ${amount:,.2f} exceeds the ${AUTO_APPROVE_AMOUNT_THRESHOLD:,.2f} auto-approval threshold; "
                f"requires {compliance.required_approval_level} approval per policy"
            )

        decision = ApprovalDecision.PENDING if route_to_human else ApprovalDecision.AUTO_APPROVED
        routing_reason = " | ".join(reasons) if reasons else f"Amount ${amount:,.2f} within threshold, all checks passed"

        approval = Approval(
            document_id=document.id,
            decision=decision.value,
            routing_reason=routing_reason,
            decided_at=datetime.now(timezone.utc) if decision == ApprovalDecision.AUTO_APPROVED else None,
        )
        db.add(approval)

        audit_service.log_action(
            db, actor_type=ActorType.AGENT, actor_id=actor_id,
            action="approval_gate_decision", entity_type="document", entity_id=document.id,
            after_state={"decision": decision.value, "routing_reason": routing_reason},
        )
        log.info("approval_gate_completed", document_id=str(document.id), decision=decision.value)
        db.commit()
        db.refresh(approval)
        return approval
    except Exception as e:
        log.error("approval_gate_failed", document_id=str(document.id), error=str(e))
        raise