import pytest
import requests
import json
import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test data
def random_suffix():
    """Generate a random string for unique usernames"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

TEST_USERNAME = f"api_tester_{random_suffix()}"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"
TEST_PASSWORD = "testpassword123"

# Fixtures
@pytest.fixture
def api_client():
    """API client for testing backend endpoints directly"""
    session = requests.Session()
    yield session
    session.close()

@pytest.fixture
def auth_token(api_client):
    """Create a test user and get auth token"""
    # Register user
    register_data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    try:
        response = api_client.post(f"{API_URL}/auth/register", json=register_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        # User might already exist, try to get token directly
        pass
    
    # Get token
    token_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    response = api_client.post(f"{API_URL}/auth/token", json=token_data)
    token = response.json()["access_token"]
    return token

@pytest.fixture
def character_id(api_client, auth_token):
    """Create a test character and return its ID"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Check if character already exists
    response = api_client.get(f"{API_URL}/characters/", headers=headers)
    characters = response.json()
    
    if characters:
        return characters[0]["id"]
    
    # Create character if none exist
    character_data = {
        "name": f"TestChar_{random_suffix()}",
        "race": "HUMAN",
        "character_class": "FIGHTER",
        "strength": 14,
        "intelligence": 10,
        "wisdom": 12,
        "dexterity": 13,
        "constitution": 15,
        "charisma": 8
    }
    
    response = api_client.post(f"{API_URL}/characters/", json=character_data, headers=headers)
    return response.json()["id"]

