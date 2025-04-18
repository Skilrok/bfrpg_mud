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

# Tests
class TestLoginPage:
    def test_login_page_loads(self, browser):
        """Test that the login page loads properly"""
        browser.get(f"{BASE_URL}/login.html")
        
        # Check for title
        assert "BFRPG MUD" in browser.title
        
        # Check for login form
        assert browser.find_element(By.ID, "login-form")
        assert browser.find_element(By.ID, "username")
        assert browser.find_element(By.ID, "password")
        assert browser.find_element(By.ID, "login-button")
    
    def test_login_page_styling(self, browser):
        """Test that login page has terminal styling"""
        browser.get(f"{BASE_URL}/login.html")
        
        # Check for terminal container
        terminal = browser.find_element(By.CLASS_NAME, "terminal")
        
        # Get computed style
        bg_color = browser.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", terminal)
        text_color = browser.execute_script("return window.getComputedStyle(arguments[0]).color", terminal)
        
        # Check for dark background (likely black or very dark)
        assert "0, 0, 0" in bg_color or "rgb(0, 0, 0)" in bg_color
        
        # Check for terminal-like text color (green, amber, or white)
        assert (
            "0, 255, 0" in text_color or  # Green
            "255, 255, 255" in text_color or  # White
            "255, 191, 0" in text_color  # Amber
        )
    
    def test_login_visual_effects(self, browser):
        """Test that login page has visual terminal effects"""
        browser.get(f"{BASE_URL}/login.html")
        
        # Look for scan lines, flicker, or glow effects
        effects = browser.find_elements(By.CSS_SELECTOR, ".scanline, .flicker, .glow, .terminal-effect")
        
        # Terminal UI should have at least one visual effect
        assert len(effects) > 0

class TestGameInterface:
    def test_game_interface_layout(self, game_session):
        """Test that the game interface has the correct layout"""
        browser = game_session
        
        # Check main UI elements
        assert browser.find_element(By.CLASS_NAME, "game-container")
        assert browser.find_element(By.CLASS_NAME, "game-output")
        assert browser.find_element(By.ID, "command-input")
        
        # Check positioning - output should be above input
        output_rect = browser.find_element(By.CLASS_NAME, "game-output").rect
        input_rect = browser.find_element(By.ID, "command-input").rect
        
        assert output_rect['y'] < input_rect['y']
    
    def test_game_terminal_styling(self, game_session):
        """Test that game interface has terminal styling"""
        browser = game_session
        
        # Check for terminal container
        terminal = browser.find_element(By.CLASS_NAME, "terminal")
        
        # Get computed style
        bg_color = browser.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", terminal)
        font_family = browser.execute_script("return window.getComputedStyle(arguments[0]).fontFamily", terminal)
        
        # Check for dark background (likely black or very dark)
        assert "0, 0, 0" in bg_color or "rgb(0, 0, 0)" in bg_color
        
        # Should use a monospace font
        assert any(font in font_family.lower() for font in ["monospace", "courier", "consolas", "lucida"])
    
    def test_command_input_styling(self, game_session):
        """Test that command input has appropriate styling"""
        browser = game_session
        
        # Get command input
        command_input = browser.find_element(By.ID, "command-input")
        
        # Get computed style
        bg_color = browser.execute_script("return window.getComputedStyle(arguments[0]).backgroundColor", command_input)
        text_color = browser.execute_script("return window.getComputedStyle(arguments[0]).color", command_input)
        border = browser.execute_script("return window.getComputedStyle(arguments[0]).border", command_input)
        
        # Command input should have contrasting background
        assert bg_color != "rgba(0, 0, 0, 0)"  # Not transparent
        
        # Should have visible text
        assert text_color != "rgba(0, 0, 0, 0)"  # Not transparent
        
        # Check if input has focus - should be focused by default
        focused_element = browser.execute_script("return document.activeElement")
        assert focused_element.get_attribute("id") == "command-input"

