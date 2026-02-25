"""Node condition - e.g. Poll_1 answer is No."""
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db import Base


class NodeCondition(Base):
    __tablename__ = "node_conditions"

    id = Column(String(36), primary_key=True)
    node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    poll_template_id = Column(String(36), ForeignKey("message_templates.id", ondelete="CASCADE"), nullable=True)
    variable_id = Column(String(36), ForeignKey("variables.id", ondelete="CASCADE"), nullable=True)
    operation = Column(String(20), nullable=False)  # equal, gt, gte, lt, lte, in, not_in
    expected_answer = Column(Text, nullable=True)  # "no", "yes", or numeric string

    node = relationship("Node", back_populates="conditions")
