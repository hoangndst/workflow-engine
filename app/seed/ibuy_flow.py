"""
Seed iBuy keyword-based flow:

Flow (simplified):
- Keyword: ibuy
- B: Welcome
- P: Have an account? (Yes/No)
  - Yes  -> B: Please use your account (end)
  - No   -> P: Gender (Male/Female)
           -> P: Age (number)
             - Age > 18 and Female -> Home Products
             - Age > 18 and Male   -> Car Products
             - Age < 18 and Male   -> Clothes
             - Age < 18 and Female -> Beauty Products
"""
import uuid
from sqlalchemy.orm import Session

from app.models import (
    TimingElement,
    Variable,
    MessageTemplate,
    Node,
    NodeCondition,
    Keyword,
)


def seed_ibuy_flow_project(db: Session, project_id: str) -> None:
    """Idempotent seed for iBuy flow."""
    # If project already has nodes, only make sure exit node/keyword exist.
    if db.query(Node).filter(Node.project_id == project_id).first():
        _ensure_ibuy_exit(db, project_id)
        return

    # Timing elements: reuse same pattern as prototype
    timings: dict[str, str] = {}
    for name, days, hours, minutes, seconds in [
        ("Instantly", 0, 0, 0, 0),
        ("Short", 0, 0, 0, 2),
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

    # Variables: Start_Date, HasAccount, Gender, Age
    var_start = str(uuid.uuid4())
    var_has_account = str(uuid.uuid4())
    var_gender = str(uuid.uuid4())
    var_age = str(uuid.uuid4())

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
    db.add(
        Variable(
            id=var_has_account,
            project_id=project_id,
            name="HasAccount_Var",
            type="Text",
            source="INTERNAL",
            is_system=False,
            is_agv=False,
        )
    )
    db.add(
        Variable(
            id=var_gender,
            project_id=project_id,
            name="Gender_Var",
            type="Text",
            source="INTERNAL",
            is_system=False,
            is_agv=False,
        )
    )
    db.add(
        Variable(
            id=var_age,
            project_id=project_id,
            name="Age_Var",
            type="Integer",
            source="INTERNAL",
            is_system=False,
            is_agv=False,
        )
    )

    # Message templates
    tpl_welcome = str(uuid.uuid4())
    tpl_have_acc = str(uuid.uuid4())
    tpl_use_acc = str(uuid.uuid4())
    tpl_gender = str(uuid.uuid4())
    tpl_age = str(uuid.uuid4())
    tpl_home = str(uuid.uuid4())
    tpl_car = str(uuid.uuid4())
    tpl_clothes = str(uuid.uuid4())
    tpl_beauty = str(uuid.uuid4())

    db.add(
        MessageTemplate(
            id=tpl_welcome,
            project_id=project_id,
            type="BROADCAST",
            name="B_Welcome",
            text_en="Welcome to iBuy! Let's find the best products for you.",
            text_es="¡Bienvenido a iBuy! Busquemos los mejores productos para ti.",
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_have_acc,
            project_id=project_id,
            type="POLL",
            name="P_HaveAccount",
            text_en="Do you already have an account? (Yes/No)",
            text_es="¿Ya tienes una cuenta? (Sí/No)",
            variable_id=var_has_account,
            choices_en=["Yes", "No"],
            choices_es=["Sí", "No"],
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_use_acc,
            project_id=project_id,
            type="BROADCAST",
            name="B_PleaseUseAccount",
            text_en="Great! Please continue using your existing account.",
            text_es="¡Genial! Por favor sigue usando tu cuenta existente.",
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_gender,
            project_id=project_id,
            type="POLL",
            name="P_Gender",
            text_en="What is your gender? (Male/Female)",
            text_es="¿Cuál es tu género? (Masculino/Femenino)",
            variable_id=var_gender,
            choices_en=["Male", "Female"],
            choices_es=["Masculino", "Femenino"],
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_age,
            project_id=project_id,
            type="POLL",
            name="P_Age",
            text_en="How old are you? (Enter a number)",
            text_es="¿Cuántos años tienes? (Introduce un número)",
            variable_id=var_age,
            choices_en=[str(i) for i in range(5, 91)],
            choices_es=[str(i) for i in range(5, 91)],
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_home,
            project_id=project_id,
            type="BROADCAST",
            name="B_HomeProducts",
            text_en="We recommend our Home Products for you.",
            text_es="Te recomendamos nuestros productos para el hogar.",
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_car,
            project_id=project_id,
            type="BROADCAST",
            name="B_CarProducts",
            text_en="We recommend our Car Products for you.",
            text_es="Te recomendamos nuestros productos para el automóvil.",
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_clothes,
            project_id=project_id,
            type="BROADCAST",
            name="B_Clothes",
            text_en="We recommend our Clothes collection for you.",
            text_es="Te recomendamos nuestra colección de ropa.",
        )
    )
    db.add(
        MessageTemplate(
            id=tpl_beauty,
            project_id=project_id,
            type="BROADCAST",
            name="B_BeautyProducts",
            text_en="We recommend our Beauty Products for you.",
            text_es="Te recomendamos nuestros productos de belleza.",
        )
    )

    db.flush()

    # Nodes
    n_start = str(uuid.uuid4())
    n_have_acc = str(uuid.uuid4())
    n_use_acc = str(uuid.uuid4())
    n_gender = str(uuid.uuid4())
    n_age = str(uuid.uuid4())
    n_home = str(uuid.uuid4())
    n_car = str(uuid.uuid4())
    n_clothes = str(uuid.uuid4())
    n_beauty = str(uuid.uuid4())

    db.add(
        Node(
            id=n_start,
            project_id=project_id,
            name="N_Welcome",
            is_terminal=False,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_welcome,
            activation_type="START_DATE",
            activation_datetime_var_id=var_start,
        )
    )
    db.add(
        Node(
            id=n_have_acc,
            project_id=project_id,
            name="N_HaveAccount",
            is_terminal=False,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_have_acc,
            activation_type="AFTER_NODE",
            activation_source_node_id=n_start,
        )
    )
    db.add(
        Node(
            id=n_use_acc,
            project_id=project_id,
            name="N_PleaseUseAccount",
            is_terminal=True,
            schedule_timing_id=timings["Short"],
            message_template_id=tpl_use_acc,
            activation_type="AFTER_POLL",
            activation_poll_id=tpl_have_acc,
        )
    )
    db.add(
        Node(
            id=n_gender,
            project_id=project_id,
            name="N_Gender",
            is_terminal=False,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_gender,
            activation_type="AFTER_POLL",
            activation_poll_id=tpl_have_acc,
        )
    )
    db.add(
        Node(
            id=n_age,
            project_id=project_id,
            name="N_Age",
            is_terminal=False,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_age,
            activation_type="AFTER_POLL",
            activation_poll_id=tpl_gender,
        )
    )
    db.add(
        Node(
            id=n_home,
            project_id=project_id,
            name="N_HomeProducts",
            is_terminal=True,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_home,
            activation_type="AFTER_POLL",
            activation_poll_id=tpl_age,
        )
    )
    db.add(
        Node(
            id=n_car,
            project_id=project_id,
            name="N_CarProducts",
            is_terminal=True,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_car,
            activation_type="AFTER_POLL",
            activation_poll_id=tpl_age,
        )
    )
    db.add(
        Node(
            id=n_clothes,
            project_id=project_id,
            name="N_Clothes",
            is_terminal=True,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_clothes,
            activation_type="AFTER_POLL",
            activation_poll_id=tpl_age,
        )
    )
    db.add(
        Node(
            id=n_beauty,
            project_id=project_id,
            name="N_BeautyProducts",
            is_terminal=True,
            schedule_timing_id=timings["Instantly"],
            message_template_id=tpl_beauty,
            activation_type="AFTER_POLL",
            activation_poll_id=tpl_age,
        )
    )

    db.flush()

    # Conditions
    # Have account? Yes -> Please use account
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_use_acc,
            variable_id=var_has_account,
            operation="equal",
            expected_answer="yes",
        )
    )
    # Have account? No -> Gender
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_gender,
            variable_id=var_has_account,
            operation="equal",
            expected_answer="no",
        )
    )
    # Age/Gender splits
    # Home Products: Age > 18 and Female
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_home,
            variable_id=var_gender,
            operation="equal",
            expected_answer="female",
        )
    )
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_home,
            variable_id=var_age,
            operation="gt",
            expected_answer="18",
        )
    )
    # Car Products: Age > 18 and Male
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_car,
            variable_id=var_gender,
            operation="equal",
            expected_answer="male",
        )
    )
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_car,
            variable_id=var_age,
            operation="gt",
            expected_answer="18",
        )
    )
    # Clothes: Age < 18 and Male
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_clothes,
            variable_id=var_gender,
            operation="equal",
            expected_answer="male",
        )
    )
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_clothes,
            variable_id=var_age,
            operation="lt",
            expected_answer="18",
        )
    )
    # Beauty Products: Age < 18 and Female
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_beauty,
            variable_id=var_gender,
            operation="equal",
            expected_answer="female",
        )
    )
    db.add(
        NodeCondition(
            id=str(uuid.uuid4()),
            node_id=n_beauty,
            variable_id=var_age,
            operation="lt",
            expected_answer="18",
        )
    )

    # Keywords: ibuy start, iexit stop
    db.add(
        Keyword(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name="Enroll iBuy Flow",
            keyword_text="ibuy",
            language="English",
            action_type="ACTIVATE_PARTICIPANT",
            referenced_node_id=n_start,
            referenced_variable_id=var_start,
        )
    )
    db.add(
        Keyword(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name="Exit iBuy Flow",
            keyword_text="iexit",
            language="English",
            action_type="DEACTIVATE_PARTICIPANT",
        )
    )
    db.commit()

    _ensure_ibuy_exit(db, project_id)


