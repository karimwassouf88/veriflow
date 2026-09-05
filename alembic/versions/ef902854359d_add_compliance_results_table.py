"""add compliance results table

Revision ID: ef902854359d
Revises: e956b8c5b399
Create Date: 2026-09-03 11:30:49.794208

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef902854359d'
down_revision: Union[str, Sequence[str], None] = 'e956b8c5b399'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'COMPLIANCE_CHECKED'")
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'COMPLIANCE_ERROR'")

    op.create_table(
        "compliance_results",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("compliant", sa.Boolean(), nullable=False),
        sa.Column("required_approval_level", sa.String(50), nullable=False),
        sa.Column("reasoning", sa.String(2000), nullable=False),
        sa.Column("policy_sources", sa.String(1000), nullable=True),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_compliance_results_document_id", "compliance_results", ["document_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_compliance_results_document_id", table_name="compliance_results")
    op.drop_table("compliance_results")