from sqlalchemy import create_engine
from app.models import Base
from app.database import DATABASE_URL

print(f"Using database URL: {DATABASE_URL}")

# Create an engine that connects to the database
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

# Create all tables in the database
print("Creating tables...")
Base.metadata.create_all(engine)
print("Tables created!") 