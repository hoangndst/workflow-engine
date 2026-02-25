"""Integration test: full prototype flow (iselect -> poll -> answer)."""
import time
import pytest
from fastapi.testclient import TestClient


def test_flow_iselect_then_poll_answer(client: TestClient):
    """After iselect, we get Broadcast_1; after answering poll we get next message (scheduler runs)."""
    r = client.get("/api/projects")
    proj = next((p for p in r.json() if p["name"] == "Prototype"), None)
    assert proj is not None
    r = client.post("/api/participants", json={"project_id": proj["id"], "language": "English"})
    assert r.status_code == 200
    pid = r.json()["id"]

    # Send iselect
    r = client.post(f"/api/participants/{pid}/message", json={"text": "iselect"})
    assert r.status_code == 200

    # Poll for messages a few times to allow scheduler to send Broadcast_1 and Poll_1
    for _ in range(8):
        time.sleep(0.6)
        r = client.get(f"/api/participants/{pid}/messages")
        assert r.status_code == 200
        messages = r.json()
        outbound = [m for m in messages if m["direction"] == "OUTBOUND"]
        if len(outbound) >= 2:
            break
    else:
        # At least we got one outbound (Broadcast_1)
        r = client.get(f"/api/participants/{pid}/messages")
        messages = r.json()
        outbound = [m for m in messages if m["direction"] == "OUTBOUND"]
        assert len(outbound) >= 1, "Expected at least Broadcast_1 from scheduler"

    # Answer poll: yes
    r = client.post(f"/api/participants/{pid}/message", json={"text": "yes"})
    assert r.status_code == 200

    # Wait for Broadcast_2 and Poll_2
    for _ in range(10):
        time.sleep(0.6)
        r = client.get(f"/api/participants/{pid}/messages")
        messages = r.json()
        outbound = [m for m in messages if m["direction"] == "OUTBOUND"]
        if len(outbound) >= 4:
            break

    # Answer Poll_2 with 3 (<=5 -> Broadcast_4)
    r = client.post(f"/api/participants/{pid}/message", json={"text": "3"})
    assert r.status_code == 200

    time.sleep(1.5)
    r = client.get(f"/api/participants/{pid}/messages")
    messages = r.json()
    texts = [m["text"] for m in messages if m["direction"] == "OUTBOUND"]
    # We should eventually see Broadcast_4 (rating 5 or below)
    assert any("5 or below" in (t or "") or "Broadcast 4" in (t or "") for t in texts)
