"""Project API routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project
from app.schemas.project import ProjectResponse

router = APIRouter()


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    return db.query(Project).order_by(Project.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get project by id."""
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


@router.post("/{project_id}/seed-prototype")
def seed_prototype(project_id: str, db: Session = Depends(get_db)):
    """
    Seed prototype project data (Timing, Variables, MessageTemplates, Nodes, Keywords).
    Idempotent: if project already has nodes, skip.
    """
    from app.seed.prototype import seed_prototype_project
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    seed_prototype_project(db, project_id)
    return {"status": "ok", "message": "Prototype data seeded"}
