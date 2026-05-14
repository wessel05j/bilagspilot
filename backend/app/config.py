from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"


def _sqlite_url(path: Path) -> str:
    return f"sqlite:///{path.as_posix()}"


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4-mini"
    database_url: str = _sqlite_url(BACKEND_DIR / "bilagspilot.db")
    upload_dir: Path = BACKEND_DIR / "uploads"
    frontend_origin: str = "http://localhost:5173"
    max_upload_bytes: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def is_openai_configured() -> bool:
    api_key = (settings.openai_api_key or "").strip()
    return bool(api_key and api_key != "your_key_here")
