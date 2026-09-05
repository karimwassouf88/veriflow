"""add vendors, purchase_orders, validation_results

Revision ID: e956b8c5b399
Revises: b00822676d00
Create Date: 2026-08-31 23:51:36.147934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e956b8c5b399'
down_revision: Union[str, Sequence[str], None] = 'b00822676d00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'VALIDATED'")
    op.execute("ALTER TYPE ingestionstatus ADD VALUE IF NOT EXISTS 'VALIDATION_ERROR'")

    op.create_table(
        "vendors",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tax_id", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_vendors_name", "vendors", ["name"])

    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("po_number", sa.String(50), nullable=False, unique=True),
        sa.Column("vendor_id", sa.Uuid(), sa.ForeignKey("vendors.id"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_purchase_orders_po_number", "purchase_orders", ["po_number"], unique=True)

    op.create_table(
        "validation_results",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("document_id", sa.Uuid(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("vendor_id", sa.Uuid(), sa.ForeignKey("vendors.id"), nullable=True),
        sa.Column("purchase_order_id", sa.Uuid(), sa.ForeignKey("purchase_orders.id"), nullable=True),
        sa.Column("vendor_status", sa.String(20), nullable=False),
        sa.Column("po_status", sa.String(20), nullable=False),
        sa.Column("amount_difference_pct", sa.Float(), nullable=True),
        sa.Column("summary", sa.String(1000), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_validation_results_document_id", "validation_results", ["document_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_validation_results_document_id", table_name="validation_results")
    op.drop_table("validation_results")
    op.drop_index("ix_purchase_orders_po_number", table_name="purchase_orders")
    op.drop_table("purchase_orders")
    op.drop_index("ix_vendors_name", table_name="vendors")
    op.drop_table("vendors")