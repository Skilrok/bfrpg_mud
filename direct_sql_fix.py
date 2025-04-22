import sqlite3
import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if db file exists
DB_PATH = "./bfrpg.db"

def check_and_fix_rooms():
    """Check if rooms exist and fix if needed"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if rooms table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rooms'")
        if not cursor.fetchone():
            logger.error("Rooms table doesn't exist, creating it")
            # Create rooms table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                room_type TEXT DEFAULT 'dungeon',
                area_id INTEGER,
                x INTEGER DEFAULT 0,
                y INTEGER DEFAULT 0,
                z INTEGER DEFAULT 0,
                is_dark BOOLEAN DEFAULT 0,
                exits TEXT DEFAULT '{}',
                properties TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

        # Check if areas table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='areas'")
        if not cursor.fetchone():
            logger.error("Areas table doesn't exist, creating it")
            # Create areas table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS areas (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                level_range TEXT,
                is_dungeon BOOLEAN DEFAULT 1,
                is_hidden BOOLEAN DEFAULT 0,
                properties TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

        # Check if exits table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exits'")
        if not cursor.fetchone():
            logger.error("Exits table doesn't exist, creating it")
            # Create exits table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS exits (
                id INTEGER PRIMARY KEY,
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
            """)

        # Check if character_locations table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='character_locations'")
        if not cursor.fetchone():
            logger.error("Character_locations table doesn't exist, creating it")
            # Create character_locations table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_locations (
                id INTEGER PRIMARY KEY,
                character_id INTEGER UNIQUE,
                room_id INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

        # Check if room 1 exists
        cursor.execute("SELECT id, name FROM rooms WHERE id = 1")
        room_1 = cursor.fetchone()
        if not room_1:
            logger.error("Room 1 doesn't exist, creating it")
            
            # Check if Starting Village area exists
            cursor.execute("SELECT id FROM areas WHERE name = 'Starting Village'")
            area = cursor.fetchone()
            if not area:
                logger.error("Starting Village area doesn't exist, creating it")
                # Create Starting Village area
                cursor.execute("""
                INSERT INTO areas (id, name, description, level_range, is_dungeon, is_hidden)
                VALUES (1, 'Starting Village', 'A small village where new adventurers begin their journey.', '1-3', 0, 0)
                """)
                area_id = 1
            else:
                area_id = area[0]
                
            # Create room 1
            cursor.execute("""
            INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark)
            VALUES (1, 'Village Square', 'The central square of the starting village. Paths lead in all directions.', 'town', ?, 0, 0, 0, 0)
            """, (area_id,))
            
            # Create surrounding rooms
            rooms_data = [
                (2, 'Village Tavern', 'A cozy tavern with a roaring fireplace. Adventurers gather here to share tales.', 'town', area_id, 0, 1, 0, 0),
                (3, 'Village Market', 'A bustling market with various stalls selling goods.', 'town', area_id, 1, 0, 0, 0),
                (4, 'Village Blacksmith', 'The sound of hammering fills the air as the blacksmith works at the forge.', 'town', area_id, 0, -1, 0, 0),
                (5, 'Village Temple', 'A peaceful temple dedicated to various deities.', 'town', area_id, -1, 0, 0, 0)
            ]
            
            for room_data in rooms_data:
                cursor.execute("""
                INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, room_data)
                
            # Create exits
            exits_data = [
                # From Village Square (Room 1) to other rooms
                (1, 'north', 'Tavern Entrance', 'The door to the village tavern.', 2, 0, 0),
                (1, 'east', 'Market Street', 'A path leading to the village market.', 3, 0, 0),
                (1, 'south', 'Smithy Road', 'A path leading to the village blacksmith.', 4, 0, 0),
                (1, 'west', 'Temple Path', 'A serene path leading to the village temple.', 5, 0, 0),
                
                # Return paths back to Village Square (Room 1)
                (2, 'south', 'Exit to Village Square', 'The door leading back to the village square.', 1, 0, 0),
                (3, 'west', 'Back to Village Square', 'The path leading back to the village square.', 1, 0, 0),
                (4, 'north', 'Back to Village Square', 'The path leading back to the village square.', 1, 0, 0),
                (5, 'east', 'Back to Village Square', 'The path leading back to the village square.', 1, 0, 0)
            ]
            
            for exit_data in exits_data:
                source_id, direction, name, description, dest_id, is_hidden, is_locked = exit_data
                cursor.execute("""
                INSERT INTO exits (source_room_id, direction, name, description, destination_room_id, is_hidden, is_locked)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (source_id, direction, name, description, dest_id, is_hidden, is_locked))
        else:
            logger.info(f"Room 1 exists: {room_1}")
            
            # Check if exits exist
            cursor.execute("SELECT COUNT(*) FROM exits")
            exit_count = cursor.fetchone()[0]
            if exit_count == 0:
                logger.error("No exits exist, creating them")
                
                # Create exits
                exits_data = [
                    # From Village Square (Room 1) to other rooms
                    (1, 'north', 'Tavern Entrance', 'The door to the village tavern.', 2, 0, 0),
                    (1, 'east', 'Market Street', 'A path leading to the village market.', 3, 0, 0),
                    (1, 'south', 'Smithy Road', 'A path leading to the village blacksmith.', 4, 0, 0),
                    (1, 'west', 'Temple Path', 'A serene path leading to the village temple.', 5, 0, 0),
                    
                    # Return paths back to Village Square (Room 1)
                    (2, 'south', 'Exit to Village Square', 'The door leading back to the village square.', 1, 0, 0),
                    (3, 'west', 'Back to Village Square', 'The path leading back to the village square.', 1, 0, 0),
                    (4, 'north', 'Back to Village Square', 'The path leading back to the village square.', 1, 0, 0),
                    (5, 'east', 'Back to Village Square', 'The path leading back to the village square.', 1, 0, 0)
                ]
                
                for exit_data in exits_data:
                    source_id, direction, name, description, dest_id, is_hidden, is_locked = exit_data
                    cursor.execute("""
                    INSERT INTO exits (source_room_id, direction, name, description, destination_room_id, is_hidden, is_locked)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (source_id, direction, name, description, dest_id, is_hidden, is_locked))
            else:
                logger.info(f"Exits exist: {exit_count}")
        
        # Get all rooms
        cursor.execute("SELECT id, name FROM rooms")
        rooms = cursor.fetchall()
        logger.info(f"All rooms: {rooms}")
        
        # Get all exits
        cursor.execute("SELECT source_room_id, direction, destination_room_id FROM exits")
        exits = cursor.fetchall()
        logger.info(f"All exits: {exits}")
        
        # Get character locations
        cursor.execute("SELECT character_id, room_id FROM character_locations")
        locations = cursor.fetchall()
        logger.info(f"Character locations: {locations}")
        
        # Fix character 1 location if needed
        cursor.execute("SELECT character_id FROM character_locations WHERE character_id = 1")
        char_1_loc = cursor.fetchone()
        if not char_1_loc:
            logger.error("Character 1 has no location, creating it")
            cursor.execute("""
            INSERT INTO character_locations (character_id, room_id)
            VALUES (1, 1)
            """)
        else:
            logger.info(f"Character 1 location exists")
            
            # Update to room 1 just to be sure
            cursor.execute("""
            UPDATE character_locations SET room_id = 1
            WHERE character_id = 1
            """)
        
        # Commit changes
        conn.commit()
        logger.info("Database check and fix completed")
        return True
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Error checking and fixing rooms: {e}")
        import traceback
        logger.error(traceback.format_exc())
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def modify_look_command():
    """Directly modify the look command with a simple implementation"""
    try:
        look_file = "app/commands/look_commands.py"
        
        # Check if file exists
        if not os.path.exists(look_file):
            logger.error(f"Look command file not found: {look_file}")
            return False
        
        # Read current content
        with open(look_file, "r") as f:
            content = f.read()
        
        # Create a simple debug implementation
        debug_method = """
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        \"\"\"Simple debug implementation of look command\"\"\"
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Debug look command executed")
        
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
        try:
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
            logger.info(f"Returning look response: {response[:100]}...")
            
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
            logger.error(f"Error in look command: {str(e)}")
            logger.error(traceback.format_exc())
            return CommandResponse(
                success=False,
                message=f"Error looking around: {str(e)}",
                errors=[str(e)],
            )
"""
        
        # Find the execute method
        start_marker = "async def execute(self, ctx: CommandContext) -> CommandResponse:"
        if start_marker in content:
            # Find the end of the execute method and replace the whole method
            execute_start = content.find(start_marker)
            
            # Find the next method or the end of the class
            # Either "    async def" or "# Register command"
            next_method_marker = "    async def"
            register_marker = "# Register command"
            
            next_method_pos = content.find(next_method_marker, execute_start + len(start_marker))
            register_pos = content.find(register_marker, execute_start + len(start_marker))
            
            # Determine where the execute method ends
            if next_method_pos != -1 and (register_pos == -1 or next_method_pos < register_pos):
                execute_end = next_method_pos
            elif register_pos != -1:
                execute_end = register_pos
            else:
                # Use a fixed amount of lines as a fallback
                execute_end = execute_start + 1000
            
            # Replace the execute method
            new_content = content[:execute_start] + debug_method + content[execute_end:]
            
            # Write back to file
            with open(look_file, "w") as f:
                f.write(new_content)
                
            logger.info("Look command modified with debug implementation")
            return True
        else:
            logger.error("Could not find execute method in look command")
            return False
    except Exception as e:
        logger.error(f"Error modifying look command: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting direct SQL fix")
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        logger.error(f"Database not found at {DB_PATH}")
        db_dir = os.path.dirname(DB_PATH)
        if not os.path.exists(db_dir) and db_dir:
            os.makedirs(db_dir)
        with open(DB_PATH, "w") as f:
            pass  # Create empty file
        logger.info(f"Created empty database file at {DB_PATH}")
    
    # Check and fix rooms
    logger.info("Checking and fixing rooms...")
    room_result = check_and_fix_rooms()
    logger.info(f"Room check and fix {'successful' if room_result else 'failed'}")
    
    # Modify look command
    logger.info("Modifying look command...")
    look_result = modify_look_command()
    logger.info(f"Look command modification {'successful' if look_result else 'failed'}")
    
    logger.info("Direct SQL fix completed") 