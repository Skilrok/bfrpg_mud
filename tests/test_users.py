import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db
from app.models.base import Base
from app.main import app
from app import models
from app.utils import get_password_hash
import os

# Create test database
TEST_DB_PATH = "test_users.db"
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

# Override dependencies for these tests
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

@pytest.fixture
def db_session():
    """Get a test database session for test data setup"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_register_user():
    """Test user registration with valid data"""
    unique_id = uuid.uuid4().hex[:8]
    response = client.post(
        "/api/users/register",
        json={
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "password_confirm": "TestPassword123!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == f"testuser_{unique_id}"
    assert data["email"] == f"test_{unique_id}@example.com"
    assert "password" not in data
    assert "hashed_password" not in data
    assert data["is_active"] == True
    assert "id" in data

def test_register_user_password_mismatch():
    """Test user registration with mismatched passwords"""
    unique_id = uuid.uuid4().hex[:8]
    response = client.post(
        "/api/users/register",
        json={
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@example.com",
            "password": "TestPassword123!",
            "password_confirm": "DifferentPassword123!"
        }
    )
    assert response.status_code == 422  # Validation error

def test_register_duplicate_username(client, test_db):
    """Test that registering a user with a duplicate username fails"""
    # Create a user directly in the database
    username = "duplicate_username_test"
    user = models.User(
        username=username,
        email="unique_email@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Try to register a new user with the same username
    response = client.post(
        "/api/users/register",
        json={
            "username": username,
            "email": "different_email@example.com",
            "password": "Password123!",
            "password_confirm": "Password123!"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_register_duplicate_email(client, test_db):
    """Test that registering a user with a duplicate email fails"""
    # Create a user directly in the database
    email = "duplicate_email@example.com"
    user = models.User(
        username="unique_username_test",
        email=email,
        hashed_password="hashed_password",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Try to register a new user with the same email
    response = client.post(
        "/api/users/register",
        json={
            "username": "different_username",
            "email": email,
            "password": "Password123!",
            "password_confirm": "Password123!"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

# Add cleanup function to delete the test database
def teardown_module(module):
    # Close all connections
    engine.dispose()
    # Clear the dependency overrides
    app.dependency_overrides.clear() 