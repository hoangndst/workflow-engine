"""Participant model."""
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String(255), nullable=True)  # simulated user id for demo
    language = Column(String(20), default="English")
    status = Column(String(20), default="ACTIVE")  # ACTIVE, INACTIVE
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="participants")
    messages = relationship("ParticipantMessage", back_populates="participant", order_by="ParticipantMessage.created_at", cascade="all, delete-orphan")
    variables = relationship("ParticipantVariable", back_populates="participant", cascade="all, delete-orphan")
    execution_logs = relationship("NodeExecutionLog", back_populates="participant", cascade="all, delete-orphan")
    scheduled_jobs = relationship("ScheduledJob", back_populates="participant", cascade="all, delete-orphan")
