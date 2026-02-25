"""Variable model."""
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.db import Base


class Variable(Base):
    __tablename__ = "variables"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # Integer, Text, Time, DateTime, None
    source = Column(String(50), default="INTERNAL")
    is_system = Column(Boolean, default=False)  # e.g. Start_Date
    is_agv = Column(Boolean, default=False)  # Automatic Generated Variable

    project = relationship("Project", back_populates="variables")
