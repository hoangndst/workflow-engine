"""Timing element model."""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.db import Base
import enum


class TimingDirection(str, enum.Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"


class TimingElement(Base):
    __tablename__ = "timing_elements"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    direction = Column(String(20), default=TimingDirection.AFTER.value)
    days = Column(Integer, default=0)
    hours = Column(Integer, default=0)
    minutes = Column(Integer, default=0)
    seconds = Column(Integer, default=0)

    project = relationship("Project", back_populates="timing_elements")
