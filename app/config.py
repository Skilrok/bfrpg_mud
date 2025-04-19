import logging
import os
import re
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic BaseSettings for validation and type conversion.
    """

    # Environment
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = ""

    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Game
    MAX_PARTY_SIZE: int = 5
    DEFAULT_STARTING_ROOM: int = 1

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


def validate_settings(settings: Settings) -> Settings:
    """Validate the settings and provide default values when needed."""
    # Validate environment
    env = settings.ENVIRONMENT.lower()
    if env not in ["development", "testing", "production"]:
        logger.warning(f"Invalid ENVIRONMENT '{env}'. Using 'development' as fallback.")
        settings.ENVIRONMENT = "development"

    # Validate DATABASE_URL
    db_url = settings.DATABASE_URL

    # Production requires PostgreSQL
    if settings.ENVIRONMENT == "production":
        if not db_url:
            logger.error("DATABASE_URL is not set in production environment!")
            raise ValueError("DATABASE_URL must be set for production environment")

        if not db_url.startswith("postgresql://"):
            logger.error("Production environment requires PostgreSQL database!")
            raise ValueError("Production environment requires PostgreSQL database")
    else:
        # Development/testing fallback to SQLite
        if not db_url:
            logger.warning("DATABASE_URL is not set. Using SQLite as fallback.")
            if settings.ENVIRONMENT == "testing":
                settings.DATABASE_URL = "sqlite:///./test.db"
            else:
                settings.DATABASE_URL = "sqlite:///./dev.db"

    # Validate SECRET_KEY
    if not settings.SECRET_KEY:
        if settings.ENVIRONMENT == "production":
            logger.error("SECRET_KEY is not set in production environment!")
            raise ValueError("SECRET_KEY must be set for production environment")
        logger.warning(
            "SECRET_KEY is not set. Using an insecure default - DO NOT USE IN PRODUCTION!"
        )
        settings.SECRET_KEY = "insecure_default_key_for_development_only_1234567890"

    # Validate log level
    log_level = settings.LOG_LEVEL.upper()
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        logger.warning(f"Invalid LOG_LEVEL '{log_level}'. Using 'INFO' as fallback.")
        settings.LOG_LEVEL = "INFO"

    return settings


@lru_cache()
def get_settings() -> Settings:
    """
    Returns the application settings, cached to avoid reloading.

    Returns:
        Settings object with validated configuration
    """
    settings = Settings()

    # Apply validation to settings
    settings = validate_settings(settings)

    # Configure logging based on settings
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    return settings


def configure_app_from_env():
    """
    Helper function to configure application from environment variables.
    Call this during application startup.
    """
    settings = get_settings()

    # Log settings summary (exclude sensitive data)
    logger.info(f"Loaded settings for {settings.ENVIRONMENT} environment")
    logger.info(f"Host: {settings.HOST}, Port: {settings.PORT}")

    if settings.ENVIRONMENT == "development":
        logger.info("Development mode: Hot reloading is enabled")
    elif settings.ENVIRONMENT == "production":
        logger.info("Production mode: Using PostgreSQL database")

    return settings
