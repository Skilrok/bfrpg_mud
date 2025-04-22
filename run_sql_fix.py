import logging
import os
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_sql_script(db_path, sql_file):
    """
    Execute SQL commands from a file on the specified database
    """
    try:
        logger.info(f"Opening database at {db_path}")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        logger.info(f"Reading SQL script from {sql_file}")
        with open(sql_file, "r") as f:
            sql_script = f.read()

        # Split script by semicolons to execute each statement
        statements = sql_script.split(";")

        for statement in statements:
            if statement.strip():
                try:
                    logger.info(f"Executing statement: {statement[:50]}...")
                    cursor.execute(statement.strip())
                except sqlite3.Error as e:
                    logger.error(f"Error executing statement: {str(e)}")
                    logger.error(f"Statement was: {statement}")

        # Commit changes
        connection.commit()
        logger.info("SQL script executed successfully")

        # Check if rooms were created
        cursor.execute("SELECT COUNT(*) FROM rooms")
        room_count = cursor.fetchone()[0]
        logger.info(f"Room count after execution: {room_count}")

        return True
    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return False
    finally:
        if connection:
            connection.close()


def fix_websocket_debug():
    """
    Add debug information to websocket handler
    """
    try:
        websocket_file = os.path.join("app", "websockets", "__init__.py")

        # Check if the file exists
        if not os.path.exists(websocket_file):
            logger.error(f"WebSocket file not found: {websocket_file}")
            return False

        # Read the current file
        with open(websocket_file, "r") as f:
            content = f.read()

        # Look for command message handler
        if "async def handle_command_message" in content:
            logger.info("Found command message handler")

            # Check if debug is already added
            if "# DEBUG - Print command info" in content:
                logger.info("Debug already added, skipping")
                return True

            # Add debug print
            modified_content = content.replace(
                "async def handle_command_message(self, websocket: WebSocket, message: dict, session_data: dict):",
                """async def handle_command_message(self, websocket: WebSocket, message: dict, session_data: dict):
        # DEBUG - Print command info
        try:
            logger.info(f"Command message: {message}")""",
            )

            # Add error handling for command execution
            modified_content = modified_content.replace(
                "return await command_handler.execute(context)",
                """try:
                result = await command_handler.execute(context)
                logger.info(f"Command result: {result.success}, message: {result.message[:100] if result.message else 'None'}")
                if not result.success:
                    logger.error(f"Command errors: {result.errors}")
                return result
            except Exception as e:
                logger.error(f"Error executing command: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                return CommandResponse(
                    success=False,
                    message=f"Error executing command: {str(e)}",
                    errors=[str(e)]
                )""",
            )

            # Add catch block for command handling
            modified_content = modified_content.replace(
                "await self.send_error(websocket, f\"Command '{command_name}' not found\")",
                """await self.send_error(websocket, f\"Command '{command_name}' not found\")
        except Exception as e:
            logger.error(f"Error in command handler: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            await self.send_error(websocket, f"Error handling command: {str(e)}")""",
            )

            # Write back the modified content
            with open(websocket_file, "w") as f:
                f.write(modified_content)

            logger.info("Added debug info to websocket handler")
            return True
        else:
            logger.error("Could not find command message handler in websocket file")
            return False
    except Exception as e:
        logger.error(f"Error fixing websocket debug: {str(e)}")
        return False


def fix_look_command():
    """
    Fix the look command in look_commands.py
    """
    try:
        look_file = os.path.join("app", "commands", "look_commands.py")

        # Check if the file exists
        if not os.path.exists(look_file):
            logger.error(f"Look command file not found: {look_file}")
            return False

        # Read the current file
        with open(look_file, "r") as f:
            content = f.read()

        # Add debug logging
        if "async def _look_at_room" in content:
            logger.info("Found _look_at_room method in look command")

            # Check if debug is already added
            if "# DEBUG - Log look command execution" in content:
                logger.info("Debug already added to look command, skipping")
                return True

            # Add debug logging
            modified_content = content.replace(
                "async def _look_at_room(self, db: Session, character_id: int) -> CommandResponse:",
                """async def _look_at_room(self, db: Session, character_id: int) -> CommandResponse:
        # DEBUG - Log look command execution
        logger.info(f"Looking at room for character {character_id}")""",
            )

            # Add error logging
            modified_content = modified_content.replace(
                "except Exception as e:",
                """except Exception as e:
            import traceback
            logger.error(f"Look command error: {str(e)}")
            logger.error(traceback.format_exc())""",
            )

            # Write back the modified content
            with open(look_file, "w") as f:
                f.write(modified_content)

            logger.info("Added debug info to look command")
            return True
        else:
            logger.error("Could not find _look_at_room method in look command")
            return False
    except Exception as e:
        logger.error(f"Error fixing look command: {str(e)}")
        return False


def modify_game_html():
    """
    Modify the game.html file to add WebSocket debugging
    """
    try:
        game_file = os.path.join("static", "game.html")

        # Check if the file exists
        if not os.path.exists(game_file):
            logger.error(f"Game HTML file not found: {game_file}")
            return False

        # Read the current file
        with open(game_file, "r") as f:
            content = f.read()

        # Check if debug is already added
        if "// DEBUG - WebSocket message handling" in content:
            logger.info("Debug already added to game.html, skipping")
            return True

        # Add debug for WebSocket message handling
        modified_content = content.replace(
            "socket.onmessage = function(event) {",
            """socket.onmessage = function(event) {
            // DEBUG - WebSocket message handling
            console.log("WebSocket message received:", event.data);
            try {
                const data = JSON.parse(event.data);
                console.log("Parsed message:", data);
            } catch (e) {
                console.error("Error parsing message:", e);
            }""",
        )

        # Write back the modified content
        with open(game_file, "w") as f:
            f.write(modified_content)

        logger.info("Added debug info to game.html")
        return True
    except Exception as e:
        logger.error(f"Error modifying game.html: {str(e)}")
        return False


if __name__ == "__main__":
    # Detect database path
    db_path = os.path.join(".", "bfrpg.db")
    if not os.path.exists(db_path):
        logger.warning(f"Database not found at {db_path}")
        alt_path = os.path.join(".", "app", "bfrpg.db")
        if os.path.exists(alt_path):
            db_path = alt_path
            logger.info(f"Using alternative database path: {db_path}")
        else:
            logger.warning(f"Alternative database not found at {alt_path}")
            logger.info("Creating new database at ./bfrpg.db")
            db_path = os.path.join(".", "bfrpg.db")

    # Run SQL script
    logger.info("Running SQL script to create rooms...")
    sql_result = run_sql_script(db_path, "create_rooms.sql")
    logger.info(f"SQL script execution {'successful' if sql_result else 'failed'}")

    # Add WebSocket debugging
    logger.info("Adding WebSocket debugging...")
    ws_result = fix_websocket_debug()
    logger.info(
        f"WebSocket debugging {'added successfully' if ws_result else 'failed'}"
    )

    # Fix look command
    logger.info("Fixing look command...")
    look_result = fix_look_command()
    logger.info(f"Look command fix {'successful' if look_result else 'failed'}")

    # Modify game.html
    logger.info("Modifying game.html...")
    html_result = modify_game_html()
    logger.info(f"Game HTML modification {'successful' if html_result else 'failed'}")

    logger.info("Fix script completed. Please restart the server to apply changes.")
