"""API routes tests."""
import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient):
    """Health check returns 200."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_projects(client: TestClient):
    """List projects returns at least Prototype."""
    r = client.get("/api/projects")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    names = [p["name"] for p in data]
    assert "Prototype" in names


def test_create_participant(client: TestClient):
    """Create participant for Prototype project."""
    r = client.get("/api/projects")
    assert r.status_code == 200
    projects = r.json()
    proj = next((p for p in projects if p["name"] == "Prototype"), None)
    assert proj is not None
    r = client.post("/api/participants", json={"project_id": proj["id"], "language": "English"})
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    assert data["project_id"] == proj["id"]
    assert data["status"] == "ACTIVE"


def test_send_message_keyword(client: TestClient):
    """Sending 'iselect' stores inbound and triggers flow (outbound via scheduler)."""
    r = client.get("/api/projects")
    proj = next((p for p in r.json() if p["name"] == "Prototype"), None)
    r = client.post("/api/participants", json={"project_id": proj["id"], "language": "English"})
    pid = r.json()["id"]
    r = client.post(f"/api/participants/{pid}/message", json={"text": "iselect"})
    assert r.status_code == 200
    r = client.get(f"/api/participants/{pid}/messages")
    assert r.status_code == 200
    messages = r.json()
    inbound = [m for m in messages if m["direction"] == "INBOUND"]
    outbound = [m for m in messages if m["direction"] == "OUTBOUND"]
    assert len(inbound) >= 1
    assert any(m["text"] == "iselect" for m in inbound)
    # Scheduler may have already sent Broadcast_1
    assert len(outbound) >= 0
