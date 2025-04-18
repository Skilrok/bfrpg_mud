import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import models, schemas
from app.database import Base
from app.main import app

client = TestClient(app)


@pytest.fixture
def test_user(db_session):
    user = models.User(
        username="testuser", email="test@example.com", hashed_password="hashedpassword"
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_character(db_session, test_user):
    character = models.Character(name="Test Character", user_id=test_user.id)
    db_session.add(character)
    db_session.commit()
    return character


def test_create_hireling(client, auth_headers, db_session, test_user):
    response = client.post(
        "/api/hirelings/",
        headers=auth_headers,
        json={
            "name": "Test Hireling",
            "character_class": "fighter",
            "level": 1,
            "wage": 10,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Hireling"
    assert data["character_class"] == "fighter"
    assert data["loyalty"] == 50.0


def test_hire_hireling(client, auth_headers, db_session, test_user, test_character):
    # Create a hireling
    hireling = models.Hireling(
        name="Test Hireling", character_class="fighter", user_id=test_user.id
    )
    db_session.add(hireling)
    db_session.commit()

    # Hire the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/hire/{test_character.id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["master_id"] == test_character.id
    assert data["is_available"] == False


def test_pay_hireling(client, auth_headers, db_session, test_user):
    # Create a hireling
    hireling = models.Hireling(
        name="Test Hireling",
        character_class="fighter",
        user_id=test_user.id,
        last_payment_date=datetime.utcnow() - timedelta(days=5),
    )
    db_session.add(hireling)
    db_session.commit()

    # Pay the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/pay?days=7", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["days_unpaid"] == 0
    assert data["loyalty"] > 50.0  # Should have increased from base 50.0


def test_reward_hireling(client, auth_headers, db_session, test_user):
    # Create a hireling
    hireling = models.Hireling(
        name="Test Hireling", character_class="fighter", user_id=test_user.id
    )
    db_session.add(hireling)
    db_session.commit()

    # Reward the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/reward?amount=50", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["loyalty"] > 50.0  # Should have increased from base 50.0


def test_loyalty_decrease_unpaid(client, auth_headers, db_session, test_user):
    # Create a hireling with old payment date
    hireling = models.Hireling(
        name="Test Hireling",
        character_class="fighter",
        user_id=test_user.id,
        last_payment_date=datetime.utcnow() - timedelta(days=10),
    )
    db_session.add(hireling)
    db_session.commit()

    # Get the hireling to trigger loyalty update
    response = client.get(f"/api/hirelings/{hireling.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["loyalty"] < 50.0  # Should have decreased from base 50.0
    assert data["days_unpaid"] == 10
