"""Pytest fixtures. Set DATABASE_URL before any app import so tests use SQLite."""
import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_dashmessaging.db")

import uuid
import pytest
from fastapi.testclient import TestClient

TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test_dashmessaging.db")


@pytest.fixture(scope="session")
def db_engine():
    """Create tables for tests. Uses SQLite for CI/local without PostgreSQL."""
    from sqlalchemy import create_engine
    from app.db import Base
    from app.models import (  # noqa: F401 - register models
        project,
        timing_element,
        variable,
        message_template,
        node,
        node_condition,
        keyword,
        participant,
        participant_message,
        participant_variable,
        node_execution_log,
        scheduled_job,
    )
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
    )
    Base.metadata.create_all(bind=engine)
    return engine


def _seed_test_project(session):
    """Create Prototype project and seed for tests."""
    from app.models import Project
    from app.seed.prototype import seed_prototype_project
    proj = session.query(Project).filter(Project.name == "Prototype").first()
    if not proj:
        proj = Project(
            id=str(uuid.uuid4()),
            name="Prototype",
            description="Prototype protocol",
            status="Active",
        )
        session.add(proj)
        session.commit()
        session.refresh(proj)
    seed_prototype_project(session, proj.id)
    return proj.id


@pytest.fixture
def db_session(db_engine):
    """Provide a transactional DB session that rolls back after each test."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_engine):
    """Test client. Override get_db to use test engine and seed prototype."""
    from sqlalchemy.orm import sessionmaker
    from app.main import app
    from app.db import get_db

    Session = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = Session()
    _seed_test_project(session)
    session.close()

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
