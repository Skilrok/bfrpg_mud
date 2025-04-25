# REMOVED: import json
import logging
import os
# REMOVED: from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_websocket_handler():
    """
    Add debug information to the WebSocket handler to diagnose the look command issue
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

        # Add debugging for command handling
        if "async def handle_command_message" in content:
            logger.info("Found command handler in WebSocket manager")

            # Check if debug is already added
            if "# ADDED DEBUG INFO" in content:
                logger.info("Debug info already added, skipping")
                return True

            # Add debug info
            debug_content = content.replace(
                " +
            "async def handle_command_message(self, websocket:"WebSocket, message: dict, session_data: dict):",
                """async def handle_command_message(self, websocket: WebSocket, message: dict, session_data: dict):
        # ADDED DEBUG INFO
        logger.info(f"Processing command: {message}")
        try:""",
            )

            # Add additional debug at execution point
            debug_content = debug_content.replace(
                "await command_handler.execute(context)",
                """# ADDED EXECUTION DEBUG
            logger.info(f"Executing command: {command_name}")
            response = await command_handler.execute(context)
            logger.info(f"Command response: {response.message[:100]}...")
            return response""",
            )

            # Add exception handling
            if "except Exception as e:" not in debug_content:
                debug_content = debug_content.replace(
                    "return await command_handler.execute(context)",
                    """try:
                return await command_handler.execute(context)
            except Exception as e:
                logger.error(f"Error executing command: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return CommandResponse(
                    success=False,
                    message=f"Error: {str(e)}",
                    errors=[str(e)]
                )""",
                )

            # Write updated content
            with open(websocket_file, "w") as f:
                f.write(debug_content)

            logger.info("Added debug info to WebSocket handler")
            return True
        else:
            logger.error("Could not find command handler in WebSocket manager")
            return False
    except Exception as e:
        logger.error(f"Error fixing WebSocket handler: {str(e)}")
        return False


def fix_look_command():
    """
    Add debug information to the look command
    """
    try:
        # Find the look command implementation
        look_file = os.path.join("app", "commands", "look_commands.py")

        # Check if file exists
        if not os.path.exists(look_file):
            logger.error(f"Look command file not found: {look_file}")
            return False

        # Read the current file
        with open(look_file, "r") as f:
            content = f.read()

        # Add debugging for look command
        if "async def _look_at_room" in content:
            logger.info("Found _look_at_room method in look command")

            # Check if debug is already added
            if "# ADDED DEBUG INFO FOR LOOK" in content:
                logger.info("Debug info already added to look command, skipping")
                return True

            # Add debug info
            debug_content = content.replace(
                "async def _look_at_room(",
                """async def _look_at_room(
        # ADDED DEBUG INFO FOR LOOK""",
            )

            # Add logging at start of method
            debug_content = debug_content.replace(
                "try:",
                """try:
            # Add debug logging
            logger.info(f"Looking at room for character {character_id}")""",
            )

            # Add debug after getting location data
            debug_content = debug_content.replace(
                "room_id = location_data[0]",
                """room_id = location_data[0]
            logger.info(f"Found room_id: {room_id}")""",
            )

            # Write updated content
            with open(look_file, "w") as f:
                f.write(debug_content)

            logger.info("Added debug info to look command")
            return True
        else:
            logger.error("Could not find _look_at_room method in look command")
            return False
    except Exception as e:
        logger.error(f"Error fixing look command: {str(e)}")
        return False


def create_debug_command():
    """
    Create a simple debug command to test the command system
    """
    try:
        # Create debug command file
        debug_file = os.path.join("app", "commands", "debug_command.py")

        # Create file content
        content = """import logging
from typing import List, Optional

from app.commands.base import CommandContext, CommandHandler, CommandResponse
from app.commands.registry import command_registry

logger = logging.getLogger(__name__)

class DebugCommand(CommandHandler):
    \"\"\"A simple debug command for testing\"\"\"

    name = "debug"
    aliases = ["dbg", "test"]
    help_text = "A debug command to test the command system"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        logger.info(f"Debug command executed with args: {ctx.args}")

        # Log context data
        logger.info(f"Context data: {ctx.data}")

        # Check if character exists
        if ctx.character:
            logger.info(f"Character: {ctx.character.name} (ID: {ctx.character.id})")
        else:
            logger.warning("No character in context")

        # Return a simple response
        return CommandResponse(
            success=True,
            message=" +
            "Debug command executed successfully! The command system is"working.",
            data={"args": ctx.args}
        )

# Register the command
command_registry.register(DebugCommand)
logger.info("Debug command registered")
"""

        # Write file
        with open(debug_file, "w") as f:
            f.write(content)

        logger.info("Created debug command")

        # Update __init__.py to import the debug command
        init_file = os.path.join("app", "commands", "__init__.py")

        if os.path.exists(init_file):
            with open(init_file, "r") as f:
                init_content = f.read()

            # Check if import is already added
            if "import app.commands.debug_command" not in init_content:
                # Add import at the end
                if init_content.strip():
                    init_content += " +
            "\n\n# Import debug command\nimport"app.commands.debug_command\n"
                else:
                    init_content = (
                        "# Import debug command\nimport app.commands.debug_command\n"
                    )

                # Write updated content
                with open(init_file, "w") as f:
                    f.write(init_content)

                logger.info("Updated __init__.py to import debug command")
        else:
            logger.warning(f"Init file not found: {init_file}")

        return True
    except Exception as e:
        logger.error(f"Error creating debug command: {str(e)}")
        return False


