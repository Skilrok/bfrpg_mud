import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app import models, schemas
from app.database import Base, get_db
from app.main import app
from app.routers.auth import get_current_user
import os
import uuid

# Create a separate test database for hirelings tests
TEST_DB_PATH = "test_hirelings.db"
if os.path.exists(TEST_DB_PATH):
    try:
        os.remove(TEST_DB_PATH)
    except PermissionError:
        pass

TEST_DATABASE_URL = f"sqlite:///./{TEST_DB_PATH}"
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency for these tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def test_user():
    # Create a unique user for this test module
    unique_id = uuid.uuid4().hex[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    
    db = next(override_get_db())
    user = models.User(
        username=username,
        email=email,
        hashed_password="hashedpassword",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Override the auth dependency
    async def get_test_current_user():
        return user
    
    app.dependency_overrides[get_current_user] = get_test_current_user
    
    return user

@pytest.fixture
def test_character(db_session, test_user):
    character = models.Character(
        name="Test Character",
        user_id=test_user.id,
        level=1,
        experience=0
    )
    db_session.add(character)
    db_session.commit()
    db_session.refresh(character)
    return character

@pytest.fixture
def auth_headers(test_user):
    # Generate token directly
    return {"Authorization": f"Bearer test_token_for_{test_user.id}"}

def test_create_hireling(client, auth_headers, db_session, test_user):
    response = client.post(
        "/api/hirelings/",
        headers=auth_headers,
        json={
            "name": "Test Hireling",
            "character_class": "fighter",
            "level": 1,
            "wage": 10
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Hireling"
    assert data["character_class"] == "fighter"
    assert data["loyalty"] == 50.0

def test_hire_hireling(client, auth_headers, db_session, test_user, test_character):
    # Create a hireling
    hireling = models.Hireling(
        name="Test Hireling",
        character_class="fighter",
        user_id=test_user.id,
        is_available=True
    )
    db_session.add(hireling)
    db_session.commit()
    db_session.refresh(hireling)

    # Hire the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/hire/{test_character.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["master_id"] == test_character.id
    assert data["is_available"] == False

def test_pay_hireling(client, auth_headers, db_session, test_user):
    # Create a hireling
    hireling = models.Hireling(
        name="Test Hireling Pay",
        character_class="fighter",
        user_id=test_user.id,
        last_payment_date=datetime.utcnow() - timedelta(days=5),
        days_unpaid=5,
        is_available=True
    )
    db_session.add(hireling)
    db_session.commit()
    db_session.refresh(hireling)

    # Pay the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/pay?days=7",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["days_unpaid"] == 0
    assert data["loyalty"] > 50.0  # Should have increased from base 50.0

def test_reward_hireling(client, auth_headers, db_session, test_user):
    # Create a hireling
    hireling = models.Hireling(
        name="Test Hireling Reward",
        character_class="fighter",
        user_id=test_user.id,
        is_available=True
    )
    db_session.add(hireling)
    db_session.commit()
    db_session.refresh(hireling)

    # Reward the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/reward?amount=50",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["loyalty"] > 50.0  # Should have increased from base 50.0

def test_loyalty_decrease_unpaid(client, auth_headers, db_session, test_user):
    # Create a hireling with old payment date
    hireling = models.Hireling(
        name="Test Hireling Loyalty",
        character_class="fighter",
        user_id=test_user.id,
        last_payment_date=datetime.utcnow() - timedelta(days=10),
        days_unpaid=0,
        is_available=True
    )
    db_session.add(hireling)
    db_session.commit()
    db_session.refresh(hireling)

    # Get the hireling to trigger loyalty update
    response = client.get(
        f"/api/hirelings/{hireling.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["loyalty"] < 50.0  # Should have decreased from base 50.0
    assert data["days_unpaid"] == 10

def teardown_module(module):
    # Dispose of the engine
    engine.dispose()
    # Remove overrides
    app.dependency_overrides.clear()
