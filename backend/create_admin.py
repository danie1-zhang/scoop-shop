import argparse
from getpass import getpass

from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from .auth import hash_password
from .database import SessionLocal
from .models import User
from .schemas import EmailCredentials, UserCreate


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create or promote a Scoop Shop administrator."
    )
    parser.add_argument(
        "email",
        help="Email address for the administrator.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        email_data = EmailCredentials(email=args.email)
    except ValidationError as exc:
        message = exc.errors()[0]["msg"]
        raise SystemExit(f"Invalid email: {message}")

    email = str(email_data.email)

    with SessionLocal() as db:
        user = (
            db.query(User)
            .filter(func.lower(User.email) == email)
            .first()
        )

        if user is None:
            password = getpass("Password: ")
            password_confirmation = getpass("Confirm password: ")

            if password != password_confirmation:
                raise SystemExit("Passwords do not match.")

            try:
                user_data = UserCreate(email=email, password=password)
            except ValidationError as exc:
                message = exc.errors()[0]["msg"]
                raise SystemExit(f"Invalid administrator data: {message}")

            admin = User(
                email=str(user_data.email),
                password_hash=hash_password(user_data.password),
                role="admin",
            )

            try:
                db.add(admin)
                db.commit()
            except IntegrityError:
                db.rollback()
                raise SystemExit(
                    "A user with this email was created concurrently."
                )

            print(f"Created administrator {email}.")
        elif user.role == "admin":
            print(f"{email} is already an administrator.")
        else:
            confirmation = input(
                f"{email} currently has role {user.role!r}. "
                "Promote to administrator? [y/N]: "
            ).strip().lower()

            if confirmation not in {"y", "yes"}:
                print("Promotion cancelled.")
                return

            user.role = "admin"
            db.commit()
            print(f"Promoted {email} to administrator.")


if __name__ == "__main__":
    main()
