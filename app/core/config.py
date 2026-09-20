from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file sits in the app folder, next to main.py (works from any cwd).
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    # No defaults for the secrets: if one is missing, the app refuses to start
    # and tells you which one, instead of quietly using an insecure value.
    database_url: str
    secret_key: str

    # Not secret, so they have sensible defaults (override in .env if needed).
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    # Real environment variables win over the .env file.
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()
