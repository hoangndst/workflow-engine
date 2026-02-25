"""Participant variable - protocol-related participant-specific variable values."""
from sqlalchemy import Column, String, ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import relationship

from app.db import Base


class ParticipantVariable(Base):
    __tablename__ = "participant_variables"

    id = Column(String(36), primary_key=True)
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    variable_id = Column(String(36), ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    value_text = Column(Text, nullable=True)
    value_int = Column(Integer, nullable=True)
    value_datetime = Column(DateTime, nullable=True)

    participant = relationship("Participant", back_populates="variables")
