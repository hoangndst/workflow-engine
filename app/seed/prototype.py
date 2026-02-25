"""
Seed prototype project per Fig.19–Fig.24: Timing, Variables, MessageTemplates, Nodes, Keywords.
"""
import uuid
from sqlalchemy.orm import Session

from app.models import (
    Project,
    TimingElement,
    Variable,
    MessageTemplate,
    Node,
    NodeCondition,
    Keyword,
)


def seed_prototype_project(db: Session, project_id: str) -> None:
    """Idempotent seed for prototype project."""
    # If project already has nodes, we only ensure exit node/keyword exist.
    if db.query(Node).filter(Node.project_id == project_id).first():
        _ensure_prototype_exit(db, project_id)
        return
    # Timing elements (Fig.20)
    timings = {}
    for name, days, hours, minutes, seconds in [
        ("Instantly", 0, 0, 0, 0),
        ("10_Seconds", 0, 0, 0, 10),
        ("15_Seconds", 0, 0, 0, 15),
        ("30_Seconds", 0, 0, 0, 30),
        ("45_Seconds", 0, 0, 0, 45),
        ("1_Minute", 0, 0, 1, 0),
    ]:
        tid = str(uuid.uuid4())
        db.add(TimingElement(
            id=tid,
            project_id=project_id,
            name=name,
            direction="AFTER",
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        ))
        timings[name] = tid

    # Variables (Fig.21): Start_Date, Poll_1_Variable, Poll_2_Variable
    var_start = str(uuid.uuid4())
    var_poll1 = str(uuid.uuid4())
    var_poll2 = str(uuid.uuid4())
    db.add(Variable(id=var_start, project_id=project_id, name="Start_Date", type="DateTime", source="INTERNAL", is_system=True, is_agv=False))
    db.add(Variable(id=var_poll1, project_id=project_id, name="Poll_1_Variable", type="Text", source="INTERNAL", is_system=False, is_agv=False))
    db.add(Variable(id=var_poll2, project_id=project_id, name="Poll_2_Variable", type="Integer", source="INTERNAL", is_system=False, is_agv=False))

    # Message templates (Fig.22): Broadcast_1..5, Poll_1, Poll_2
    tpl_b1 = str(uuid.uuid4())
    tpl_b2 = str(uuid.uuid4())
    tpl_b3 = str(uuid.uuid4())
    tpl_b4 = str(uuid.uuid4())
    tpl_b5 = str(uuid.uuid4())
    tpl_p1 = str(uuid.uuid4())
    tpl_p2 = str(uuid.uuid4())
    db.add(MessageTemplate(id=tpl_b1, project_id=project_id, type="BROADCAST", name="Broadcast_1", text_en="Welcome! This is Broadcast 1.", text_es="¡Bienvenido! Este es Broadcast 1."))
    db.add(MessageTemplate(id=tpl_b2, project_id=project_id, type="BROADCAST", name="Broadcast_2", text_en="You said Yes. Here is Broadcast 2.", text_es="Dijiste Sí. Aquí está Broadcast 2."))
    db.add(MessageTemplate(id=tpl_b3, project_id=project_id, type="BROADCAST", name="Broadcast_3", text_en="You said No. Here is Broadcast 3.", text_es="Dijiste No. Aquí está Broadcast 3."))
    db.add(MessageTemplate(id=tpl_b4, project_id=project_id, type="BROADCAST", name="Broadcast_4", text_en="Thanks for rating 5 or below. Broadcast 4.", text_es="Gracias por puntuar 5 o menos. Broadcast 4."))
    db.add(MessageTemplate(id=tpl_b5, project_id=project_id, type="BROADCAST", name="Broadcast_5", text_en="Thanks for rating above 5. Broadcast 5.", text_es="Gracias por puntuar más de 5. Broadcast 5."))
    db.add(MessageTemplate(id=tpl_p1, project_id=project_id, type="POLL", name="Poll_1", text_en="Do you want to continue? (Yes/No)", text_es="¿Quieres continuar? (Sí/No)", variable_id=var_poll1, choices_en=["Yes", "No"], choices_es=["Sí", "No"]))
    db.add(MessageTemplate(id=tpl_p2, project_id=project_id, type="POLL", name="Poll_2", text_en="Rate from 1 to 10.", text_es="Califica del 1 al 10.", variable_id=var_poll2, choices_en=[str(i) for i in range(1, 11)], choices_es=[str(i) for i in range(1, 11)]))

    db.flush()

    # Nodes (Fig.23): Node_Start, Node_0..Node_5
    node_start = str(uuid.uuid4())
    node_0 = str(uuid.uuid4())
    node_1 = str(uuid.uuid4())
    node_2 = str(uuid.uuid4())
    node_3 = str(uuid.uuid4())
    node_4 = str(uuid.uuid4())
    node_5 = str(uuid.uuid4())

    db.add(Node(
        id=node_start,
        project_id=project_id,
        name="Node_Start",
        is_terminal=False,
        schedule_timing_id=timings["Instantly"],
        message_template_id=tpl_b1,
        activation_type="START_DATE",
        activation_datetime_var_id=var_start,
    ))
    db.add(Node(
        id=node_0,
        project_id=project_id,
        name="Node_0",
        is_terminal=False,
        schedule_timing_id=timings["45_Seconds"],
        message_template_id=tpl_p1,
        activation_type="AFTER_NODE",
        activation_source_node_id=node_start,
    ))
    db.add(Node(
        id=node_1,
        project_id=project_id,
        name="Node_1",
        is_terminal=True,
        schedule_timing_id=timings["15_Seconds"],
        message_template_id=tpl_b3,
        activation_type="AFTER_POLL",
        activation_poll_id=tpl_p1,
    ))
    db.add(Node(
        id=node_2,
        project_id=project_id,
        name="Node_2",
        is_terminal=False,
        schedule_timing_id=timings["10_Seconds"],
        message_template_id=tpl_b2,
        activation_type="AFTER_POLL",
        activation_poll_id=tpl_p1,
    ))
    db.add(Node(
        id=node_3,
        project_id=project_id,
        name="Node_3",
        is_terminal=False,
        schedule_timing_id=timings["30_Seconds"],
        message_template_id=tpl_p2,
        activation_type="AFTER_NODE",
        activation_source_node_id=node_2,
    ))
    db.add(Node(
        id=node_4,
        project_id=project_id,
        name="Node_4",
        is_terminal=True,
        schedule_timing_id=timings["Instantly"],
        message_template_id=tpl_b4,
        activation_type="AFTER_POLL",
        activation_poll_id=tpl_p2,
    ))
    db.add(Node(
        id=node_5,
        project_id=project_id,
        name="Node_5",
        is_terminal=True,
        schedule_timing_id=timings["Instantly"],
        message_template_id=tpl_b5,
        activation_type="AFTER_POLL",
        activation_poll_id=tpl_p2,
    ))
    db.flush()

    # Node conditions: Node_1 when Poll_1 = No; Node_2 when Poll_1 = Yes; Node_4 when Poll_2 <= 5; Node_5 when Poll_2 > 5
    db.add(NodeCondition(id=str(uuid.uuid4()), node_id=node_1, variable_id=var_poll1, operation="equal", expected_answer="no"))
    db.add(NodeCondition(id=str(uuid.uuid4()), node_id=node_2, variable_id=var_poll1, operation="equal", expected_answer="yes"))
    db.add(NodeCondition(id=str(uuid.uuid4()), node_id=node_4, variable_id=var_poll2, operation="lte", expected_answer="5"))
    db.add(NodeCondition(id=str(uuid.uuid4()), node_id=node_5, variable_id=var_poll2, operation="gt", expected_answer="5"))

    # Keywords (Fig.24): iselect -> activate + Node_Start, iexit -> deactivate
    db.add(Keyword(
        id=str(uuid.uuid4()),
        project_id=project_id,
        name="Enroll Participant (English)",
        keyword_text="iselect",
        language="English",
        action_type="ACTIVATE_PARTICIPANT",
        referenced_node_id=node_start,
        referenced_variable_id=var_start,
    ))
    db.add(Keyword(
        id=str(uuid.uuid4()),
        project_id=project_id,
        name="Exit Participant",
        keyword_text="iexit",
        language="English",
        action_type="DEACTIVATE_PARTICIPANT",
    ))
    db.commit()


