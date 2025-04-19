"""
Character State Management Test Script

This script tests the character state management and deletion endpoints.
"""

import json
import logging
import requests
import sys
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define API URL
API_URL = "http://localhost:8000"

def test_character_state_and_deletion():
    """Test character state management and deletion endpoints"""
    
    # Step 1: Login to get authentication token
    login_data = {
        "username": "apitest_1745026090.844878",  # Use the test user created by test_api.py
        "password": "Password123!"
    }
    
    login_response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
    logger.info(f"Login response: {login_response.status_code}")
    
    if login_response.status_code != 200:
        logger.error(f"Failed to login: {login_response.text}")
        return False
    
    token_data = login_response.json()
    token = token_data.get("access_token")
    logger.info(f"Successfully logged in and got token")
    
    auth_header = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get a list of characters for the user
    characters_response = requests.get(f"{API_URL}/api/characters", headers=auth_header)
    
    if characters_response.status_code != 200:
        logger.error(f"Failed to get characters: {characters_response.text}")
        return False
    
    characters = characters_response.json()
    logger.info(f"Got {len(characters)} characters")
    
    if not characters:
        logger.info("Creating a test character first")
        # If no characters exist, create one
        character_data = {
            "name": "Test Character",
            "race": "human",
            "character_class": "fighter",
            "strength": 14,
            "dexterity": 12,
            "constitution": 15,
            "intelligence": 10,
            "wisdom": 8,
            "charisma": 13
        }
        
        create_response = requests.post(f"{API_URL}/api/characters", json=character_data, headers=auth_header)
        
        if create_response.status_code != 201:
            logger.error(f"Failed to create character: {create_response.text}")
            return False
        
        # Get the updated list of characters
        characters_response = requests.get(f"{API_URL}/api/characters", headers=auth_header)
        if characters_response.status_code != 200:
            logger.error(f"Failed to get characters after creation: {characters_response.text}")
            return False
        
        characters = characters_response.json()
    
    # Get the first character for testing state updates
    character = characters[0]
    character_id = character["id"]
    logger.info(f"Using character: {character['name']} (ID: {character_id}) for state update test")
    
    # Step 3: Update the character state
    update_data = {
        "hit_points": character["hit_points"] - 3,  # Reduce HP by 3
        "experience": character["experience"] + 1000,  # Add experience
        "gold": character["gold"] + 50  # Add gold
    }
    
    update_response = requests.patch(
        f"{API_URL}/api/characters/{character_id}/state", 
        json=update_data,
        headers=auth_header
    )
    
    if update_response.status_code != 200:
        logger.error(f"Failed to update character state: {update_response.text}")
        return False
    
    updated_character = update_response.json()
    logger.info(f"Character state updated: Level={updated_character['level']}, HP={updated_character['hit_points']}, Gold={updated_character['gold']}")
    
    # Step 4: Create a character specifically for deletion testing
    del_character_data = {
        "name": "Character To Delete",
        "race": "dwarf",
        "character_class": "cleric",
        "strength": 12,
        "dexterity": 10,
        "constitution": 16,
        "intelligence": 9,
        "wisdom": 14,
        "charisma": 11
    }
    
    create_response = requests.post(f"{API_URL}/api/characters", json=del_character_data, headers=auth_header)
    
    if create_response.status_code != 201:
        logger.error(f"Failed to create character for deletion test: {create_response.text}")
        return False
    
    del_character = create_response.json()
    del_character_id = del_character["id"]
    logger.info(f"Created character for deletion: {del_character['name']} (ID: {del_character_id})")
    
    # Delete the character
    delete_response = requests.delete(f"{API_URL}/api/characters/{del_character_id}", headers=auth_header)
    
    if delete_response.status_code != 204:
        logger.error(f"Failed to delete character: {delete_response.text}")
        return False
    
    logger.info(f"Successfully deleted character with ID: {del_character_id}")
    
    # Verify deletion by trying to get the character
    get_response = requests.get(f"{API_URL}/api/characters/{del_character_id}", headers=auth_header)
    if get_response.status_code == 404:
        logger.info("Character deletion verified - character not found")
    else:
        logger.error(f"Character deletion verification failed: {get_response.status_code}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_character_state_and_deletion()
    if success:
        logger.info("✅ Character state and deletion test passed")
        sys.exit(0)
    else:
        logger.error("❌ Character state and deletion test failed")
        sys.exit(1) 