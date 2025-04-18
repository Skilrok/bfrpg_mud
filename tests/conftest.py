import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from tests.test_auth import get_test_token
from app import models
from app.routers.auth import get_current_user, create_access_token
import os
import uuid
from datetime import timedelta

# Explicitly import all models to ensure they're registered with Base metadata
from app.models import User, Character, Hireling

# Use SQLite for testing
TEST_DB_PATH = "test.db"
# Try to clean up any existing test database
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        # File might be locked by another process, we'll try to continue
        pass

TEST_DATABASE_URL = f"sqlite:///./{TEST_DB_PATH}"

# Test environment variables
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"


@pytest.fixture(scope="session")
def engine():
    # Create test database engine
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.drop_all(bind=engine)  # Drop all tables first
    Base.metadata.create_all(bind=engine)  # Create tables fresh

    # Override the get_db dependency for the entire test session
    def override_get_db():
        connection = engine.connect()
        transaction = connection.begin()
        session = sessionmaker(bind=connection)()
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()
            connection.close()
            
    app.dependency_overrides[get_db] = override_get_db
    
    yield engine
    
    # Clean up after tests
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user(db_session):
    # Create a unique user for each test
    unique_id = uuid.uuid4().hex[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    
    # Create and add user to the database
    user = models.User(
        username=username,
        email=email,
        hashed_password="hashedpassword",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Override the auth dependency for testing
    async def override_get_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    return user


@pytest.fixture
def test_token(test_user):
    return get_test_token(test_user.id)


@pytest.fixture
def auth_headers(test_user):
    # Create an access token for the test user
    access_token = create_access_token(
        data={"sub": test_user.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_character(db_session, test_user):
    # Create a test character
    character = models.Character(
        name="Test Character",
        description="A test character",
        level=1,
        experience=0,
        user_id=test_user.id
    )
    db_session.add(character)
    db_session.commit()
    db_session.refresh(character)
    return character


# Cleanup after tests
def teardown_module(module):
    # Clear dependency overrides
    app.dependency_overrides.clear()
    
    # Close connections
    engine.dispose()
    
    # We won't try to delete the DB file as it might be locked on Windows
    # Let the OS handle it when the process exits
