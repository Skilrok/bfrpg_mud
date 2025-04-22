import json
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_websocket_command_response():
    """
    Improve the WebSocket command response handling
    """
    try:
        # Find the websocket manager implementation
        websocket_file = os.path.join("app", "websockets", "__init__.py")

        # Check if file exists
        if not os.path.exists(websocket_file):
            logger.error(f"WebSocket file not found: {websocket_file}")
            return False

        # Read the current file
        with open(websocket_file, "r") as f:
            content = f.read()

        # Check if this fix is needed
        if "# Fixed WebSocket response handling" in content:
            logger.info("WebSocket response handling already fixed")
            return True

        # Find the code section that handles commands
        if "await websocket.send_json" in content and "response.success" in content:
            # Log what we found
            logger.info("Found command response section in WebSocket code")

            # Let's update the command execution code to ensure responses are processed correctly
            original_code = """                            # Execute command
                            response = await command_registry.execute_command(ctx)

                            # Send response back to client
                            await websocket.send_json(
                                {
                                    "success": response.success,
                                    "message": response.message,
                                    "errors": response.errors,
                                    "data": response.data,
                                    "command": {
                                        "raw": command_text,
                                        "name": cmd,
                                        "args": args
                                    }
                                }
                            )"""

            new_code = """                            # Execute command
                            # Fixed WebSocket response handling
                            response = await command_registry.execute_command(ctx)

                            # Add debug logging for response
                            logger.info(f"Command response: success={response.success}, message={response.message[:50]}...")

                            # Prepare response for client
                            response_data = {
                                "success": response.success,
                                "message": response.message,
                                "errors": response.errors or [],
                                "data": response.data or {},
                                "command": {
                                    "raw": command_text,
                                    "name": cmd,
                                    "args": args
                                }
                            }

                            # Log response before sending
                            logger.info(f"Sending response to client for command: {cmd}")

                            try:
                                # Send response back to client
                                await websocket.send_json(response_data)
                                logger.info("Response sent successfully")
                            except Exception as e:
                                logger.error(f"Error sending response: {str(e)}")"""

            # Update the content
            updated_content = content.replace(original_code, new_code)

            # Write the updated content
            with open(websocket_file, "w") as f:
                f.write(updated_content)

            logger.info("Updated WebSocket command response handling")
            return True
        else:
            logger.error("Could not find WebSocket command response section")
            return False

    except Exception as e:
        logger.error(f"Error fixing WebSocket command response: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def enhance_debug_command():
    """
    Improve the debug command to return more useful information
    """
    try:
        # Find the debug command file
        debug_file = os.path.join("app", "commands", "debug_command.py")

        # Check if file exists
        if not os.path.exists(debug_file):
            logger.error(f"Debug command file not found: {debug_file}")
            return False

        # Read the current file
        with open(debug_file, "r") as f:
            content = f.read()

        # Check if the command needs enhancement
        if "# Enhanced debug command" in content:
            logger.info("Debug command already enhanced")
            return True

        # Update the execute method to return more useful information
        if "async def execute(self, ctx: CommandContext)" in content:
            # Log what we found
            logger.info("Found debug command execute method")

            # Find the section that returns the response
            original_code = """        # Return a simple response
        return CommandResponse(
            success=True,
            message="Debug command executed successfully! The command system is working.",
            data={"args": ctx.args}
        )"""

            new_code = """        # Enhanced debug command
        # Return a more detailed response with useful debugging info
        room_id = None
        room_name = None
        if ctx.data and 'db' in ctx.data and ctx.character:
            db = ctx.data['db']
            from app.commands.movement_commands import get_character_location
            try:
                location = await get_character_location(db, ctx.character.id)
                if location and location.room_id:
                    room_id = location.room_id
                    from app.models import Room
                    room = db.query(Room).filter(Room.id == room_id).first()
                    if room:
                        room_name = room.name
            except Exception as e:
                logger.error(f"Error getting location: {str(e)}")

        return CommandResponse(
            success=True,
            message=f"Debug command executed successfully at {datetime.now().strftime('%H:%M:%S')}! The command system is working.\\n" +
                    f"Character: {ctx.character.name if ctx.character else 'None'}\\n" +
                    f"Location: {room_name or 'Unknown'} (ID: {room_id or 'Unknown'})\\n" +
                    f"Args: {ctx.args}\\n" +
                    f"WebSocket is operational.",
            data={
                "args": ctx.args,
                "character_id": ctx.character.id if ctx.character else None,
                "character_name": ctx.character.name if ctx.character else None,
                "room_id": room_id,
                "room_name": room_name,
                "timestamp": datetime.now().isoformat()
            }
        )"""

            # Update the content
            updated_content = content.replace(original_code, new_code)

            # Add datetime import if needed
            if "from datetime import datetime" not in updated_content:
                updated_content = (
                    "import logging\nfrom datetime import datetime\nfrom typing import List, Optional\n"
                    + updated_content[updated_content.find("from app") :]
                )

            # Write the updated content
            with open(debug_file, "w") as f:
                f.write(updated_content)

            logger.info("Updated debug command to provide more useful information")
            return True
        else:
            logger.error("Could not find debug command execute method")
            return False

    except Exception as e:
        logger.error(f"Error enhancing debug command: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


def fix_javascript_websocket():
    """
    Improve client-side WebSocket handling to better display command responses
    """
    try:
        # Find the game.js file
        game_js_file = os.path.join("static", "js", "game.js")

        # Check if file exists
        if not os.path.exists(game_js_file):
            logger.error(f"game.js file not found: {game_js_file}")
            return False

        # Read the current file
        with open(game_js_file, "r") as f:
            content = f.read()

        # Check if this fix is needed
        if "// Fixed WebSocket message handling" in content:
            logger.info("JavaScript WebSocket handling already fixed")
            return True

        # Find the onmessage handler
        if "wsConnection.onmessage = function(event)" in content:
            # Log what we found
            logger.info("Found WebSocket onmessage handler in game.js")

            # Find the section that parses and displays messages
            original_code = """            // Listen for messages
            wsConnection.onmessage = function(event) {
                const data = JSON.parse(event.data);

                if (data.message) {
                    if (!data.success) {
                        // Handle error messages
                        displayMessage(data.message, "error");

                        // If token is invalid, redirect to login
                        if (data.message.includes("Invalid or expired token")) {
                            displayMessage("Session expired. Please log in again.", "error");
                            setTimeout(() => {
                                localStorage.removeItem('token');
                                window.location.href = 'login.html';
                            }, 2000);
                        }
                    } else {
                        // Regular success messages
                        displayMessage(data.message, "normal");
                    }
                }

                // Update character info if provided
                if (data.data && data.data.character) {
                    updateCharacterInfo(data.data.character);
                }

                // Update inventory if provided
                if (data.data && data.data.inventory) {
                    updateInventory(data.data.inventory);
                }

                // Update journal if provided
                if (data.data && data.data.journal) {
                    addJournalEntry(data.data.journal);
                }
            };"""

            new_code = """            // Listen for messages
            // Fixed WebSocket message handling
            wsConnection.onmessage = function(event) {
                try {
                    console.log("WebSocket message received:", event.data);

                    const data = JSON.parse(event.data);

                    // Handle command responses with improved error handling
                    if (data.message) {
                        if (!data.success) {
                            // Handle error messages
                            displayMessage(data.message, "error");

                            // If token is invalid, redirect to login
                            if (data.message && data.message.includes && data.message.includes("Invalid or expired token")) {
                                displayMessage("Session expired. Please log in again.", "error");
                                setTimeout(() => {
                                    localStorage.removeItem('token');
                                    window.location.href = 'login.html';
                                }, 2000);
                            }
                        } else {
                            // Regular success messages
                            displayMessage(data.message, "normal");
                        }
                    } else {
                        // Handle messages without a message property
                        console.warn("WebSocket message missing 'message' property:", data);
                    }

                    // Update character info if provided
                    if (data.data && data.data.character) {
                        updateCharacterInfo(data.data.character);
                    }

                    // Update inventory if provided
                    if (data.data && data.data.inventory) {
                        updateInventory(data.data.inventory);
                    }

                    // Update journal if provided
                    if (data.data && data.data.journal) {
                        addJournalEntry(data.data.journal);
                    }

                    // Log command information if available
                    if (data.command) {
                        console.log("Command processed:", data.command);
                    }
                } catch (e) {
                    console.error("Error processing WebSocket message:", e);
                    displayMessage("Error processing server response. Check console for details.", "error");
                }
            };"""

            # Update the content
            updated_content = content.replace(original_code, new_code)

            # Write the updated content
            with open(game_js_file, "w") as f:
                f.write(updated_content)

            logger.info("Updated JavaScript WebSocket message handling")
            return True
        else:
            logger.error("Could not find WebSocket onmessage handler in game.js")
            return False

    except Exception as e:
        logger.error(f"Error fixing JavaScript WebSocket handling: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("Starting WebSocket and command response fixes...")

    print("Step 1: Fixing WebSocket command response handling...")
    ws_result = fix_websocket_command_response()
    print(
        f"WebSocket command response fix result: {'Success' if ws_result else 'Failed'}"
    )

    print("Step 2: Enhancing debug command...")
    debug_result = enhance_debug_command()
    print(
        f"Debug command enhancement result: {'Success' if debug_result else 'Failed'}"
    )

    print("Step 3: Fixing JavaScript WebSocket handling...")
    js_result = fix_javascript_websocket()
    print(f"JavaScript WebSocket fix result: {'Success' if js_result else 'Failed'}")

    if ws_result and debug_result and js_result:
        print("All fixes completed successfully!")
    else:
        print("Some fixes failed, please check the logs for details")

    print("Please restart the server to apply changes")
