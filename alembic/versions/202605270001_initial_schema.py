"""initial schema

Revision ID: 202605270001
Revises:
Create Date: 2026-05-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "202605270001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("google_place_id", sa.String(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("website", sa.String(), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_leads_user_id", "leads", ["user_id"])
    op.create_index("ix_leads_google_place_id", "leads", ["google_place_id"])
    op.create_index("ix_leads_name", "leads", ["name"])

    op.create_table(
        "lead_analyses",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("lead_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("opportunity_score", sa.Float(), nullable=True),
        sa.Column("diagnosis", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_lead_analyses_lead_id", "lead_analyses", ["lead_id"])
    op.create_index("ix_lead_analyses_user_id", "lead_analyses", ["user_id"])

    op.create_table(
        "pipeline_items",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("lead_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("stage", sa.String(length=40), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_pipeline_items_lead_id", "pipeline_items", ["lead_id"])
    op.create_index("ix_pipeline_items_user_id", "pipeline_items", ["user_id"])
    op.create_index("ix_pipeline_items_stage", "pipeline_items", ["stage"])


def downgrade() -> None:
    op.drop_index("ix_pipeline_items_stage", table_name="pipeline_items")
    op.drop_index("ix_pipeline_items_user_id", table_name="pipeline_items")
    op.drop_index("ix_pipeline_items_lead_id", table_name="pipeline_items")
    op.drop_table("pipeline_items")

    op.drop_index("ix_lead_analyses_user_id", table_name="lead_analyses")
    op.drop_index("ix_lead_analyses_lead_id", table_name="lead_analyses")
    op.drop_table("lead_analyses")

    op.drop_index("ix_leads_name", table_name="leads")
    op.drop_index("ix_leads_google_place_id", table_name="leads")
    op.drop_index("ix_leads_user_id", table_name="leads")
    op.drop_table("leads")
