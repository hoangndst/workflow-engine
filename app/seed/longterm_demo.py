"""
Seed a Long-term Demo project to showcase multi-day scheduling
(compressed to minutes for demo).

Flow:
- Keyword: ilongterm
- Immediately: Welcome message.
- \"Day 1\" message after a short delay.
- \"Day 2\" message after another delay.
- \"Day 3 09:00\" style message after a longer delay.

In production these delays would be days/hours; in the demo we
approximate days with minutes so the flow can be observed quickly.
"""
import uuid
from sqlalchemy.orm import Session

from app.models import TimingElement, Variable, MessageTemplate, Node, Keyword


def seed_longterm_demo_project(db: Session, project_id: str) -> None:
    """Idempotent seed for Long-term Demo flow."""
    # If project already has nodes, assume it was seeded.
    if db.query(Node).filter(Node.project_id == project_id).first():
        return

    # Timing elements (demo: minutes instead of real days)
    timings: dict[str, str] = {}
    for name, days, hours, minutes, seconds in [
        ("Instantly", 0, 0, 0, 0),
        # Demo \"1 day\" ~ 1 minute
        ("Demo_Day", 0, 0, 1, 0),
        # Demo \"Day 3 09:00\" ~ 2 minutes
        ("Demo_Day3_09h", 0, 0, 2, 0),
    ]:
        tid = str(uuid.uuid4())
        db.add(
            TimingElement(
                id=tid,
                project_id=project_id,
                name=name,
                direction="AFTER",
                days=days,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
            )
        )
        timings[name] = tid

    # Variables: Start_Date to anchor scheduling
    var_start = str(uuid.uuid4())
    db.add(
        Variable(
            id=var_start,
            project_id=project_id,
            name="Start_Date",
            type="DateTime",
            source="INTERNAL",
            is_system=True,
            is_agv=False,
        )
    )

    # Message templates for each \"day\"
    tpl_welcome = str(uuid.uuid4())
    tpl_day1 = str(uuid.uuid4())
    tpl_day2 = str(uuid.uuid4())
    tpl_day3 = str(uuid.uuid4())

    db.add(
        MessageTemplate(
            id=tpl_welcome,
            project_id=project_id,
            type="BROADCAST",
            name="LT_Welcome",
            text_en="Welcome to the long-term demo! This simulates messages over several days.",
            text_es="¡Bienvenido a la demo a largo plazo! Esto simula mensajes durante varios días.",
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_day1,
            project_id=project_id,
            type="BROADCAST",
            name="LT_Day1",
            text_en="[Day 1] Thanks for staying with us. This is your first follow-up message.",
            text_es="[Día 1] Gracias por seguir con nosotros. Este es tu primer mensaje de seguimiento.",
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_day2,
            project_id=project_id,
            type="BROADCAST",
            name="LT_Day2",
            text_en="[Day 2] Here is your second follow-up message.",
            text_es="[Día 2] Este es tu segundo mensaje de seguimiento.",
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_day3,
            project_id=project_id,
            type="BROADCAST",
            name="LT_Day3_09h",
            text_en="[Day 3, 09:00] Morning reminder from the long-term demo.",
            text_es="[Día 3, 09:00] Recordatorio matutino de la demo a largo plazo.",
        )
    )

    db.flush()

    # Nodes chained by timing (Start -> Day1 -> Day2 -> Day3)
    n_start = str(uuid.uuid4())
    n_day1 = str(uuid.uuid4())
    n_day2 = str(uuid.uuid4())
    n_day3 = str(uuid.uuid4())

    db.add(
        Node(
            id=n_start,
            project_id=project_id,
            name="LT_Node_Start",
            is_terminal=False,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_welcome,
            activation_type="START_DATE",
            activation_datetime_var_id=var_start,
        )
    )
    db.add(
        Node(
            id=n_day1,
            project_id=project_id,
            name="LT_Node_Day1",
            is_terminal=False,
            schedule_timing_id=timings["Demo_Day"],
            message_template_id=tpl_day1,
            activation_type="AFTER_NODE",
            activation_source_node_id=n_start,
        )
    )
    db.add(
        Node(
            id=n_day2,
            project_id=project_id,
            name="LT_Node_Day2",
            is_terminal=False,
            schedule_timing_id=timings["Demo_Day"],
            message_template_id=tpl_day2,
            activation_type="AFTER_NODE",
            activation_source_node_id=n_day1,
        )
    )
    db.add(
        Node(
            id=n_day3,
            project_id=project_id,
            name="LT_Node_Day3_09h",
            is_terminal=True,
            schedule_timing_id=timings["Demo_Day3_09h"],
            message_template_id=tpl_day3,
            activation_type="AFTER_NODE",
            activation_source_node_id=n_day2,
        )
    )

    db.flush()

    # Keyword to activate this flow
    db.add(
        Keyword(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name="Enroll Long-term Demo",
            keyword_text="ilongterm",
            language="English",
            action_type="ACTIVATE_PARTICIPANT",
            referenced_node_id=n_start,
            referenced_variable_id=var_start,
        )
    )

    # Simple exit keyword (reuse generic exit handling)
    db.add(
        Keyword(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name="Exit Long-term Demo",
            keyword_text="iexit",
            language="English",
            action_type="DEACTIVATE_PARTICIPANT",
        )
    )

    db.commit()

