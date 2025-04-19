"""
Test configuration and common fixtures.

This module contains pytest fixtures for setting up the test environment,
database, and common test objects.
"""

import os
import threading
import uuid
from typing import Any, Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Character, User
from app.routers.auth import create_access_token, get_current_user
from tests.factories import (
    create_test_character,
    create_test_hireling,
    create_test_item,
    create_test_room,
    create_test_token,
    create_test_user,
)

# Set testing environment variable for all tests
os.environ["TESTING"] = "True"

# Create a unique file-based test database for each test session
# This uses thread ID to avoid conflicts in parallel test runs
TEST_DB_PATH = f"test_database_{threading.get_ident()}.db"
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        # File might be locked, generate a new unique name
        TEST_DB_PATH = (
            f"test_database_{threading.get_ident()}_{uuid.uuid4().hex[:8]}.db"
        )

TEST_DB_URL = f"sqlite:///./{TEST_DB_PATH}"


@pytest.fixture(scope="session")
def test_engine():
    """
    Create a SQLAlchemy engine for testing.

    This fixture creates a database engine that is used for the entire test session.
    """
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        # Limit connection pool size to prevent thread issues
        pool_size=1,
        max_overflow=0,
    )

    # Drop all tables first to ensure clean state
    Base.metadata.drop_all(engine)

    # Create all tables before running any tests
    Base.metadata.create_all(engine)

    yield engine

    # Cleanup after all tests
    engine.dispose()

    # Remove test database file
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except OSError as e:
        print(f"Failed to remove test database: {e}")


@pytest.fixture
def test_db(test_engine) -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.

    This fixture provides a clean database session for each test, and ensures
    that all tables are cleared before and after each test.
    """
    # Create a thread-local session factory using scoped_session
    TestSessionLocal = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    )

    # Get a session from the factory
    session = TestSessionLocal()

    # Set testing environment flag
    os.environ["TESTING"] = "True"

    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            # Don't close the session here as it's managed by the fixture
            pass

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
    session.close()

    # Remove the session from the registry
    TestSessionLocal.remove()


@pytest.fixture
def client(test_db) -> TestClient:
    """
    Create a test client with a new database session.

    This fixture provides a FastAPI TestClient for making HTTP requests to the API.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(test_db) -> User:
    """
    Create a test user for each test.

    This fixture provides a user for authentication and authorization tests.
    """
    user = create_test_user(test_db)
    return user


@pytest.fixture
def test_admin(test_db) -> User:
    """
    Create a test admin user for each test.

    This fixture provides an admin user for testing admin-only functionality.
    """
    user = create_test_user(
        test_db, username="admin", email="admin@example.com", is_active=True
    )
    # Set admin role directly in the user record
    user.is_admin = True
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user) -> Dict[str, str]:
    """
    Create authentication headers for testing.

    This fixture provides the Authorization header with a valid JWT token
    for the test user.
    """
    token = create_test_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(test_admin) -> Dict[str, str]:
    """
    Create authentication headers for admin testing.

    This fixture provides the Authorization header with a valid JWT token
    for the admin user.
    """
    token = create_test_token(test_admin.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_current_user(test_user):
    """
    Mock the current_user dependency.

    This fixture allows tests to run without authentication by mocking
    the get_current_user dependency.
    """

    # Override the auth dependency for testing
    async def override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    yield test_user

    # Clean up the override after the test
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]


@pytest.fixture
def test_character(test_db, test_user) -> Character:
    """
    Create a test character for each test.

    This fixture provides a character for testing character-related functionality.
    """
    character = create_test_character(test_db, test_user.id)
    return character


@pytest.fixture
def test_room(test_db):
    """
    Create a test room for each test.

    This fixture provides a room for testing room-related functionality.
    """
    room = create_test_room(test_db, is_starting_room=True)
    return room


@pytest.fixture
def test_item(test_db):
    """
    Create a test item for each test.

    This fixture provides an item for testing item-related functionality.
    """
    item = create_test_item(test_db)
    return item


@pytest.fixture
def test_hireling(test_db):
    """
    Create a test hireling for each test.

    This fixture provides a hireling for testing hireling-related functionality.
    """
    hireling = create_test_hireling(test_db)
    return hireling


@pytest.fixture(autouse=True)
def cleanup_dependency_overrides():
    """
    Clean up dependency overrides after each test.

    This fixture ensures that dependency overrides are cleaned up
    even if tests fail.
    """
    yield
    # Clear all dependency overrides
    app.dependency_overrides.clear()


def teardown_module(module):
    """
    Clean up after the test module.

    This function is called after all tests in a module have been run.
    """
    # Clear dependency overrides
    app.dependency_overrides.clear()

    # Try to remove the test database
    try:
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
    except OSError:
        pass
