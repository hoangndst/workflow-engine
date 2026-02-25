"""
DashMessaging protocol engine.

Executes nodes: send message, log AGV, schedule dependent nodes.
Handles keywords (iselect, iexit) and poll answers.
"""
from datetime import datetime, timedelta
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app.models import (
    Participant,
    Node,
    MessageTemplate,
    Variable,
    ParticipantMessage,
    ParticipantVariable,
    NodeExecutionLog,
    ScheduledJob,
    Keyword,
)
from app.models.scheduled_job import JobStatus


def _timedelta_from_timing(timing) -> timedelta:
    """Convert TimingElement to timedelta."""
    if not timing:
        return timedelta(0)
    return timedelta(
        days=timing.days or 0,
        hours=timing.hours or 0,
        minutes=timing.minutes or 0,
        seconds=timing.seconds or 0,
    )


def _resolve_text(template: MessageTemplate, language: str) -> str:
    """Get message text in participant language."""
    if not template:
        return ""
    if (language or "").lower() in ("spanish", "es"):
        return (template.text_es or template.text_en) or ""
    return (template.text_en or template.text_es) or ""


def _condition_matches(
    db: Session,
    participant_id: str,
    node: Node,
    now: datetime,
) -> bool:
    """Evaluate node conditions for this participant. True = should run."""
    if not node.conditions:
        return True
    for cond in node.conditions:
        # Get participant's value for cond.variable_id
        pv = (
            db.query(ParticipantVariable)
            .filter(
                ParticipantVariable.participant_id == participant_id,
                ParticipantVariable.variable_id == cond.variable_id,
            )
            .first()
        )
        if pv is None:
            return False
        # Compare by variable type
        var = db.query(Variable).filter(Variable.id == cond.variable_id).first()
        expected = (cond.expected_answer or "").strip().lower()
        if var and var.type and "int" in (var.type or "").lower():
            try:
                val = pv.value_int
                if val is None:
                    return False
                exp_val = int(expected) if expected and str(expected).strip().isdigit() else None
                if exp_val is not None:
                    if cond.operation == "equal":
                        if val != exp_val:
                            return False
                    elif cond.operation == "gt":
                        if val <= exp_val:
                            return False
                    elif cond.operation == "gte":
                        if val < exp_val:
                            return False
                    elif cond.operation == "lt":
                        if val >= exp_val:
                            return False
                    elif cond.operation == "lte":
                        if val > exp_val:
                            return False
                    else:
                        if val != exp_val:
                            return False
                else:
                    if cond.operation == "lte":
                        if val > 5:
                            return False
                    elif cond.operation == "gt":
                        if val <= 5:
                            return False
                continue
            except (TypeError, ValueError):
                return False
        else:
            # Text comparison (e.g. yes/no)
            val = (pv.value_text or "").strip().lower()
            if cond.operation == "equal":
                if val != expected:
                    return False
            else:
                if val != expected:
                    return False
    return True


def _create_outbound_message(
    db: Session,
    participant_id: str,
    template: MessageTemplate,
    language: str,
) -> ParticipantMessage:
    """Create and persist one OUTBOUND message from a template."""
    text = _resolve_text(template, language)
    msg = ParticipantMessage(
        id=str(uuid.uuid4()),
        participant_id=participant_id,
        direction="OUTBOUND",
        message_template_id=template.id,
        text=text,
    )
    db.add(msg)
    db.flush()
    return msg


def _log_agv(db: Session, participant_id: str, node_id: str) -> None:
    """Record AGV: node was sent at this time."""
    log = NodeExecutionLog(
        id=str(uuid.uuid4()),
        participant_id=participant_id,
        node_id=node_id,
        executed_at=datetime.utcnow(),
    )
    db.add(log)


