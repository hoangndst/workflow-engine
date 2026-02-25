"""Initial schema - projects, timing, variables, templates, nodes, keywords, participants.

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "timing_elements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("direction", sa.String(20), nullable=True),
        sa.Column("days", sa.Integer(), nullable=True),
        sa.Column("hours", sa.Integer(), nullable=True),
        sa.Column("minutes", sa.Integer(), nullable=True),
        sa.Column("seconds", sa.Integer(), nullable=True),
    )
    op.create_table(
        "variables",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=True),
        sa.Column("is_agv", sa.Boolean(), nullable=True),
    )
    op.create_table(
        "message_templates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("text_en", sa.Text(), nullable=True),
        sa.Column("text_es", sa.Text(), nullable=True),
        sa.Column("variable_id", sa.String(36), sa.ForeignKey("variables.id", ondelete="SET NULL"), nullable=True),
        sa.Column("choices_en", sa.JSON(), nullable=True),
        sa.Column("choices_es", sa.JSON(), nullable=True),
    )
    op.create_table(
        "nodes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("is_terminal", sa.Boolean(), nullable=True),
        sa.Column("schedule_timing_id", sa.String(36), sa.ForeignKey("timing_elements.id", ondelete="SET NULL"), nullable=True),
        sa.Column("message_template_id", sa.String(36), sa.ForeignKey("message_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("activation_type", sa.String(50), nullable=False),
        sa.Column("activation_source_node_id", sa.String(36), sa.ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("activation_poll_id", sa.String(36), sa.ForeignKey("message_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("activation_datetime_var_id", sa.String(36), sa.ForeignKey("variables.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_table(
        "node_conditions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("node_id", sa.String(36), sa.ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("poll_template_id", sa.String(36), sa.ForeignKey("message_templates.id", ondelete="CASCADE"), nullable=True),
        sa.Column("variable_id", sa.String(36), sa.ForeignKey("variables.id", ondelete="CASCADE"), nullable=True),
        sa.Column("operation", sa.String(20), nullable=False),
        sa.Column("expected_answer", sa.Text(), nullable=True),
    )
    op.create_table(
        "keywords",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("keyword_text", sa.String(255), nullable=False),
        sa.Column("language", sa.String(20), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("referenced_node_id", sa.String(36), sa.ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("referenced_variable_id", sa.String(36), sa.ForeignKey("variables.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_table(
        "participants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("language", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "participant_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("participant_id", sa.String(36), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("direction", sa.String(20), nullable=False),
        sa.Column("message_template_id", sa.String(36), sa.ForeignKey("message_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "participant_variables",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("participant_id", sa.String(36), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("variable_id", sa.String(36), sa.ForeignKey("variables.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("value_int", sa.Integer(), nullable=True),
        sa.Column("value_datetime", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "node_execution_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("participant_id", sa.String(36), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_id", sa.String(36), sa.ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("executed_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "scheduled_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("participant_id", sa.String(36), sa.ForeignKey("participants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("node_id", sa.String(36), sa.ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("scheduled_jobs")
    op.drop_table("node_execution_logs")
    op.drop_table("participant_variables")
    op.drop_table("participant_messages")
    op.drop_table("participants")
    op.drop_table("keywords")
    op.drop_table("node_conditions")
    op.drop_table("nodes")
    op.drop_table("message_templates")
    op.drop_table("variables")
    op.drop_table("timing_elements")
    op.drop_table("projects")
