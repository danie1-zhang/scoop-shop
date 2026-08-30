"""snapshot flavor names on order items

Revision ID: 54e61d6e019b
Revises: 3c634de370f5
Create Date: 2026-08-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "54e61d6e019b"
down_revision: Union[str, Sequence[str], None] = "3c634de370f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add and backfill the immutable flavor-name snapshot."""
    op.add_column(
        "order_items",
        sa.Column("flavor_name_at_purchase", sa.String(length=100), nullable=True),
    )
    op.execute(
        """
        UPDATE order_items
        SET flavor_name_at_purchase = flavors.name
        FROM flavors
        WHERE order_items.flavor_id = flavors.id
        """
    )
    op.alter_column(
        "order_items",
        "flavor_name_at_purchase",
        existing_type=sa.String(length=100),
        nullable=False,
    )


def downgrade() -> None:
    """Remove the flavor-name snapshot."""
    op.drop_column("order_items", "flavor_name_at_purchase")
