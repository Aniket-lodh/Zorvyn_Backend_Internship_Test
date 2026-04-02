from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/finance_db"
    )

    APP_NAME: str = "Finance Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
