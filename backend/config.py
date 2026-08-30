import os
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"{name} environment variable is required")

    return value


SECRET_KEY = get_required_env("JWT_SECRET_KEY")
DATABASE_URL = get_required_env("DATABASE_URL")
CORS_ORIGINS = [
    origin.strip()
    for origin in get_required_env("CORS_ORIGINS").split(",")
    if origin.strip()
]
