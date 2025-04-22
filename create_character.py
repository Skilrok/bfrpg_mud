import requests
import json
import sys
import time

def login_admin(username, password):
    """Login as admin and get access token"""
    login_url = "http://localhost:8000/api/auth/login"
    
    # Prepare login payload
    login_data = {
        "username": username,
        "password": password
    }
    
    # Make login request
    try:
        response = requests.post(
            login_url, 
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if successful
        if response.status_code == 200:
            token_data = response.json()
            print(f"Login successful!")
            return token_data['access_token']
        else:
            print(f"Login failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login request: {str(e)}")
        return None

def create_character(token, character_data):
    """Create a character for the authenticated user"""
    create_url = "http://localhost:8000/api/characters"
    
    try:
        response = requests.post(
            create_url,
            json=character_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code in [200, 201]:
            character = response.json()
            print(f"Character created successfully!")
            print(f"Character ID: {character.get('id')}")
            print(f"Character Name: {character.get('name')}")
            return character
        else:
            print(f"Failed to create character: {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating character: {str(e)}")
        return None

def execute_command(token, cmd):
    """Execute a single command and return the result"""
    command_url = "http://localhost:8000/api/commands"
    
    try:
        print(f"Executing command: {cmd}")
        response = requests.post(
            command_url,
            json={"command": cmd},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Command result: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"Failed to execute command: {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return None

def try_character_creation_command(token, character_name):
    """Try to create a character using the command endpoint"""
    
    # Try a series of commands to create a character
    commands = [
        f"create character {character_name}",
        "race human",
        "class fighter",
        "standard",  # Use standard stats
        "confirm"  # Confirm character creation
    ]
    
    for cmd in commands:
        result = execute_command(token, cmd)
        
        if not result or not result.get("success", False):
            print(f"Command failed: {result.get('message', 'Unknown error') if result else 'No response'}")
            return None
            
        # Add a small delay between commands to allow server to process
        time.sleep(1)
    
    # If all commands succeeded, verify character was created
    print("\nVerifying character creation...")
    look_result = execute_command(token, "look")
    
    return look_result

if __name__ == "__main__":
    # Default login credentials
    username = "admin"
    password = "admin123"
    character_name = "Adventurer"
    
    # Allow character name override from command line
    if len(sys.argv) > 1:
        character_name = sys.argv[1]
    
    # Login as admin
    token = login_admin(username, password)
    
    if token:
        # Try to create the character using API endpoint
        character_data = {
            "name": character_name,
            "race": "human",
            "character_class": "fighter",
            "level": 1,
            "hit_points": 10,
            "strength": 16,
            "intelligence": 12,
            "wisdom": 10,
            "dexterity": 14,
            "constitution": 15,
            "charisma": 13,
            "armor_class": 12,
            "gold": 100,
            "save_death_ray_poison": 12,
            "save_magic_wands": 13,
            "save_paralysis_petrify": 14,
            "save_dragon_breath": 15,
            "save_spells": 16
        }
        
        character = create_character(token, character_data)
        
        # If direct API fails, try using commands
        if not character:
            print("\nTrying character creation via commands...")
            try_character_creation_command(token, character_name) 