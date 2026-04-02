from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/finance_db"
    )

    APP_NAME: str = "Finance Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL.startswith("postgres://"):
            return self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL


settings = Settings()
