from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import JSON
import sqlalchemy as sa
import enum

# Define SQLAlchemy Base
Base = declarative_base()

# Define JSON type that works across different database backends
if hasattr(sa, 'JSON'):
    # Use native JSON type if available (PostgreSQL, SQLite 3.9+)
    JSON_TYPE = sa.JSON
else:
    # Fallback to Text type for older SQLite
    JSON_TYPE = sa.Text 