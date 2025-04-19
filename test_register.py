"""
Registration Test Script

This script tests the registration endpoint by creating a new user.
"""

import json
import logging
import requests
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"


def test_registration():
    """Test the registration endpoint"""
    
    # Create test user data
    timestamp = datetime.utcnow().timestamp()
    test_username = f"testuser_{timestamp}"
    test_email = f"{test_username}@example.com"
    test_password = "Password123!"
    
    user_data = {
        "username": test_username,
        "email": test_email,
        "password": test_password,
        "password_confirm": test_password
    }
    
    try:
        # Make the request
        logger.info(f"Sending registration request for user: {test_username}")
        response = requests.post(
            f"{API_URL}/api/auth/register",
            data=json.dumps(user_data),
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        if response.status_code == 200:
            logger.info(f"Registration successful!")
            logger.info(f"Response: {response.json()}")
            return True
        else:
            logger.error(f"Registration failed with status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_registration()
    if success:
        logger.info("Registration test completed successfully")
        sys.exit(0)
    else:
        logger.error("Registration test failed")
        sys.exit(1) 