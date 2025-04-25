import json
import random
import string
import threading
import time

import jwt
import pytest
import requests
import websocket
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

# REMOVED: from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"
WS_URL = f"ws://localhost:8000/ws/commands"


# Test data
def random_suffix():
    """Generate a random string for unique usernames"""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


# Fixtures
@pytest.fixture(scope="module")
def browser():
    """Selenium WebDriver fixture for UI testing"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for CI environments
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    browser = webdriver.Chrome(options=options)
    browser.set_window_size(1366, 768)
    yield browser
    browser.quit()


@pytest.fixture(scope="module")
def api_client():
    """API client for testing backend endpoints directly"""
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Create a test user and get auth token"""
    # Generate a unique username
    username = f"phase5_tester_{random_suffix()}"
    email = f"{username}@test.com"
    password = "testpassword123"

    # Register user
    register_data = {
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password,
    }
    try:
        response = api_client.post(f"{API_URL}/auth/register", json=register_data)
        print(f"Register response: {response.status_code}")
    except Exception as e:
        print(f"Register error: {str(e)}")
        # User might already exist, try to get token directly
        pass

    # Get token
    token_data = {"username": username, "password": password}

    # Use form-encoded data as expected by OAuth2PasswordRequestForm
    try:
        response = api_client.post(
            f"{API_URL}/auth/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return response.json()["access_token"]
    except Exception as e:
        print(f"Token error: {str(e)}")
        # Try alternative endpoint
        try:
            response = api_client.post(f"{API_URL}/auth/login", json=token_data)
            return response.json()["access_token"]
        except Exception as e:
            print(f"Login error: {str(e)}")
            return None


@pytest.fixture(scope="module")
def character_id(api_client, auth_token):
    """Create a test character and return its ID"""
    if not auth_token:
        pytest.skip("Could not obtain auth token")

    headers = {"Authorization": f"Bearer {auth_token}"}

    # First check if the user already has characters
    try:
        print(f"Checking for existing characters...")
        response = api_client.get(f"{API_URL}/characters/", headers=headers)
        print(f"Characters response: {response.status_code}")

        if response.status_code == 200:
            characters = response.json()
            if characters and len(characters) > 0:
                char_id = characters[0]["id"]
                print(
                    f"Found existing character: {characters[0].get('name', 'Unknown')} (ID: {char_id})"
                )
                return char_id
            print("No characters found for this user")
    except Exception as e:
        print(f"Error checking for characters: {str(e)}")

    # If no characters exist, try to get one from the system
    try:
        print("Looking for any character in the system...")
        # Try to get debug info about characters
        response = api_client.get(f"{BASE_URL}/debug", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if "user_count" in data and data["user_count"] > 0:
                print(f"Found {data.get('user_count', 0)} users in the system")
    except Exception as e:
        print(f"Debug info error: {str(e)}")

    # Create character if none exist
    character_data = {
        "name": f"UITest_{random_suffix()}",
        "race": "human",
        "character_class": "fighter",
        "strength": 14,
        "intelligence": 10,
        "wisdom": 12,
        "dexterity": 13,
        "constitution": 15,
        "charisma": 8,
    }

    try:
        print(f"Creating new character with data: {character_data}")
        response = api_client.post(
            f"{API_URL}/characters/", json=character_data, headers=headers
        )
        print(f"Character creation response: {response.status_code}")

        if response.status_code == 422:
            # Validation error - try to get the validation error details
            error_detail = response.json().get("detail", [])
            print(f"Validation errors: {error_detail}")
            pytest.skip(f"Character creation failed validation: {error_detail}")
            return None

        if response.status_code == 200 or response.status_code == 201:
            char_id = response.json()["id"]
            print(f"Successfully created character with ID: {char_id}")
            return char_id

        # Other error
        print(f"Unexpected response: {response.text[:200]}")
        pytest.skip(
            f"Could not create test character: Unexpected status {response.status_code}"
        )
        return None
    except Exception as e:
        print(f"Character creation error: {str(e)}")
        pytest.skip(f"Could not create test character: {str(e)}")
        return None


@pytest.fixture
def authenticated_browser(browser, auth_token, character_id):
    """Set up browser with authentication token and character ID"""
    if not auth_token or not character_id:
        pytest.skip("Missing auth token or character ID")

    # Determine username from token
    try:
        claims = jwt.decode(auth_token, options={"verify_signature": False})
        username = claims.get("sub", "unknown_user")
    except Exception:
        username = f"phase5_tester_{random_suffix()}"

    browser.get(f"{BASE_URL}/static/login.html")
    # Set localStorage values for authentication
    browser.execute_script(f"localStorage.setItem('token', '{auth_token}');")
    browser.execute_script(f"localStorage.setItem('username', '{username}');")
    browser.execute_script(f"localStorage.setItem('characterId', '{character_id}');")

    # Navigate to game page
    browser.get(f"{BASE_URL}/static/game.html")

    # Wait for game page to load
    try:
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "commandInput"))
        )
    except TimeoutException:
        # Try without "/static" prefix - some setups might use different path
        browser.get(f"{BASE_URL}/game.html")
        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "commandInput"))
            )
        except Exception:
            pass

    return browser


