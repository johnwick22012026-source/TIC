"""
Application settings and environment configuration loader.
"""
from pydantic import BaseSettings


def _get_env_file():
    try:
        # Load .env file in project root
        from pathlib import Path
        env_path = Path(__file__).resolve().parent.parent / ".env"
        return str(env_path)
    except Exception:
        return None


class Settings(BaseSettings):
    app_name: str = "Tic-Tac-Toe API"
    debug: bool = True

    class Config:
        env_file = _get_env_file()
        env_file_encoding = "utf-8"


settings = Settings()
