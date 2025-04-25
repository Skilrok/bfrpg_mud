import asyncio
import logging

from sqlalchemy import text

from app.commands.base import CommandContext, CommandResponse
from app.commands.look_commands import LookCommand
from app.database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_look_command():
    """Test the look command to make sure it's working properly"""
    # Create a db session
    db = next(get_db())

    try:
        # Verify rooms and exits exist
        rooms = db.execute(text("SELECT id, name FROM rooms")).fetchall()
        logger.info(f"Found {len(rooms)} rooms:")
        for room in rooms:
            logger.info(f"  Room {room[0]}: {room[1]}")

        exits = db.execute(
            text("SELECT source_room_id, direction, destination_room_id FROM exits")
        ).fetchall()
        logger.info(f"Found {len(exits)} exits:")
        for exit_data in exits:
            logger.info(
                f"  From Room {exit_data[0]} {exit_data[1]} to Room {exit_data[2]}"
            )

        # Check character location
        character_id = 1
        location = db.execute(
            text(
                "SELECT room_id FROM character_locations WHERE character_id = :char_id"
            ),
            {"char_id": character_id},
        ).fetchone()

        if location:
            logger.info(f"Character {character_id} is in room {location[0]}")
        else:
            logger.info(f"Character {character_id} has no location")
            # Try to create a location
            db.execute(
                text(
                    " +
            "INSERT INTO character_locations (character_id, room_id)"VALUES (:char_id, 1)"
                ),
                {"char_id": character_id},
            )
            db.commit()
            logger.info(f"Created location for character {character_id} in room 1")

        # Create a command context
        ctx = CommandContext(
            command="look",
            args=[],
            data={"db": db, "character_id": character_id},
            character=None,  # We're using character_id from data instead
        )

        # Execute the look command
        look_command = LookCommand()
        logger.info("Executing look command...")
        response = await look_command.execute(ctx)

        logger.info(f"Look command success: {response.success}")
        logger.info(f"Look command message: {response.message}")
        if not response.success:
            logger.error(f"Look command errors: {response.errors}")

        # If debugging is needed, try a lower level look
        logger.info("Executing debug look...")
        debug_response = await look_command.debug_look(ctx)
        logger.info(f"Debug look success: {debug_response.success}")
        logger.info(f"Debug look message: {debug_response.message}")

        return response.success
    except Exception as e:
        logger.error(f"Error testing look command: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Testing look command...")
    asyncio.run(test_look_command())
