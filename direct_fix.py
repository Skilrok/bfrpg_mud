import os
import sys
import logging
from sqlalchemy import text
from app.database import get_db
from app.commands import registry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database():
    """Check if rooms and character locations exist"""
    db = next(get_db())
    try:
        # Check if tables exist first
        tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        table_names = [table[0] for table in tables]
        logger.info(f"Tables found in database: {table_names}")
        
        # Check rooms
        try:
            rooms = db.execute(text("SELECT id, name FROM rooms")).fetchall()
            if rooms:
                logger.info(f"Rooms found in database: {[room[0] for room in rooms]}")
                for room in rooms:
                    logger.info(f"  Room {room[0]}: {room[1]}")
            else:
                logger.warning("No rooms found in database")
        except Exception as e:
            logger.error(f"Error querying rooms: {str(e)}")
        
        # Check character locations
        try:
            locations = db.execute(text("SELECT character_id, room_id FROM character_locations")).fetchall()
            if locations:
                logger.info(f"Character locations found: {len(locations)}")
                for loc in locations:
                    logger.info(f"  Character {loc[0]} is in room {loc[1]}")
            else:
                logger.warning("No character locations found")
        except Exception as e:
            logger.error(f"Error querying character locations: {str(e)}")
            
        # Check exits
        try:
            exits = db.execute(text("SELECT source_room_id, direction, destination_room_id FROM exits")).fetchall()
            if exits:
                logger.info(f"Exits found: {len(exits)}")
                for exit in exits:
                    logger.info(f"  Exit from room {exit[0]} {exit[1]} to room {exit[2]}")
            else:
                logger.warning("No exits found")
        except Exception as e:
            logger.error(f"Error querying exits: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"Database check error: {str(e)}")
        return False
    finally:
        db.close()

def fix_character_location(character_id=1):
    """Fix a specific character's location"""
    db = next(get_db())
    try:
        # Check if character exists
        character = db.execute(
            text("SELECT id, name FROM characters WHERE id = :char_id"),
            {"char_id": character_id}
        ).fetchone()
        
        if not character:
            logger.error(f"Character {character_id} not found")
            return False
        
        logger.info(f"Found character {character[0]}: {character[1]}")
        
        # Check if character already has a location
        location = db.execute(
            text("SELECT id, room_id FROM character_locations WHERE character_id = :char_id"),
            {"char_id": character_id}
        ).fetchone()
        
        if location:
            logger.info(f"Character {character_id} already has location: room {location[1]}")
            # Update to room 1
            db.execute(
                text("UPDATE character_locations SET room_id = 1 WHERE character_id = :char_id"),
                {"char_id": character_id}
            )
            db.commit()
            logger.info(f"Updated character {character_id} location to room 1")
        else:
            logger.info(f"Character {character_id} has no location, creating one")
            # Create location record
            db.execute(
                text("""
                INSERT INTO character_locations (character_id, room_id)
                VALUES (:char_id, 1)
                """),
                {"char_id": character_id}
            )
            db.commit()
            logger.info(f"Created location for character {character_id} in room 1")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing character location: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        db.rollback()
        return False
    finally:
        db.close()

def debug_look_command():
    """Debug the look command execution"""
    try:
        # Check if we can find look command in registry
        from app.commands.registry import command_registry
        
        # Get all command names 
        command_names = []
        for handler_class in registry.command_registry._commands.values():
            command_names.append(handler_class.name)
        
        logger.info(f"Registered commands: {command_names}")
        
        # Get the look command
        look_command = None
        for handler_class in registry.command_registry._commands.values():
            if handler_class.name == "look":
                look_command = handler_class()
                break
        
        if look_command:
            logger.info(f"Found look command: {look_command.name} with aliases {look_command.aliases}")
            
            # Modify the _look_at_room method to add debugging
            if hasattr(look_command, "_look_at_room"):
                original_method = look_command._look_at_room
                
                async def debug_look_at_room(self, db, character_id):
                    logger.info(f"DEBUG: Looking at room for character {character_id}")
                    try:
                        result = await original_method(db, character_id)
                        logger.info(f"DEBUG: Look result success: {result.success}")
                        logger.info(f"DEBUG: Look result message: {result.message[:100]}...")
                        return result
                    except Exception as e:
                        logger.error(f"DEBUG: Look error: {str(e)}")
                        import traceback
                        logger.error(traceback.format_exc())
                        from app.commands.base import CommandResponse
                        return CommandResponse(
                            success=False,
                            message=f"Error looking: {str(e)}",
                            errors=[str(e)]
                        )
                
                # Replace the method
                from types import MethodType
                look_command._look_at_room = MethodType(debug_look_at_room, look_command)
                logger.info("Added debug wrapper to _look_at_room method")
            else:
                logger.error("Look command doesn't have _look_at_room method")
        else:
            logger.error("Look command not found in registry")
        
        return True
    except Exception as e:
        logger.error(f"Error debugging look command: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("Starting direct fix...")
    
    # Check database
    logger.info("Checking database...")
    db_result = check_database()
    logger.info(f"Database check {'successful' if db_result else 'failed'}")
    
    # Fix character location
    logger.info("Fixing character location...")
    char_result = fix_character_location()
    logger.info(f"Character location fix {'successful' if char_result else 'failed'}")
    
    # Debug look command
    logger.info("Debugging look command...")
    look_result = debug_look_command()
    logger.info(f"Look command debug {'successful' if look_result else 'failed'}")
    
    logger.info("Direct fix completed") 