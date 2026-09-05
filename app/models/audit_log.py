import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Enum as SAEnum, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
from app.db.base import Base

class ActorType(str, enum.Enum):
    HUMAN = "human"
    AGENT = "agent"

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    actor_type: Mapped[ActorType] = mapped_column(SAEnum(ActorType), nullable=False)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
    before_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))