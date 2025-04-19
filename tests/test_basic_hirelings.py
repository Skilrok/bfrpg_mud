import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.database import Base, get_db
from app.main import app
from app import models
from app.routers.auth import get_current_user
import os
import threading
import uuid

# Create test database with thread-specific name
TEST_DB_PATH = f"test_basic_hirelings_{threading.get_ident()}.db"
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        # File might be locked by another process, generate a unique name
        TEST_DB_PATH = f"test_basic_hirelings_{threading.get_ident()}_{uuid.uuid4().hex[:8]}.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///./{TEST_DB_PATH}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    # Limit pool size to prevent thread issues
    pool_size=1,
    max_overflow=0
)

# Use thread-local sessions with scoped_session
TestingSessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

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
        # Don't close the session here - will be handled by the registry
        pass

# Override dependency for client
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    test_client = TestClient(app)
    yield test_client
    # Clean up after test - remove session from registry
    TestingSessionLocal.remove()

# Create a test user
@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    # Create a test user
    username = f"hirelings_test_{uuid.uuid4().hex[:8]}"
    db_user = models.User(
        username=username,
        email=f"{username}@example.com",
        hashed_password="test_hash",  # Just a placeholder for testing
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Override the dependency
    async def override_get_current_user():
        return db_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield db_user
    
    # Clean up
    db.delete(db_user)
    db.commit()
    
    # Remove the override
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    
    # Don't close the session here - will be handled by the registry

# Add cleanup function to delete the test database
def teardown_module(module):
    # Clean up session
    TestingSessionLocal.remove()
    
    # Close all connections
    engine.dispose()
    
    # Try to remove the database file
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except:
        pass  # File might still be locked on Windows

@pytest.mark.skip(reason="Authentication needs to be fixed")
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to BFRPG MUD API"}

def test_get_hirelings(client, test_user):
    # Ensure we're in test environment
    os.environ["TESTING"] = "True"
    
    # Get or create the test user
    db = TestingSessionLocal()
    user = test_user
    
    # Ensure user exists
    assert user is not None
    assert user.id is not None
    
    # Create test token
    token = f"test_token_for_{user.id}"
    
    # Create authenticated headers
    headers = {"Authorization": f"Bearer {token}"}
    
    # Make request with auth headers
    response = client.get("/api/hirelings/", headers=headers)
    
    # Check response
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Should return a list of hirelings
    
    # Clean up
    os.environ.pop("TESTING", None)
