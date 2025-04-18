import pytest
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import string

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Test data
def random_suffix():
    """Generate a random string for unique usernames"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

TEST_USERNAME = f"command_tester_{random_suffix()}"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"
TEST_PASSWORD = "testpassword123"

# Fixtures
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
def send_command(browser, command):
    """Send a command and return the output"""
    command_input = browser.find_element(By.ID, "command-input")
    command_input.clear()
    command_input.send_keys(command)
    command_input.submit()
    
    # Wait for response
    time.sleep(1)  # Allow time for processing
    
    # Return the game output
    return browser.find_element(By.CLASS_NAME, "game-output").text

# Tests
class TestBasicCommands:
    def test_help_command(self, game_session):
        """Test the help command"""
        browser = game_session
        output = send_command(browser, "help")
        
        assert "Available commands" in output
        assert "look" in output.lower()
        assert "inventory" in output.lower()
    
    def test_look_command(self, game_session):
        """Test the look command"""
        browser = game_session
        output = send_command(browser, "look")
        
        # Basic check that look returns some description
        assert len(output) > 20
        assert "You see" in output or "You are" in output
    
    def test_inventory_command(self, game_session):
        """Test the inventory command"""
        browser = game_session
        output = send_command(browser, "inventory")
        
        assert "inventory" in output.lower()
        # A new character should have some starting equipment
        assert "You are carrying" in output or "You have" in output
    
    def test_stats_command(self, game_session):
        """Test the stats command"""
        browser = game_session
        output = send_command(browser, "stats")
        
        assert "stats" in output.lower()
        # Should show ability scores
        assert "strength" in output.lower()
        assert "dexterity" in output.lower()
        assert "constitution" in output.lower()
        assert "intelligence" in output.lower()
        assert "wisdom" in output.lower()
        assert "charisma" in output.lower()

    def test_unknown_command(self, game_session):
        """Test response to unknown command"""
        browser = game_session
        output = send_command(browser, f"nonsense_{random_suffix()}")
        
        assert "unknown command" in output.lower() or "don't understand" in output.lower()

class TestInventoryCommands:
    def test_equip_command(self, game_session, api_client, auth_token, character_id):
        """Test equipping an item"""
        browser = game_session
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get inventory to find an equippable item
        response = api_client.get(f"{API_URL}/items/inventory/{character_id}?include_details=true", headers=headers)
        inventory = response.json()
        
        # Find an equippable weapon
        equippable_item = None
        for item in inventory:
            if "weapon" in item.get("item_type", "").lower():
                equippable_item = item
                break
        
        if equippable_item:
            output = send_command(browser, f"equip {equippable_item['name']}")
            assert "equipped" in output.lower() or "wearing" in output.lower() or "wielding" in output.lower()
        else:
            # If no equippable item found, at least verify the command structure works
            output = send_command(browser, "equip sword")
            assert output  # Should get some response
    
    def test_unequip_command(self, game_session):
        """Test unequipping an item"""
        browser = game_session
        
        # First try to equip something (continuing from previous test)
        send_command(browser, "equip sword")
        
        # Now try to unequip
        output = send_command(browser, "unequip sword")
        assert output  # Should get some response
    
    def test_examine_command(self, game_session, api_client, auth_token, character_id):
        """Test examining an item"""
        browser = game_session
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get inventory
        response = api_client.get(f"{API_URL}/items/inventory/{character_id}", headers=headers)
        inventory = response.json()
        
        if inventory:
            test_item = inventory[0]
            output = send_command(browser, f"examine {test_item['name']}")
            assert test_item['name'].lower() in output.lower()
        else:
            # Fallback test
            output = send_command(browser, "examine backpack")
            assert output  # Should get some response

class TestMovementCommands:
    def test_direction_commands(self, game_session):
        """Test basic movement commands"""
        browser = game_session
        
        # Test each cardinal direction
        directions = ["north", "east", "south", "west"]
        
        for direction in directions:
            output = send_command(browser, direction)
            
            # We don't know if movement is possible in the test environment,
            # but we should get some response
            assert len(output) > 0
            assert direction in output.lower() or "can't go" in output.lower() or "moved" in output.lower()
    
    def test_go_command(self, game_session):
        """Test the 'go' command"""
        browser = game_session
        output = send_command(browser, "go north")
        
        # We don't know if movement is possible in the test environment,
        # but we should get some response
        assert len(output) > 0
        assert "north" in output.lower() or "can't go" in output.lower() or "moved" in output.lower()

class TestChatCommands:
    def test_say_command(self, game_session):
        """Test the say command"""
        browser = game_session
        test_message = f"Hello world {random_suffix()}"
        output = send_command(browser, f"say {test_message}")
        
        assert "say" in output.lower() or "said" in output.lower()
        assert test_message in output
    
    def test_emote_command(self, game_session):
        """Test the emote command"""
        browser = game_session
        test_emote = f"waves {random_suffix()}"
        output = send_command(browser, f"emote {test_emote}")
        
        assert TEST_USERNAME in output
        assert test_emote in output 