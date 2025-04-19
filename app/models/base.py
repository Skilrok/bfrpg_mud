import datetime

import sqlalchemy as sa
from sqlalchemy import JSON, Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr


# Define our base model class with common fields and methods
class BaseModel:
    """Base model for all SQLAlchemy models with common fields and methods"""

    # Common columns for all models
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        nullable=False,
    )

    # Automatically generate tablename from class name
    @declared_attr
    def __tablename__(cls):
        # Convert CamelCase to snake_case and make plural
        # e.g. UserProfile -> user_profiles
        name = cls.__name__
        # Add underscore before capitals and convert to lowercase
        snake = "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip(
            "_"
        )
        # Make plural by adding 's' (simplistic approach)
        return snake + "s"


# Create base with our custom class
Base = declarative_base(cls=BaseModel)

# Define JSON type that works across different database backends
if hasattr(sa, "JSON"):
    # Use native JSON type if available (PostgreSQL, SQLite 3.9+)
    JSON_TYPE = sa.JSON
else:
    # Fallback to Text type for older SQLite
    JSON_TYPE = sa.Text
