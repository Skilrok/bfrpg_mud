import json
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_inventory_command_route():
    """Test if the inventory command route exists and works as expected"""
    import requests

    # Get token from environment or prompt user
    token = os.environ.get("MUD_TOKEN")
    if not token:
        token = input("Enter your authentication token: ")

    # Get character ID from environment or prompt user
    character_id = os.environ.get("MUD_CHARACTER_ID")
    if not character_id:
        character_id = input("Enter your character ID: ")

    # Test base URL
    base_url = "http://localhost:8000"

    # Test URLs
    urls_to_test = [
        # 1. Test original API approach used in our fix
        {
            "url": f"{base_url}/api/commands/execute",
            "method": "POST",
            "data": {"command": "inventory", "character_id": character_id},
        },
        # 2. Test the commands endpoint used in the app
        {
            "url": f"{base_url}/api/commands",
            "method": "POST",
            "data": {"command": "inventory", "character_id": character_id},
        },
        # 3. Test the command endpoint used in the app (singular)
        {
            "url": f"{base_url}/api/commands/command",
            "method": "POST",
            "data": {"command": "inventory", "character_id": character_id},
        },
        # 4. Test if there's a dedicated inventory endpoint
        {
            "url": f"{base_url}/api/characters/{character_id}/inventory",
            "method": "GET",
            "data": None,
        },
    ]

    # Headers for authentication
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    results = {}

    # Try each URL
    for test in urls_to_test:
        logger.info(f"Testing {test['method']} {test['url']}")
        try:
            if test["method"] == "GET":
                response = requests.get(test["url"], headers=headers)
            else:  # POST
                response = requests.post(
                    test["url"], headers=headers, json=test["data"]
                )

            # Log response status and part of content
            logger.info(f"Response status: {response.status_code}")
            if response.status_code == 200:
                content = response.json()
                logger.info(
                    f"Response preview: {json.dumps(content, indent=2)[:200]}..."
                )
                results[test["url"]] = {
                    "status": response.status_code,
                    "success": True,
                    "data": content,
                }
            else:
                logger.error(f"Error response: {response.text}")
                results[test["url"]] = {
                    "status": response.status_code,
                    "success": False,
                    "error": response.text,
                }
        except Exception as e:
            logger.error(f"Exception testing {test['url']}: {str(e)}")
            results[test["url"]] = {
                "status": "error",
                "success": False,
                "error": str(e),
            }

    return results


def test_inventory_js_function():
    """Generates test code to check the loadInventory function in the browser console"""
    test_code = """
// Test for loadInventory function
// Copy and paste this into your browser console when on the game page
(async function() {
    console.log("Testing inventory loading...");

    // Get current character ID
    const characterId = localStorage.getItem('characterId');
    if (!characterId) {
        console.error("No character ID found in localStorage");
        return;
    }

    console.log(`Testing for character ID: ${characterId}`);

    // Test 1: Check if loadInventory function exists
    if (typeof loadInventory !== 'function') {
        console.error("loadInventory function does not exist!");

        console.log("Investigating available functions in the game.js context...");
        // Look at all functions defined in the current scope
        let functionNames = Object.keys(window).filter(key =>
            typeof window[key] === 'function' &&
            !key.startsWith('_') &&
            key !== key.toUpperCase()
        );
        console.log("Functions available:", functionNames.sort());

        // Try to inspect the structure of game.js directly
        const scriptElement = Array.from(document.querySelectorAll('script'))
            .find(s => s.src && s.src.includes('game.js'));

        if (scriptElement) {
            console.log("Game.js script element found:", scriptElement);
        } else {
            console.log("Could not find game.js script element");
        }
    } else {
        console.log("loadInventory function exists, testing it...");
        try {
            await loadInventory(characterId);
            console.log("loadInventory executed without errors");
        } catch (error) {
            console.error("Error calling loadInventory:", error);
        }
    }

    // Test 2: Check if direct inventory command works
    console.log("Testing inventory command directly...");
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            console.error("No auth token found");
            return;
        }

        // Try the command API endpoint
        const response = await fetch('/api/commands', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                character_id: characterId,
                command: "inventory"
            })
        });

        if (!response.ok) {
            console.error("API Error:", response.status, response.statusText);
            return;
        }

        const data = await response.json();
        console.log("Inventory command response:", data);

        // If successful, update the UI directly
        if (data.success && data.data && data.data.inventory) {
            console.log("Received inventory data, updating UI...");
            if (typeof updateInventory === 'function') {
                updateInventory(data.data.inventory);
                console.log("Inventory UI updated");
            } else {
                console.error("updateInventory function does not exist");
            }
        }
    } catch (error) {
        console.error("Error testing inventory command:", error);
    }
})();
    """

    print("\n\n=== Browser Console Test Code ===")
    print(test_code)
    print("=== End Browser Console Test Code ===\n")
    return test_code


if __name__ == "__main__":
    print("Running inventory loading tests...")

    # Test API routes
    results = test_inventory_command_route()

    # Generate and display browser test code
    test_inventory_js_function()

    # Display summary of results
    print("\n=== API Test Results ===")
    for url, result in results.items():
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"{status}: {url} - Status: {result['status']}")

    # Instructions for next steps
    print("\n=== Next Steps ===")
    print("1. Run the browser console test code to check client-side functionality")
    print(
        "2. Based on API results, update the loadInventory function to use the working endpoint"
    )
    print("3. Check for any errors in the updateInventory and related functions")
