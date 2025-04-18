import requests
import json
import random

# API endpoint URL
BASE_URL = "http://localhost:8000"

# Test user data
test_user = {
    "username": f"testuser_{random.randint(1000, 9999)}",
    "email": f"test_{random.randint(1000, 9999)}@example.com",
    "password": "testpassword123",
    "password_confirm": "testpassword123"
}

# Make the request
url = f"{BASE_URL}/api/auth/register"
print(f"Making request to: {url}")
print(f"With data: {json.dumps(test_user, indent=2)}")

try:
    # Enable request debugging
    requests_log = requests.packages.urllib3.add_stderr_logger()
    
    # Make the request with verbose error handling
    response = requests.post(url, json=test_user)
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    # Try to parse the response
    try:
        resp_json = response.json()
        print(f"Response JSON: {json.dumps(resp_json, indent=2)}")
    except json.JSONDecodeError:
        print(f"Raw response: {response.text}")
        
except Exception as e:
    print(f"Error: {e}") 