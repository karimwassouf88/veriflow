import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document import Document, IngestionStatus
from app.models.document_extraction import DocumentExtraction
from app.models.compliance_result import ComplianceResult
from app.models.audit_log import ActorType
from app.services import audit_service
from app.rag.retrieval import retrieve_relevant_chunks
from app.agents import compliance_agent
from app.core.logging_config import log

def run_compliance_check(db: Session, document: Document, actor_id: uuid.UUID) -> ComplianceResult:
    document.ingestion_status = IngestionStatus.PROCESSING
    db.commit()
    log.info("compliance_check_started", document_id=str(document.id))
    try:
        rows = db.scalars(select(DocumentExtraction).where(DocumentExtraction.document_id == document.id)).all()
        fields = {row.field_name: row.extracted_value for row in rows}

        total_amount = fields.get("total_amount")
        query = f"approval requirements and policy for a purchase of ${total_amount}" if total_amount else "general purchase approval policy"
        chunks = retrieve_relevant_chunks(query, top_k=5)

        result_data = compliance_agent.check_compliance(fields, chunks)

        record = ComplianceResult(
            document_id=document.id,
            compliant=result_data.get("compliant", False),
            required_approval_level=result_data.get("required_approval_level", "unknown"),
            reasoning=result_data.get("reasoning", ""),
            policy_sources=",".join(sorted({c["filename"] for c in chunks})) if chunks else None,
            model_version=f"{compliance_agent.MODEL_NAME}/{compliance_agent.PROMPT_VERSION}",
        )
        db.add(record)
        document.ingestion_status = IngestionStatus.COMPLIANCE_CHECKED

        audit_service.log_action(
            db, actor_type=ActorType.AGENT, actor_id=actor_id,
            action="document_compliance_checked", entity_type="document", entity_id=document.id,
            after_state={"compliant": record.compliant, "required_approval_level": record.required_approval_level},
        )
        log.info("compliance_check_completed", document_id=str(document.id), compliant=record.compliant, required_approval_level=record.required_approval_level)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        log.error("compliance_check_failed", document_id=str(document.id), error=str(e))
        document.ingestion_status = IngestionStatus.COMPLIANCE_ERROR
        db.commit()
        raise