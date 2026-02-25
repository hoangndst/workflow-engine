"""Keyword model - e.g. iselect, iexit."""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    keyword_text = Column(String(255), nullable=False)
    language = Column(String(20), nullable=False)  # English, Spanish
    action_type = Column(String(50), nullable=False)  # ACTIVATE_PARTICIPANT, DEACTIVATE_PARTICIPANT, MOVE_TO_NODE
    referenced_node_id = Column(String(36), ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True)
    referenced_variable_id = Column(String(36), ForeignKey("variables.id", ondelete="SET NULL"), nullable=True)

    project = relationship("Project", back_populates="keywords")
