import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app import models
import os

# Make sure tests run in test environment
os.environ["TESTING"] = "True"

def test_create_hireling(client, auth_headers, test_db, test_user):
    """Test creating a new hireling"""
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

def test_hire_hireling(client, auth_headers, test_db, test_user, test_character):
    """Test hiring a hireling for a character"""
    # Print debug info about the character
    print(f"Test character ID: {test_character.id}, User ID: {test_user.id}")
    print(f"Character details: race={test_character.race}, class={test_character.character_class}")
    
    # Create a hireling directly in the database
    hireling = models.Hireling(
        name="Test Hireling",
        character_class="fighter",
        user_id=test_user.id,
        is_available=True
    )
    test_db.add(hireling)
    test_db.commit()
    test_db.refresh(hireling)
    
    print(f"Created hireling with ID: {hireling.id}, User ID: {hireling.user_id}")

    # Hire the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/hire/{test_character.id}",
        headers=auth_headers
    )
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["master_id"] == test_character.id
    assert data["is_available"] == False

def test_pay_hireling(client, auth_headers, test_db, test_user):
    """Test paying a hireling"""
    # Create a hireling with unpaid days
    hireling = models.Hireling(
        name="Test Hireling Pay",
        character_class="fighter",
        user_id=test_user.id,
        last_payment_date=datetime.utcnow() - timedelta(days=5),
        days_unpaid=5,
        is_available=True
    )
    test_db.add(hireling)
    test_db.commit()
    test_db.refresh(hireling)

    # Pay the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/pay?days=7",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["days_unpaid"] == 0
    assert data["loyalty"] > 50.0  # Should have increased from base 50.0

def test_reward_hireling(client, auth_headers, test_db, test_user):
    """Test rewarding a hireling"""
    # Create a hireling
    hireling = models.Hireling(
        name="Test Hireling Reward",
        character_class="fighter",
        user_id=test_user.id,
        is_available=True
    )
    test_db.add(hireling)
    test_db.commit()
    test_db.refresh(hireling)

    # Reward the hireling
    response = client.put(
        f"/api/hirelings/{hireling.id}/reward?amount=50",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["loyalty"] > 50.0  # Should have increased from base 50.0

def test_loyalty_decrease_unpaid(client, auth_headers, test_db, test_user):
    """Test hireling loyalty decreases when unpaid"""
    # Create a hireling with old payment date
    hireling = models.Hireling(
        name="Test Hireling Loyalty",
        character_class="fighter",
        user_id=test_user.id,
        last_payment_date=datetime.utcnow() - timedelta(days=10),
        days_unpaid=0,
        is_available=True
    )
    test_db.add(hireling)
    test_db.commit()
    test_db.refresh(hireling)

    # Get the hireling to trigger loyalty update
    response = client.get(
        f"/api/hirelings/{hireling.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["loyalty"] < 50.0  # Should have decreased from base 50.0
    assert data["days_unpaid"] == 10
