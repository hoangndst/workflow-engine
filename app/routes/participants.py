"""Participant and message API routes."""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Participant, ParticipantMessage, NodeExecutionLog, Node, MessageTemplate
from app.schemas.participant import ParticipantCreate, ParticipantResponse, MessageSend, MessageResponse, NodeFlowItem
from app.core.engine import process_keyword, process_poll_answer

router = APIRouter()


@router.post("", response_model=ParticipantResponse)
def create_participant(body: ParticipantCreate, db: Session = Depends(get_db)):
    """Create a new participant for a project (demo: start conversation)."""
    from app.models import Project
    proj = db.query(Project).filter(Project.id == body.project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    p = Participant(
        id=str(uuid.uuid4()),
        project_id=body.project_id,
        language=body.language or "English",
        status="ACTIVE",
        external_id=body.external_id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/{participant_id}", response_model=ParticipantResponse)
def get_participant(participant_id: str, db: Session = Depends(get_db)):
    """Get participant by id."""
    p = db.query(Participant).filter(Participant.id == participant_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    return p


@router.get("/{participant_id}/messages", response_model=list[MessageResponse])
def list_messages(participant_id: str, db: Session = Depends(get_db)):
    """List all messages for a participant (inbound + outbound)."""
    p = db.query(Participant).filter(Participant.id == participant_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    messages = (
        db.query(ParticipantMessage)
        .filter(ParticipantMessage.participant_id == participant_id)
        .order_by(ParticipantMessage.created_at.asc())
        .all()
    )
    return messages


@router.post("/{participant_id}/message", response_model=MessageResponse)
def send_message(participant_id: str, body: MessageSend, db: Session = Depends(get_db)):
    """
    Participant sends a message (keyword or poll answer).
    Stores INBOUND message, then processes as keyword or poll answer; outbound replies come from scheduler.
    """
    p = db.query(Participant).filter(Participant.id == participant_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    text = (body.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message text required")

    # Store inbound message
    inbound = ParticipantMessage(
        id=str(uuid.uuid4()),
        participant_id=participant_id,
        direction="INBOUND",
        message_template_id=None,
        text=text,
    )
    db.add(inbound)
    db.commit()
    db.refresh(inbound)

    # Try keyword first
    err = process_keyword(db, participant_id, text)
    if err:
        raise HTTPException(status_code=400, detail=err)
    # Try poll answer (no error if not applicable)
    process_poll_answer(db, participant_id, text)
    return inbound


@router.get("/{participant_id}/timeline", response_model=list[NodeFlowItem])
def get_timeline(participant_id: str, db: Session = Depends(get_db)):
    """Return execution timeline of nodes for this participant (for UI flow visualization)."""
    p = db.query(Participant).filter(Participant.id == participant_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Participant not found")
    rows = (
        db.query(NodeExecutionLog, Node, MessageTemplate)
        .join(Node, NodeExecutionLog.node_id == Node.id)
        .join(MessageTemplate, Node.message_template_id == MessageTemplate.id)
        .filter(NodeExecutionLog.participant_id == participant_id)
        .order_by(NodeExecutionLog.executed_at.asc())
        .all()
    )
    items: list[NodeFlowItem] = []
    for log, node, tpl in rows:
        items.append(
            NodeFlowItem(
                node_id=node.id,
                node_name=node.name,
                template_name=tpl.name,
                executed_at=log.executed_at,
            )
        )
    return items
