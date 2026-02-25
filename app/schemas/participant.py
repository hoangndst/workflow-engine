"""Participant and message schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ParticipantCreate(BaseModel):
    project_id: str
    language: str = "English"
    external_id: Optional[str] = None


class ParticipantResponse(BaseModel):
    id: str
    project_id: str
    language: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageSend(BaseModel):
    text: str


class MessageResponse(BaseModel):
    id: str
    participant_id: str
    direction: str
    message_template_id: Optional[str] = None
    text: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NodeFlowItem(BaseModel):
    node_id: str
    node_name: str
    template_name: str
    executed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
