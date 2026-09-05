import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
from app.db.base import Base

class DocumentExtraction(Base):
    __tablename__ = "document_extractions"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("documents.id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(50), nullable=False)
    extracted_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))