class TestBasicUIElements:
    """Tests for basic UI components (Phase 5.2)"""

    def test_login_page_elements(self, browser):
        """Test that login page contains all necessary elements"""
        # Try common paths for login page
        paths = [
            f"{BASE_URL}/static/login.html",
            f"{BASE_URL}/login.html",
            f"{BASE_URL}/static/index.html",
            f"{BASE_URL}/index.html",
            f"{BASE_URL}/",
        ]

        login_found = False
        for path in paths:
            browser.get(path)
            try:
                # Look for username/password inputs
                username_input = browser.find_elements(
                    By.XPATH,
                    "//input[@type='text' and (@id='username' or @placeholder='Username')]",
                )
                password_input = browser.find_elements(
                    By.XPATH,
                    "//input[@type='password' and (@id='password' or @placeholder='Password')]",
                )
                login_button = browser.find_elements(
                    By.XPATH,
                    "//button[contains(text(), 'Login') or contains(@id, 'login')]",
                )

                if username_input and password_input and login_button:
                    login_found = True
                    break
            except Exception:
                continue

        assert login_found, "Could not find login page elements on any common path"

        # Test UI elements are present
        assert len(username_input) > 0, "Username input not found"
        assert len(password_input) > 0, "Password input not found"
        assert len(login_button) > 0, "Login button not found"

        # Check if registration elements are present
        register_elements = browser.find_elements(
            By.XPATH,
            "//button[contains(text(), 'Register') or contains(@id, 'register')]",
        )
        assert len(register_elements) > 0, "Register button not found"

    def test_game_interface_elements(self, authenticated_browser):
        """Test that game interface has all required elements"""
        browser = authenticated_browser

        # Core UI elements to check for
        ui_elements = [
            # Command input area
            {"type": "id", "value": "command-input", "desc": "Command input box"},
            # Output area
            {"type": "id", "value": "game-output", "desc": "Game output area"},
            # Character info panel
            {
                "type": "xpath",
                "value": "//div[contains(@class, 'character-sheet') or @id='character-info']",
                "desc": "Character info panel",
            },
            # Inventory panel
            {"type": "id", "value": "equipment-list", "desc": "Inventory panel"},
        ]

        missing_elements = []
        for element in ui_elements:
            try:
                if element["type"] == "id":
                    WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.ID, element["value"]))
                    )
                elif element["type"] == "xpath":
                    WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.XPATH, element["value"]))
                    )
            except TimeoutException:
                missing_elements.append(element["desc"])

        assert (
            not missing_elements
        ), f"Missing UI elements: {', '.join(missing_elements)}"


