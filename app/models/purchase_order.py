import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Float, Enum as SAEnum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
from app.db.base import Base

class PurchaseOrderStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    po_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    vendor_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("vendors.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[PurchaseOrderStatus] = mapped_column(
        SAEnum(PurchaseOrderStatus, native_enum=False), default=PurchaseOrderStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))