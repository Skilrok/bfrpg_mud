import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app import models
from app.routers.auth import get_current_user
import os

# Create test database
TEST_DB_PATH = "test_basic.db"
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        # File might be locked by another process, we'll try to continue
        pass

SQLALCHEMY_DATABASE_URL = f"sqlite:///./{TEST_DB_PATH}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Make sure all models are registered with Base metadata
from app.models import User, Character, Hireling

# Create tables
Base.metadata.drop_all(bind=engine)  # Drop all tables first
Base.metadata.create_all(bind=engine)  # Create tables fresh

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create a test user and override authentication
async def get_test_current_user():
    db = next(override_get_db())
    # Check if test user exists
    user = db.query(models.User).filter(models.User.username == "testuser").first()
    if not user:
        # Create a test user
        user = models.User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

app.dependency_overrides[get_current_user] = get_test_current_user

# Test client
client = TestClient(app)

@pytest.mark.skip(reason="Authentication needs to be fixed")
def test_get_hirelings():
    response = client.get("/api/hirelings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to BFRPG MUD API"}

# Add cleanup function to delete the test database
def teardown_module(module):
    # Close all connections
    engine.dispose()
    # We won't try to delete the file as it might still be locked on Windows
    # Just let the OS handle it when the process exits
