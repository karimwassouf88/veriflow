import uuid
from sqlalchemy.orm import Session
from app.models.document import Document, IngestionStatus
from app.models.audit_log import ActorType
from app.services import audit_service
from app.services.pdf_reader import extract_text_from_pdf
from app.rag.chunking import chunk_text
from app.rag import vector_store

def ingest_policy_document(db: Session, document: Document, actor_id: uuid.UUID) -> int:
    document.ingestion_status = IngestionStatus.PROCESSING
    db.commit()
    try:
        raw_text = extract_text_from_pdf(document.file_path)
        if not raw_text.strip():
            raise ValueError("No extractable text found in this PDF — scanned/image PDFs aren't supported yet")

        chunks = chunk_text(raw_text)
        vector_store.delete_document_chunks(document.id)  # makes re-ingestion idempotent
        chunk_count = vector_store.upsert_chunks(document.id, document.original_filename, chunks)

        document.ingestion_status = IngestionStatus.RAG_INGESTED
        audit_service.log_action(
            db, actor_type=ActorType.AGENT, actor_id=actor_id,
            action="document_rag_ingested", entity_type="document", entity_id=document.id,
            after_state={"chunk_count": chunk_count},
        )
        db.commit()
        return chunk_count
    except Exception:
        document.ingestion_status = IngestionStatus.RAG_INGESTION_FAILED
        db.commit()
        raise