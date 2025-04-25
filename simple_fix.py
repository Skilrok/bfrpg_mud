import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_look_command():
    """Add simple debug to the look command"""
    try:
        # Find the look command file
        file_path = "app/commands/look_commands.py"

        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Look command file not found: {file_path}")
            return False

        # Read the file
        with open(file_path, "r") as f:
            content = f.read()

        # Check if we already added debug
        if "# DEBUG ADDED" in content:
            logger.info("Debug already added, skipping")
            return True

        # Add a comment to mark it as debugged
        modified = content.replace(
            " +
            "async def _look_at_room(self, db: Session, character_id:"int) -> CommandResponse:",
            """async def _look_at_room(self, db: Session, character_id: int) -> CommandResponse:
        # DEBUG ADDED
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Looking at room for character {character_id}")""",
        )

        # Add debug after getting location
        modified = modified.replace(
            "room_id = location_data[0]",
            """room_id = location_data[0]
            logger.info(f"Found room ID: {room_id}")""",
        )

        # Add debug for room data
        modified = modified.replace(
            "room_name = room_data[1]",
            """room_name = room_data[1]
            logger.info(f"Room name: {room_name}")""",
        )

        # Add debug for response
        modified = modified.replace(
            "return CommandResponse(",
            """logger.info("Returning room description")
            return CommandResponse(""",
        )

        # Add more error logging
        modified = modified.replace(
            "except Exception as e:",
            """except Exception as e:
            import traceback
            logger.error(f"Error in look command: {str(e)}")
            logger.error(traceback.format_exc())""",
        )

        # Write the modified content back
        with open(file_path, "w") as f:
            f.write(modified)

        logger.info("Added debug to look command")
        return True
    except Exception as e:
        logger.error(f"Error fixing look command: {str(e)}")
        return False


def fix_websocket():
    """Add debug to WebSocket handling"""
    try:
        # Find the WebSocket file
        file_path = "app/websockets/__init__.py"

        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"WebSocket file not found: {file_path}")
            return False

        # Read the file
        with open(file_path, "r") as f:
            content = f.read()

        # Check if we already added debug
        if "# DEBUG ADDED TO WEBSOCKET" in content:
            logger.info("WebSocket debug already added, skipping")
            return True

        # Add debugging to command handling
        if "async def handle_command_message" in content:
            modified = content.replace(
                " +
            "async def handle_command_message(self, websocket:"WebSocket, message: dict, session_data: dict):",
                """async def handle_command_message(self, websocket: WebSocket, message: dict, session_data: dict):
        # DEBUG ADDED TO WEBSOCKET
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Received command message: {message}")
        try:""",
            )

            # Add debug to command execution
            modified = modified.replace(
                "return await command_handler.execute(context)",
                """try:
                result = await command_handler.execute(context)
                logger.info(f"Command executed with result: {result.success}")
                if result.message and len(result.message) > 0:
                    logger.info(f"Message (first 100 chars): {result.message[:100]}")
                else:
                    logger.warning("No message in command response")
                return result
            except Exception as e:
                import traceback
                logger.error(f"Error executing command: {str(e)}")
                logger.error(traceback.format_exc())
                from app.commands.base import CommandResponse
                return CommandResponse(
                    success=False,
                    message=f"Error: {str(e)}",
                    errors=[str(e)]
                )""",
            )

            # Add catch block to handle general errors
            modified = modified.replace(
                "await self.send_error(websocket, f\"Command '{command_name}' not found\")",
                """await self.send_error(websocket, f"Command '{command_name}' not found")
        except Exception as e:
            import traceback
            logger.error(f"Error in handle_command_message: {str(e)}")
            logger.error(traceback.format_exc())
            await self.send_error(websocket, f"Error: {str(e)}")""",
            )

            # Write the modified content back
            with open(file_path, "w") as f:
                f.write(modified)

            logger.info("Added debug to WebSocket command handling")
            return True
        else:
            logger.error("Could not find handle_command_message method")
            return False
    except Exception as e:
        logger.error(f"Error fixing WebSocket: {str(e)}")
        return False


# Simple direct fix for JavaScript
def fix_client_js():
    """Add debug to client-side JavaScript"""
    try:
        # Find the game.html file
        file_path = "static/game.html"

        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Game HTML file not found: {file_path}")
            return False

        # Read the file
        with open(file_path, "r") as f:
            content = f.read()

        # Check if we already added debug
        if "/* DEBUG ADDED TO CLIENT */" in content:
            logger.info("Client debug already added, skipping")
            return True

        # Find the socket.onmessage handler
        if "socket.onmessage = function(event)" in content:
            modified = content.replace(
                "socket.onmessage = function(event) {",
                """socket.onmessage = function(event) {
            /* DEBUG ADDED TO CLIENT */
            console.log("WebSocket message received:", event.data);
            try {
                const parsed = JSON.parse(event.data);
                console.log("Parsed message:", parsed);
            } catch (e) {
                console.error("Failed to parse message:", e);
            }""",
            )

            # Add debug to command sending
            if "function sendCommand()" in modified:
                modified = modified.replace(
                    "function sendCommand() {",
                    """function sendCommand() {
            /* DEBUG ADDED TO COMMAND SEND */
            console.log("Sending command:", commandInput.value);""",
                )

                # Add debug to WebSocket connection
                modified = modified.replace(
                    "socket.onopen = function(e) {",
                    """socket.onopen = function(e) {
            /* DEBUG ADDED TO WEBSOCKET OPEN */
            console.log("WebSocket connection opened");""",
                )

                # Add error handling for WebSocket
                if "socket.onerror = " not in modified:
                    modified = modified.replace(
                        "socket.onclose = function(event) {",
                        """socket.onerror = function(error) {
            console.error("WebSocket error:", error);
            appendToTerminal('<span class="error">WebSocket error. Check console for details.</span>');
        };

        socket.onclose = function(event) {
            /* DEBUG ADDED TO WEBSOCKET CLOSE */
            console.log("WebSocket connection closed:", event);""",
                    )

            # Write the modified content back
            with open(file_path, "w") as f:
                f.write(modified)

            logger.info("Added debug to client JavaScript")
            return True
        else:
            logger.error("Could not find socket.onmessage handler")
            return False
    except Exception as e:
        logger.error(f"Error fixing client JS: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Starting simple fix...")

    # Fix look command
    logger.info("Fixing look command...")
    look_result = fix_look_command()
    logger.info(f"Look command fix {'successful' if look_result else 'failed'}")

    # Fix WebSocket
    logger.info("Fixing WebSocket...")
    ws_result = fix_websocket()
    logger.info(f"WebSocket fix {'successful' if ws_result else 'failed'}")

    # Fix client JS
    logger.info("Fixing client JavaScript...")
    js_result = fix_client_js()
    logger.info(f"Client JavaScript fix {'successful' if js_result else 'failed'}")

    logger.info("Simple fix completed, please restart the server")
