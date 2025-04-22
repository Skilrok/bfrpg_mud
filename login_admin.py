import requests
import json

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
            print(f"Login successful! Token: {token_data['access_token']}")
            return token_data['access_token']
        else:
            print(f"Login failed with status code {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login request: {str(e)}")
        return None

def get_user_info(token):
    """Get information about the current user"""
    user_url = "http://localhost:8000/api/auth/me"
    
    try:
        response = requests.get(
            user_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"User information: {json.dumps(user_info, indent=2)}")
            return user_info
        else:
            print(f"Failed to get user info: {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting user info: {str(e)}")
        return None

def list_all_routes(token):
    """Try to discover available API routes"""
    base_url = "http://localhost:8000"
    potential_routes = [
        "/api",
        "/api/rooms",
        "/api/areas",
        "/api/characters",
        "/api/users",
        "/api/items",
        "/api/commands",
        "/docs",
        "/openapi.json"
    ]
    
    print("\nDiscovering available API routes:")
    for route in potential_routes:
        try:
            if route in ["/docs", "/openapi.json"]:
                # These don't need authentication
                response = requests.get(f"{base_url}{route}")
            else:
                response = requests.get(
                    f"{base_url}{route}",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )
            
            print(f"{route}: {response.status_code}")
        except Exception as e:
            print(f"{route}: Error - {str(e)}")

def check_character_location(token):
    """Check if the user has a character and where it's located"""
    characters_url = "http://localhost:8000/api/characters"
    
    try:
        response = requests.get(
            characters_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            characters = response.json()
            if characters and len(characters) > 0:
                print(f"Found {len(characters)} characters for the user")
                for idx, character in enumerate(characters):
                    print(f"\nCharacter {idx+1}:")
                    print(f"ID: {character.get('id')}")
                    print(f"Name: {character.get('name')}")
                    
                    # Try to get character location if possible
                    character_id = character.get('id')
                    if character_id:
                        location_url = f"http://localhost:8000/api/characters/{character_id}/location"
                        location_response = requests.get(
                            location_url,
                            headers={
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json"
                            }
                        )
                        
                        if location_response.status_code == 200:
                            location = location_response.json()
                            print(f"Location: {json.dumps(location, indent=2)}")
                        else:
                            print(f"Failed to get character location: {location_response.status_code}")
            else:
                print("No characters found for this user.")
        else:
            print(f"Failed to get characters: {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error checking character location: {str(e)}")

def explore_using_command_endpoint(token):
    """Try to use the command endpoint to execute a 'look' command"""
    command_url = "http://localhost:8000/api/commands"
    
    command_data = {
        "command": "look"
    }
    
    try:
        response = requests.post(
            command_url,
            json=command_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nCommand 'look' result: {json.dumps(result, indent=2)}")
        else:
            print(f"\nFailed to execute command: {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error executing command: {str(e)}")

if __name__ == "__main__":
    username = "admin"
    password = "admin123"
    
    # Login as admin
    token = login_admin(username, password)
    
    # If login successful, explore
    if token:
        # Get user information
        user_info = get_user_info(token)
        
        # List available routes
        list_all_routes(token)
        
        # Check if user has characters and their locations
        check_character_location(token)
        
        # Try using the command endpoint to look around
        explore_using_command_endpoint(token) 