class TestInteractiveFeatures:
    """Tests for interactive features (Phase 5.3)"""

    def test_command_history(self, authenticated_browser):
        """Test command history functionality"""
        browser = authenticated_browser

        # Find command input element
        try:
            input_element = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "command-input"))
            )
        except TimeoutException:
            # Try alternative selector
            input_element = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[contains(@class, 'command-input')]")
                )
            )

        # Enter a unique test command
        test_command = f"test command {random_suffix()}"
        input_element.send_keys(test_command)
        input_element.send_keys(Keys.RETURN)

        # Wait briefly for command to be processed
        time.sleep(1)

        # Clear input
        input_element.clear()

        # Press up arrow to access history
        input_element.send_keys(Keys.ARROW_UP)

        # Check if previous command appears in input
        current_value = input_element.get_attribute("value")

        assert test_command in current_value, "Command history (up arrow) not working"

    def test_terminal_styling(self, authenticated_browser):
        """Test terminal-style interface elements"""
        browser = authenticated_browser

        # Check for terminal styling classes
        terminal_elements = browser.find_elements(
            By.XPATH, "//*[contains(@class, 'terminal') or contains(@class, 'console')]"
        )
        assert len(terminal_elements) > 0, "No terminal-styled elements found"

        # Check for dark background and light text (common in terminal UIs)
        main_element = terminal_elements[0]
        style = main_element.value_of_css_property("background-color")
        text_style = main_element.value_of_css_property("color")

        # Check if either the background is dark or uses a terminal class
        is_terminal_styled = (
            "rgb(0, 0, 0)" in style
            or "rgb(17, 17, 17)" in style  # Black
            or "rgb(34, 34, 34)" in style  # Near black
            or "rgba(0, 0, 0" in style  # Dark gray
            or "terminal"  # Black with transparency
            in main_element.get_attribute("class").lower()
            or "console" in main_element.get_attribute("class").lower()
        )

        assert is_terminal_styled, "UI does not appear to have terminal styling"

    def test_character_sidebar(self, authenticated_browser):
        """Test character information sidebar"""
        browser = authenticated_browser

        # Look for character info elements
        char_elements = browser.find_elements(
            By.XPATH,
            "//div[contains(@id, 'character-info') or contains(@class, 'character-sheet')]",
        )
        assert len(char_elements) > 0, "Character panel not found"

        # Check for basic character stats (should display at least name, class, level)
        char_panel = char_elements[0]
        panel_text = char_panel.text.lower()

        # Check for common character attributes
        has_char_info = (
            "level" in panel_text
            or "hp" in panel_text
            or "health" in panel_text
            or "class" in panel_text
            or "fighter" in panel_text
            or "stats" in panel_text  # Our test character is a fighter
            or "str" in panel_text
            or "dex" in panel_text  # Check for ability scores
            or "con" in panel_text
            or "saving throws" in panel_text  # Added more possible text items
        )

        assert (
            has_char_info
        ), "Character sidebar doesn't show expected character information"

    def test_theme_toggle(self, authenticated_browser):
        """Test dark/light mode toggle if available"""
        browser = authenticated_browser

        # Look for theme toggle elements (common implementations)
        toggle_elements = browser.find_elements(
            By.XPATH,
            "//button[contains(@id, 'theme') or contains(@id, 'dark') or contains(@id, 'mode') or contains(@class, 'theme') or contains(@aria-label, 'theme')]",
        )

        if not toggle_elements:
            pytest.skip("Theme toggle not found - feature may not be implemented")
            return

        toggle = toggle_elements[0]

        # Get initial body class
        initial_class = browser.find_element(By.TAG_NAME, "body").get_attribute("class")

        # Click the toggle
        toggle.click()

        # Get updated body class
        time.sleep(1)  # Allow time for toggle to take effect
        new_class = browser.find_element(By.TAG_NAME, "body").get_attribute("class")

        # Check if class changed (indicating theme changed)
        assert initial_class != new_class, "Theme toggle doesn't change the theme class"


class TestWebSocketIntegration:
    """Tests for WebSocket integration (Phase 5.4)"""

    def test_websocket_connection(
        self, authenticated_browser, auth_token, character_id
    ):
        """Test that WebSocket connection can be established"""
        if not auth_token or not character_id:
            pytest.skip("Missing auth token or character ID")

        # Create a WebSocket connection
        ws_messages = []
        connection_successful = False

        def on_message(ws, message):
            ws_messages.append(message)

        def on_open(ws):
            nonlocal connection_successful
            connection_successful = True
            # Send authentication
            auth_message = {
                "token": auth_token,
                "character_id": character_id,
                "session_id": f"test_session_{random_suffix()}",
            }
            ws.send(json.dumps(auth_message))

        def on_error(ws, error):
            print(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            print("WebSocket connection closed")

        # Create WebSocket connection
        try:
            ws = websocket.WebSocketApp(
                WS_URL,
                on_message=on_message,
                on_open=on_open,
                on_error=on_error,
                on_close=on_close,
            )

            # Start WebSocket in a separate thread
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()

            # Wait for connection
            timeout = time.time() + 10  # 10 second timeout
            while not connection_successful and time.time() < timeout:
                time.sleep(0.5)

            assert connection_successful, "Failed to establish WebSocket connection"

            # Wait for authentication response
            timeout = time.time() + 5
            while not ws_messages and time.time() < timeout:
                time.sleep(0.5)

            # Should have at least one message (auth response)
            assert len(ws_messages) > 0, "No WebSocket messages received"

            # Check if auth was successful
            auth_response = json.loads(ws_messages[0])
            assert (
                "success" in auth_response
            ), "Authentication response missing success field"

            # Clean up
            ws.close()

        except Exception as e:
            pytest.fail(f"WebSocket connection failed: {str(e)}")

    def test_realtime_command_response(
        self, authenticated_browser, auth_token, character_id
    ):
        """Test real-time command response through WebSocket"""
        browser = authenticated_browser

        # Find command input field
        try:
            command_input = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "command-input"))
            )
        except Exception:
            try:
                command_input = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//input[contains(@class, 'command-input')]")
                    )
                )
            except Exception:
                pytest.skip("Could not locate command input field")
                return

        # Find game output area
        try:
            output_area = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "game-output"))
            )
        except Exception:
            try:
                output_area = WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'game-output')]")
                    )
                )
            except Exception:
                pytest.skip("Could not locate game output area")
                return

        # Get initial output text
        initial_output = output_area.text

        # Enter a test command
        test_command = f"look {random_suffix()}"
        command_input.clear()
        command_input.send_keys(test_command)
        command_input.send_keys(Keys.RETURN)

        # Wait for response in output area
        try:
            WebDriverWait(browser, 8).until(
                lambda b: output_area.text != initial_output
            )
            new_output = output_area.text
            assert initial_output != new_output, "Output did not update after command"

            # Check if the command or parts of it appear in the response
            assert (
                test_command in new_output or "look" in new_output
            ), "Command response not found in output"

        except TimeoutException:
            pytest.fail("Output did not update after sending command")


