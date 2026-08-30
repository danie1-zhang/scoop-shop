import os
from decimal import Decimal
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is required to run backend tests")

database_name = make_url(TEST_DATABASE_URL).database or ""
if not database_name.endswith("_test"):
    raise RuntimeError(
        "Refusing to run tests unless TEST_DATABASE_URL names a *_test database"
    )

# backend.config reads DATABASE_URL during import. Point this pytest process at
# the isolated test database before importing the application.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from backend.auth import hash_password  # noqa: E402
from backend.database import SessionLocal, engine  # noqa: E402
from backend.dependencies import get_db  # noqa: E402
from backend.main import app, order_attempts  # noqa: E402
from backend.models import Flavor, User  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    """Rebuild only the dedicated test schema and apply every migration."""
    with engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as connection:
        connection.exec_driver_sql("DROP SCHEMA public CASCADE")
        connection.exec_driver_sql("CREATE SCHEMA public")

    alembic_config = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(alembic_config, "head")
    yield


@pytest.fixture(autouse=True)
def clean_database(migrated_database):
    """Give every test empty application tables and fresh primary-key IDs."""
    with engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE order_items, orders, cart_items, flavors, users "
                "RESTART IDENTITY CASCADE"
            )
        )
    order_attempts.clear()
    yield
    order_attempts.clear()


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def create_user(db: Session):
    def factory(
        email: str,
        *,
        password: str = "password123",
        role: str = "customer",
    ) -> User:
        user = User(
            email=email.lower(),
            password_hash=hash_password(password),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return factory


@pytest.fixture
def auth_headers(client: TestClient, create_user):
    def factory(
        email: str,
        *,
        password: str = "password123",
        role: str = "customer",
    ) -> dict[str, str]:
        create_user(email, password=password, role=role)
        response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return factory


@pytest.fixture
def create_flavor(db: Session):
    def factory(
        name: str = "Vanilla",
        *,
        price: str = "4.50",
        available: bool = True,
    ) -> Flavor:
        flavor = Flavor(
            name=name,
            description=f"{name} description",
            price=Decimal(price),
            available=available,
        )
        db.add(flavor)
        db.commit()
        db.refresh(flavor)
        return flavor

    return factory
