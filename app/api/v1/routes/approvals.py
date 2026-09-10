import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.approval import Approval, ApprovalDecision
from app.models.audit_log import ActorType
from app.schemas.approval import ApprovalOut, ApprovalDecisionRequest, ApprovalWithDocumentOut
from app.api.v1.deps import require_role
from app.services import audit_service
from app.models.document import Document

router = APIRouter(prefix="/approvals", tags=["approvals"])
APPROVER_ROLES = (UserRole.ADMIN, UserRole.APPROVER)
ALL_ROLES = (UserRole.ADMIN, UserRole.CLERK, UserRole.APPROVER, UserRole.AUDITOR)

@router.get("", response_model=list[ApprovalWithDocumentOut])
def list_approvals(
    pending_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ALL_ROLES)),
):
    query = select(Approval).order_by(Approval.created_at.desc())
    if pending_only:
        query = query.where(Approval.decision == ApprovalDecision.PENDING.value)
    approvals = db.scalars(query).all()

    doc_ids = {a.document_id for a in approvals}
    documents = {d.id: d for d in db.scalars(select(Document).where(Document.id.in_(doc_ids))).all()} if doc_ids else {}

    return [
        ApprovalWithDocumentOut(
            id=a.id, document_id=a.document_id, decision=a.decision, routing_reason=a.routing_reason,
            approver_id=a.approver_id, comment=a.comment, decided_at=a.decided_at, created_at=a.created_at,
            document_filename=documents[a.document_id].original_filename if a.document_id in documents else None,
            document_type=documents[a.document_id].type.value if a.document_id in documents else None,
        )
        for a in approvals
    ]

@router.post("/{approval_id}/decision", response_model=ApprovalOut)
def decide_approval(
    approval_id: uuid.UUID,
    payload: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*APPROVER_ROLES)),
):
    approval = db.get(Approval, approval_id)
    if approval is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Approval not found")
    if approval.decision != ApprovalDecision.PENDING.value:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"This approval was already resolved: '{approval.decision}'")
    if payload.decision not in (ApprovalDecision.APPROVED, ApprovalDecision.REJECTED):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Decision must be 'approved' or 'rejected'")

    before_state = {"decision": approval.decision}
    approval.decision = payload.decision.value
    approval.approver_id = current_user.id
    approval.comment = payload.comment
    approval.decided_at = datetime.now(timezone.utc)

    audit_service.log_action(
        db, actor_type=ActorType.HUMAN, actor_id=current_user.id,
        action="approval_decision", entity_type="approval", entity_id=approval.id,
        before_state=before_state, after_state={"decision": approval.decision, "comment": approval.comment},
    )
    db.commit()
    db.refresh(approval)
    return approval