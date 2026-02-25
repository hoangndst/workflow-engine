"""Unit tests for protocol engine (conditions, keyword, poll)."""
import uuid
from datetime import datetime
from unittest.mock import patch
import pytest
from sqlalchemy.orm import Session

from app.models import (
    Project,
    Participant,
    Variable,
    MessageTemplate,
    Node,
    NodeCondition,
    ParticipantVariable,
    TimingElement,
)
from app.core.engine import _condition_matches, _resolve_text, _timedelta_from_timing


@pytest.fixture
def project_and_participant(db_session):
    """Create a minimal project with one variable and one participant."""
    from app.seed.prototype import seed_prototype_project
    proj = Project(id=str(uuid.uuid4()), name="Test", description="Test", status="Active")
    db_session.add(proj)
    db_session.commit()
    db_session.refresh(proj)
    seed_prototype_project(db_session, proj.id)
    p = Participant(id=str(uuid.uuid4()), project_id=proj.id, language="English", status="ACTIVE")
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return proj, p


def test_timedelta_from_timing():
    """Timing element converts to timedelta correctly."""
    class T:
        days = 0
        hours = 0
        minutes = 1
        seconds = 30
    delta = _timedelta_from_timing(T())
    assert delta.total_seconds() == 90


def test_resolve_text_english():
    """Message template resolves to English when language is English."""
    class T:
        text_en = "Hello"
        text_es = "Hola"
    assert _resolve_text(T(), "English") == "Hello"


def test_resolve_text_spanish():
    """Message template resolves to Spanish when language is Spanish."""
    class T:
        text_en = "Hello"
        text_es = "Hola"
    assert _resolve_text(T(), "Spanish") == "Hola"


def test_condition_matches_text_equal(db_session, project_and_participant):
    """Condition Poll_1 = no matches when participant variable is 'no'."""
    proj, participant = project_and_participant
    var = db_session.query(Variable).filter(Variable.project_id == proj.id, Variable.name == "Poll_1_Variable").first()
    node = db_session.query(Node).filter(Node.project_id == proj.id, Node.name == "Node_1").first()
    assert node is not None and var is not None
    pv = ParticipantVariable(
        id=str(uuid.uuid4()),
        participant_id=participant.id,
        variable_id=var.id,
        value_text="no",
    )
    db_session.add(pv)
    db_session.commit()
    assert _condition_matches(db_session, participant.id, node, datetime.utcnow()) is True


def test_condition_matches_text_no_match(db_session, project_and_participant):
    """Condition Poll_1 = no does not match when value is 'yes'."""
    proj, participant = project_and_participant
    var = db_session.query(Variable).filter(Variable.project_id == proj.id, Variable.name == "Poll_1_Variable").first()
    node = db_session.query(Node).filter(Node.project_id == proj.id, Node.name == "Node_1").first()
    pv = ParticipantVariable(
        id=str(uuid.uuid4()),
        participant_id=participant.id,
        variable_id=var.id,
        value_text="yes",
    )
    db_session.add(pv)
    db_session.commit()
    assert _condition_matches(db_session, participant.id, node, datetime.utcnow()) is False