def _schedule_node(
    db: Session,
    participant_id: str,
    node_id: str,
    run_at: datetime,
) -> ScheduledJob:
    """Create a PENDING scheduled job."""
    job = ScheduledJob(
        id=str(uuid.uuid4()),
        participant_id=participant_id,
        node_id=node_id,
        run_at=run_at,
        status=JobStatus.PENDING.value,
    )
    db.add(job)
    db.flush()
    return job


def execute_node(db: Session, participant_id: str, node_id: str) -> Optional[ParticipantMessage]:
    """
    Execute a single node for a participant: send message, log AGV, schedule dependents.
    Returns the outbound message created, or None if not executed.
    """
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant or participant.status != "ACTIVE":
        return None
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node or node.project_id != participant.project_id:
        return None

    template = db.query(MessageTemplate).filter(MessageTemplate.id == node.message_template_id).first()
    if not template:
        return None

    # 1. Send message
    msg = _create_outbound_message(db, participant_id, template, participant.language or "English")
    # 2. AGV
    _log_agv(db, participant_id, node_id)

    now = datetime.utcnow()
    delay = _timedelta_from_timing(node.schedule_timing)
    run_at = now + delay

    # 3. Find dependent nodes and schedule if conditions match
    # Nodes that activate AFTER this node (activation_type=AFTER_NODE, activation_source_node_id=node_id)
    dependents = (
        db.query(Node)
        .filter(
            Node.project_id == participant.project_id,
            Node.activation_type == "AFTER_NODE",
            Node.activation_source_node_id == node_id,
        )
        .all()
    )
    for dep in dependents:
        if _condition_matches(db, participant_id, dep, now):
            _schedule_node(db, participant_id, dep.id, run_at)

    db.commit()
    return msg


def process_keyword(db: Session, participant_id: str, text: str) -> Optional[str]:
    """
    Process inbound text as keyword (e.g. iselect, iexit).
    Returns error message if invalid; None if handled.
    """
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        return "Participant not found"
    keyword_text = (text or "").strip().lower()
    kw = (
        db.query(Keyword)
        .filter(
            Keyword.project_id == participant.project_id,
            Keyword.keyword_text == keyword_text,
        )
        .first()
    )
    if not kw:
        return None  # Not a keyword; might be poll answer

    if kw.action_type == "DEACTIVATE_PARTICIPANT" or keyword_text == "iexit":
        # Optional exit node/message before deactivating
        if kw.referenced_node_id:
            node = db.query(Node).filter(Node.id == kw.referenced_node_id).first()
            if node:
                execute_node(db, participant_id, node.id)
        # Then deactivate participant and cancel pending jobs
        participant.status = "INACTIVE"
        for job in db.query(ScheduledJob).filter(
            ScheduledJob.participant_id == participant_id,
            ScheduledJob.status == JobStatus.PENDING.value,
        ).all():
            job.status = JobStatus.CANCELLED.value
        db.commit()
        return None
    if kw.action_type == "ACTIVATE_PARTICIPANT" or keyword_text in ("iselect", "ibuy"):
        # Reactivate participant if previously inactive
        participant.status = "ACTIVE"
        # Set Start_Date variable to now
        start_date_var = (
            db.query(Variable)
            .filter(
                Variable.project_id == participant.project_id,
                Variable.name == "Start_Date",
            )
            .first()
        )
        if start_date_var:
            existing = (
                db.query(ParticipantVariable)
                .filter(
                    ParticipantVariable.participant_id == participant_id,
                    ParticipantVariable.variable_id == start_date_var.id,
                )
                .first()
            )
            now = datetime.utcnow()
            if existing:
                existing.value_datetime = now
            else:
                pv = ParticipantVariable(
                    id=str(uuid.uuid4()),
                    participant_id=participant_id,
                    variable_id=start_date_var.id,
                    value_datetime=now,
                )
                db.add(pv)
        # Schedule nodes that activate on START_DATE (referenced by keyword's node or by Start_Date)
        start_node = kw.referenced_node_id
        if start_node:
            node = db.query(Node).filter(Node.id == start_node).first()
            if node:
                timing = node.schedule_timing
                delay = _timedelta_from_timing(timing) if timing else timedelta(0)
                _schedule_node(db, participant_id, node.id, datetime.utcnow() + delay)
        else:
            # Find nodes with activation_type START_DATE for this project
            for node in db.query(Node).filter(
                Node.project_id == participant.project_id,
                Node.activation_type == "START_DATE",
            ).all():
                if _condition_matches(db, participant_id, node, datetime.utcnow()):
                    delay = _timedelta_from_timing(node.schedule_timing) or timedelta(0)
                    _schedule_node(db, participant_id, node.id, datetime.utcnow() + delay)
        db.commit()
        return None
    return None


