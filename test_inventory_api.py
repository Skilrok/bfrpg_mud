"""
Manual test script for testing the inventory system
This script performs a series of API calls to test the inventory functionality
"""
import requests
import json
import sys
import time
import random
import string

# API base URL
BASE_URL = "http://localhost:8000"

# Generate a unique username to avoid conflicts
RANDOM_SUFFIX = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
USERNAME = f"inventory_tester_{RANDOM_SUFFIX}"
PASSWORD = "password123"


def print_separator():
    print("\n" + "=" * 70 + "\n")


def create_test_user():
    """Create a test user if it doesn't exist"""
    print(f"\nRegistering test user '{USERNAME}'...")
    
    # Create test user
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "username": USERNAME,
            "email": f"test_{RANDOM_SUFFIX}@example.com",
            "password": PASSWORD,
            "password_confirm": PASSWORD
        }
    )
    
    if response.status_code == 200:
        print("Test user registered successfully")
        return True
    elif "already exists" in response.text or "already registered" in response.text:
        print("User already exists, continuing...")
        return True
    else:
        print(f"Could not register user: {response.status_code} - {response.text}")
        return False


def get_token():
    """Get authentication token"""
    print("Getting auth token...")
    response = requests.post(
        f"{BASE_URL}/api/auth/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code != 200:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        sys.exit(1)
    
    token = response.json()["access_token"]
    print("Token obtained successfully")
    return token


def create_test_character(token):
    """Create a test character"""
    print("\nCreating test character...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # First check if we already have characters
    response = requests.get(
        f"{BASE_URL}/api/characters/", 
        headers=headers
    )
    
    if response.status_code == 200 and len(response.json()) > 0:
        print("Using existing character")
        return response.json()[0]["id"]
    
    # Create new test character
    character_data = {
        "name": "Inventory Tester",
        "description": "A character for testing inventory functions",
        "race": "human",
        "character_class": "fighter",
        "strength": 16,
        "intelligence": 10,
        "wisdom": 12,
        "dexterity": 14,
        "constitution": 15,
        "charisma": 8
    }
    
    response = requests.post(
        f"{BASE_URL}/api/characters/",
        json=character_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to create test character: {response.status_code} - {response.text}")
        sys.exit(1)
    
    character_id = response.json()["id"]
    print(f"Test character created with ID {character_id}")
    return character_id


def list_items(token):
    """List all items in the database"""
    print("\nListing all items...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/items/", 
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to list items: {response.status_code} - {response.text}")
        return []
    
    items = response.json()
    print(f"Found {len(items)} items")
    # Print first few items
    for i, item in enumerate(items[:5]):
        print(f"{i+1}. {item['name']} ({item['item_type']})")
    
    if len(items) > 5:
        print(f"...and {len(items) - 5} more")
    
    return items


def get_item_details(token, item_id):
    """Get details for a specific item"""
    print(f"\nGetting details for item {item_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/items/{item_id}", 
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get item details: {response.status_code} - {response.text}")
        return None
    
    item = response.json()
    print(f"Item: {item['name']} (Type: {item['item_type']})")
    return item


def create_test_item(token):
    """Create a test item"""
    print("\nCreating a test item...")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_item = {
        "name": "Test Magic Sword",
        "description": "A powerful sword created for testing",
        "item_type": "weapon",
        "value": 500,
        "weight": 3.0,
        "properties": {
            "damage": "2d6",
            "damage_type": "slashing",
            "magical": True,
            "bonus": 2
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/items/",
        json=test_item,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to create test item: {response.status_code} - {response.text}")
        sys.exit(1)
    
    item = response.json()
    print(f"Created test item '{item['name']}' with ID {item['id']}")
    return item["id"]


def get_character_inventory(token, character_id):
    """Get a character's inventory"""
    print(f"\nGetting inventory for character {character_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/items/inventory/{character_id}?include_details=true", 
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get inventory: {response.status_code} - {response.text}")
        return {}
    
    inventory = response.json()
    print(f"Character has {len(inventory)} item types in inventory")
    
    # Print inventory contents
    for item_id, item_data in inventory.items():
        print(f"- {item_data.get('name', 'Unknown')} (x{item_data['quantity']}) [ID: {item_id}]")
        if item_data.get('equipped', False):
            print(f"  [Equipped in slot: {item_data['slot']}]")
    
    return inventory


def get_character_details(token, character_id):
    """Get character details including equipment"""
    print(f"\nGetting details for character {character_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/characters/{character_id}", 
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get character details: {response.status_code} - {response.text}")
        return None
    
    character = response.json()
    print(f"Character: {character['name']}")
    print(f"Equipment: {json.dumps(character['equipment'], indent=2)}")
    print(f"Inventory (summary): {character['inventory'].keys()}")
    
    return character


def add_item_to_inventory(token, character_id, item_id, quantity=1):
    """Add an item to a character's inventory"""
    print(f"\nAdding item {item_id} (x{quantity}) to character {character_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    request_data = {
        "item_id": item_id,
        "quantity": quantity
    }
    
    print(f"Request data: {json.dumps(request_data)}")
    
    response = requests.post(
        f"{BASE_URL}/api/items/inventory/{character_id}/add",
        json=request_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to add item to inventory: {response.status_code} - {response.text}")
        return False
    
    print(f"Successfully added item to inventory")
    
    # Print the updated character data
    character_data = response.json()
    print(f"Updated inventory keys: {character_data['inventory'].keys()}")
    
    # Extra verification step - check if item was actually added
    item_id_str = str(item_id)
    if item_id_str in character_data['inventory']:
        print(f"✅ Item {item_id} was added to inventory successfully")
        print(f"Item data: {json.dumps(character_data['inventory'][item_id_str])}")
        return True
    else:
        print(f"❌ ERROR: Item {item_id} was NOT added to inventory!")
        print(f"Inventory contents: {list(character_data['inventory'].keys())}")
        return False


def equip_item(token, character_id, item_id, slot):
    """Equip an item in a specific slot"""
    print(f"\nEquipping item {item_id} in slot '{slot}' for character {character_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    request_data = {
        "item_id": item_id,
        "slot": slot
    }
    
    print(f"Request data: {json.dumps(request_data)}")
    
    response = requests.post(
        f"{BASE_URL}/api/items/inventory/{character_id}/equip",
        json=request_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to equip item: {response.status_code} - {response.text}")
        return False
    
    print(f"Successfully equipped item in slot '{slot}'")
    # Print the updated character data
    character_data = response.json()
    print(f"Updated equipment: {json.dumps(character_data['equipment'], indent=2)}")
    return True


def unequip_item(token, character_id, slot):
    """Unequip an item from a specific slot"""
    print(f"\nUnequipping item from slot '{slot}' for character {character_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/items/inventory/{character_id}/unequip?slot={slot}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to unequip item: {response.status_code} - {response.text}")
        return False
    
    print(f"Successfully unequipped item from slot '{slot}'")
    return True


def run_tests():
    """Run all inventory system tests"""
    print("Starting inventory system tests")
    print_separator()
    
    # Register user first
    create_test_user()
    
    # Get login token
    token = get_token()
    
    # Create test character
    character_id = create_test_character(token)
    
    # List items in database
    items = list_items(token)
    if not items:
        print("No items found in database. Please run seed_items.py first.")
        sys.exit(1)
    
    # Find an existing weapon in the database to work with
    existing_weapon = None
    for item in items:
        if item['item_type'] == 'weapon' and item['name'] == 'Longsword':
            existing_weapon = item
            break
    
    if existing_weapon:
        print(f"\nFound existing weapon: {existing_weapon['name']} (ID: {existing_weapon['id']})")
    else:
        print("No suitable weapon found in the database")
        sys.exit(1)
    
    # Get character's starting inventory
    inventory = get_character_inventory(token, character_id)
    
    # Get character details including equipment
    character = get_character_details(token, character_id)
    
    # Find Longsword in inventory
    longsword_id = None
    for item_id, item_data in inventory.items():
        if item_data.get('name') == 'Longsword':
            longsword_id = int(item_id)
            print(f"Found Longsword in inventory with ID: {longsword_id}")
            break
    
    if not longsword_id:
        print("Longsword not found in inventory")
        sys.exit(1)
    
    # Equip Longsword in main hand slot
    equip_result = equip_item(token, character_id, longsword_id, "main_hand")
    
    # Get character details to verify equipment
    character = get_character_details(token, character_id)
    
    # Only try to unequip if equip was successful
    if equip_result:
        # Unequip item
        unequip_item(token, character_id, "main_hand")
        
        # Final check of inventory and equipment
        get_character_inventory(token, character_id)
        get_character_details(token, character_id)
    
    print_separator()
    print("All inventory system tests completed successfully!")


if __name__ == "__main__":
    run_tests() 