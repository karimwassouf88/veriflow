import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
from app.db.base import Base

class ComplianceResult(Base):
    __tablename__ = "compliance_results"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("documents.id"), nullable=False, index=True)
    compliant: Mapped[bool] = mapped_column(Boolean, nullable=False)
    required_approval_level: Mapped[str] = mapped_column(String(50), nullable=False)
    reasoning: Mapped[str] = mapped_column(String(2000), nullable=False)
    policy_sources: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))