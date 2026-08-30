"""validate user roles

Revision ID: 323e7b9db92f
Revises: 99d5203f2d6f
Create Date: 2026-08-29 23:15:47.912615

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '323e7b9db92f'
down_revision: Union[str, Sequence[str], None] = '99d5203f2d6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_users_role_valid",
        "users",
        "role IN ('customer', 'admin')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_users_role_valid",
        "users",
        type_="check",
    )
