"""validate order prices

Revision ID: 9c09e2beecdd
Revises: 96b1586a17cf
Create Date: 2026-08-30 14:52:29.660882

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '9c09e2beecdd'
down_revision: Union[str, Sequence[str], None] = '96b1586a17cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_orders_total_price_positive",
        "orders",
        "total_price > 0",
    )
    op.create_check_constraint(
        "ck_order_items_price_positive",
        "order_items",
        "price_at_purchase > 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_order_items_price_positive",
        "order_items",
        type_="check",
    )
    op.drop_constraint(
        "ck_orders_total_price_positive",
        "orders",
        type_="check",
    )
