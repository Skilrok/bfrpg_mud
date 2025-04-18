from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bfrpg.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models - using declarative_base for backward compatibility
# but with a note for future updates
Base = declarative_base()

# SQLite JSON Type Adapter - to ensure proper JSON serialization/deserialization
if DATABASE_URL.startswith("sqlite"):
    # Register JSON serialization/deserialization for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        
    # Add JSON serialization for SQLite
    import sqlalchemy.types as types
    
    class JSONEncodedDict(types.TypeDecorator):
        """Represents a JSON structure as a string."""
        impl = types.TEXT
        
        def process_bind_param(self, value, dialect):
            if value is not None:
                value = json.dumps(value)
            return value
            
        def process_result_value(self, value, dialect):
            if value is not None:
                value = json.loads(value)
            return value


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
