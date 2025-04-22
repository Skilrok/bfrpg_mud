import logging
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = "./bfrpg.db"


def create_exits():
    """Create exits between rooms"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # First check if exits table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='exits'"
        )
        if not cursor.fetchone():
            # Create exits table
            logger.info("Creating exits table")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS exits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    direction TEXT NOT NULL,
                    name TEXT,
                    description TEXT,
                    source_room_id INTEGER NOT NULL,
                    destination_room_id INTEGER NOT NULL,
                    is_hidden BOOLEAN DEFAULT 0,
                    is_locked BOOLEAN DEFAULT 0,
                    properties TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

        # Check how many exits exist
        cursor.execute("SELECT COUNT(*) FROM exits")
        exit_count = cursor.fetchone()[0]
        logger.info(f"Current exit count: {exit_count}")

        if exit_count > 0:
            # Delete existing exits to avoid duplicates
            logger.info("Deleting existing exits")
            cursor.execute("DELETE FROM exits")

        # Insert exits from Village Square (Room 1) to other rooms
        exits_data = [
            # From Village Square (Room 1) to other rooms
            (1, "north", "Tavern Entrance", "The door to the village tavern.", 2, 0, 0),
            (
                1,
                "east",
                "Market Street",
                "A path leading to the village market.",
                3,
                0,
                0,
            ),
            (
                1,
                "south",
                "Smithy Road",
                "A path leading to the village blacksmith.",
                4,
                0,
                0,
            ),
            (
                1,
                "west",
                "Temple Path",
                "A serene path leading to the village temple.",
                5,
                0,
                0,
            ),
            # Return paths back to Village Square (Room 1)
            (
                2,
                "south",
                "Exit to Village Square",
                "The door leading back to the village square.",
                1,
                0,
                0,
            ),
            (
                3,
                "west",
                "Back to Village Square",
                "The path leading back to the village square.",
                1,
                0,
                0,
            ),
            (
                4,
                "north",
                "Back to Village Square",
                "The path leading back to the village square.",
                1,
                0,
                0,
            ),
            (
                5,
                "east",
                "Back to Village Square",
                "The path leading back to the village square.",
                1,
                0,
                0,
            ),
        ]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insert exits
        for exit_data in exits_data:
            source_id, direction, name, description, dest_id, is_hidden, is_locked = (
                exit_data
            )
            properties = "{}"

            cursor.execute(
                """
                INSERT INTO exits (
                    source_room_id, direction, name, description,
                    destination_room_id, is_hidden, is_locked, properties,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    source_id,
                    direction,
                    name,
                    description,
                    dest_id,
                    is_hidden,
                    is_locked,
                    properties,
                    now,
                    now,
                ),
            )

        # Commit changes
        conn.commit()

        # Check exit count after insert
        cursor.execute("SELECT COUNT(*) FROM exits")
        new_exit_count = cursor.fetchone()[0]
        logger.info(f"New exit count: {new_exit_count}")

        # List exits
        cursor.execute(
            """
            SELECT source_room_id, direction, destination_room_id
            FROM exits
            ORDER BY source_room_id, direction
        """
        )
        exits = cursor.fetchall()

        for exit_row in exits:
            source_id, direction, dest_id = exit_row
            logger.info(f"Exit from room {source_id} {direction} to room {dest_id}")

        return True
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {str(e)}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Error creating exits: {str(e)}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def create_debug_function():
    """Create a debug function in the look_commands.py file"""
    try:
        with open("app/commands/look_commands.py", "r") as f:
            content = f.read()

        # Check if debug function already exists
        if "# DEBUG FUNCTION FOR LOOK COMMAND" in content:
            logger.info("Debug function already exists, skipping")
            return True

        # Find the end of the LookCommand class
        class_end_pos = content.find("# Register command")

        if class_end_pos == -1:
            logger.error("Could not find end of LookCommand class")
            return False

        # Add debug function
        debug_function = """
    # DEBUG FUNCTION FOR LOOK COMMAND
    async def debug_look(self, ctx: CommandContext) -> CommandResponse:
        \"\"\"Debug version of look command\"\"\"
        logger.info(f"DEBUG LOOK COMMAND EXECUTED")
        try:
            # Get DB session
            db = ctx.data.get("db")
            if not db:
                return CommandResponse(
                    success=False, message="Error: Database unavailable", errors=["No database"]
                )

            # Get character ID
            character_id = None
            if ctx.character:
                character_id = ctx.character.id
            else:
                character_id = ctx.data.get("character_id")

            if not character_id:
                return CommandResponse(
                    success=False,
                    message="You need an active character to look around.",
                    errors=["No active character"],
                )

            logger.info(f"Looking at room for character {character_id}")

            # Get character's current location using direct SQL
            location_data = db.execute(
                \"\"\"SELECT room_id FROM character_locations WHERE character_id = :char_id\"\"\",
                {"char_id": character_id}
            ).fetchone()

            if not location_data:
                logger.error(f"No location found for character {character_id}")
                return CommandResponse(
                    success=False,
                    message="You aren't anywhere in the game world yet.",
                    errors=["No location found"],
                )

            room_id = location_data[0]
            logger.info(f"Character {character_id} is in room {room_id}")

            # Get room data using direct SQL
            room_data = db.execute(
                \"\"\"SELECT id, name, description FROM rooms WHERE id = :room_id\"\"\",
                {"room_id": room_id}
            ).fetchone()

            if not room_data:
                logger.error(f"Room {room_id} not found")
                return CommandResponse(
                    success=False,
                    message="The room you're in seems to have vanished!",
                    errors=["Room not found"],
                )

            room_name = room_data[1]
            room_description = room_data[2]
            logger.info(f"Found room: {room_name}")

            # Get exits from this room
            exits_data = db.execute(
                \"\"\"SELECT direction, destination_room_id, name
                FROM exits
                WHERE source_room_id = :room_id\"\"\",
                {"room_id": room_id}
            ).fetchall()

            exits_description = ""
            if exits_data:
                exits_description = "\\n\\nExits:"
                for exit_data in exits_data:
                    direction, dest_id, exit_name = exit_data
                    exits_description += f"\\n- {direction}: {exit_name if exit_name else 'an exit'}"
                logger.info(f"Found {len(exits_data)} exits")
            else:
                exits_description = "\\n\\nThere are no obvious exits."
                logger.warning(f"No exits found for room {room_id}")

            # Prepare response
            response = f"{room_name}\\n\\n{room_description}{exits_description}"

            logger.info(f"Returning look response")
            return CommandResponse(
                success=True,
                message=response,
                data={
                    "room_id": room_id,
                    "room_name": room_name,
                    "exits": [{"direction": exit[0], "destination": exit[1], "name": exit[2]} for exit in exits_data],
                },
            )
        except Exception as e:
            import traceback
            logger.error(f"Error in debug_look: {str(e)}")
            logger.error(traceback.format_exc())
            return CommandResponse(
                success=False,
                message=f"Error looking around: {str(e)}",
                errors=[str(e)],
            )

"""

        # Insert debug function
        modified_content = (
            content[:class_end_pos] + debug_function + content[class_end_pos:]
        )

        # Update the alias list to add the debug look command
        modified_content = modified_content.replace(
            'aliases = ["l"]', 'aliases = ["l", "debuglook"]'
        )

        # Replace the execute method to use the debug method
        old_execute = """    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check if character exists
        if not ctx.character:
            # Try to get character ID from context data
            character_id = ctx.data.get("character_id")
            if not character_id:
                return CommandResponse(
                    success=False,
                    message="You need an active character to look around.",
                    errors=["No active character"],
                )"""

        new_execute = """    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Use debug look function instead
        return await self.debug_look(ctx)

        # Original implementation:
        # Check if character exists
        if not ctx.character:
            # Try to get character ID from context data
            character_id = ctx.data.get("character_id")
            if not character_id:
                return CommandResponse(
                    success=False,
                    message="You need an active character to look around.",
                    errors=["No active character"],
                )"""

        modified_content = modified_content.replace(old_execute, new_execute)

        # Write changes back to file
        with open("app/commands/look_commands.py", "w") as f:
            f.write(modified_content)

        logger.info("Added debug function to look_commands.py")
        return True
    except Exception as e:
        logger.error(f"Error creating debug function: {str(e)}")
        return False


