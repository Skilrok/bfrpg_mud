import datetime
import json
import sys

import requests

# API endpoint for token generation
API_URL = "http://localhost:8000/api/auth/login"  # Corrected endpoint path

# User credentials
# Based on database check, we found these users in dev.db
CREDENTIALS = {
    "admin": {
        "username": "admin",
        "password": "password123",  # Updated with correct password
    },
    "test": {
        "username": "testuser",
        "password": "password",  # Default test password, assumption based on common practice
    },
}


def generate_token(user_type="admin"):
    """Generate a fresh authentication token"""
    try:
        # Get appropriate credentials
        if user_type not in CREDENTIALS:
            print(
                f"Error: Unknown user type '{user_type}'. Available options: {list(CREDENTIALS.keys())}"
            )
            return False

        creds = CREDENTIALS[user_type]
        username = creds["username"]
        password = creds["password"]

        print(f"Generating new token for user: {username}")

        # Prepare the request - using JSON format
        response = requests.post(
            API_URL, json={"username": username, "password": password}
        )

        # Logging full response for debugging
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text[:200]}")

        # Check if the request was successful
        if response.status_code == 200:
            token_data = response.json()

            if "access_token" in token_data:
                token = token_data["access_token"]
                token_type = token_data.get("token_type", "bearer")

                print("\n=== TOKEN GENERATED SUCCESSFULLY ===")
                print(f"Token Type: {token_type}")
                print(f"Access Token: {token}")

                # Decode token to get expiration
                try:
                    import base64

                    # Extract payload part of the JWT
                    token_parts = token.split(".")
                    if len(token_parts) >= 2:
                        # Adjust padding for base64 decoding
                        payload = token_parts[1]
                        payload += "=" * ((4 - len(payload) % 4) % 4)
                        decoded = base64.b64decode(payload)
                        payload_data = json.loads(decoded)

                        if "exp" in payload_data:
                            exp_timestamp = payload_data["exp"]
                            exp_date = datetime.datetime.fromtimestamp(exp_timestamp)
                            print(f"\nToken expires at: {exp_date}")

                            # Calculate time until expiration
                            now = datetime.datetime.now()
                            time_left = exp_date - now
                            hours, remainder = divmod(time_left.seconds, 3600)
                            minutes, seconds = divmod(remainder, 60)

                            print(
                                f"Valid for: {hours} hours, {minutes} minutes, {seconds} seconds"
                            )

                except Exception as e:
                    print(f"Could not decode token expiration: {e}")

                # Update test_look_command.py with the new token
                try:
                    with open("test_look_command.py", "r") as f:
                        content = f.read()

                    # Replace the token
                    import re

                    updated = re.sub(
                        r'AUTH_TOKEN = "[^"]*"', f'AUTH_TOKEN = "{token}"', content
                    )

                    with open("test_look_command.py", "w") as f:
                        f.write(updated)

                    print("\nUpdated test_look_command.py with new token")
                except Exception as e:
                    print(f"Could not update test script: {e}")
                    print("Please manually update AUTH_TOKEN in test_look_command.py")

                return True
            else:
                print(f"Error: Token data does not contain access_token: {token_data}")
                return False
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"Error generating token: {e}")
        import traceback

        print(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("Token Generator")
    print("==============\n")

    # Parse command-line arguments for user type
    user_type = "admin"  # Default
    if len(sys.argv) > 1:
        user_type = sys.argv[1]

    success = generate_token(user_type)
    if success:
        print("\nToken generation completed successfully!")
        sys.exit(0)
    else:
        print("\nToken generation failed!")
        sys.exit(1)