def _ensure_prototype_exit(db: Session, project_id: str) -> None:
    """Ensure there is an exit node + message for keyword iexit."""
    # Find or create exit message template
    exit_tpl = (
        db.query(MessageTemplate)
        .filter(
            MessageTemplate.project_id == project_id,
            MessageTemplate.name == "Broadcast_Exit",
        )
        .first()
    )
    if not exit_tpl:
        exit_tpl = MessageTemplate(
            id=str(uuid.uuid4()),
            project_id=project_id,
            type="BROADCAST",
            name="Broadcast_Exit",
            text_en="You have exited the prototype flow. Thank you!",
            text_es="Has salido del flujo prototipo. ¡Gracias!",
        )
        db.add(exit_tpl)
        db.flush()

    # Find timing "Instantly"
    timing = (
        db.query(TimingElement)
        .filter(
            TimingElement.project_id == project_id,
            TimingElement.name == "Instantly",
        )
        .first()
    )

    # Find or create exit node
    exit_node = (
        db.query(Node)
        .filter(
            Node.project_id == project_id,
            Node.name == "Node_Exit",
        )
        .first()
    )
    if not exit_node:
        exit_node = Node(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name="Node_Exit",
            is_terminal=True,
            schedule_timing_id=timing.id if timing else None,
            message_template_id=exit_tpl.id,
            activation_type="AFTER_NODE",
        )
        db.add(exit_node)
        db.flush()

    # Update / create iexit keyword to reference this node
    kw = (
        db.query(Keyword)
        .filter(
            Keyword.project_id == project_id,
            Keyword.keyword_text == "iexit",
        )
        .first()
    )
    if not kw:
        kw = Keyword(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name="Exit Participant",
            keyword_text="iexit",
            language="English",
            action_type="DEACTIVATE_PARTICIPANT",
        )
        db.add(kw)
    kw.referenced_node_id = exit_node.id
    db.commit()
