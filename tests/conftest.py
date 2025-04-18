import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from tests.test_auth import get_test_token
from app import models
from app.routers.auth import get_current_user
import os

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


@pytest.fixture
def test_user(db_session):
    # Check if test user already exists
    existing_user = db_session.query(models.User).filter(
        models.User.username == "testuser"
    ).first()
    
    if existing_user:
        return existing_user
        
    user = models.User(
        username="testuser", 
        email="test@example.com", 
        hashed_password="hashedpassword",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_token(test_user):
    return get_test_token(test_user.id)


@pytest.fixture
def auth_headers(test_token):
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture(autouse=True)
def override_auth_dependency(test_user):
    """Override the authentication dependency for all tests"""
    
    async def get_test_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = get_test_current_user
    yield
    # We don't clear the dependency overrides here since we're sharing the dependency
    # across multiple tests
