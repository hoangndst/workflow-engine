"""Web UI demo routes - dashboard and participant chat."""
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project, Participant

router = APIRouter()
_templates_dir = (Path(__file__).resolve().parent.parent / "web" / "templates").resolve()
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard: list projects and link to prototype demo."""
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "projects": projects})


@router.get("/demo", response_class=RedirectResponse)
def demo_start(request: Request, db: Session = Depends(get_db)):
    """Start new conversation: create participant for selected project and redirect to chat."""
    project_id = request.query_params.get("project_id")
    if project_id:
        proj = db.query(Project).filter(Project.id == project_id).first()
    else:
        proj = db.query(Project).filter(Project.name == "Prototype").first()
        if not proj:
            proj = db.query(Project).first()
    if not proj:
        return RedirectResponse(url="/", status_code=302)
    p = Participant(
        id=str(uuid.uuid4()),
        project_id=proj.id,
        language="English",
        status="ACTIVE",
    )
    db.add(p)
    db.commit()
    return RedirectResponse(url=f"/demo/{p.id}", status_code=302)


@router.get("/demo/{participant_id}", response_class=HTMLResponse)
def demo_chat(request: Request, participant_id: str, db: Session = Depends(get_db)):
    """Participant chat UI: message thread and input."""
    p = db.query(Participant).filter(Participant.id == participant_id).first()
    if not p:
        return RedirectResponse(url="/", status_code=302)
    project = db.query(Project).filter(Project.id == p.project_id).first()
    project_name = project.name if project else "DashMessaging"

    # Dynamic hint text per project/flow
    if project_name == "Prototype":
        hint = (
            'Send "iselect" to start the prototype flow, "iexit" to exit. '
            "Reply to polls with Yes/No or a number 1–10."
        )
        placeholder = 'Type message (e.g. iselect)'
    elif project_name == "iBuy Flow":
        hint = (
            'Send "ibuy" to start the iBuy flow, "iexit" to exit. '
            "Answer account question with Yes/No, then gender (Male/Female) and age (number)."
        )
        placeholder = 'Type message (e.g. ibuy)'
    elif project_name == "Long-term Demo":
        hint = (
            'Send "ilongterm" to start the long-term scheduling demo, "iexit" to exit. '
            "Then wait to see Day 1/2/3 messages arrive over time."
        )
        placeholder = 'Type message (e.g. ilongterm)'
    else:
        hint = (
            'Send the appropriate keyword to start (e.g. "iselect", "ibuy"), '
            'and "iexit" to exit. Reply to questions as instructed.'
        )
        placeholder = 'Type message...'

    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "participant_id": participant_id,
            "language": p.language or "English",
            "project_name": project_name,
            "hint_text": hint,
            "input_placeholder": placeholder,
        },
    )
