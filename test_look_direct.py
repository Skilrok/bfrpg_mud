import sqlite3
import logging
import asyncio
import json

from app.commands.look_commands import LookCommand
from app.commands.base import CommandContext, CommandResponse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database path
DB_PATH = "./bfrpg.db"

class MockDb:
    """Mock SQLAlchemy-like database session"""
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        
    def execute(self, query, params=None):
        """Execute the query and return a result proxy"""
        if isinstance(query, str):
            # Direct string query
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
        else:
            # Assume it's a sqlalchemy text object and extract the text
            query_text = str(query)
            # Extract just the SQL part
            if hasattr(query, 'text'):
                query_text = query.text
            else:
                # Try to handle text() function result
                if 'text(' in str(query):
                    query_text = str(query).split('text(')[1].split(')')[0].strip("'")
                
            if params:
                self.cursor.execute(query_text, params)
            else:
                self.cursor.execute(query_text)
                
        return self
    
    def fetchone(self):
        """Fetch one row"""
        return self.cursor.fetchone()
    
    def fetchall(self):
        """Fetch all rows"""
        return self.cursor.fetchall()
    
    def commit(self):
        """Commit the transaction"""
        self.conn.commit()
    
    def close(self):
        """Close the connection"""
        self.conn.close()

async def test_look_command():
    """Test the look command with a direct database connection"""
    try:
        # Connect to the database directly
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create a mock db session
        db = MockDb(conn, cursor)
        
        # Check rooms
        cursor.execute("SELECT id, name FROM rooms")
        rooms = cursor.fetchall()
        logger.info(f"Found {len(rooms)} rooms:")
        for room in rooms:
            logger.info(f"  Room {room[0]}: {room[1]}")
            
        # Check exits
        cursor.execute("SELECT source_room_id, direction, destination_room_id FROM exits")
        exits = cursor.fetchall()
        logger.info(f"Found {len(exits)} exits:")
        for exit_data in exits:
            logger.info(f"  From Room {exit_data[0]} {exit_data[1]} to Room {exit_data[2]}")
            
        # Create character location if needed
        character_id = 1
        cursor.execute("SELECT room_id FROM character_locations WHERE character_id = ?", (character_id,))
        location = cursor.fetchone()
        
        if location:
            logger.info(f"Character {character_id} is in room {location[0]}")
        else:
            logger.info(f"Character {character_id} has no location, creating one")
            cursor.execute(
                "INSERT INTO character_locations (character_id, room_id) VALUES (?, ?)",
                (character_id, 1)
            )
            conn.commit()
            logger.info(f"Created location for character {character_id} in room 1")
        
        # Create a command context
        ctx = CommandContext(
            command="look",
            args=[],
            data={"db": db, "character_id": character_id},
            character=None
        )
        
        # Execute the look command
        look_command = LookCommand()
        logger.info("Executing look command...")
        response = await look_command.execute(ctx)
        
        logger.info(f"Look command success: {response.success}")
        logger.info(f"Look command message: {response.message}")
        if response.data:
            logger.info(f"Look command data: {json.dumps(response.data, indent=2)}")
        if not response.success:
            logger.error(f"Look command errors: {response.errors}")
            
        return response.success
    except Exception as e:
        logger.error(f"Error testing look command: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    logger.info("Running direct look command test...")
    asyncio.run(test_look_command()) 