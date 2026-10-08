from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE)

    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_user: str
    db_password: str
    db_name: str
