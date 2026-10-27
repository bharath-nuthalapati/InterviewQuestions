from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def now():
    return datetime.now(timezone.utc)

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(100), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(200), index=True)
    document_url: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="queued", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
