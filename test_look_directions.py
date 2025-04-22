import asyncio
import json
import logging
import sqlite3

from app.commands.base import CommandContext, CommandResponse
from app.commands.look_commands import LookCommand

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


async def test_look_direction(direction):
    """Test looking in a specific direction"""
    try:
        # Connect to the database directly
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create a mock db session
        db = MockDb(conn, cursor)

        # Make sure character 1 exists and is in room 1
        cursor.execute("SELECT name FROM characters WHERE id = 1")
        character_row = cursor.fetchone()
        if not character_row:
            cursor.execute(
                "INSERT INTO characters (id, name, description) VALUES (1, 'Bob', 'A test character')"
            )
            conn.commit()
            character_name = "Bob"
        else:
            character_name = character_row[0]

        # Make sure character location exists and is room 1
        cursor.execute("SELECT room_id FROM character_locations WHERE character_id = 1")
        location_row = cursor.fetchone()
        if not location_row:
            cursor.execute(
                "INSERT INTO character_locations (character_id, room_id) VALUES (1, 1)"
            )
            conn.commit()
        elif location_row[0] != 1:
            cursor.execute(
                "UPDATE character_locations SET room_id = 1 WHERE character_id = 1"
            )
            conn.commit()

        logger.info(f"Character 1 ({character_name}) is in the Village Square")

        # Create command context for look command
        ctx = CommandContext(
            command="look",
            args=[direction],
            data={"db": db, "character_id": 1},
            character=None,
        )

        # Execute look command
        look_command = LookCommand()
        logger.info(f"Looking {direction}...")
        response = await look_command.execute(ctx)

        logger.info(f"Look command success: {response.success}")
        logger.info(f"Look command message: {response.message}")
        if response.data:
            logger.info(f"Look command data: {json.dumps(response.data, indent=2)}")
        if not response.success:
            logger.error(f"Look command errors: {response.errors}")

        return response.success
    except Exception as e:
        logger.error(f"Error testing look {direction}: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False
    finally:
        if conn:
            conn.close()


async def test_all_directions():
    """Test looking in all main directions"""
    directions = ["north", "east", "south", "west"]
    results = {}

    for direction in directions:
        logger.info(f"\n--- Testing look {direction} ---")
        results[direction] = await test_look_direction(direction)

    # Log summary
    logger.info("\n--- Results Summary ---")
    for direction, success in results.items():
        logger.info(f"  {direction}: {'SUCCESS' if success else 'FAILED'}")

    return all(results.values())


if __name__ == "__main__":
    logger.info("Testing look command in all directions...")
    asyncio.run(test_all_directions())
