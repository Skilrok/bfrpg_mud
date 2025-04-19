import json
import logging
import os
import urllib.parse
from contextlib import contextmanager
from typing import Any, Generator

from sqlalchemy import JSON, TypeDecorator, create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Determine database URL based on environment
# For production: use PostgreSQL
# For development/testing: use SQLite (with fallback)
if settings.ENVIRONMENT == "production":
    if not settings.DATABASE_URL or not settings.DATABASE_URL.startswith(
        "postgresql://"
    ):
        raise ValueError(
            "Production environment requires PostgreSQL. Check DATABASE_URL setting."
        )
    DATABASE_URL = settings.DATABASE_URL
else:
    # For development/testing, use SQLite as fallback
    if not settings.DATABASE_URL or not settings.DATABASE_URL.startswith(
        "postgresql://"
    ):
        logger.warning(
            "Non-PostgreSQL database detected for development/testing. Using SQLite."
        )
        # Use SQLite database based on environment
        if settings.ENVIRONMENT == "testing":
            DATABASE_URL = "sqlite:///./test.db"
        else:
            DATABASE_URL = "sqlite:///./dev.db"
    else:
        DATABASE_URL = settings.DATABASE_URL

# Create database engine with appropriate configuration
engine_args = {
    "pool_pre_ping": True,  # Check connection liveness before using
    "echo": settings.ENVIRONMENT == "development",  # Log SQL in development
}

# Add connect_args for SQLite for thread safety
if DATABASE_URL.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, **engine_args)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Define JSON type for SQLite (which doesn't natively support JSON)
class JSON_TYPE(TypeDecorator):
    impl = JSON

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "sqlite":
            return json.loads(value)
        return value

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "sqlite":
            return json.dumps(value)
        return value


# SQLite specific configuration
if DATABASE_URL.startswith("sqlite"):
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Dependency to get DB session
def get_db():
    """
    Get a database session for use in a FastAPI dependency.
    Auto-closes the session when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Any, None, None]:
    """
    Context manager for DB sessions.
    Use this in sync contexts when you can't use the dependency injection.

    Example:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """
    Initialize the database, creating tables if they don't exist.
    Call this during application startup.
    """
    try:
        # Import Base here to avoid circular imports
        # Import all models here to ensure they're registered with the Base
        import app.models
        from app.models.base import Base

        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info(
            f"Database tables created successfully (using {DATABASE_URL.split('://')[0]})"
        )
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


def get_database_info():
    """Return information about the database configuration"""
    db_type = DATABASE_URL.split("://")[0]
    return {
        "type": db_type,
        "environment": settings.ENVIRONMENT,
        "url": (
            DATABASE_URL.replace(
                urllib.parse.urlparse(DATABASE_URL).password or "", "****"
            )
            if "postgresql" in DATABASE_URL
            else DATABASE_URL
        ),
    }
