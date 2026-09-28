"""
Application configuration.

All configurable values are read from environment variables (or a .env file
during local development). Nothing sensitive is hard-coded here.
"""
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Application ---
    APP_NAME: str = "Employee Leave & Approval Workflow Management System"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- Database ---
    DATABASE_URL: str = "postgresql://postgres@localhost:5432/employee_leave_db"

    # --- JWT / Auth ---
    JWT_SECRET_KEY: str = "change-this-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int | None = None

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def sync_config(self):
        if self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES is not None:
            self.ACCESS_TOKEN_EXPIRE_MINUTES = self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        url = self.DATABASE_URL.strip().strip("'\"")
        if url.startswith("ostgresql://"):
            url = "p" + url
        elif url.startswith("ostgres://"):
            url = "postgresql://" + url[len("ostgres://"):]
        elif url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        self.DATABASE_URL = url
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
