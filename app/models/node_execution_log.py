"""Node execution log - AGV (Automatic Generated Variable) timestamp."""
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class NodeExecutionLog(Base):
    __tablename__ = "node_execution_logs"

    id = Column(String(36), primary_key=True)
    participant_id = Column(String(36), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)

    participant = relationship("Participant", back_populates="execution_logs")
    node = relationship("Node")
