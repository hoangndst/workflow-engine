"""Scheduled job - when to run which node for which participant."""
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.db import Base
import enum


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id = Column(String(36), primary_key=True)
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    run_at = Column(DateTime, nullable=False)
    status = Column(String(20), default=JobStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)

    participant = relationship("Participant", back_populates="scheduled_jobs")