def fix_js_websocket():
    """
    Fix the JavaScript WebSocket handling in game.html
    """
    try:
        # Find the game.html file
        game_file = os.path.join("static", "game.html")

        # Check if file exists
        if not os.path.exists(game_file):
            logger.error(f"Game file not found: {game_file}")
            return False

        # Read the current file
        with open(game_file, "r") as f:
            content = f.read()

        # Look for WebSocket handling
        if "function connectWebSocket()" in content:
            logger.info("Found WebSocket connection function in game.html")

            # Check if debug is already added
            if "// ADDED DEBUG FOR WEBSOCKET" in content:
                logger.info("Debug info already added to WebSocket JS, skipping")
                return True

            # Add debug to WebSocket message handling
            debug_content = content.replace(
                "socket.onmessage = function(event) {",
                """socket.onmessage = function(event) {
            // ADDED DEBUG FOR WEBSOCKET
            console.log("WebSocket message received:", event.data);""",
            )

            # Add debug for sending commands
            if "function sendCommand()" in debug_content:
                debug_content = debug_content.replace(
                    "function sendCommand() {",
                    """function sendCommand() {
            // ADDED DEBUG FOR COMMAND SENDING
            console.log("Sending command:", commandInput.value);""",
                )

                # Add debug for WebSocket connection
                debug_content = debug_content.replace(
                    "socket.onopen = function(e) {",
                    """socket.onopen = function(e) {
            // ADDED DEBUG FOR WEBSOCKET CONNECTION
            console.log("WebSocket connection established");""",
                )

                # Add WebSocket error handling
                debug_content = debug_content.replace(
                    "socket.onclose = function(event) {",
                    """socket.onerror = function(error) {
            console.error("WebSocket error:", error);
            appendToTerminal('<span class="error">Connection error</span>');
        };

        socket.onclose = function(event) {
            // ADDED DEBUG FOR WEBSOCKET CLOSE
            console.log("WebSocket connection closed:", event);""",
                )

                # Write updated content
                with open(game_file, "w") as f:
                    f.write(debug_content)

                logger.info("Added debug info to WebSocket JS")
                return True
            else:
                logger.error("Could not find sendCommand function in game.html")
                return False
        else:
            logger.error("Could not find WebSocket connection function in game.html")
            return False
    except Exception as e:
        logger.error(f"Error fixing JS WebSocket: {str(e)}")
        return False


def enhance_client_debugging():
    """
    Add enhanced client-side debugging for the look command in game.js
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

        # Check if this enhancement is already added
        if "// Enhanced debug for look command" in content:
            logger.info("Client-side look command debugging already enhanced")
            return True

        # Find the onmessage handler section with data.command logging
        target_section = 'if (data.command) {\n                        console.log("Command processed:", data.command);\n                    }'

        enhanced_section = """if (data.command) {
                        console.log("Command processed:", data.command);

                        // Enhanced debug for look command
                        if (data.command.name === "look" || data.command.name === "l") {
                            console.log("LOOK COMMAND RESPONSE:", {
                                success: data.success,
                                message: data.message,
                                data: data.data || {}
                            });

                            // Special handling for look command responses
                            if (data.success && data.data) {
                                // Log room details if available
                                if (data.data.room_id) {
                                    console.log("Room details:", {
                                        id: data.data.room_id,
                                        name: data.data.room_name,
                                        exits: data.data.exits || [],
                                        items: data.data.items || [],
                                        npcs: data.data.npcs || [],
                                        characters: data.data.characters || []
                                    });
                                }
                            }
                        }
                    }"""

        # Update the content
        updated_content = content.replace(target_section, enhanced_section)

        # Write the updated content
        with open(game_js_file, "w") as f:
            f.write(updated_content)

        logger.info("Enhanced client-side debugging for look command")
        return True
    except Exception as e:
        logger.error(f"Error enhancing client debugging: {str(e)}")
        return False


def main():
    """Run all fixes"""
    logger.info("Running WebSocket and command fixes...")

    fixes_applied = 0

    if fix_websocket_handler():
        fixes_applied += 1

    if fix_look_command():
        fixes_applied += 1

    if create_debug_command():
        fixes_applied += 1

    if enhance_client_debugging():
        fixes_applied += 1

    logger.info(f"Applied {fixes_applied} fixes successfully")


if __name__ == "__main__":
    main()
