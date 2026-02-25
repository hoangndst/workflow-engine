"""Message template model (Broadcast / Poll)."""
from sqlalchemy import Column, String, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.db import Base
import enum


class MessageTemplateType(str, enum.Enum):
    BROADCAST = "BROADCAST"
    POLL = "POLL"


class MessageTemplate(Base):
    __tablename__ = "message_templates"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20), nullable=False)  # BROADCAST, POLL
    name = Column(String(255), nullable=False)
    text_en = Column(Text, nullable=True)
    text_es = Column(Text, nullable=True)
    variable_id = Column(String(36), ForeignKey("variables.id", ondelete="SET NULL"), nullable=True)  # for Poll: store answer
    choices_en = Column(JSON, nullable=True)  # ["Yes", "No"] for Poll
    choices_es = Column(JSON, nullable=True)

    project = relationship("Project", back_populates="message_templates")
    variable = relationship("Variable", foreign_keys=[variable_id])
