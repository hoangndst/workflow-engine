"""Participant message - inbound/outbound history."""
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship

from app.db import Base
import enum


class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class ParticipantMessage(Base):
    __tablename__ = "participant_messages"

    id = Column(String(36), primary_key=True)
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    direction = Column(String(20), nullable=False)  # INBOUND, OUTBOUND
    message_template_id = Column(String(36), ForeignKey("message_templates.id", ondelete="SET NULL"), nullable=True)
    text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    participant = relationship("Participant", back_populates="messages")
