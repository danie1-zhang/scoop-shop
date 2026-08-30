from types import SimpleNamespace

from backend import create_admin
from backend.models import User


def test_admin_cli_creates_new_administrator(monkeypatch, capsys, db):
    monkeypatch.setattr(
        create_admin,
        "parse_args",
        lambda: SimpleNamespace(email="Admin@Example.com"),
    )
    passwords = iter(["password123", "password123"])
    monkeypatch.setattr(create_admin, "getpass", lambda _prompt: next(passwords))

    create_admin.main()

    admin = db.query(User).filter(User.email == "admin@example.com").one()
    assert admin.role == "admin"
    assert "Created administrator admin@example.com." in capsys.readouterr().out


def test_admin_cli_promotes_customer(monkeypatch, capsys, db, create_user):
    create_user("customer@example.com")
    monkeypatch.setattr(
        create_admin,
        "parse_args",
        lambda: SimpleNamespace(email="customer@example.com"),
    )
    monkeypatch.setattr(create_admin, "input", lambda _prompt: "yes", raising=False)

    create_admin.main()

    db.expire_all()
    user = db.query(User).filter(User.email == "customer@example.com").one()
    assert user.role == "admin"
    assert "Promoted customer@example.com" in capsys.readouterr().out
