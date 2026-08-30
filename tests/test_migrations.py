from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from backend.database import engine


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_latest_migration_can_downgrade_and_upgrade():
    config = Config(str(PROJECT_ROOT / "alembic.ini"))

    try:
        command.downgrade(config, "-1")
        columns = {
            column["name"]
            for column in inspect(engine).get_columns("order_items")
        }
        assert "flavor_name_at_purchase" not in columns
    finally:
        command.upgrade(config, "head")

    columns = {
        column["name"]
        for column in inspect(engine).get_columns("order_items")
    }
    assert "flavor_name_at_purchase" in columns
