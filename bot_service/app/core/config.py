from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Общие
    APP_NAME: str = "bot-service"
    ENV: str = "local"

    # Telegram
    TELEGRAM_BOT_TOKEN: str  # обязательное поле

    # JWT 
    JWT_SECRET: str  # обязательное
    JWT_ALG: str = "HS256"

    # Redis и RabbitMQ (значения по умолчанию для docker-compose)
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"

    # OpenRouter
    OPENROUTER_API_KEY: str  # обязательное
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "stepfun/step-3.5-flash:free"
    OPENROUTER_SITE_URL: str = "https://example.com"
    OPENROUTER_APP_NAME: str = "bot-service"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()