def debug_command_handling():
    """Add debugging to command registry and handling"""
    try:
        # Add debug to registry.py
        with open("app/commands/registry.py", "r") as f:
            registry_content = f.read()

        # Check if debug is already added
        if "# DEBUG COMMAND REGISTRY" in registry_content:
            logger.info("Command registry debug already added, skipping")
        else:
            # Add debug to get_command method
            if "def get_command(self, command_name: str)" in registry_content:
                modified_registry = registry_content.replace(
                    "def get_command(self, command_name: str)",
                    """def get_command(self, command_name: str)
        # DEBUG COMMAND REGISTRY
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Looking for command: {command_name}")
        logger.info(f"Available commands: {list(self._commands.keys())}")""",
                )

                # Write changes
                with open("app/commands/registry.py", "w") as f:
                    f.write(modified_registry)

                logger.info("Added debug to command registry")
            else:
                logger.warning("Could not find get_command method in registry.py")

        # Add debug to WebSocketManager
        websocket_file = "app/websockets/__init__.py"
        with open(websocket_file, "r") as f:
            websocket_content = f.read()

        # Check if debug is already added
        if "# DEBUG WEBSOCKET MANAGER" in websocket_content:
            logger.info("WebSocket debug already added, skipping")
        else:
            # Add debug to handle_command_message
            if "async def handle_command_message" in websocket_content:
                modified_websocket = websocket_content.replace(
                    "async def handle_command_message(self, websocket: WebSocket, message: dict, session_data: dict):",
                    """async def handle_command_message(self, websocket: WebSocket, message: dict, session_data: dict):
        # DEBUG WEBSOCKET MANAGER
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Command message received: {message}")
        try:""",
                )

                # Add exception handling
                modified_websocket = modified_websocket.replace(
                    "await self.send_error(websocket, f\"Command '{command_name}' not found\")",
                    """await self.send_error(websocket, f"Command '{command_name}' not found")
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error in handle_command_message: {str(e)}")
            logger.error(traceback.format_exc())
            await self.send_error(websocket, f"Error: {str(e)}")""",
                )

                # Write changes
                with open(websocket_file, "w") as f:
                    f.write(modified_websocket)

                logger.info("Added debug to WebSocket manager")
            else:
                logger.warning(
                    "Could not find handle_command_message in WebSocket manager"
                )

        return True
    except Exception as e:
        logger.error(f"Error adding command handling debug: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Starting fix script...")

    # Create exits
    logger.info("Creating exits...")
    exits_result = create_exits()
    logger.info(f"Exit creation {'successful' if exits_result else 'failed'}")

    # Create debug function
    logger.info("Creating debug function...")
    debug_result = create_debug_function()
    logger.info(f"Debug function creation {'successful' if debug_result else 'failed'}")

    # Debug command handling
    logger.info("Adding command handling debug...")
    handler_result = debug_command_handling()
    logger.info(
        f"Command handling debug {'successful' if handler_result else 'failed'}"
    )

    logger.info("Fix script completed, please restart the server")
