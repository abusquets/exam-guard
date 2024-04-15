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


settings = Settings()
