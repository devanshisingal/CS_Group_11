import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
DEFAULT_DATABASE_URL = f"sqlite:///{(ROOT_DIR / 'securebank.db').as_posix()}"


def get_database_url() -> str:
    return os.getenv("SECUREBANK_DATABASE_URL", DEFAULT_DATABASE_URL)


def get_session_secret() -> str:
    return os.getenv("SECUREBANK_SESSION_SECRET", "local-demo-secret-change-before-deployment")