class TestGameOutput:
    def test_command_echo(self, game_session):
        """Test that commands are echoed to the output"""
        browser = game_session
        
        # Get initial output
        initial_output = browser.find_element(By.CLASS_NAME, "game-output").text
        
        # Send a test command
        command_input = browser.find_element(By.ID, "command-input")
        test_command = f"test {random_suffix()}"
        command_input.clear()
        command_input.send_keys(test_command)
        command_input.submit()
        
        # Wait for update
        time.sleep(1)
        
        # Get updated output
        updated_output = browser.find_element(By.CLASS_NAME, "game-output").text
        
        # Check that command was added to output
        assert test_command in updated_output
        assert len(updated_output) > len(initial_output)
    
    def test_output_scrolling(self, game_session):
        """Test that output scrolls with multiple commands"""
        browser = game_session
        command_input = browser.find_element(By.ID, "command-input")
        
        # Send multiple commands
        for i in range(10):
            test_command = f"test command {i}"
            command_input.clear()
            command_input.send_keys(test_command)
            command_input.submit()
            time.sleep(0.2)
        
        # Get scroll position
        scroll_position = browser.execute_script(
            "return document.querySelector('.game-output').scrollTop"
        )
        scroll_height = browser.execute_script(
            "return document.querySelector('.game-output').scrollHeight"
        )
        
        # Output should be scrolled down (not at top)
        assert scroll_position > 0
        
        # Should be near the bottom
        client_height = browser.execute_script(
            "return document.querySelector('.game-output').clientHeight"
        )
        max_scroll = scroll_height - client_height
        
        # Should be at or near max scroll (allowing some margin)
        assert scroll_position >= max_scroll - 50
    
    def test_output_formatting(self, game_session):
        """Test that output has appropriate text formatting"""
        browser = game_session
        
        # Send a look command to get formatted output
        command_input = browser.find_element(By.ID, "command-input")
        command_input.clear()
        command_input.send_keys("look")
        command_input.submit()
        
        time.sleep(1)
        
        # Get line height and font size
        output_element = browser.find_element(By.CLASS_NAME, "game-output")
        line_height = browser.execute_script("return window.getComputedStyle(arguments[0]).lineHeight", output_element)
        font_size = browser.execute_script("return window.getComputedStyle(arguments[0]).fontSize", output_element)
        
        # Line height should be reasonable for terminal output
        # Convert values to numbers for comparison
        line_height_value = float(line_height.replace("px", "")) if "px" in line_height else float(line_height)
        font_size_value = float(font_size.replace("px", ""))
        
        # Line height should be appropriate (typically 1.2-1.6x font size)
        assert line_height_value >= font_size_value  # At least equal to font size
        assert line_height_value <= font_size_value * 1.6  # Not too spaced out

class TestResponsiveness:
    def test_mobile_viewport(self, browser, api_client, auth_token, character_id):
        """Test that the game interface is responsive on mobile viewport"""
        # Set mobile viewport
        browser.set_window_size(375, 667)  # iPhone 8 size
        
        # Set up session
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
        
        # Check that elements are visible and properly sized
        game_container = browser.find_element(By.CLASS_NAME, "game-container")
        output = browser.find_element(By.CLASS_NAME, "game-output")
        input_field = browser.find_element(By.ID, "command-input")
        
        # Container should not overflow viewport
        assert game_container.rect['width'] <= 375
        
        # Input should be visible without scrolling
        viewport_height = browser.execute_script("return window.innerHeight")
        input_bottom = input_field.rect['y'] + input_field.rect['height']
        
        assert input_bottom <= viewport_height

    def test_landscape_viewport(self, browser, api_client, auth_token, character_id):
        """Test that the game interface works in landscape orientation"""
        # Set landscape viewport
        browser.set_window_size(740, 360)  # Mobile landscape
        
        # Set up session
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
        
        # Check that elements are visible and properly sized
        output = browser.find_element(By.CLASS_NAME, "game-output")
        input_field = browser.find_element(By.ID, "command-input")
        
        # Output should have reasonable height
        assert output.rect['height'] > 100
        
        # Input should be visible without scrolling
        viewport_height = browser.execute_script("return window.innerHeight")
        input_bottom = input_field.rect['y'] + input_field.rect['height']
        
        assert input_bottom <= viewport_height 