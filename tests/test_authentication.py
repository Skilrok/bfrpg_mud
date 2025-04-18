import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.database import get_db
from app.models.base import Base
from app.main import app
from app import models
from app.utils import get_password_hash, verify_password
import os
import uuid
import threading
from jose import jwt
from app.routers.auth import SECRET_KEY, ALGORITHM
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.routers.auth import get_current_user

# Create test database with thread-specific name
TEST_DB_PATH = f"test_authentication_{threading.get_ident()}.db"
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        # File might be locked by another process, generate a unique name
        TEST_DB_PATH = f"test_authentication_{threading.get_ident()}_{uuid.uuid4().hex[:8]}.db"

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

# Setup and teardown for each test
@pytest.fixture
def client():
    # Set up
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    TestingSessionLocal.remove()
    app.dependency_overrides.clear()

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

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user for authentication tests"""
    unique_id = uuid.uuid4().hex[:8]
    username = f"auth_user_{unique_id}"
    plain_password = "TestPassword123!"
    
    # Set testing environment flag
    os.environ["TESTING"] = "True"
    
    # Create with direct password hash to ensure it's saved correctly
    hashed_password = get_password_hash(plain_password)
    
    user = models.User(
        username=username,
        email=f"auth_{unique_id}@example.com",
        hashed_password=hashed_password,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create a token for the user
    access_token_expires = timedelta(minutes=30)
    access_token = jwt.encode(
        {"sub": user.username, "exp": datetime.utcnow() + access_token_expires},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    # Override the get_current_user dependency for this test
    async def override_get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    user_dict = {"user": user, "password": plain_password, "token": access_token}
    yield user_dict
    
    # Clean up the override after the test
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    
    # Remove testing flag
    os.environ.pop("TESTING", None)

def test_login_success(client, test_db, test_user):
    """Test successful login and token generation"""
    # Create a specific user for this test
    username = f"login_test_user_{datetime.utcnow().timestamp()}"
    password = "TestPassword123!"
    
    # Check if user already exists
    existing_user = test_db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        test_db.delete(existing_user)
        test_db.commit()
        
    # Create fresh user for login test
    test_hash = f"test_hash_{password}"
    user = models.User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=test_hash, 
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Now try to log in
    response = client.post(
        "/api/auth/token",
        data={
            "username": username,
            "password": password
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Verify token contains expected data
    token = data["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == username

def test_login_invalid_username(client):
    """Test login with invalid username"""
    response = client.post(
        "/api/auth/token",
        data={
            "username": "nonexistent_user",
            "password": "TestPassword123!"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_invalid_password(client, test_db):
    """Test login with invalid password"""
    # Create a specific user for this test
    username = f"password_test_user_{datetime.utcnow().timestamp()}"
    password = "TestPassword123!"
    
    # Check if user already exists
    existing_user = test_db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        test_db.delete(existing_user)
        test_db.commit()
        
    # Create fresh user for password test
    test_hash = f"test_hash_{password}"
    user = models.User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=test_hash, 
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    
    # Try login with wrong password
    response = client.post(
        "/api/auth/token",
        data={
            "username": username,
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_token_route(client, test_db):
    """Test just the token creation endpoint"""
    # Create a specific user for this test
    username = f"token_test_user_{datetime.utcnow().timestamp()}"
    password = "TestPassword123!"
    
    # Make sure we're in test environment
    os.environ["TESTING"] = "True"
    
    # Check if user already exists
    existing_user = test_db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        test_db.delete(existing_user)
        test_db.commit()
        
    # Create fresh user for token test with test_hash format
    test_hash = f"test_hash_{password}"
    user = models.User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=test_hash, 
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Now try to log in
    response = client.post(
        "/api/auth/token",
        data={
            "username": username,
            "password": password
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_route_with_token(client, test_db):
    """Test accessing a protected route with a valid token"""
    # Create a specific user for this test
    username = f"protected_route_user_{datetime.utcnow().timestamp()}"
    password = "TestPassword123!"
    
    # Ensure we're in test environment
    os.environ["TESTING"] = "True"
    
    # Check if user already exists
    existing_user = test_db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        test_db.delete(existing_user)
        test_db.commit()
        
    # Create fresh user for token test with test_hash format
    test_hash = f"test_hash_{password}"
    user = models.User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=test_hash, 
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # First login to get token
    login_response = client.post(
        "/api/auth/token",
        data={
            "username": username,
            "password": password
        }
    )
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Access logout endpoint which requires authentication
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Successfully logged out"}

def test_protected_route_without_token(client):
    """Test accessing a protected route without a token"""
    response = client.post("/api/auth/logout")
    assert response.status_code == 401

def test_protected_route_with_invalid_token(client):
    """Test accessing a protected route with an invalid token"""
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    assert response.status_code == 401

# Add cleanup function to delete the test database
def teardown_module(module):
    # Close all connections
    engine.dispose()
    # Clear the dependency overrides
    app.dependency_overrides.clear() 
