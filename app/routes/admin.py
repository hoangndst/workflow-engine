"""Admin UI routes for inspecting project configuration (Timing, Variables, Templates, Nodes, Keywords)."""
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Project, TimingElement, Variable, MessageTemplate, Node, Keyword, NodeCondition


router = APIRouter()
_templates_dir = (Path(__file__).resolve().parent.parent / "web" / "templates").resolve()
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/admin/projects/{project_id}", response_class=HTMLResponse)
def admin_project(request: Request, project_id: str, db: Session = Depends(get_db)):
    """Read-only admin view of a project's core entities."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/", status_code=302)

    timings = (
        db.query(TimingElement)
        .filter(TimingElement.project_id == project_id)
        .order_by(TimingElement.name.asc())
        .all()
    )
    variables = (
        db.query(Variable)
        .filter(Variable.project_id == project_id)
        .order_by(Variable.name.asc())
        .all()
    )
    templates_q = (
        db.query(MessageTemplate)
        .filter(MessageTemplate.project_id == project_id)
        .order_by(MessageTemplate.name.asc())
        .all()
    )
    nodes = db.query(Node).filter(Node.project_id == project_id).order_by(Node.name.asc()).all()
    keywords = db.query(Keyword).filter(Keyword.project_id == project_id).order_by(Keyword.keyword_text.asc()).all()

    # Build a lightweight edge list to visualize node connections (for table)
    node_by_id = {n.id: n for n in nodes}
    tpl_by_id = {t.id: t for t in templates_q}
    timing_by_id = {t.id: t for t in timings}
    vars_by_id = {v.id: v for v in variables}

    edges = []
    for n in nodes:
        activation = n.activation_type or ""
        from_label = ""
        if activation == "AFTER_NODE" and n.activation_source_node_id:
            src = node_by_id.get(n.activation_source_node_id)
            from_label = src.name if src else n.activation_source_node_id
        elif activation == "AFTER_POLL" and n.activation_poll_id:
            poll_tpl = tpl_by_id.get(n.activation_poll_id)
            from_label = poll_tpl.name if poll_tpl else n.activation_poll_id
        elif activation == "START_DATE":
            from_label = "Start_Date"
        elif activation == "AFTER_DATE_TIME_VAR" and n.activation_datetime_var_id:
            var = vars_by_id.get(n.activation_datetime_var_id)
            from_label = var.name if var else "DateTimeVar"

        timing = timing_by_id.get(n.schedule_timing_id) if n.schedule_timing_id else None
        timing_label = timing.name if timing else ""

        # Conditions summary for this node (if any)
        conds = db.query(NodeCondition).filter(NodeCondition.node_id == n.id).all()
        if conds:
            cond_strs = []
            for c in conds:
                var = vars_by_id.get(c.variable_id)
                var_name = var.name if var else c.variable_id
                cond_strs.append(f"{var_name} {c.operation} {c.expected_answer}")
            cond_label = "; ".join(cond_strs)
        else:
            cond_label = "Always"

        edges.append(
            {
                "from": from_label or "(start)",
                "to": n.name,
                "activation": activation,
                "timing": timing_label,
                "condition": cond_label,
            }
        )

    # Build Cytoscape elements: only NODE_x connected by flow edges
    graph_elements = []

    has_start = any((n.activation_type or "") == "START_DATE" for n in nodes)
    if has_start:
        graph_elements.append(
            {
                "data": {"id": "start_root", "label": "Start_Date", "kind": "start"},
            }
        )

    # Precompute mapping from poll template to node (for AFTER_POLL edges)
    node_by_template_id = {}
    for n in nodes:
        if n.message_template_id:
            node_by_template_id.setdefault(n.message_template_id, n)

    # Create node elements
    for n in nodes:
        graph_elements.append(
            {
                "data": {
                    "id": n.id,
                    "label": n.name,
                    "kind": "node",
                }
            }
        )

    # Flow edges between nodes according to activation
    for n in nodes:
        activation = n.activation_type or ""
        src_id = None
        if activation == "AFTER_NODE" and n.activation_source_node_id:
            src_id = n.activation_source_node_id
        elif activation == "AFTER_POLL" and n.activation_poll_id:
            poll_node = node_by_template_id.get(n.activation_poll_id)
            if poll_node:
                src_id = poll_node.id
        elif activation == "START_DATE" and has_start:
            src_id = "start_root"

        if not src_id:
            continue

        timing = timing_by_id.get(n.schedule_timing_id) if n.schedule_timing_id else None
        timing_label = timing.name if timing else ""

        # Find matching table edge to reuse its condition label
        cond_label = ""
        for e in edges:
            if e["to"] == n.name:
                cond_label = e["condition"]
                break
        label_parts: list[str] = []
        if timing_label:
            label_parts.append(timing_label)
        if cond_label and cond_label != "Always":
            label_parts.append(cond_label)
        flow_label = " • ".join(label_parts)

        graph_elements.append(
            {
                "data": {
                    "id": f"edge_flow_{n.id}",
                    "source": src_id,
                    "target": n.id,
                    "kind": "flowEdge",
                    "label": flow_label,
                }
            }
        )

    # Map node -> template details for click inspection
    node_templates = {}
    for n in nodes:
        tpl = tpl_by_id.get(n.message_template_id)
        if tpl:
            node_templates[n.name] = {
                "template_name": tpl.name,
                "type": tpl.type,
                "text_en": tpl.text_en,
                "text_es": tpl.text_es,
            }

    return templates.TemplateResponse(
        "admin_project.html",
        {
            "request": request,
            "project": project,
            "timings": timings,
            "variables": variables,
            "templates": templates_q,
            "nodes": nodes,
            "keywords": keywords,
            "edges": edges,
            "graph_elements": graph_elements,
            "node_templates": node_templates,
        },
    )