def process_poll_answer(
    db: Session,
    participant_id: str,
    text: str,
) -> Optional[str]:
    """
    Treat inbound text as answer to the last sent Poll. Store in variable and schedule dependent nodes.
    Returns error message if invalid; None if handled.
    """
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant or participant.status != "ACTIVE":
        return "Participant not found or inactive"

    # Last outbound message that is a Poll (we're waiting for answer)
    last_out = (
        db.query(ParticipantMessage)
        .join(MessageTemplate, ParticipantMessage.message_template_id == MessageTemplate.id)
        .filter(
            ParticipantMessage.participant_id == participant_id,
            ParticipantMessage.direction == "OUTBOUND",
            MessageTemplate.type == "POLL",
        )
        .order_by(ParticipantMessage.created_at.desc())
        .first()
    )
    if not last_out or not last_out.message_template_id:
        return None  # No poll waiting; might be keyword
    template = db.query(MessageTemplate).get(last_out.message_template_id)
    if not template or template.type != "POLL":
        return None

    # Normalize answer
    raw = (text or "").strip()
    answer_lower = raw.lower()
    choices_en = template.choices_en or []
    choices_es = template.choices_es or []
    # Accept if matches any choice (en or es), case-insensitive
    valid_choices = [str(c).lower() for c in choices_en] + [str(c).lower() for c in choices_es]
    # Also allow numeric for rating poll (1-10)
    try:
        num = int(raw)
        if 1 <= num <= 10:
            valid_choices.extend([str(i) for i in range(1, 11)])
    except ValueError:
        pass
    if not valid_choices:
        valid_choices = ["yes", "no", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

    # Store in variable
    var = db.query(Variable).filter(Variable.id == template.variable_id).first() if template.variable_id else None
    if not var:
        db.commit()
        return None
    existing = (
        db.query(ParticipantVariable)
        .filter(
            ParticipantVariable.participant_id == participant_id,
            ParticipantVariable.variable_id == var.id,
        )
        .first()
    )
    if var.type and "int" in var.type.lower():
        try:
            value_int = int(raw)
        except ValueError:
            value_int = None
        if existing:
            existing.value_int = value_int
            existing.value_text = raw
        else:
            db.add(ParticipantVariable(
                id=str(uuid.uuid4()),
                participant_id=participant_id,
                variable_id=var.id,
                value_int=value_int,
                value_text=raw,
            ))
    else:
        if existing:
            existing.value_text = raw
        else:
            db.add(ParticipantVariable(
                id=str(uuid.uuid4()),
                participant_id=participant_id,
                variable_id=var.id,
                value_text=raw,
            ))
    db.flush()

    now = datetime.utcnow()
    # Nodes that activate AFTER this poll
    dependents = (
        db.query(Node)
        .filter(
            Node.project_id == participant.project_id,
            Node.activation_type == "AFTER_POLL",
            Node.activation_poll_id == template.id,
        )
        .all()
    )
    for dep in dependents:
        if _condition_matches(db, participant_id, dep, now):
            delay = _timedelta_from_timing(dep.schedule_timing) or timedelta(0)
            _schedule_node(db, participant_id, dep.id, now + delay)
    db.commit()
    return None
