import requests
import json
import traceback

# API endpoint URL
BASE_URL = "http://localhost:8000"

# Test user credentials
username = "testuser"
password = "password123"

def get_token():
    url = f"{BASE_URL}/api/auth/token"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None
    
    print("Login successful")
    return response.json()["access_token"]

def check_character_endpoint(token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try a simple GET request first
    try:
        print("\nTesting GET /api/characters/")
        response = requests.get(f"{BASE_URL}/api/characters/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception during GET: {e}")
        traceback.print_exc()
    
    # Try the character creation with verbose debugging
    try:
        print("\nTesting POST /api/characters/")
        character_data = {
            "name": "TestChar",
            "description": "Test character",
            "race": "human",
            "character_class": "fighter",
            "strength": 16,
            "intelligence": 14,
            "wisdom": 12,
            "dexterity": 14,
            "constitution": 15,
            "charisma": 13
        }
        
        print(f"Sending data: {json.dumps(character_data, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/characters/", 
            headers=headers, 
            json=character_data,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(f"Raw response: {response.text}")
            
    except Exception as e:
        print(f"Exception during POST: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    token = get_token()
    if token:
        check_character_endpoint(token) 