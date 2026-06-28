from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Общие
    APP_NAME: str = "auth-service"
    ENV: str = "local"

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # База данных
    SQLITE_PATH: str = "./auth.db"

    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()