@pytest.fixture
def browser():
    """Selenium WebDriver fixture for UI testing"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headless for CI environments
    browser = webdriver.Chrome(options=options)
    browser.set_window_size(1366, 768)
    yield browser
    browser.quit()

@pytest.fixture
def game_session(browser, api_client, auth_token, character_id):
    """Set up a game session with a logged-in user and loaded character"""
    # Set token in localStorage
    browser.get(f"{BASE_URL}/login.html")
    browser.execute_script(f"localStorage.setItem('token', '{auth_token}');")
    browser.execute_script(f"localStorage.setItem('username', '{TEST_USERNAME}');")
    browser.execute_script(f"localStorage.setItem('characterId', '{character_id}');")
    
    # Navigate to game page
    browser.get(f"{BASE_URL}/game.html")
    
    # Wait for page to load
    WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.ID, "command-input"))
    )
    
    return browser

# Helper functions
def capture_network_requests(browser, url_filter=None):
    """Capture network requests made by the browser"""
    requests = []
    
    def request_interceptor(request):
        if url_filter is None or url_filter in request.url:
            requests.append({
                'url': request.url,
                'method': request.method,
                'headers': request.headers,
                'body': request.body
            })
    
    # Enable network interception
    browser.execute_cdp_cmd('Network.enable', {})
    browser.execute_cdp_cmd('Network.setRequestInterception', {'patterns': [{'urlPattern': '*'}]})
    
    # Register interceptor
    browser.request_interceptor = request_interceptor
    
    return requests

def send_command(browser, command):
    """Send a command to the game interface and return the output"""
    # Get initial output
    initial_output = browser.find_element(By.CLASS_NAME, "game-output").text
    
    # Send command
    command_input = browser.find_element(By.ID, "command-input")
    command_input.clear()
    command_input.send_keys(command)
    command_input.submit()
    
    # Wait for update
    time.sleep(1)
    
    # Get updated output
    updated_output = browser.find_element(By.CLASS_NAME, "game-output").text
    
    # Return only the new text
    if initial_output in updated_output:
        return updated_output[len(initial_output):].strip()
    return updated_output

# Tests
# Mark all API integration tests as expected to fail if running against a real API server
pytestmark = pytest.mark.xfail(reason="Integration tests require a running server and database")

class TestAuthenticationAPI:
    def test_register_api(self, api_client):
        """Test user registration API"""
        unique_username = f"test_user_{random_suffix()}"
        register_data = {
            "username": unique_username,
            "email": f"{unique_username}@test.com",
            "password": "testpassword123"
        }
        
        response = api_client.post(f"{API_URL}/auth/register", json=register_data)
        
        assert response.status_code == 200
        assert "id" in response.json()
        assert "username" in response.json()
        assert response.json()["username"] == unique_username
    
    def test_login_api(self, api_client):
        """Test user login API"""
        # Create a user first
        unique_username = f"login_test_{random_suffix()}"
        register_data = {
            "username": unique_username,
            "email": f"{unique_username}@test.com",
            "password": "testpassword123"
        }
        api_client.post(f"{API_URL}/auth/register", json=register_data)
        
        # Test login
        login_data = {
            "username": unique_username,
            "password": "testpassword123"
        }
        response = api_client.post(f"{API_URL}/auth/token", json=login_data)
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_login_ui_api_integration(self, browser):
        """Test that the login UI sends correct API requests"""
        # Generate unique test user
        unique_username = f"ui_login_test_{random_suffix()}"
        
        # Register user via API first
        session = requests.Session()
        register_data = {
            "username": unique_username,
            "email": f"{unique_username}@test.com",
            "password": "testpassword123"
        }
        session.post(f"{API_URL}/auth/register", json=register_data)
        
        # Navigate to login page
        browser.get(f"{BASE_URL}/login.html")
        
        # Fill login form
        username_field = browser.find_element(By.ID, "username")
        password_field = browser.find_element(By.ID, "password")
        login_button = browser.find_element(By.ID, "login-button")
        
        username_field.send_keys(unique_username)
        password_field.send_keys("testpassword123")
        
        # Setup network monitoring
        browser.execute_script("""
        window.lastRequest = null;
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            window.lastRequest = args;
            return originalFetch(...args);
        };
        """)
        
        # Click login
        login_button.click()
        
        # Wait for request to complete
        time.sleep(2)
        
        # Get request details
        request_info = browser.execute_script("return window.lastRequest;")
        
        # Check request was made to correct endpoint
        assert request_info and len(request_info) >= 1
        assert "/api/auth/token" in request_info[0]
        
        # Verify localStorage was updated
        token = browser.execute_script("return localStorage.getItem('token');")
        username = browser.execute_script("return localStorage.getItem('username');")
        
        assert token is not None and len(token) > 0
        assert username == unique_username

class TestCharacterAPI:
    def test_character_creation_api(self, api_client, auth_token):
        """Test character creation API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        character_data = {
            "name": f"TestChar_{random_suffix()}",
            "race": "HUMAN",
            "character_class": "FIGHTER",
            "strength": 14,
            "intelligence": 10,
            "wisdom": 12,
            "dexterity": 13,
            "constitution": 15,
            "charisma": 8
        }
        
        response = api_client.post(f"{API_URL}/characters/", json=character_data, headers=headers)
        
        assert response.status_code == 200
        assert "id" in response.json()
        assert "name" in response.json()
        assert response.json()["name"] == character_data["name"]
    
    def test_character_retrieval_api(self, api_client, auth_token, character_id):
        """Test character retrieval API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = api_client.get(f"{API_URL}/characters/{character_id}", headers=headers)
        
        assert response.status_code == 200
        assert "id" in response.json()
        assert response.json()["id"] == character_id
        assert "name" in response.json()
        assert "race" in response.json()
        assert "character_class" in response.json()
    
    def test_character_stats_api(self, api_client, auth_token, character_id):
        """Test character stats API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = api_client.get(f"{API_URL}/characters/{character_id}/stats", headers=headers)
        
        assert response.status_code == 200
        assert "strength" in response.json()
        assert "intelligence" in response.json()
        assert "wisdom" in response.json()
        assert "dexterity" in response.json()
        assert "constitution" in response.json()
        assert "charisma" in response.json()

