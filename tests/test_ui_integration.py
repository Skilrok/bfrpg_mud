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

TEST_USERNAME = f"ui_tester_{random_suffix()}"
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

# Tests
class TestLoginPage:
    def test_login_page_loads(self, browser):
        """Test that the login page loads correctly"""
        browser.get(f"{BASE_URL}/login.html")
        assert "BFRPG MUD" in browser.title
        
        # Check for key elements
        assert browser.find_element(By.ID, "username-input").is_displayed()
        assert browser.find_element(By.ID, "password-input").is_displayed()
        assert browser.find_element(By.ID, "login-button").is_displayed()
    
    def test_login_functionality(self, browser, api_client, auth_token):
        """Test login functionality"""
        # First ensure user exists by using auth_token fixture
        assert auth_token
        
        # Now test the login UI
        browser.get(f"{BASE_URL}/login.html")
        
        username_input = browser.find_element(By.ID, "username-input")
        password_input = browser.find_element(By.ID, "password-input")
        login_button = browser.find_element(By.ID, "login-button")
        
        username_input.send_keys(TEST_USERNAME)
        password_input.send_keys(TEST_PASSWORD)
        login_button.click()
        
        # Wait for redirect to game page
        try:
            WebDriverWait(browser, 5).until(
                EC.url_to_be(f"{BASE_URL}/game.html")
            )
            assert browser.current_url == f"{BASE_URL}/game.html"
        except TimeoutException:
            pytest.fail("Login failed, did not redirect to game page")

class TestGameInterface:
    def test_game_ui_elements(self, browser, api_client, auth_token):
        """Test that the game UI has all required elements"""
        # Set token in localStorage to simulate logged in state
        browser.get(f"{BASE_URL}/login.html")
        browser.execute_script(f"localStorage.setItem('token', '{auth_token}');")
        browser.execute_script(f"localStorage.setItem('username', '{TEST_USERNAME}');")
        
        # Navigate to game page
        browser.get(f"{BASE_URL}/game.html")
        
        # Check for key UI elements
        assert browser.find_element(By.CLASS_NAME, "sidebar").is_displayed()
        assert browser.find_element(By.CLASS_NAME, "character-panel").is_displayed()
        assert browser.find_element(By.CLASS_NAME, "game-output").is_displayed()
        assert browser.find_element(By.ID, "command-input").is_displayed()
    
    def test_character_data_loaded(self, browser, api_client, auth_token, character_id):
        """Test that character data is loaded correctly in the UI"""
        # Get character data directly for comparison
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = api_client.get(f"{API_URL}/characters/{character_id}", headers=headers)
        character_data = response.json()
        
        # Set token in localStorage
        browser.get(f"{BASE_URL}/login.html")
        browser.execute_script(f"localStorage.setItem('token', '{auth_token}');")
        browser.execute_script(f"localStorage.setItem('username', '{TEST_USERNAME}');")
        browser.execute_script(f"localStorage.setItem('characterId', '{character_id}');")
        
        # Navigate to game page
        browser.get(f"{BASE_URL}/game.html")
        
        # Wait for character data to load
        try:
            WebDriverWait(browser, 5).until(
                EC.text_to_be_present_in_element(
                    (By.ID, "character-name"), 
                    character_data["name"]
                )
            )
            
            # Check basic character info
            assert character_data["name"] in browser.find_element(By.ID, "character-name").text
            assert character_data["race"] in browser.find_element(By.ID, "character-race").text
            assert character_data["character_class"] in browser.find_element(By.ID, "character-class").text
        except TimeoutException:
            pytest.fail("Character data did not load properly")
            
    def test_command_input(self, browser, api_client, auth_token, character_id):
        """Test that commands can be entered and processed"""
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
        
        # Enter and submit a command
        command_input = browser.find_element(By.ID, "command-input")
        command_input.send_keys("look")
        command_input.submit()
        
        # Wait for command output
        try:
            WebDriverWait(browser, 3).until(
                EC.text_to_be_present_in_element(
                    (By.CLASS_NAME, "game-output"), 
                    "look"
                )
            )
            output_text = browser.find_element(By.CLASS_NAME, "game-output").text
            assert "look" in output_text
        except TimeoutException:
            pytest.fail("Command did not produce output")
            
class TestInventorySystem:
    def test_inventory_display(self, browser, api_client, auth_token, character_id):
        """Test that inventory items are displayed correctly"""
        # Get inventory data directly
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = api_client.get(f"{API_URL}/items/inventory/{character_id}?include_details=true", headers=headers)
        inventory_data = response.json()
        
        # Setup browser session
        browser.get(f"{BASE_URL}/login.html")
        browser.execute_script(f"localStorage.setItem('token', '{auth_token}');")
        browser.execute_script(f"localStorage.setItem('username', '{TEST_USERNAME}');")
        browser.execute_script(f"localStorage.setItem('characterId', '{character_id}');")
        
        # Navigate to game page
        browser.get(f"{BASE_URL}/game.html")
        
        # Wait for inventory to load
        try:
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "equipment-list"))
            )
            
            equipment_list = browser.find_element(By.CLASS_NAME, "equipment-list")
            equipment_items = equipment_list.find_elements(By.TAG_NAME, "li")
            
            # Check that we have items
            assert len(equipment_items) > 0
            
            # Verify at least one item from API is in the list
            item_names = [item.text for item in equipment_items]
            api_item_names = [item["name"] for item in inventory_data]
            
            # Check if at least one API item is in the displayed list
            matching_items = [name for name in api_item_names if any(name in item_text for item_text in item_names)]
            assert len(matching_items) > 0, "No inventory items from API found in UI"
            
        except TimeoutException:
            pytest.fail("Inventory did not load properly")
    
    def test_equip_item(self, browser, api_client, auth_token, character_id):
        """Test that items can be equipped"""
        # Get inventory to find an item to equip
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = api_client.get(f"{API_URL}/items/inventory/{character_id}?include_details=true", headers=headers)
        inventory_data = response.json()
        
        # Find an equippable item (weapon or armor)
        equippable_item = None
        for item in inventory_data:
            if item["item_type"] in ["WEAPON", "ARMOR", "SHIELD"]:
                equippable_item = item
                break
        
        if not equippable_item:
            pytest.skip("No equippable items found in inventory")
            
        # Setup browser session
        browser.get(f"{BASE_URL}/login.html")
        browser.execute_script(f"localStorage.setItem('token', '{auth_token}');")
        browser.execute_script(f"localStorage.setItem('username', '{TEST_USERNAME}');")
        browser.execute_script(f"localStorage.setItem('characterId', '{character_id}');")
        
        # Navigate to game page
        browser.get(f"{BASE_URL}/game.html")
        
        # Wait for command input to be ready
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, "command-input"))
        )
        
        # Enter equip command
        command_input = browser.find_element(By.ID, "command-input")
        command_input.send_keys(f"equip {equippable_item['name']}")
        command_input.submit()
        
        # Check for equipped status via API
        time.sleep(2)  # Give some time for the command to process
        response = api_client.get(f"{API_URL}/characters/{character_id}", headers=headers)
        character_data = response.json()
        
        # Check if any slot has the item equipped
        equipment = character_data.get("equipment", {})
        assert any(item_id == equippable_item["id"] for item_id in equipment.values()), "Item was not equipped" 