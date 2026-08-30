"""validate flavors and cart quantities

Revision ID: 3c634de370f5
Revises: 8cb49ddbd76d
Create Date: 2026-08-30 15:36:01.017187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c634de370f5'
down_revision: Union[str, Sequence[str], None] = '8cb49ddbd76d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_flavors_name_length",
        "flavors",
        "length(btrim(name)) BETWEEN 1 AND 100",
    )
    op.create_check_constraint(
        "ck_flavors_description_length",
        "flavors",
        "length(btrim(description)) BETWEEN 1 AND 1000",
    )
    op.create_check_constraint(
        "ck_cart_items_quantity_max",
        "cart_items",
        "quantity <= 100",
    )
    op.create_check_constraint(
        "ck_order_items_quantity_max",
        "order_items",
        "quantity <= 100",
    )
    op.create_index('uq_flavors_name_lower', 'flavors', [sa.literal_column('lower(name)')], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('uq_flavors_name_lower', table_name='flavors')
    op.drop_constraint(
        "ck_order_items_quantity_max",
        "order_items",
        type_="check",
    )
    op.drop_constraint(
        "ck_cart_items_quantity_max",
        "cart_items",
        type_="check",
    )
    op.drop_constraint(
        "ck_flavors_description_length",
        "flavors",
        type_="check",
    )
    op.drop_constraint(
        "ck_flavors_name_length",
        "flavors",
        type_="check",
    )
