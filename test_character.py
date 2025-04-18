import requests
import json

# API endpoint URL
BASE_URL = "http://localhost:8000"

# Test user credentials
username = "testuser"
password = "password123"

# Step 1: Login and get token
def get_token():
    url = f"{BASE_URL}/api/auth/token"
    data = {
        "username": username,
        "password": password
    }
    
    print(f"Logging in as {username}...")
    response = requests.post(url, data=data)
    
    if response.status_code != 200:
        print(f"Login failed with status code {response.status_code}")
        print(response.text)
        return None
    
    token_data = response.json()
    print("Login successful, token obtained")
    return token_data["access_token"]

# Step 2: Create a character
def create_character(token):
    url = f"{BASE_URL}/api/characters/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Character data
    character_data = {
        "name": "Aragorn",
        "description": "A rugged ranger from the North",
        "race": "human",
        "character_class": "fighter",
        "strength": 16,
        "intelligence": 14,
        "wisdom": 12,
        "dexterity": 14,
        "constitution": 15,
        "charisma": 13
    }
    
    print("Creating character...")
    print(f"POST {url}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(character_data, indent=2)}")
    
    response = requests.post(url, headers=headers, json=character_data)
    
    print(f"Response status code: {response.status_code}")
    
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    except:
        print(f"Raw response: {response.text}")
        
        # Check server logs
        try:
            debug_response = requests.get(f"{BASE_URL}/debug")
            print("\nDebug endpoint response:")
            print(f"Status: {debug_response.status_code}")
            print(json.dumps(debug_response.json(), indent=2))
        except Exception as e:
            print(f"Failed to get debug info: {e}")
        
        return None

# Main function
def main():
    # Get token
    token = get_token()
    if not token:
        return
    
    # Create character
    character = create_character(token)
    
    if character:
        print(f"\nCharacter created successfully: {character['name']}")
    else:
        print("\nFailed to create character")

if __name__ == "__main__":
    main() 