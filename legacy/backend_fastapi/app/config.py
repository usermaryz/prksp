from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
# Каталог для SQLite и прочих файлов данных (создаётся при старте приложения).
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "prksp-dev-change-in-production"
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_days: int = 7

    db_url: str = f"sqlite:///{DATA_DIR.resolve()}/prksp.db"

    # Дополнительные origin для CORS (через запятую), например https://app.onrender.com
    cors_extra_origins: str = ""


settings = Settings()
