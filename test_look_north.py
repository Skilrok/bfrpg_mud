import asyncio
import json
import logging
import sqlite3

from app.commands.base import CommandContext, CommandResponse
from app.commands.look_commands import LookCommand
from app.commands.movement_commands import MoveCommand, NorthCommand

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
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
            if hasattr(query, "text"):
                query_text = query.text
            else:
                # Try to handle text() function result
                if "text(" in str(query):
                    query_text = str(query).split("text(")[1].split(")")[0].strip("'")

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


async def test_north_then_look():
    """Test going north then looking at the tavern"""
    try:
        # Connect to the database directly
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create a mock db session
        db = MockDb(conn, cursor)

        # Create character location and make sure it's in the Village Square
        character_id = 1
        cursor.execute(
            "UPDATE character_locations SET room_id = 1 WHERE character_id = ?",
            (character_id,),
        )
        conn.commit()

        # Retrieve character name
        cursor.execute("SELECT name FROM characters WHERE id = ?", (character_id,))
        character_name = cursor.fetchone()[0]
        logger.info(
            f"Character {character_id} ({character_name}) is in the Village Square"
        )

        # Create a mock character object
        class MockCharacter:
            def __init__(self, id, name):
                self.id = id
                self.name = name

        character = MockCharacter(character_id, character_name)

        # Create command context for north command
        ctx = CommandContext(
            command="north", args=[], data={"db": db}, character=character
        )

        # Execute north command
        north_command = NorthCommand()
        logger.info("Executing north command...")
        response = await north_command.execute(ctx)

        logger.info(f"North command success: {response.success}")
        logger.info(f"North command message: {response.message}")
        if not response.success:
            logger.error(f"North command errors: {response.errors}")
            return False

        # Create command context for look
        ctx = CommandContext(
            command="look", args=[], data={"db": db}, character=character
        )

        # Execute look command
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
        logger.error(f"Error testing north and look commands: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    logger.info("Testing north and look commands...")
    asyncio.run(test_north_then_look())
