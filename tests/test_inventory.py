import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import string
import os
import json
import shutil
from datetime import datetime, timedelta
from jose import jwt

from app.main import app
from app.database import Base, get_db
from app.models import User, Character, Item, ItemType
from app.schemas import CharacterRace, CharacterClass
from app.routers.auth import SECRET_KEY, ALGORITHM

# Use in-memory SQLite for testing to avoid file access issues
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    # Create test data
    create_test_data(db)
    
    try:
        yield db
    finally:
        # Clean up after test
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    # Override the get_db dependency to use our test database
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


def create_test_data(db):
    # Create a test user 
    test_user = User(
        username="testuser",
        email="test@example.com",
        # Skip bcrypt hashing by using a predefined hash
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        is_active=True
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    
    # Create test items
    items = [
        Item(
            name="Test Sword",
            description="A test sword",
            item_type=ItemType.WEAPON,
            value=10,
            weight=2.0,
            properties={"damage": "1d6"}
        ),
        Item(
            name="Test Armor",
            description="Test armor",
            item_type=ItemType.ARMOR,
            value=50,
            weight=10.0,
            properties={"ac_bonus": 4}
        ),
        Item(
            name="Test Potion",
            description="A test potion",
            item_type=ItemType.POTION,
            value=5,
            weight=0.5,
            properties={"effect": "healing", "amount": "1d8"}
        )
    ]
    
    for item in items:
        db.add(item)
    
    # Create a test character
    test_character = Character(
        name="Test Character",
        description="A character for testing",
        race=CharacterRace.HUMAN,
        character_class=CharacterClass.FIGHTER,
        level=1,
        experience=0,
        strength=16,
        intelligence=10,
        wisdom=12,
        dexterity=14,
        constitution=15,
        charisma=8,
        hit_points=10,
        armor_class=12,
        gold=100,
        inventory={},
        equipment={},
        languages="Common",
        save_death_ray_poison=12,
        save_magic_wands=13,
        save_paralysis_petrify=14,
        save_dragon_breath=15,
        save_spells=16,
        special_abilities=[],
        user_id=test_user.id
    )
    db.add(test_character)
    db.commit()


@pytest.fixture
def auth_token():
    # Skip login process and create JWT token directly
    access_token_expires = datetime.utcnow() + timedelta(minutes=30)
    to_encode = {
        "sub": "testuser",
        "exp": access_token_expires
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def test_get_items(client, auth_token):
    # Test listing all items
    response = client.get(
        "/api/items/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 3  # At least our 3 test items
    assert items[0]["name"] == "Test Sword"


def test_get_item(client, auth_token, test_db):
    # Get the first item
    item = test_db.query(Item).first()
    
    # Test getting a specific item
    response = client.get(
        f"/api/items/{item.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Sword"


def test_create_item(client, auth_token):
    # Test creating a new item
    new_item = {
        "name": "New Test Item",
        "description": "A newly created test item",
        "item_type": "weapon",
        "value": 15,
        "weight": 3.0,
        "properties": {"damage": "1d8"}
    }
    
    response = client.post(
        "/api/items/",
        json=new_item,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    created_item = response.json()
    assert created_item["name"] == "New Test Item"
    assert created_item["item_type"] == "weapon"


def test_add_item_to_inventory(client, auth_token, test_db):
    # Get character and item
    character = test_db.query(Character).first()
    item = test_db.query(Item).first()
    
    # Test adding item to inventory
    response = client.post(
        f"/api/items/inventory/{character.id}/add",
        json={"item_id": item.id, "quantity": 2},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    updated_character = response.json()
    
    # Check inventory contains the item
    item_id_str = str(item.id)
    assert item_id_str in updated_character["inventory"]
    assert updated_character["inventory"][item_id_str]["quantity"] == 2


def test_equip_item(client, auth_token, test_db):
    # Get character and item
    character = test_db.query(Character).first()
    item = test_db.query(Item).filter(Item.item_type == ItemType.WEAPON).first()
    
    # First add item to inventory
    response = client.post(
        f"/api/items/inventory/{character.id}/add",
        json={"item_id": item.id, "quantity": 1},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Now equip the item
    response = client.post(
        f"/api/items/inventory/{character.id}/equip",
        json={"item_id": item.id, "slot": "main_hand"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    updated_character = response.json()
    
    # Check equipment contains the item
    assert "main_hand" in updated_character["equipment"]
    assert updated_character["equipment"]["main_hand"] == item.id
    
    # Check inventory item is marked as equipped
    item_id_str = str(item.id)
    assert updated_character["inventory"][item_id_str]["equipped"] == True
    assert updated_character["inventory"][item_id_str]["slot"] == "main_hand"


def test_unequip_item(client, auth_token, test_db):
    # Get character
    character = test_db.query(Character).first()
    
    # First add and equip an item
    item = test_db.query(Item).filter(Item.item_type == ItemType.WEAPON).first()
    client.post(
        f"/api/items/inventory/{character.id}/add",
        json={"item_id": item.id, "quantity": 1},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        f"/api/items/inventory/{character.id}/equip",
        json={"item_id": item.id, "slot": "main_hand"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Now unequip the item
    response = client.post(
        f"/api/items/inventory/{character.id}/unequip?slot=main_hand",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    updated_character = response.json()
    
    # Check equipment doesn't contain the item
    assert "main_hand" not in updated_character["equipment"]
    
    # Check inventory item is marked as not equipped
    item_id_str = str(item.id)
    assert updated_character["inventory"][item_id_str]["equipped"] == False
    assert updated_character["inventory"][item_id_str]["slot"] == None


def test_create_character_with_equipment(client, auth_token):
    # Test character creation with automatic equipment
    new_character = {
        "name": "Equipment Tester",
        "description": "Testing automatic equipment",
        "race": "human",
        "character_class": "fighter",
        "strength": 16,
        "intelligence": 10,
        "wisdom": 12,
        "dexterity": 14,
        "constitution": 15,
        "charisma": 8
    }
    
    response = client.post(
        "/api/characters/",
        json=new_character,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    created_character = response.json()
    
    # Verify character was created with inventory
    assert len(created_character["inventory"]) > 0
    
    # Verify character has some equipment
    assert len(created_character["equipment"]) > 0 