"""add extraction fields and document_extractions table

Revision ID: b285a244777e
Revises: 3125612776b9
Create Date: 2026-08-27 22:03:17.602332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b285a244777e'
down_revision: Union[str, Sequence[str], None] = '3125612776b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'processing'")
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'extracted'")
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'extraction_failed'")

    op.create_table(
        "document_extractions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("field_name", sa.String(50), nullable=False),
        sa.Column("extracted_value", sa.String(500), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_document_extractions_document_id", "document_extractions", ["document_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_document_extractions_document_id", table_name="document_extractions")
    op.drop_table("document_extractions")
    # Postgres can't remove enum values, so the ADD VALUE calls above aren't reversible here