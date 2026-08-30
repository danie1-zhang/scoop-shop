import pytest
import jwt

from backend.auth import ALGORITHM
from backend.config import SECRET_KEY


def test_register_normalizes_email_and_rejects_duplicate(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "  Customer@Example.com  ", "password": "password123"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "customer@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    duplicate = client.post(
        "/api/auth/register",
        json={"email": "CUSTOMER@example.com", "password": "password123"},
    )
    assert duplicate.status_code == 409


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("not-an-email", "password123"),
        ("valid@example.com", "short"),
    ],
)
def test_register_rejects_invalid_credentials(client, email, password):
    response = client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )

    assert response.status_code == 422


def test_login_and_current_user(client):
    client.post(
        "/api/auth/register",
        json={"email": "customer@example.com", "password": "password123"},
    )

    login = client.post(
        "/api/auth/login",
        json={"email": "CUSTOMER@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"

    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    current_user = client.get("/api/me", headers=headers)
    assert current_user.status_code == 200
    assert current_user.json()["email"] == "customer@example.com"

    assert client.get("/api/me").status_code == 401
    assert client.get(
        "/api/me", headers={"Authorization": "Bearer invalid"}
    ).status_code == 401


def test_login_rejects_wrong_password(client, create_user):
    create_user("customer@example.com")

    response = client.post(
        "/api/auth/login",
        json={"email": "customer@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_token_without_subject_is_rejected(client):
    token = jwt.encode({}, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
