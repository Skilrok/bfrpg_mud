"""
API Test Script

This script tests various API endpoints to diagnose validation errors.
"""

import json
import logging
import requests
import sys
from datetime import datetime
from pprint import pprint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"


def test_endpoints():
    """Test various API endpoints"""
    
    # Check debug validation endpoint
    logger.info("Checking debug validation endpoint")
    debug_response = requests.get(f"{API_URL}/api/auth/debug-validation")
    if debug_response.status_code == 200:
        logger.info("Debug validation endpoint working")
        validation_info = debug_response.json()
        logger.info("Expected formats:")
        pprint(validation_info)
    else:
        logger.error(f"Debug validation endpoint failed: {debug_response.status_code}")
        logger.error(debug_response.text)
    
    # Test registration
    test_timestamp = datetime.utcnow().timestamp()
    test_username = f"apitest_{test_timestamp}"
    test_email = f"{test_username}@example.com"
    test_password = "Password123!"
    
    registration_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "password_confirm": test_password
    }
    
    logger.info(f"Testing registration for user: {test_username}")
    reg_response = requests.post(
        f"{API_URL}/api/auth/register",
        json=registration_data,
        headers={"Content-Type": "application/json"}
    )
    
    if reg_response.status_code == 200:
        logger.info("Registration successful!")
        logger.info(f"Response: {reg_response.json()}")
    else:
        logger.error(f"Registration failed with status {reg_response.status_code}")
        logger.error(f"Response: {reg_response.text}")
        
    # Test new login endpoint (JSON)
    login_data = {
        "username": test_username,
        "password": test_password
    }
    
    logger.info(f"Testing JSON login for user: {test_username}")
    login_response = requests.post(
        f"{API_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code == 200:
        logger.info("Login successful!")
        token_data = login_response.json()
        logger.info(f"Token type: {token_data['token_type']}")
        logger.info(f"Token: {token_data['access_token'][:20]}...")
    else:
        logger.error(f"Login failed with status {login_response.status_code}")
        logger.error(f"Response: {login_response.text}")
    
    # Test token endpoint (form data)
    logger.info(f"Testing form-based token endpoint for user: {test_username}")
    token_response = requests.post(
        f"{API_URL}/api/auth/token",
        data={"username": test_username, "password": test_password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if token_response.status_code == 200:
        logger.info("Token endpoint successful!")
        token_data = token_response.json()
        logger.info(f"Token type: {token_data['token_type']}")
        logger.info(f"Token: {token_data['access_token'][:20]}...")
    else:
        logger.error(f"Token endpoint failed with status {token_response.status_code}")
        logger.error(f"Response: {token_response.text}")
    
    return True


if __name__ == "__main__":
    success = test_endpoints()
    if success:
        logger.info("API test completed")
        sys.exit(0)
    else:
        logger.error("API test failed")
        sys.exit(1) 