"""
Authentication Test Script

This script tests the registration and token generation endpoints.
"""

import json
import random
import string

import requests

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


# Generate a random username
def random_suffix():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


TEST_USERNAME = f"test_user_{random_suffix()}"
TEST_PASSWORD = "testpassword123"
TEST_EMAIL = f"{TEST_USERNAME}@example.com"


def test_auth():
    print(f"Testing authentication with user: {TEST_USERNAME}")
    session = requests.Session()

    # 1. Try the debug validation endpoint
    print("\nChecking debug validation endpoint...")
    try:
        response = session.get(f"{API_URL}/auth/debug-validation")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")

    # 2. Register a user
    print("\nRegistering user...")
    register_data = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "password_confirm": TEST_PASSWORD,
    }
    try:
        response = session.post(f"{API_URL}/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {str(e)}")

    # 3. Get a token using form data
    print("\nGetting token...")
    token_data = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
    try:
        response = session.post(
            f"{API_URL}/auth/token",
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                print(f"Token: {token[:20]}...")
                return token
    except Exception as e:
        print(f"Error: {str(e)}")

    # 4. Try alternative login endpoint
    print("\nTrying login endpoint...")
    try:
        response = session.post(f"{API_URL}/auth/login", json=token_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                print(f"Token: {token[:20]}...")
                return token
    except Exception as e:
        print(f"Error: {str(e)}")

    return None


if __name__ == "__main__":
    token = test_auth()
    if token:
        print("Authentication test passed!")
    else:
        print("Authentication test failed - could not obtain token")
