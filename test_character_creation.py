import requests
import json
import random

# API endpoint URL
BASE_URL = "http://localhost:8000"

# Register a new user
def register_user():
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "username": f"testuser_{random.randint(1000, 9999)}",
        "email": f"test_{random.randint(1000, 9999)}@example.com",
        "password": "testpassword123",
        "password_confirm": "testpassword123"
    }
    
    response = requests.post(url, json=data)
    print(f"Register User Response: {response.status_code}")
    if response.status_code != 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print("User registered successfully!")
    return data

# Login and get access token
def login_user(username, password):
    # For token endpoint, FastAPI expects form data, not JSON
    url = f"{BASE_URL}/api/auth/token"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, data=data)
    print(f"Login Response: {response.status_code}")
    if response.status_code != 200:
        print(json.dumps(response.json(), indent=2))
        raise Exception("Login failed")
    
    result = response.json()
    print("Login successful, token obtained")
    return result["access_token"]

# Create a new character
def create_character(access_token):
    url = f"{BASE_URL}/api/characters/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Static ability scores for testing
    character_data = {
        "name": f"Hero_{random.randint(1000, 9999)}",
        "description": "A brave adventurer",
        "race": "human",
        "character_class": "fighter",
        "strength": 16,
        "intelligence": 10,
        "wisdom": 12,
        "dexterity": 14,
        "constitution": 15,
        "charisma": 8
    }
    
    response = requests.post(url, json=character_data, headers=headers)
    print(f"Create Character Response: {response.status_code}")
    if response.status_code != 200:
        print(json.dumps(response.json(), indent=2))
        raise Exception("Character creation failed")
    else:
        char_data = response.json()
        print(f"Character '{char_data['name']}' created successfully!")
        print(f"Hit Points: {char_data['hit_points']}")
        print(f"Armor Class: {char_data['armor_class']}")
        print(f"Gold: {char_data['gold']}")
    
    return response.json()

def main():
    try:
        print("=== Testing BFRPG MUD API ===")
        
        # Register a new user
        user_data = register_user()
        
        # Login with the new user
        access_token = login_user(user_data["username"], user_data["password"])
        
        # Create a new character
        character = create_character(access_token)
        
        print("\n=== Test Completed Successfully ===")
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main() 