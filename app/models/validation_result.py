import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
from app.db.base import Base

class ValidationResult(Base):
    __tablename__ = "validation_results"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("documents.id"), nullable=False, index=True)
    vendor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("vendors.id"), nullable=True)
    purchase_order_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("purchase_orders.id"), nullable=True)
    vendor_status: Mapped[str] = mapped_column(String(20), nullable=False)   # "matched" / "not_found"
    po_status: Mapped[str] = mapped_column(String(20), nullable=False)       # "matched" / "amount_mismatch" / "not_found" / "not_referenced"
    amount_difference_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))