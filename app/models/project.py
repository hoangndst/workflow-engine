"""Project model."""
from datetime import datetime
from sqlalchemy import Column, DateTime, String, Enum
from sqlalchemy.orm import relationship

from app.db import Base
import enum


class ProjectStatus(str, enum.Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    status = Column(String(20), default=ProjectStatus.ACTIVE.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    timing_elements = relationship("TimingElement", back_populates="project", cascade="all, delete-orphan")
    variables = relationship("Variable", back_populates="project", cascade="all, delete-orphan")
    message_templates = relationship("MessageTemplate", back_populates="project", cascade="all, delete-orphan")
    nodes = relationship("Node", back_populates="project", foreign_keys="Node.project_id", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="project", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="project", cascade="all, delete-orphan")
