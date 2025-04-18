import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import app
from fastapi.testclient import TestClient
from tests.test_auth import get_test_token
from app import models
from app.routers.auth import get_current_user
import os

# Use SQLite for testing
TEST_DATABASE_URL = "sqlite:///./test.db"

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

    yield engine

    # Clean up after tests
    Base.metadata.drop_all(bind=engine)
    try:
        os.remove("test.db")
    except OSError:
        pass


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
    user = models.User(
        username="testuser", email="test@example.com", hashed_password="hashedpassword"
    )
    db_session.add(user)
    db_session.commit()
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
    app.dependency_overrides.clear()
