import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
from app.db.base import Base

class EvalRun(Base):
    __tablename__ = "eval_runs"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    prompt_version: Mapped[str] = mapped_column(String(100), nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    total_fields: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_fields: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy_pct: Mapped[float] = mapped_column(Float, nullable=False)
    hallucination_count: Mapped[int] = mapped_column(Integer, nullable=False)
    hallucination_rate_pct: Mapped[float] = mapped_column(Float, nullable=False)
    details: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))