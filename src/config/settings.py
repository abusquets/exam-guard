from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = 'ExamGuard API'
    PROJECT_DESCRIPTION: str = 'ExamGuard API - WorldSensing'
    VERSION: str = '0.1.0'
    APP_LOGGER_NAME: str = 'examguard'

    APP_ENV: str = 'dev'
    DEBUG: bool = False

    DATABASE_URL: str = 'postgresql+asyncpg://postgres:change-me@postgres:5432/postgres'
    BROKER_URL: str = 'amqp://admin:1234@rabbit:5672/test'

    BROKER_RETRY_TIMES: int = 5
    BROKER_RETRY_DELAY_IN_SECONDS: int = 5


settings = Settings()
