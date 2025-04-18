import requests
import json
import random

# Test the health check endpoint
url = "http://localhost:8000/health"
print(f"Testing API health check: {url}")

try:
    response = requests.get(url)
    print(f"Response status code: {response.status_code}")
    
    try:
        resp_json = response.json()
        print(f"Response JSON: {json.dumps(resp_json, indent=2)}")
    except json.JSONDecodeError:
        print(f"Raw response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")

BASE_URL = "http://127.0.0.1:8000/api"

def test_api():
    print("=== Testing BFRPG MUD API ===")
    
    # Check health endpoint first
    try:
        health_response = requests.get("http://127.0.0.1:8000/health")
        print(f"Health check response: {health_response.status_code}")
    except Exception as e:
        print(f"Health check error: {e}")
        return
    
    # Test user registration with random username to avoid conflicts
    random_num = random.randint(1000, 9999)
    username = f"testuser{random_num}"
    email = f"testuser{random_num}@example.com"
    password = "securepassword123"
    
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password
    }
    
    try:
        # Try simplified registration endpoint first
        simple_response = requests.post(f"{BASE_URL}/auth/register-simple", json=register_data)
        print(f"Simple Register Response: {simple_response.status_code}")
        if simple_response.status_code == 200:
            print(f"Simple registration successful: {simple_response.json()}")
        else:
            print(f"Simple Register Error: {simple_response.text}")
            
        # Register user
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Register User Response: {register_response.status_code}")
        
        if register_response.status_code == 200:
            user_data = register_response.json()
            print(f"User registered successfully: {user_data}")
            user_id = user_data.get("id")
            
            # Login user
            login_data = {
                "username": username,
                "password": password
            }
            
            login_response = requests.post(
                f"{BASE_URL}/auth/token", 
                data=login_data,  # Note: token endpoint expects form data, not JSON
            )
            
            print(f"Login Response: {login_response.status_code}")
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                print(f"Login successful, received token")
                
                # Test character creation with the token
                if access_token:
                    headers = {
                        "Authorization": f"Bearer {access_token}"
                    }
                    
                    # Create a character
                    character_data = {
                        "name": f"TestChar{random_num}",
                        "description": "A test character",
                        "race": "human",
                        "character_class": "fighter",
                        "strength": 15,
                        "intelligence": 10,
                        "wisdom": 10,
                        "dexterity": 12,
                        "constitution": 14,
                        "charisma": 10
                    }
                    
                    create_character_response = requests.post(
                        f"{BASE_URL}/characters/", 
                        json=character_data,
                        headers=headers
                    )
                    
                    print(f"Create Character Response: {create_character_response.status_code}")
                    
                    if create_character_response.status_code == 200:
                        character = create_character_response.json()
                        print(f"Character created successfully: {character}")
                        
                        # Get all characters for user
                        get_characters_response = requests.get(
                            f"{BASE_URL}/characters/", 
                            headers=headers
                        )
                        
                        print(f"Get Characters Response: {get_characters_response.status_code}")
                        
                        if get_characters_response.status_code == 200:
                            characters = get_characters_response.json()
                            print(f"Retrieved {len(characters)} characters")
                    else:
                        print(f"Create Character Error: {create_character_response.text}")
            else:
                print(f"Login Error: {login_response.text}")
        else:
            print(f"Register Error: {register_response.text}")
                
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    test_api() 