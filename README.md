# DashMessaging Protocol

Smart Chatbot Platform implementing the Dash Messaging Protocol (per the design document). Built with FastAPI, PostgreSQL (or SQLite for tests), and a Material Design demo UI.

## Features

- **Projects**: Create and manage chatbot projects (Prototype project is seeded on first run).
- **Protocol engine**: Timing elements, variables, message templates (Broadcast/Poll), nodes with conditions, keywords (`iselect`, `iexit`).
- **Scheduler**: Background worker runs scheduled nodes (delays per timing elements).
- **Demo UI**: Dashboard and participant chat to send/receive messages and verify the flow (e.g. send `iselect`, answer polls).

## Requirements

- Python 3.11+
- PostgreSQL (for production) or set `DATABASE_URL` to a SQLite path for development.

## Setup

```bash
# Install dependencies
pip install -e . && pip install -e ".[dev]"

# Set database (optional; default below)
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/dashmessaging"

# Run migrations (PostgreSQL)
alembic upgrade head

# Or create DB and run migrations manually
# createdb dashmessaging && alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --reload
```

- **API**: http://127.0.0.1:8000
- **Docs**: http://127.0.0.1:8000/docs
- **Demo UI**: http://127.0.0.1:8000/ → “Open prototype demo” → send `iselect`, then answer polls (Yes/No, then 1–10).

## Test flow (per document)

1. Open the demo and start a new conversation.
2. Send **iselect** → you receive Broadcast_1.
3. After ~45s you receive Poll_1 (Yes/No).
4. Reply **yes** → after ~10s Broadcast_2, then ~30s later Poll_2 (rate 1–10).
5. Reply **3** → you receive Broadcast_4 (rating ≤5). Reply **8** → Broadcast_5 (rating >5).
6. Reply **no** to Poll_1 → after ~15s you receive Broadcast_3.
7. Send **iexit** to deactivate.

## Tests

```bash
# Uses SQLite by default (no PostgreSQL required)
pip install -e ".[dev]"
pytest tests/ -v
```

## Project layout

- `app/main.py` – FastAPI app, lifespan, router registration.
- `app/config.py` – Settings (e.g. `DATABASE_URL`).
- `app/db.py` – SQLAlchemy engine and session.
- `app/models/` – Projects, TimingElements, Variables, MessageTemplates, Nodes, NodeConditions, Keywords, Participants, Messages, ParticipantVariables, NodeExecutionLog, ScheduledJobs.
- `app/core/engine.py` – Execute node, keyword handling, poll answer handling, condition evaluation.
- `app/core/scheduler.py` – Background scheduler for pending jobs.
- `app/routes/` – API (projects, participants/messages) and web (dashboard, demo chat).
- `app/seed/prototype.py` – Seed data for the Prototype project (Fig.19–Fig.24).
- `app/web/templates/` – Jinja2 templates (Materialize CSS).

SMS, Facebook, and webhooks are not integrated in this version; the engine is designed so adapters can be added later.
