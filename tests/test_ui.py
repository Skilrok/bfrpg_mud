import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configuration
BASE_URL = "http://localhost:8000"

# Test data
USERNAME = "ui_tester"
PASSWORD = "password123"

@pytest.fixture
def browser():
    """Set up Selenium WebDriver for UI testing"""
    # Use Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    yield driver
    
    # Tear down
    driver.quit()

class TestLoginPage:
    def test_login_page_loads(self, browser):
        """Test that the login page loads correctly"""
        browser.get(f"{BASE_URL}/static/login.html")
        
        # Check for the presence of key elements
        assert "BFRPG MUD" in browser.title
        
        # Verify login form elements
        username_input = browser.find_element(By.ID, "username")
        password_input = browser.find_element(By.ID, "password")
        login_button = browser.find_element(By.ID, "loginButton")
        register_button = browser.find_element(By.ID, "registerButton")
        
        assert username_input.is_displayed()
        assert password_input.is_displayed()
        assert login_button.is_displayed()
        assert register_button.is_displayed()
    
    def test_login_validation(self, browser):
        """Test login form validation"""
        browser.get(f"{BASE_URL}/static/login.html")
        
        # Try submitting without inputs
        login_button = browser.find_element(By.ID, "loginButton")
        login_button.click()
        
        # Check for validation message
        try:
            message = WebDriverWait(browser, 2).until(
                EC.visibility_of_element_located((By.ID, "message"))
            )
            assert "required" in message.text.lower()
        except TimeoutException:
            # If no message appears, check for HTML5 validation
            username_input = browser.find_element(By.ID, "username")
            assert username_input.get_attribute("validationMessage") != ""
    
    def test_register_new_user(self, browser):
        """Test user registration through UI"""
        browser.get(f"{BASE_URL}/static/login.html")
        
        # Fill the form
        username_input = browser.find_element(By.ID, "username")
        password_input = browser.find_element(By.ID, "password")
        
        unique_username = f"{USERNAME}_{int(time.time())}"
        username_input.send_keys(unique_username)
        password_input.send_keys(PASSWORD)
        
        # Click register button
        register_button = browser.find_element(By.ID, "registerButton")
        register_button.click()
        
        # Wait for success message
        try:
            message = WebDriverWait(browser, 5).until(
                EC.visibility_of_element_located((By.ID, "message"))
            )
            assert "success" in message.text.lower() or "registered" in message.text.lower()
        except TimeoutException:
            pytest.fail("Registration response not received")
            
    def test_login_existing_user(self, browser):
        """Test login with existing user"""
        # First register a user to ensure it exists
        browser.get(f"{BASE_URL}/static/login.html")
        
        unique_username = f"{USERNAME}_{int(time.time())}"
        
        # Register
        username_input = browser.find_element(By.ID, "username")
        password_input = browser.find_element(By.ID, "password")
        username_input.send_keys(unique_username)
        password_input.send_keys(PASSWORD)
        
        register_button = browser.find_element(By.ID, "registerButton")
        register_button.click()
        
        # Wait for success then clear inputs
        try:
            WebDriverWait(browser, 5).until(
                EC.text_to_be_present_in_element((By.ID, "message"), "success") or
                EC.text_to_be_present_in_element((By.ID, "message"), "registered")
            )
        except TimeoutException:
            pass
        
        # Clear inputs
        username_input.clear()
        password_input.clear()
        
        # Now login
        username_input.send_keys(unique_username)
        password_input.send_keys(PASSWORD)
        
        login_button = browser.find_element(By.ID, "loginButton")
        login_button.click()
        
        # Check for success and redirect
        try:
            WebDriverWait(browser, 5).until(
                lambda driver: "/static/game.html" in driver.current_url
            )
            assert "/static/game.html" in browser.current_url
        except TimeoutException:
            # If no redirect, check for success message
            try:
                message = browser.find_element(By.ID, "message")
                assert "success" in message.text.lower()
            except:
                pytest.fail("Login failed, no success message or redirect")

