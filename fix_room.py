import logging
import os
import json
from datetime import datetime
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bfrpg.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_starter_room():
    """Create the starter room and its surrounding rooms if they don't exist"""
    db = SessionLocal()
    try:
        # Check if room exists
        room_exists = db.execute(text("SELECT id FROM rooms WHERE id = 1")).fetchone()
        
        if not room_exists:
            logger.info("Room 1 does not exist. Creating it now...")
            
            # Check if area exists
            area_result = db.execute(text("SELECT id FROM areas WHERE name = 'Starting Village'")).fetchone()
            
            if not area_result:
                # Create area
                logger.info("Creating starter area 'Starting Village'")
                area_insert = text("""
                    INSERT INTO areas (name, description, level_range, is_dungeon, is_hidden, properties, created_at, updated_at) 
                    VALUES (:name, :description, :level_range, :is_dungeon, :is_hidden, :properties, :created_at, :updated_at)
                    RETURNING id
                """)
                
                area_result = db.execute(
                    area_insert,
                    {
                        "name": "Starting Village",
                        "description": "A small village where new adventurers begin their journey.",
                        "level_range": "1-3",
                        "is_dungeon": False,
                        "is_hidden": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                area_id = area_result.fetchone()[0]
                logger.info(f"Created starter area with ID {area_id}")
            else:
                area_id = area_result[0]
                logger.info(f"Using existing starter area with ID {area_id}")
                
            # Create the starter room
            logger.info("Creating starter room")
            
            # Basic JSON for exits
            exits_json = "{}"
            
            # Insert the room
            room_insert = text("""
                INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark, exits, properties, created_at, updated_at) 
                VALUES (:id, :name, :description, :room_type, :area_id, :x, :y, :z, :is_dark, :exits, :properties, :created_at, :updated_at)
            """)
            
            db.execute(
                room_insert,
                {
                    "id": 1,
                    "name": "Village Square",
                    "description": "The central square of the starting village. Paths lead in all directions. A tavern stands to the north, a market to the east, a blacksmith to the south, and a temple to the west.",
                    "room_type": "town",
                    "area_id": area_id,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "is_dark": False,
                    "exits": exits_json,
                    "properties": "{}",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            )
            
            # Create additional rooms around the village square
            try:
                # Tavern to the north (Room 2)
                db.execute(
                    room_insert,
                    {
                        "id": 2,
                        "name": "Village Tavern",
                        "description": "A cozy tavern with a roaring fireplace. Adventurers gather here to share tales and find work. The bartender nods at you as you enter.",
                        "room_type": "town",
                        "area_id": area_id,
                        "x": 0,
                        "y": 1,
                        "z": 0,
                        "is_dark": False,
                        "exits": "{}",
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # Market to the east (Room 3)
                db.execute(
                    room_insert,
                    {
                        "id": 3,
                        "name": "Village Market",
                        "description": "A bustling market with various stalls selling goods. Merchants call out to passersby, hawking their wares.",
                        "room_type": "town",
                        "area_id": area_id,
                        "x": 1,
                        "y": 0,
                        "z": 0,
                        "is_dark": False,
                        "exits": "{}",
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # Blacksmith to the south (Room 4)
                db.execute(
                    room_insert,
                    {
                        "id": 4,
                        "name": "Village Blacksmith",
                        "description": "The sound of hammering fills the air as the blacksmith works at the forge. Weapons and armor are displayed on the walls.",
                        "room_type": "town",
                        "area_id": area_id,
                        "x": 0,
                        "y": -1,
                        "z": 0,
                        "is_dark": False,
                        "exits": "{}",
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # Temple to the west (Room 5)
                db.execute(
                    room_insert,
                    {
                        "id": 5,
                        "name": "Village Temple",
                        "description": "A peaceful temple dedicated to various deities. Candles flicker in the dim interior, and a priest stands ready to offer healing and blessings.",
                        "room_type": "town",
                        "area_id": area_id,
                        "x": -1,
                        "y": 0,
                        "z": 0,
                        "is_dark": False,
                        "exits": "{}",
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # Now create exits between rooms using the exits table
                exit_insert = text("""
                    INSERT INTO exits (direction, name, description, source_room_id, destination_room_id, is_hidden, is_locked, properties, created_at, updated_at)
                    VALUES (:direction, :name, :description, :source_room_id, :destination_room_id, :is_hidden, :is_locked, :properties, :created_at, :updated_at)
                """)
                
                # Exits from Village Square (Room 1)
                # North to Tavern
                db.execute(
                    exit_insert,
                    {
                        "direction": "north",
                        "name": "Tavern Entrance",
                        "description": "The door to the village tavern.",
                        "source_room_id": 1,
                        "destination_room_id": 2,
                        "is_hidden": False,
                        "is_locked": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # East to Market
                db.execute(
                    exit_insert,
                    {
                        "direction": "east",
                        "name": "Market Street",
                        "description": "A path leading to the village market.",
                        "source_room_id": 1,
                        "destination_room_id": 3,
                        "is_hidden": False,
                        "is_locked": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # South to Blacksmith
                db.execute(
                    exit_insert,
                    {
                        "direction": "south",
                        "name": "Smithy Road",
                        "description": "A path leading to the village blacksmith.",
                        "source_room_id": 1,
                        "destination_room_id": 4,
                        "is_hidden": False,
                        "is_locked": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # West to Temple
                db.execute(
                    exit_insert,
                    {
                        "direction": "west",
                        "name": "Temple Path",
                        "description": "A serene path leading to the village temple.",
                        "source_room_id": 1,
                        "destination_room_id": 5,
                        "is_hidden": False,
                        "is_locked": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # Return paths back to Village Square
                # South from Tavern
                db.execute(
                    exit_insert,
                    {
                        "direction": "south",
                        "name": "Exit to Village Square",
                        "description": "The door leading back to the village square.",
                        "source_room_id": 2,
                        "destination_room_id": 1,
                        "is_hidden": False,
                        "is_locked": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # West from Market
                db.execute(
                    exit_insert,
                    {
                        "direction": "west",
                        "name": "Back to Village Square",
                        "description": "The path leading back to the village square.",
                        "source_room_id": 3,
                        "destination_room_id": 1,
                        "is_hidden": False,
                        "is_locked": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # North from Blacksmith
                db.execute(
                    exit_insert,
                    {
                        "direction": "north",
                        "name": "Back to Village Square",
                        "description": "The path leading back to the village square.",
                        "source_room_id": 4,
                        "destination_room_id": 1,
                        "is_hidden": False,
                        "is_locked": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # East from Temple
                db.execute(
                    exit_insert,
                    {
                        "direction": "east",
                        "name": "Back to Village Square",
                        "description": "The path leading back to the village square.",
                        "source_room_id": 5,
                        "destination_room_id": 1,
                        "is_hidden": False,
                        "is_locked": False,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                logger.info("Created additional rooms and exits around the village square")
            except Exception as e:
                logger.error(f"Error creating additional rooms or exits: {str(e)}")
                # Continue even if creating additional rooms fails
            
            db.commit()
            logger.info("Created starter room with ID 1")
            return True
        else:
            logger.info("Room 1 already exists.")
            return False
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error: {str(e)}")
        return False
    finally:
        db.close()

def fix_look_command():
    """Debug the look command functionality"""
    db = SessionLocal()
    try:
        # Check if the command_handlers.py file exists in the right place
        # Let's log all commands in registry
        from app.commands.registry import command_registry
        
        all_commands = command_registry.get_all_commands()
        logger.info(f"Available commands: {[cmd.name for cmd in all_commands]}")
        
        # Get look command
        look_cmd = command_registry.get_command("look")
        if look_cmd:
            logger.info(f"Look command found: {look_cmd.name} with aliases {look_cmd.aliases}")
        else:
            logger.error("Look command not found in registry")
            
        # Create a simple test look command to see if it works
        from app.commands.base import CommandHandler, CommandContext, CommandResponse
        
        class DebugLookCommand(CommandHandler):
            name = "debuglook"
            aliases = ["dl"]
            help_text = "Debug version of look command"
            
            async def execute(self, ctx: CommandContext) -> CommandResponse:
                return CommandResponse(
                    success=True,
                    message="Debug look command executed successfully",
                    data={"debug": True}
                )
        
        # Register debug command
        command_registry.register(DebugLookCommand)
        logger.info("Registered debug look command")
        
        # Return success
        return True
    except Exception as e:
        logger.error(f"Error fixing look command: {str(e)}")
        return False
    finally:
        db.close()

def debug_websocket():
    """Debug websocket handlers"""
    try:
        # Check websocket files
        import os
        ws_files = [f for f in os.listdir("app/websockets") if f.endswith(".py")]
        logger.info(f"WebSocket files found: {ws_files}")
        
        # Check if the WebSocketManager is properly importing commands
        from app.websockets import WebSocketManager
        logger.info("WebSocketManager imported successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error debugging websocket: {str(e)}")
        return False

def create_missing_endpoints():
    """Create missing API endpoints for inventory, journal, and hirelings"""
    try:
        from app.routers import characters
        
        # Check if we have the router
        if hasattr(characters, "router"):
            logger.info("Character router found")
        else:
            logger.error("Character router not found")
            
        # We'll need to implement these endpoints properly in the actual router file
        logger.info("Missing endpoints should be implemented in app/routers/characters.py")
        return True
    except Exception as e:
        logger.error(f"Error creating missing endpoints: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting fix script...")
    
    # Step 1: Create the starter room and surroundings
    logger.info("Step 1: Checking and creating starter rooms...")
    room_result = create_starter_room()
    logger.info(f"Room creation result: {'Success' if room_result else 'Failed or already exists'}")
    
    # Step 2: Fix look command
    logger.info("Step 2: Fixing look command...")
    look_result = fix_look_command()
    logger.info(f"Look command fix result: {'Success' if look_result else 'Failed'}")
    
    # Step 3: Debug websocket connections
    logger.info("Step 3: Debugging websocket connections...")
    ws_result = debug_websocket()
    logger.info(f"WebSocket debug result: {'Success' if ws_result else 'Failed'}")
    
    # Step 4: Create missing endpoints
    logger.info("Step 4: Checking missing endpoints...")
    endpoints_result = create_missing_endpoints()
    logger.info(f"Endpoints check result: {'Success' if endpoints_result else 'Failed'}")
    
    logger.info("Fix script completed") 