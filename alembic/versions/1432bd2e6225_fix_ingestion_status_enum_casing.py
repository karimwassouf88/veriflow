"""fix ingestion status enum casing

Revision ID: 1432bd2e6225
Revises: b285a244777e
Create Date: 2026-08-28 00:29:52.970322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1432bd2e6225'
down_revision: Union[str, Sequence[str], None] = 'b285a244777e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'PROCESSING'")
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'EXTRACTED'")
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'EXTRACTION_FAILED'")


def downgrade() -> None:
    """Downgrade schema."""
    pass  # Postgres can't remove enum values