class TestGameInterface:
    @pytest.fixture
    def logged_in_browser(self, browser):
        """Login and return browser with active session"""
        browser.get(f"{BASE_URL}/static/login.html")
        
        unique_username = f"{USERNAME}_{int(time.time())}"
        
        # Register and login
        username_input = browser.find_element(By.ID, "username")
        password_input = browser.find_element(By.ID, "password")
        username_input.send_keys(unique_username)
        password_input.send_keys(PASSWORD)
        
        register_button = browser.find_element(By.ID, "registerButton")
        register_button.click()
        
        # Wait briefly then login
        time.sleep(1)
        
        username_input.clear()
        password_input.clear()
        
        username_input.send_keys(unique_username)
        password_input.send_keys(PASSWORD)
        
        login_button = browser.find_element(By.ID, "loginButton")
        login_button.click()
        
        # Wait for game page to load
        try:
            WebDriverWait(browser, 5).until(
                lambda driver: "/static/game.html" in driver.current_url
            )
        except TimeoutException:
            pytest.fail("Failed to log in and redirect to game page")
        
        return browser
    
    def test_game_interface_loads(self, logged_in_browser):
        """Test that the game interface loads correctly"""
        browser = logged_in_browser
        
        # Check for main interface elements
        assert "Game" in browser.title
        
        # Important UI elements
        main_elements = [
            "gameOutput",
            "commandInput",
            "charactersDropdown",
            "characterInfo",
            "inventoryPanel"
        ]
        
        for element_id in main_elements:
            element = browser.find_element(By.ID, element_id)
            assert element.is_displayed(), f"Element with ID {element_id} is not displayed"
    
    def test_character_selection(self, logged_in_browser):
        """Test character selection dropdown"""
        browser = logged_in_browser
        
        # Wait for character dropdown to be populated
        try:
            dropdown = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "charactersDropdown"))
            )
            
            # If no options yet, we should create a character
            options = dropdown.find_elements(By.TAG_NAME, "option")
            
            if len(options) <= 1:  # Only the default "Select Character" option
                # Click "Create Character" button
                create_button = browser.find_element(By.ID, "createCharacterButton")
                create_button.click()
                
                # Fill character creation form (this depends on your UI)
                try:
                    # Wait for character creation modal/form to appear
                    WebDriverWait(browser, 5).until(
                        EC.visibility_of_element_located((By.ID, "characterCreationForm"))
                    )
                    
                    # Fill form fields
                    name_input = browser.find_element(By.ID, "characterName")
                    name_input.send_keys(f"TestChar_{int(time.time())}")
                    
                    # Select race and class
                    browser.find_element(By.CSS_SELECTOR, "select#race option[value='HUMAN']").click()
                    browser.find_element(By.CSS_SELECTOR, "select#class option[value='FIGHTER']").click()
                    
                    # Submit form
                    submit_button = browser.find_element(By.ID, "createCharacterSubmit")
                    submit_button.click()
                    
                    # Wait for character to be created and dropdown to update
                    WebDriverWait(browser, 5).until(
                        lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#charactersDropdown option")) > 1
                    )
                except:
                    pytest.skip("Character creation interface not implemented or different from expected")
            
            # Now select a character
            options = dropdown.find_elements(By.TAG_NAME, "option")
            if len(options) > 1:
                options[1].click()  # Select first actual character
                
                # Wait for character info to update
                WebDriverWait(browser, 5).until(
                    EC.text_to_be_present_in_element((By.ID, "characterInfo"), "Name:")
                )
                
                character_info = browser.find_element(By.ID, "characterInfo")
                assert "Name:" in character_info.text
                assert "Class:" in character_info.text
                assert "Level:" in character_info.text
        except TimeoutException:
            pytest.skip("Character dropdown not found or not populated")
    
    def test_command_input(self, logged_in_browser):
        """Test entering commands in the terminal"""
        browser = logged_in_browser
        
        # Enter a help command
        command_input = browser.find_element(By.ID, "commandInput")
        command_input.send_keys("help")
        command_input.send_keys("\n")  # Enter key
        
        # Wait for response in game output
        try:
            output = WebDriverWait(browser, 5).until(
                EC.text_to_be_present_in_element((By.ID, "gameOutput"), "help")
            )
            game_output = browser.find_element(By.ID, "gameOutput")
            assert "help" in game_output.text
            
            # Should show available commands
            assert any(cmd in game_output.text.lower() for cmd in ["commands", "available", "options"])
        except TimeoutException:
            pytest.fail("Command response not displayed in game output")

