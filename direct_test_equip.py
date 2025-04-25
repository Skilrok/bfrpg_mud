import asyncio

# REMOVED: import json

import requests


# Function to send command via API
async def execute_command(character_name, command):
    """Execute a command via API for the specified character"""
    url = "http://localhost:8000/api/commands/command"
    data = {"command": command, "character_name": character_name}

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error communicating with API: {e}")
        return None


# Main function to test equipment commands
async def test_equip_commands(character_name="EquipmentTest"):
    """Test equip and unequip commands for a character"""
    print(f"Testing equipment commands for character: {character_name}")

    # First check inventory to see what we have
    result = await execute_command(character_name, "inventory")
    if result:
        print("\nInventory:")
        print(result["message"])

    # Try to equip the Hand Axe
    print("\nAttempting to equip Hand Axe...")
    result = await execute_command(character_name, "equip Hand Axe")
    if result:
        print("Result:", result["message"])
        print("Success:", result["success"])

    # Check inventory again to verify equipment status
    result = await execute_command(character_name, "inventory")
    if result:
        print("\nUpdated Inventory:")
        print(result["message"])

    # Try to unequip the Hand Axe
    print("\nAttempting to unequip Hand Axe...")
    result = await execute_command(character_name, "unequip Hand Axe")
    if result:
        print("Result:", result["message"])
        print("Success:", result["success"])

    # Check inventory one more time
    result = await execute_command(character_name, "inventory")
    if result:
        print("\nFinal Inventory:")
        print(result["message"])


if __name__ == "__main__":
    asyncio.run(test_equip_commands())
