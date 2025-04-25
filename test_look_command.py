import asyncio
import datetime
import json as json_lib
import logging
import sys

import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
WS_URL = "ws://localhost:8000/ws/commands"
AUTH_TOKEN = " +
            ""eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0NTQ2MDgzNn0.cXclT2FsE23hCW9rshAwZnRbCGfiUE0Tb_zlrOOxwHw"
CHARACTER_ID = 10  # Change to your character ID


async def test_look_command():
    """Test the WebSocket connection and look command"""
    try:
        logger.info(f"Connecting to WebSocket at {WS_URL}")
        async with websockets.connect(WS_URL) as ws:
            # Send authentication
            auth_message = {
                "token": AUTH_TOKEN,
                "character_id": CHARACTER_ID,
                "session_id": "test_session_123",
            }
            logger.info(f"Sending authentication: {auth_message}")
            await ws.send(json_lib.dumps(auth_message))

            # Wait for authentication response
            response = await ws.recv()
            logger.info(f"Authentication response: {response}")

            # Check for auth errors
            response_data = json_lib.loads(response)
            if not response_data.get("success", False):
                if "Invalid or expired token" in response_data.get("message", ""):
                    print("\n===== TOKEN EXPIRED =====")
                    print(
                        " +
            "Your authentication token has expired. Please generate a"new token."
                    )
                    print("To generate a new token, you can use the login endpoint:")
                    print("POST /api/auth/login with username/password")

                    # Calculate expiration date from token
                    import base64

                    # Extract payload part of the JWT
                    try:
                        token_parts = AUTH_TOKEN.split(".")
                        if len(token_parts) >= 2:
                            # Adjust padding for base64 decoding
                            payload = token_parts[1]
                            payload += "=" * ((4 - len(payload) % 4) % 4)
                            decoded = base64.b64decode(payload)
                            payload_data = json_lib.loads(decoded)

                            if "exp" in payload_data:
                                exp_timestamp = payload_data["exp"]
                                exp_date = datetime.datetime.fromtimestamp(
                                    exp_timestamp
                                )
                                print(f"\nToken expires at: {exp_date}")
                                print(f"Current time: {datetime.datetime.now()}")
                    except Exception as e:
                        print(f"Could not parse token expiration: {e}")

                    return False
                else:
                    print(f"\nAuthentication failed: {response_data.get('message')}")
                    return False

            # Send look command
            logger.info("Sending 'look' command")
            await ws.send(json_lib.dumps({"command": "look"}))

            # Wait for command response
            response = await ws.recv()
            logger.info(f"Look command response received!")

            # Pretty print the response
            response_data = json_lib.loads(response)
            print("\n=== LOOK COMMAND RESPONSE ===")
            print(f"Success: {response_data.get('success')}")
            print(f"Message: {response_data.get('message')}")
            print("\nData:")
            if response_data.get("data"):
                for key, value in response_data["data"].items():
                    if isinstance(value, list) and len(value) > 0:
                        print(f"  {key}: {len(value)} items")
                    else:
                        print(f"  {key}: {value}")
            else:
                print("  No data returned")

            print("\nErrors:")
            if response_data.get("errors") and len(response_data["errors"]) > 0:
                for error in response_data["errors"]:
                    print(f"  - {error}")
            else:
                print("  No errors")

            # Send debug command as a test
            logger.info("Sending 'debug' command")
            await ws.send(json_lib.dumps({"command": "debug"}))

            # Wait for command response
            response = await ws.recv()
            debug_response = json_lib.loads(response)
            print("\n=== DEBUG COMMAND RESPONSE ===")
            print(f"Success: {debug_response.get('success')}")
            print(f"Message: {debug_response.get('message')}")

            logger.info("Test completed successfully")

    except websockets.exceptions.ConnectionClosedOK:
        logger.error(
            "Connection closed normally - likely due to authentication failure"
        )
        return False
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False

    return True


if __name__ == "__main__":
    print("WebSocket Look Command Test")
    print("==========================\n")

    try:
        result = asyncio.run(test_look_command())
        if result:
            print("\nTest completed successfully!")
            sys.exit(0)
        else:
            print("\nTest failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(2)
