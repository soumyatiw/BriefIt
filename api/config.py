# api/config.py
#
# SINGLE SOURCE OF TRUTH for all environment/config values.
# Every other module must import `settings` from here.
# Do NOT call os.environ.get(...) anywhere else in this project.

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from the .env file at startup.
    All fields map directly to environment variable names (case-insensitive).
    """

    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Day 7+ (sentiment / summarization) — empty string is fine until then
    groq_api_key: str = ""
    openai_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")


# Module-level singleton — import this, don't instantiate Settings yourself.
settings = Settings()
