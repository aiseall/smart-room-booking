from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./booking.db"
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480
    ENVIRONMENT: str = "development"
    AUTO_RELEASE_MINUTES: int = 15
    AUTO_RELEASE_CHECK_INTERVAL: int = 60

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