def _ensure_ibuy_exit(db: Session, project_id: str) -> None:
    """Ensure iBuy flow has an exit node + message for iexit keyword."""
    # Try to find an existing exit template/node by name
    exit_tpl = (
        db.query(MessageTemplate)
        .filter(
            MessageTemplate.project_id == project_id,
            MessageTemplate.name == "B_Exit_iBuy",
        )
        .first()
    )
    if not exit_tpl:
        exit_tpl = MessageTemplate(
            id=str(uuid.uuid4()),
            project_id=project_id,
            type="BROADCAST",
            name="B_Exit_iBuy",
            text_en="You have exited the iBuy flow. See you next time!",
            text_es="Has salido del flujo iBuy. ¡Hasta la próxima!",
        )
        db.add(exit_tpl)
        db.flush()

    timing = (
        db.query(TimingElement)
        .filter(
            TimingElement.project_id == project_id,
            TimingElement.name == "Instantly",
        )
        .first()
    )

    exit_node = (
        db.query(Node)
        .filter(
            Node.project_id == project_id,
            Node.name == "N_Exit_iBuy",
        )
        .first()
    )
    if not exit_node:
        exit_node = Node(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name="N_Exit_iBuy",
            is_terminal=True,
            schedule_timing_id=timing.id if timing else None,
            message_template_id=exit_tpl.id,
            activation_type="AFTER_NODE",
        )
        db.add(exit_node)
        db.flush()

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
            name="Exit iBuy Flow",
            keyword_text="iexit",
            language="English",
            action_type="DEACTIVATE_PARTICIPANT",
        )
        db.add(kw)
    kw.referenced_node_id = exit_node.id
    db.commit()
