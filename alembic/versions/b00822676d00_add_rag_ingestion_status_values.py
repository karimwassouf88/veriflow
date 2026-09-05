"""add rag ingestion status values

Revision ID: b00822676d00
Revises: 1432bd2e6225
Create Date: 2026-08-30 19:17:08.795228

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b00822676d00'
down_revision: Union[str, Sequence[str], None] = '1432bd2e6225'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'RAG_INGESTED'")
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'RAG_INGESTION_FAILED'")


def downgrade() -> None:
    """Downgrade schema."""
    pass  # Postgres can't remove enum values