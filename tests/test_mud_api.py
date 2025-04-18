import pytest
import requests
import random
import string
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test data
def random_suffix():
    """Generate a random string for unique usernames"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

TEST_USERNAME = f"api_tester_{random_suffix()}"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"
TEST_PASSWORD = "testpassword123"

# Fixtures
@pytest.fixture
def api_client():
    """API client for testing backend endpoints"""
    session = requests.Session()
    yield session
    session.close()

@pytest.fixture
def auth_token(api_client):
    """Create a test user and get auth token"""
    # Register user
    register_data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    try:
        response = api_client.post(f"{API_URL}/auth/register", json=register_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        # User might already exist, try to get token directly
        pass
    
    # Get token
    token_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = api_client.post(f"{API_URL}/auth/token", json=token_data)
    token = response.json()["access_token"]
    return token

@pytest.fixture
def character_id(api_client, auth_token):
    """Create a test character and return its ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Check if character already exists
    response = api_client.get(f"{API_URL}/characters/", headers=headers)
    characters = response.json()
    
    if characters:
        return characters[0]["id"]
    
    # Create character if none exist
    character_data = {
        "name": f"TestChar_{random_suffix()}",
        "race": "HUMAN",
        "character_class": "FIGHTER",
        "strength": 14,
        "intelligence": 10,
        "wisdom": 12,
        "dexterity": 13,
        "constitution": 15,
        "charisma": 8
    }
    
    response = api_client.post(f"{API_URL}/characters/", json=character_data, headers=headers)
    return response.json()["id"]

# Tests
class TestAuthAPI:
    def test_health_check(self, api_client):
        """Test if the API is running"""
        response = api_client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
    def test_register_user(self, api_client):
        """Test user registration"""
        # Create a unique username for this test
        username = f"register_test_{random_suffix()}"
        email = f"{username}@test.com"
        
        register_data = {
            "username": username,
            "email": email,
            "password": TEST_PASSWORD
        }
        
        response = api_client.post(f"{API_URL}/auth/register", json=register_data)
        assert response.status_code == 200
        assert "id" in response.json()
        
    def test_token_generation(self, api_client, auth_token):
        """Test token generation"""
        # Just use the auth_token fixture
        assert auth_token is not None
        assert len(auth_token) > 0

class TestCharacterAPI:
    def test_character_creation(self, api_client, auth_token):
        """Test creating a new character"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        character_data = {
            "name": f"CreateTest_{random_suffix()}",
            "race": "DWARF",
            "character_class": "CLERIC",
            "strength": 12,
            "intelligence": 14,
            "wisdom": 16,
            "dexterity": 10,
            "constitution": 14,
            "charisma": 10
        }
        
        response = api_client.post(f"{API_URL}/characters/", json=character_data, headers=headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["id"] is not None
        assert result["name"] == character_data["name"]
        assert result["race"] == character_data["race"]
        assert result["character_class"] == character_data["character_class"]
        assert result["strength"] == character_data["strength"]
        
    def test_get_characters(self, api_client, auth_token, character_id):
        """Test retrieving all characters"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = api_client.get(f"{API_URL}/characters/", headers=headers)
        assert response.status_code == 200
        
        characters = response.json()
        assert isinstance(characters, list)
        assert len(characters) > 0
        assert any(char["id"] == character_id for char in characters)
        
    def test_get_character_by_id(self, api_client, auth_token, character_id):
        """Test retrieving a specific character"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = api_client.get(f"{API_URL}/characters/{character_id}", headers=headers)
        assert response.status_code == 200
        
        character = response.json()
        assert character["id"] == character_id

class TestInventoryAPI:
    def test_get_items(self, api_client, auth_token):
        """Test retrieving all items"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = api_client.get(f"{API_URL}/items/", headers=headers)
        assert response.status_code == 200
        
        items = response.json()
        assert isinstance(items, list)
        assert len(items) > 0
        
    def test_get_character_inventory(self, api_client, auth_token, character_id):
        """Test retrieving a character's inventory"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = api_client.get(f"{API_URL}/items/inventory/{character_id}", headers=headers)
        assert response.status_code == 200
        
        inventory = response.json()
        assert isinstance(inventory, list)
        # A newly created character should have starting equipment
        assert len(inventory) > 0
        
    def test_add_item_to_inventory(self, api_client, auth_token, character_id):
        """Test adding an item to inventory"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First get available items
        response = api_client.get(f"{API_URL}/items/", headers=headers)
        all_items = response.json()
        
        # Find an item not in inventory
        response = api_client.get(f"{API_URL}/items/inventory/{character_id}", headers=headers)
        inventory = response.json()
        inventory_ids = [item["id"] for item in inventory]
        
        # Find an item not in inventory
        test_item = None
        for item in all_items:
            if item["id"] not in inventory_ids:
                test_item = item
                break
        
        if test_item is None:
            pytest.skip("No suitable test item found (all items already in inventory)")
            
        # Add the item to inventory
        response = api_client.post(
            f"{API_URL}/items/inventory/{character_id}/add/{test_item['id']}", 
            headers=headers
        )
        assert response.status_code == 200
        
        # Verify item was added
        response = api_client.get(f"{API_URL}/items/inventory/{character_id}", headers=headers)
        updated_inventory = response.json()
        updated_ids = [item["id"] for item in updated_inventory]
        assert test_item["id"] in updated_ids
        
    def test_equip_unequip_item(self, api_client, auth_token, character_id):
        """Test equipping and unequipping an item"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get inventory
        response = api_client.get(
            f"{API_URL}/items/inventory/{character_id}?include_details=true", 
            headers=headers
        )
        inventory = response.json()
        
        # Find a weapon
        weapon = None
        for item in inventory:
            if item["item_type"] == "WEAPON" and item.get("equippable", False):
                weapon = item
                break
                
        if not weapon:
            pytest.skip("No equippable weapon in inventory")
            
        # Equip the weapon
        response = api_client.post(
            f"{API_URL}/items/inventory/{character_id}/equip",
            json={"item_id": weapon["id"], "slot": "main_hand"},
            headers=headers
        )
        assert response.status_code in [200, 201]
        
        # Verify it's equipped
        response = api_client.get(f"{API_URL}/characters/{character_id}", headers=headers)
        character = response.json()
        equipment = character.get("equipment", {})
        assert equipment.get("main_hand") == weapon["id"]
        
        # Unequip the weapon
        response = api_client.post(
            f"{API_URL}/items/inventory/{character_id}/unequip",
            params={"slot": "main_hand"},
            headers=headers
        )
        assert response.status_code == 200
        
        # Verify it's unequipped
        response = api_client.get(f"{API_URL}/characters/{character_id}", headers=headers)
        character = response.json()
        equipment = character.get("equipment", {})
        assert "main_hand" not in equipment or equipment["main_hand"] is None 