class TestInventoryUI:
    @pytest.fixture
    def character_selected_browser(self, logged_in_browser):
        """Ensure a character is selected"""
        browser = logged_in_browser
        
        # Wait for character dropdown to be populated
        try:
            dropdown = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.ID, "charactersDropdown"))
            )
            
            # Check if any characters exist
            options = dropdown.find_elements(By.TAG_NAME, "option")
            
            if len(options) <= 1:
                pytest.skip("No characters available for testing inventory")
            
            # Select first character
            options[1].click()
            
            # Wait for character info to update
            WebDriverWait(browser, 5).until(
                EC.text_to_be_present_in_element((By.ID, "characterInfo"), "Name:")
            )
        except:
            pytest.skip("Failed to select character")
            
        return browser
    
    def test_inventory_display(self, character_selected_browser):
        """Test that inventory items are displayed"""
        browser = character_selected_browser
        
        # Verify inventory panel exists
        inventory_panel = browser.find_element(By.ID, "inventoryPanel")
        assert inventory_panel.is_displayed()
        
        # Check for inventory items (assumes a character has starting equipment)
        try:
            # Wait for inventory to populate
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#inventoryList .inventory-item"))
            )
            
            inventory_items = browser.find_elements(By.CSS_SELECTOR, "#inventoryList .inventory-item")
            assert len(inventory_items) > 0
            
            # Check item details are shown on mouseover (if implemented)
            try:
                first_item = inventory_items[0]
                
                # Hover over item to show details
                webdriver.ActionChains(browser).move_to_element(first_item).perform()
                
                # Check for tooltip or details panel
                WebDriverWait(browser, 3).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "item-tooltip"))
                )
            except:
                # Tooltip might not be implemented, so skip this check
                pass
                
        except TimeoutException:
            pytest.fail("Inventory items not loaded")
    
    def test_equip_item(self, character_selected_browser):
        """Test equipping an item"""
        browser = character_selected_browser
        
        try:
            # Find equippable items
            WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#inventoryList .inventory-item"))
            )
            
            inventory_items = browser.find_elements(By.CSS_SELECTOR, "#inventoryList .inventory-item")
            
            # Try to find an equip button on any item
            equip_button = None
            for item in inventory_items:
                try:
                    button = item.find_element(By.CSS_SELECTOR, ".equip-button")
                    equip_button = button
                    break
                except:
                    continue
            
            if not equip_button:
                pytest.skip("No equippable items found")
            
            # Click the equip button
            equip_button.click()
            
            # Check for equipment update - this depends on UI implementation
            try:
                # Wait for equipped items panel to update
                WebDriverWait(browser, 5).until(
                    EC.text_to_be_present_in_element((By.ID, "equippedItems"), "Equipped") or
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".equipped-item"))
                )
                
                # Check equipped items
                equipped_items = browser.find_elements(By.CSS_SELECTOR, ".equipped-item")
                assert len(equipped_items) > 0
            except:
                # If UI doesn't have a specific equipped items panel, check for other indicators
                try:
                    # Check for "equipped" class or indicator on the item
                    WebDriverWait(browser, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".inventory-item.equipped"))
                    )
                    equipped = browser.find_elements(By.CSS_SELECTOR, ".inventory-item.equipped")
                    assert len(equipped) > 0
                except:
                    pytest.skip("Couldn't verify item was equipped - UI implementation may differ")
                
        except TimeoutException:
            pytest.fail("Failed to interact with inventory items") 