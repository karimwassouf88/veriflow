from app.core.logging_config import log
import uuid
from sqlalchemy.orm import Session
from app.models.document import Document, IngestionStatus
from app.models.document_extraction import DocumentExtraction
from app.models.audit_log import ActorType
from app.services import audit_service
from app.services.pdf_reader import extract_text_from_pdf
from app.services.confidence_scoring import score_extraction
from app.agents.extraction_agent import run_extraction_call, MODEL_NAME, PROMPT_VERSION

INVOICE_FIELDS = ["vendor_name", "invoice_number", "invoice_date", "due_date", "total_amount", "currency", "po_reference"]

def run_extraction(db: Session, document: Document, actor_id: uuid.UUID) -> None:
    document.ingestion_status = IngestionStatus.PROCESSING
    db.commit()
    log.info("extraction_started", document_id=str(document.id))

    try:
        raw_text = extract_text_from_pdf(document.file_path)
        if not raw_text.strip():
            raise ValueError(
                "No extractable text found in this PDF — it may be a scanned "
                "image without a text layer (OCR isn't supported yet)"
            )

        run_1 = run_extraction_call(raw_text, temperature=0.2)
        run_2 = run_extraction_call(raw_text, temperature=0.6)
        scored_fields = score_extraction(INVOICE_FIELDS, run_1, run_2, raw_text)

        db.query(DocumentExtraction).filter(DocumentExtraction.document_id == document.id).delete()
        for field_name, (value, confidence) in scored_fields.items():
            db.add(DocumentExtraction(
                document_id=document.id,
                field_name=field_name,
                extracted_value=str(value) if value is not None else None,
                confidence_score=confidence,
                model_version=f"{MODEL_NAME}/{PROMPT_VERSION}",
            ))

        document.ingestion_status = IngestionStatus.EXTRACTED
        audit_service.log_action(
            db, actor_type=ActorType.AGENT, actor_id=actor_id,
            action="document_extracted", entity_type="document", entity_id=document.id,
            after_state={"fields_extracted": len(scored_fields)},
        )
        log.info("extraction_completed", document_id=str(document.id), fields_extracted=len(scored_fields))
        db.commit()
    except Exception as e:
        log.error("extraction_failed", document_id=str(document.id), error=str(e))
        document.ingestion_status = IngestionStatus.EXTRACTION_FAILED
        db.commit()
        raise