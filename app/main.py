"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI


def _ensure_seed_projects():
    """Create default demo projects and seed if not present."""
    from app.db import SessionLocal
    from app.models import Project
    from app.seed.prototype import seed_prototype_project
    from app.seed.ibuy_flow import seed_ibuy_flow_project
    from app.seed.longterm_demo import seed_longterm_demo_project

    db = SessionLocal()
    try:
        import uuid

        # Prototype project (Fig.19 flow)
        proto = db.query(Project).filter(Project.name == "Prototype").first()
        if not proto:
            proto = Project(
                id=str(uuid.uuid4()),
                name="Prototype",
                description="Prototype protocol",
                status="Active",
            )
            db.add(proto)
            db.commit()
            db.refresh(proto)
        seed_prototype_project(db, proto.id)

        # iBuy flow project
        ibuy = db.query(Project).filter(Project.name == "iBuy Flow").first()
        if not ibuy:
            ibuy = Project(
                id=str(uuid.uuid4()),
                name="iBuy Flow",
                description="iBuy keyword flow (account, gender, age, products).",
                status="Active",
            )
            db.add(ibuy)
            db.commit()
            db.refresh(ibuy)
        seed_ibuy_flow_project(db, ibuy.id)

        # Long-term Demo project (multi-day scheduling demo)
        longterm = db.query(Project).filter(Project.name == "Long-term Demo").first()
        if not longterm:
            longterm = Project(
                id=str(uuid.uuid4()),
                name="Long-term Demo",
                description="Multi-day scheduling demo (days compressed to minutes).",
                status="Active",
            )
            db.add(longterm)
            db.commit()
            db.refresh(longterm)
        seed_longterm_demo_project(db, longterm.id)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle."""
    from app.core.scheduler import start_scheduler, stop_scheduler
    _ensure_seed_projects()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="DashMessaging",
    description="Smart Chatbot Platform - Protocol Engine",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static and templates when web routes are added
# app.mount("/static", StaticFiles(directory="app/web/static"), name="static")
# templates = Jinja2Templates(directory="app/web/templates")


@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}


from app.routes import projects, participants, web, admin

app.include_router(web.router, tags=["web"])
app.include_router(admin.router, tags=["admin"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(participants.router, prefix="/api/participants", tags=["participants"])
