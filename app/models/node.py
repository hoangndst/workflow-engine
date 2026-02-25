"""Node model - logical container for message delivery."""
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db import Base


class Node(Base):
    __tablename__ = "nodes"

    id = Column(String(36), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    is_terminal = Column(Boolean, default=False)
    schedule_timing_id = Column(String(36), ForeignKey("timing_elements.id", ondelete="SET NULL"), nullable=True)
    message_template_id = Column(String(36), ForeignKey("message_templates.id", ondelete="CASCADE"), nullable=False)

    # Activation: when this node should be considered for execution
    activation_type = Column(String(50), nullable=False)  # AFTER_NODE, AFTER_POLL, AFTER_DATE_TIME_VAR, START_DATE
    activation_source_node_id = Column(String(36), ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True)
    activation_poll_id = Column(String(36), ForeignKey("message_templates.id", ondelete="SET NULL"), nullable=True)
    activation_datetime_var_id = Column(String(36), ForeignKey("variables.id", ondelete="SET NULL"), nullable=True)

    project = relationship("Project", back_populates="nodes", foreign_keys=[project_id])
    schedule_timing = relationship("TimingElement", foreign_keys=[schedule_timing_id])
    message_template = relationship("MessageTemplate", foreign_keys=[message_template_id])
    activation_source_node = relationship("Node", remote_side=[id], foreign_keys=[activation_source_node_id])
    activation_poll = relationship("MessageTemplate", foreign_keys=[activation_poll_id])
    activation_datetime_var = relationship("Variable", foreign_keys=[activation_datetime_var_id])

    conditions = relationship("NodeCondition", back_populates="node", cascade="all, delete-orphan")