class TestInventoryAPI:
    def test_inventory_retrieval_api(self, api_client, auth_token, character_id):
        """Test inventory retrieval API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = api_client.get(f"{API_URL}/characters/{character_id}/inventory", headers=headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        # New characters should have starting equipment
        assert len(response.json()) > 0
    
    def test_item_retrieval_api(self, api_client, auth_token):
        """Test item retrieval API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = api_client.get(f"{API_URL}/items/", headers=headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0
        
        # Check item structure
        first_item = response.json()[0]
        assert "id" in first_item
        assert "name" in first_item
        assert "item_type" in first_item
    
    def test_add_item_to_inventory_api(self, api_client, auth_token, character_id):
        """Test adding an item to inventory via API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get list of available items
        items_response = api_client.get(f"{API_URL}/items/", headers=headers)
        items = items_response.json()
        
        # Select an item to add
        item_id = items[0]["id"]
        
        # Add item to inventory
        add_data = {"item_id": item_id}
        response = api_client.post(
            f"{API_URL}/characters/{character_id}/inventory/add",
            json=add_data,
            headers=headers
        )
        
        assert response.status_code == 200
        assert "success" in response.json()
        assert response.json()["success"] is True

class TestGameCommandAPI:
    def test_look_command_api(self, api_client, auth_token, character_id):
        """Test 'look' command API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        command_data = {"command": "look"}
        response = api_client.post(
            f"{API_URL}/game/command",
            json=command_data,
            headers=headers
        )
        
        assert response.status_code == 200
        assert "response" in response.json()
        assert len(response.json()["response"]) > 0
    
    def test_help_command_api(self, api_client, auth_token, character_id):
        """Test 'help' command API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        command_data = {"command": "help"}
        response = api_client.post(
            f"{API_URL}/game/command",
            json=command_data,
            headers=headers
        )
        
        assert response.status_code == 200
        assert "response" in response.json()
        assert "Available commands" in response.json()["response"]
    
    def test_inventory_command_api(self, api_client, auth_token, character_id):
        """Test 'inventory' command API"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        command_data = {"command": "inventory"}
        response = api_client.post(
            f"{API_URL}/game/command",
            json=command_data,
            headers=headers
        )
        
        assert response.status_code == 200
        assert "response" in response.json()
        assert "You are carrying" in response.json()["response"]

class TestUIAPIIntegration:
    def test_command_input_api_call(self, game_session):
        """Test that command input in UI triggers API call"""
        browser = game_session
        
        # Setup fetch monitoring
        browser.execute_script("""
        window.apiCalls = [];
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            window.apiCalls.push(args);
            return originalFetch(...args);
        };
        """)
        
        # Send command
        command_input = browser.find_element(By.ID, "command-input")
        command_input.clear()
        command_input.send_keys("look")
        command_input.submit()
        
        # Wait for API call
        time.sleep(1)
        
        # Check API call was made
        api_calls = browser.execute_script("return window.apiCalls;")
        
        # Find calls to command endpoint
        command_calls = [call for call in api_calls if "/api/game/command" in call[0]]
        
        assert len(command_calls) > 0
        
        # Check request body
        request_details = command_calls[0][1] if len(command_calls[0]) > 1 else {}
        method = request_details.get("method")
        
        assert method == "POST"
    
    def test_command_response_display(self, game_session):
        """Test that command responses from API are displayed correctly"""
        browser = game_session
        
        # Send help command
        output = send_command(browser, "help")
        
        # Check for expected content in output
        assert "Available commands" in output
        
        # Send look command
        output = send_command(browser, "look")
        
        # Check for expected content in output
        assert len(output) > 0  # Should have some description
    
    def test_error_handling(self, game_session):
        """Test that API errors are handled and displayed properly"""
        browser = game_session
        
        # Send an invalid command that should trigger an error
        output = send_command(browser, "invalidcommandthatdoesntexist")
        
        # Check for error message
        assert "Unknown command" in output or "not recognized" in output
        
        # Check that UI is still responsive after error
        command_input = browser.find_element(By.ID, "command-input")
        assert command_input.is_enabled()
    
    def test_authentication_required(self, browser):
        """Test that unauthenticated access redirects to login"""
        # Go directly to game page without authentication
        browser.get(f"{BASE_URL}/game.html")
        
        # Wait briefly
        time.sleep(1)
        
        # Should redirect to login
        assert "login.html" in browser.current_url
    
    def test_persistent_game_state(self, api_client, auth_token, character_id, game_session):
        """Test that game state persists across page reloads"""
        browser = game_session
        
        # Send command to modify game state
        output = send_command(browser, "inventory")
        initial_inventory = output
        
        # Reload page
        browser.refresh()
        
        # Wait for page to load
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, "command-input"))
        )
        
        # Check inventory again
        output = send_command(browser, "inventory")
        reloaded_inventory = output
        
        # Should show same inventory
        assert initial_inventory in reloaded_inventory 