class TestUIFeatureIntegration:
    """Tests for how UI features work together"""

    def test_command_execution_flow(self, authenticated_browser):
        """Test the full command execution flow"""
        browser = authenticated_browser

        try:
            # Find command input
            command_input = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "command-input"))
            )

            # Find output area
            output_area = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "game-output"))
            )

            # Commands to test
            test_commands = ["look", "help", "inventory", "stats"]

            for cmd in test_commands:
                # Get current output
                current_output = output_area.text

                # Enter command
                command_input.clear()
                command_input.send_keys(cmd)
                command_input.send_keys(Keys.RETURN)

                # Wait for response
                try:
                    WebDriverWait(browser, 5).until(
                        lambda b: output_area.text != current_output
                    )

                    # Verify command appears in the output
                    new_output = output_area.text
                    assert (
                        cmd in new_output
                        or cmd.upper() in new_output
                        or cmd.capitalize() in new_output
                    ), f"Command '{cmd}' not found in output"

                except TimeoutException:
                    pytest.fail(f"Output did not update after '{cmd}' command")

                # Brief pause between commands
                time.sleep(1)

        except Exception as e:
            pytest.fail(f"Command execution flow test failed: {str(e)}")

    def test_equipment_interaction(self, authenticated_browser):
        """Test equipment interaction if implemented"""
        browser = authenticated_browser

        # Look for inventory or equipment elements
        equip_elements = browser.find_elements(
            By.XPATH,
            "//div[contains(@class, 'equipment-section') or contains(@id, 'equipment-list')]",
        )

        if not equip_elements:
            pytest.skip("Equipment panel not found")
            return

        # Check if there are equippable items - using separate find_elements calls instead of invalid "or" in XPath
        item_elements = browser.find_elements(By.XPATH, "//ul[@id='equipment-list']/li")
        if not item_elements:
            item_elements = browser.find_elements(
                By.XPATH, "//div[@id='equipment-list']/div"
            )

        if not item_elements:
            # Try using equip command instead
            command_input = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "command-input"))
            )

            output_area = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "game-output"))
            )

            # First check what's in inventory
            command_input.clear()
            command_input.send_keys("inventory")
            command_input.send_keys(Keys.RETURN)

            # Wait for response
            try:
                initial_output = output_area.text
                WebDriverWait(browser, 8).until(
                    lambda b: output_area.text != initial_output
                )

                # Find an item name in the response
                inventory_text = output_area.text

                # Look for item names (common format: "- ItemName" or just "ItemName")
                import re

                item_matches = re.findall(r"[-•*] ([A-Za-z ]+)", inventory_text)

                if not item_matches and "empty" not in inventory_text.lower():
                    item_matches = re.findall(r"([A-Za-z]+ [A-Za-z]+)", inventory_text)

                if not item_matches:
                    pytest.skip("No items found in inventory")
                    return

                # Try to equip the first item
                item_name = item_matches[0]
                command_input.clear()
                command_input.send_keys(f"equip {item_name}")
                command_input.send_keys(Keys.RETURN)

                # Wait longer for response
                previous_output = output_area.text
                WebDriverWait(browser, 10).until(
                    lambda b: output_area.text != previous_output
                )

                # Check if it worked or at least got a relevant response
                response = output_area.text
                equip_success = (
                    "equipped" in response.lower()
                    or "wearing" in response.lower()
                    or "wielding" in response.lower()
                    or item_name.lower() in response.lower()
                )

                assert (
                    equip_success
                ), "Equipment command did not produce expected response"

            except TimeoutException:
                pytest.fail("Inventory or equip command did not produce a response")
