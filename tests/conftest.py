import pytest
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from app.models import User, Character, Hireling
from app.routers.auth import create_access_token
from datetime import datetime, timedelta
from typing import Dict, Any

# Set testing environment variable for all tests
os.environ["TESTING"] = "True"

# Create a file-based test database instead of in-memory
TEST_DB_PATH = "test_database.db"
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        pass  # File might be locked, we'll try to continue

TEST_DB_URL = f"sqlite:///./{TEST_DB_PATH}"

@pytest.fixture(scope="session")
def test_engine():
    """Create a SQLAlchemy engine for testing"""
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    
    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(engine)
    
    # Create all tables before running any tests
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup after all tests
    engine.dispose()

@pytest.fixture
def test_db(test_engine):
    """Create a fresh database session for each test"""
    # Create a new session for each test
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    
    # Set testing environment flag
    os.environ["TESTING"] = "True"
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            pass  # Don't close the session here
    
    # Apply the dependency override
    app.dependency_overrides[get_db] = override_get_db
    
    # Start with a clean state for each test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    
    yield session
    
    # Cleanup after the test
    session.rollback()
    
    # Clear tables for next test
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    
    # Clean up
    os.environ.pop("TESTING", None)
    session.close()

@pytest.fixture
def client(test_db):
    """Create a test client with a new database session"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_user(test_db):
    """Create a test user for each test"""
    # Create a unique user for each test
    unique_id = uuid.uuid4().hex[:8]
    username = f"testuser_{unique_id}"
    plain_password = "TestPassword123!"
    
    # Use a pre-defined hash for testing
    hashed_password = f"test_hash_{plain_password}"
    
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Override the auth dependency for testing
    from app.routers.auth import get_current_user
    
    async def override_get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield user
    
    # Clean up the override after the test
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for testing"""
    # Generate a test token directly with a format the auth system will recognize 
    token = f"test_token_for_{test_user.id}"
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_character(test_db, test_user):
    """Create a test character for each test"""
    # Create a test character
    character = Character(
        name="Test Character",
        description="A test character",
        race="human",
        character_class="fighter",
        level=1,
        experience=0,
        strength=10,
        intelligence=10,
        wisdom=10,
        dexterity=10,
        constitution=10,
        charisma=10,
        hit_points=8,
        armor_class=10,
        user_id=test_user.id
    )
    test_db.add(character)
    test_db.commit()
    test_db.refresh(character)
    return character

# Teardown to clean up after all tests
def teardown_module(module):
    # Clear dependency overrides
    app.dependency_overrides.clear()
    
    # Remove test database file
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except:
            pass
