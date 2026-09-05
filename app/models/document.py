import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Enum as SAEnum, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
from app.db.base import Base

class DocumentType(str, enum.Enum):
    INVOICE = "invoice"
    PURCHASE_ORDER = "purchase_order"
    CONTRACT = "contract"
    POLICY = "policy"

class IngestionStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    READY = "ready"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    EXTRACTION_FAILED = "extraction_failed"
    RAG_INGESTED = "rag_ingested"
    RAG_INGESTION_FAILED = "rag_ingestion_failed"
    VALIDATED = "validated"
    VALIDATION_ERROR = "validation_error"
    COMPLIANCE_CHECKED = "compliance_checked"
    COMPLIANCE_ERROR = "compliance_error"
    
class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    type: Mapped[DocumentType] = mapped_column(SAEnum(DocumentType), nullable=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    ingestion_status: Mapped[IngestionStatus] = mapped_column(
        SAEnum(IngestionStatus), default=IngestionStatus.UPLOADED, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))