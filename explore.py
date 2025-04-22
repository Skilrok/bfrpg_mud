import json
import sys
import time

import requests


def login_admin(username, password):
    """Login as admin and get access token"""
    login_url = "http://localhost:8000/api/auth/login"

    # Prepare login payload
    login_data = {"username": username, "password": password}

    # Make login request
    try:
        response = requests.post(
            login_url, json=login_data, headers={"Content-Type": "application/json"}
        )

        # Check if successful
        if response.status_code == 200:
            token_data = response.json()
            print(f"Login successful!")
            return token_data["access_token"]
        else:
            print(
                f"Login failed with status code {response.status_code}: {response.text}"
            )
            return None
    except Exception as e:
        print(f"Error during login request: {str(e)}")
        return None


def execute_command(token, cmd, character_id=None):
    """Execute a single command and return the result"""
    command_url = "http://localhost:8000/api/commands"

    # Prepare command payload
    command_data = {"command": cmd}
    if character_id:
        command_data["character_id"] = character_id

    try:
        print(f"\nExecuting command: {cmd} (character_id: {character_id})")
        response = requests.post(
            command_url,
            json=command_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code == 200:
            result = response.json()
            print(f"Result: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"Failed to execute command: {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error executing command: {str(e)}")
        return None


def list_characters(token):
    """List all characters belonging to the user"""
    characters_url = "http://localhost:8000/api/characters"

    try:
        response = requests.get(
            characters_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code == 200:
            characters = response.json()
            if characters and len(characters) > 0:
                print(f"\nFound {len(characters)} characters:")
                for idx, character in enumerate(characters):
                    print(
                        f"{idx+1}. {character.get('name')} (ID: {character.get('id')})"
                    )
                return characters
            else:
                print("No characters found for this user.")
                return []
        else:
            print(f"Failed to get characters: {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"Error listing characters: {str(e)}")
        return []


def activate_character(token, character_id):
    """Activate a character for the current session"""
    activate_url = f"http://localhost:8000/api/characters/{character_id}/activate"

    try:
        response = requests.post(
            activate_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code in [200, 201, 204]:
            print(f"Character with ID {character_id} activated successfully!")
            return True
        else:
            print(
                f"Failed to activate character: {response.status_code}: {response.text}"
            )
            return False
    except Exception as e:
        print(f"Error activating character: {str(e)}")
        return False


def select_character_via_command(token, character_id):
    """Try to select a character using commands if the API endpoint doesn't work"""
    command = f"select character {character_id}"
    result = execute_command(token, command)

    if result and result.get("success", False):
        print(f"Character with ID {character_id} selected successfully!")
        return True
    else:
        # Try alternative command format
        command = f"use character {character_id}"
        result = execute_command(token, command)
        if result and result.get("success", False):
            print(f"Character with ID {character_id} selected successfully!")
            return True
        else:
            print(f"Failed to select character using commands.")
            return False


def explore_world(token, character_id):
    """Explore the MUD world using various commands"""
    # List of commands to try
    commands = [
        "look",  # Look at the current room
        "inventory",  # Check inventory
        "north",  # Try to move north
        "south",  # Try to move south
        "east",  # Try to move east
        "west",  # Try to move west
        "examine room",  # Examine the room
        "help",  # Get help
    ]

    for cmd in commands:
        result = execute_command(token, cmd, character_id)
        if not result:
            print(f"Command '{cmd}' failed, skipping...")
        elif not result.get("success", False):
            print(
                f"Command '{cmd}' didn't succeed. Message: {result.get('message', 'Unknown error')}"
            )

        # Add a small delay between commands
        time.sleep(1)


if __name__ == "__main__":
    # Default login credentials
    username = "admin"
    password = "admin123"

    # Login as admin
    token = login_admin(username, password)

    if token:
        # List characters to confirm they exist
        characters = list_characters(token)

        if characters:
            # Use the first character for exploration
            character_id = characters[0].get("id")
            print(f"\nUsing character with ID {character_id} for exploration")

            # Explore the world with this character
            explore_world(token, character_id)
        else:
            print("No characters found, please create a character first.")
            sys.exit(1)
