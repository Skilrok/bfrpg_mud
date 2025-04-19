import os
import threading
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.constants import CharacterClass, CharacterRace, ItemType
from app.database import Base, get_db
from app.main import app
from app.models import Character, Hireling, Item, User
from app.routers.auth import create_access_token

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
    """Create a SQLAlchemy engine for testing"""
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
        print(
            f"Failed to remove test database: {e}"
        )  # Log error instead of bare except


@pytest.fixture
def test_db(test_engine):
    """Create a fresh database session for each test"""
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
    os.environ.pop("TESTING", None)
    session.close()

    # Remove the session from the registry
    TestSessionLocal.remove()


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
        is_active=True,
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
        user_id=test_user.id,
    )
    test_db.add(character)
    test_db.commit()
    test_db.refresh(character)
    return character


def create_test_user(
    db, username="testuser", email="test@example.com", password="password123"
):
    """Factory function to create a test user"""
    from app.utils import get_password_hash

    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_character(
    db,
    user_id: int,
    name: str = "Test Character",
    race: CharacterRace = CharacterRace.HUMAN,
    character_class: CharacterClass = CharacterClass.FIGHTER,
    level: int = 1,
    strength: int = 16,
    intelligence: int = 10,
    wisdom: int = 10,
    dexterity: int = 12,
    constitution: int = 14,
    charisma: int = 8,
    hit_points: int = 10,
    gold: int = 100,
) -> Character:
    """
    Factory function to create a test character with customizable attributes.

    Args:
        db: Database session
        user_id: User ID to associate the character with
        name: Character name
        race: Character race (from CharacterRace enum)
        character_class: Character class (from CharacterClass enum)
        level: Character level
        strength, intelligence, wisdom, dexterity, constitution, charisma: Ability scores
        hit_points: Character hit points
        gold: Starting gold

    Returns:
        Character: The created character object
    """
    character = Character(
        name=name,
        race=race,
        character_class=character_class,
        level=level,
        user_id=user_id,
        strength=strength,
        intelligence=intelligence,
        wisdom=wisdom,
        dexterity=dexterity,
        constitution=constitution,
        charisma=charisma,
        hit_points=hit_points,
        armor_class=10,  # Base armor class
        gold=gold,
        # Initialize empty collections
        equipment={},
        inventory={},
        special_abilities=[],
        spells_known=[],
        thief_abilities={},
    )

    # Add calculated saving throws based on class and level
    character.save_death_ray_poison = 14  # Default values, should be calculated
    character.save_magic_wands = 15
    character.save_paralysis_petrify = 16
    character.save_dragon_breath = 17
    character.save_spells = 18

    db.add(character)
    db.commit()
    db.refresh(character)
    return character


def create_test_item(
    db,
    name: str = "Test Item",
    description: str = "A test item",
    item_type: ItemType = ItemType.MISCELLANEOUS,
    value: int = 10,
    weight: float = 1.0,
    properties: Optional[Dict[str, Any]] = None,
) -> Item:
    """
    Factory function to create a test item with customizable attributes.

    Args:
        db: Database session
        name: Item name
        description: Item description
        item_type: Type of item (from ItemType enum)
        value: Value in gold pieces
        weight: Weight in pounds
        properties: Additional item properties

    Returns:
        Item: The created item object
    """
    if properties is None:
        properties = {}

    item = Item(
        name=name,
        description=description,
        item_type=item_type,
        value=value,
        weight=weight,
        properties=properties,
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item


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
