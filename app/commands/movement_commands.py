import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.commands.base import CommandContext, CommandHandler, CommandResponse
from app.commands.parser import parse_direction
from app.commands.registry import command_registry
from app.models import CharacterLocation, Exit, Room
from app.services.character_service import set_character_starting_location

logger = logging.getLogger(__name__)


async def get_character_location(
    db: Session, character_id: int
) -> Optional[CharacterLocation]:
    """Get the character's current location"""
    try:
        # Use direct SQL query to get location data
        location_data = db.execute(
            text(
                "SELECT room_id FROM character_locations WHERE character_id = :char_id"
            ),
            {"char_id": character_id},
        ).fetchone()

        if not location_data:
            # Try to create a default location in room 1
            success = set_character_starting_location(db, character_id)

            if success:
                # Try to get the location again with direct SQL
                location_data = db.execute(
                    text(
                        "SELECT room_id FROM character_locations WHERE character_id = :char_id"
                    ),
                    {"char_id": character_id},
                ).fetchone()
                logger.info(
                    f"Created new default location for character {character_id}"
                )

        if location_data:
            # Create a CharacterLocation object with the retrieved data
            location = CharacterLocation(
                character_id=character_id, room_id=location_data[0]
            )
            return location

        return None
    except Exception as e:
        logger.error(f"Error getting character location: {str(e)}")
        return None


async def move_character(db: Session, character_id: int, room_id: int) -> bool:
    """Move a character to a different room."""
    try:
        # Check if character has a location
        location = await get_character_location(db, character_id)

        if not location:
            return False

        # Check if the room exists
        room_exists = db.execute(
            text("SELECT id FROM rooms WHERE id = :room_id"), {"room_id": room_id}
        ).fetchone()

        if not room_exists:
            logger.error(
                f"Cannot move character {character_id} to non-existent room {room_id}"
            )
            return False

        # Update the character's location using raw SQL
        db.execute(
            text(
                "UPDATE character_locations SET room_id = :room_id WHERE character_id = :char_id"
            ),
            {"room_id": room_id, "char_id": character_id},
        )
        db.commit()

        logger.info(f"Character {character_id} moved to room {room_id}")
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error moving character {character_id} to room {room_id}: {str(e)}"
        )
        return False
    except Exception as e:
        logger.error(
            f"Error moving character {character_id} to room {room_id}: {str(e)}"
        )
        return False


async def set_character_starting_location(db: Session, character_id: int) -> int:
    """Set a character's location to the default starting room (1)"""
    try:
        # Check if a location already exists
        existing_location = db.execute(
            text(
                "SELECT room_id FROM character_locations WHERE character_id = :char_id"
            ),
            {"char_id": character_id},
        ).fetchone()

        if existing_location:
            return existing_location[0]

        # Create a new location using room ID 1 (default starting room)
        db.execute(
            text(
                "INSERT INTO character_locations (character_id, room_id) VALUES (:char_id, :room_id)"
            ),
            {"char_id": character_id, "room_id": 1},
        )
        db.commit()

        logger.info(f"Set character {character_id} to starting location (room 1)")
        return 1
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(
            f"Database error setting starting location for character {character_id}: {str(e)}"
        )
        return 0
    except Exception as e:
        logger.error(
            f"Error setting starting location for character {character_id}: {str(e)}"
        )
        return 0


class MoveCommand(CommandHandler):
    """Base handler for movement commands"""

    name = ""
    direction = ""

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check if character exists
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to move.",
                errors=["No active character"],
            )

        # Get DB session
        db = ctx.data.get("db")
        if not db:
            return CommandResponse(
                success=False,
                message="Database session not available.",
                errors=["No database session"],
            )

        # Get character's current location
        location = await get_character_location(db, ctx.character.id)
        if not location or not location.room_id:
            # Character isn't in a room yet, place them in the starting room
            starting_room = db.query(Room).filter(Room.id == 1).first()
            if not starting_room:
                return CommandResponse(
                    success=False,
                    message="Could not find a starting room.",
                    errors=["No starting room found"],
                )

            # Place character in starting room
            success = await move_character(db, ctx.character.id, starting_room.id)
            if not success:
                return CommandResponse(
                    success=False,
                    message="Could not place you in the starting room.",
                    errors=["Failed to place character in starting room"],
                )

            return CommandResponse(
                success=True,
                message=f"You have been placed in {starting_room.name}.\n\n{starting_room.description}",
                data={"room_id": starting_room.id, "room_name": starting_room.name},
            )

        # Get current room
        current_room = db.query(Room).filter(Room.id == location.room_id).first()
        if not current_room:
            return CommandResponse(
                success=False,
                message="You are nowhere to be found.",
                errors=["Current room not found"],
            )

        # First try to find exit using the Exit model
        exit = (
            db.query(Exit)
            .filter(
                Exit.source_room_id == current_room.id,
                Exit.direction == self.direction,
                Exit.is_hidden == False,  # Only consider visible exits
            )
            .first()
        )

        # If exit found through Exit model, use it
        if exit:
            # Check if exit is locked
            if exit.is_locked:
                return CommandResponse(
                    success=False,
                    message=f"The way {self.direction} is locked.",
                    errors=["Exit is locked"],
                )

            destination_room = (
                db.query(Room).filter(Room.id == exit.destination_room_id).first()
            )
            if not destination_room:
                return CommandResponse(
                    success=False,
                    message=f"The way {self.direction} leads nowhere.",
                    errors=["Destination room not found"],
                )

            # Move character to new room
            success = await move_character(db, ctx.character.id, destination_room.id)
            if not success:
                return CommandResponse(
                    success=False,
                    message=f"You couldn't move {self.direction}.",
                    errors=["Failed to move character"],
                )

            # Build description with exit name/description if available
            direction_desc = f"{self.direction}"
            if exit.name:
                direction_desc = f"{self.direction} through {exit.name}"

            msg = f"You move {direction_desc} to {destination_room.name}."
            if exit.description:
                msg += f" {exit.description}"

            msg += f"\n\n{destination_room.description}"

            return CommandResponse(
                success=True,
                message=msg,
                data={
                    "room_id": destination_room.id,
                    "room_name": destination_room.name,
                    "direction": self.direction,
                    "exit_id": exit.id,
                },
            )

        # If no Exit model exit found, fallback to legacy exits field for backward compatibility
        elif current_room.exits and self.direction in current_room.exits:
            # Check if direction is valid for this room using legacy exits
            destination_room_id = current_room.exits[self.direction]
            destination_room = (
                db.query(Room).filter(Room.id == destination_room_id).first()
            )

            if not destination_room:
                return CommandResponse(
                    success=False,
                    message=f"The way {self.direction} seems blocked.",
                    errors=["Destination room not found"],
                )

            # Move character to new room
            success = await move_character(db, ctx.character.id, destination_room.id)
            if not success:
                return CommandResponse(
                    success=False,
                    message=f"You couldn't move {self.direction}.",
                    errors=["Failed to move character"],
                )

            # Return success message with description of new room
            return CommandResponse(
                success=True,
                message=f"You move {self.direction} to {destination_room.name}.\n\n{destination_room.description}",
                data={
                    "room_id": destination_room.id,
                    "room_name": destination_room.name,
                    "direction": self.direction,
                },
            )
        else:
            # No exit found in either system
            return CommandResponse(
                success=False,
                message=f"You can't go {self.direction} from here.",
                errors=[f"No exit in direction {self.direction}"],
            )


class NorthCommand(MoveCommand):
    """Handler for the north command"""

    name = "north"
    aliases = ["n"]
    help_text = "Move north. Usage: north"
    direction = "north"


class SouthCommand(MoveCommand):
    """Handler for the south command"""

    name = "south"
    aliases = ["s"]
    help_text = "Move south. Usage: south"
    direction = "south"


class EastCommand(MoveCommand):
    """Handler for the east command"""

    name = "east"
    aliases = ["e"]
    help_text = "Move east. Usage: east"
    direction = "east"


class WestCommand(MoveCommand):
    """Handler for the west command"""

    name = "west"
    aliases = ["w"]
    help_text = "Move west. Usage: west"
    direction = "west"


class UpCommand(MoveCommand):
    """Handler for the up command"""

    name = "up"
    aliases = ["u"]
    help_text = "Move up. Usage: up"
    direction = "up"


class DownCommand(MoveCommand):
    """Handler for the down command"""

    name = "down"
    aliases = ["d"]
    help_text = "Move down. Usage: down"
    direction = "down"


class GoCommand(CommandHandler):
    """Handler for the go command"""

    name = "go"
    aliases = ["move"]
    help_text = "Move in a specified direction. Usage: go <direction>"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check if character exists
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to move.",
                errors=["No active character"],
            )

        # Check if direction was specified
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="Go where? You need to specify a direction.",
                errors=["No direction specified"],
            )

        # Parse direction
        direction_text = ctx.args[0].lower()
        direction = parse_direction(direction_text)

        if not direction:
            return CommandResponse(
                success=False,
                message=f"'{direction_text}' is not a valid direction.",
                errors=["Invalid direction"],
            )

        # Create the appropriate directional command and execute it
        direction_handlers = {
            "north": NorthCommand(),
            "south": SouthCommand(),
            "east": EastCommand(),
            "west": WestCommand(),
            "up": UpCommand(),
            "down": DownCommand(),
        }

        if direction in direction_handlers:
            handler = direction_handlers[direction]
            return await handler.execute(ctx)
        else:
            return CommandResponse(
                success=False,
                message=f"You can't go in that direction.",
                errors=["Unsupported direction"],
            )


# Register movement commands
command_registry.register(NorthCommand)
command_registry.register(SouthCommand)
command_registry.register(EastCommand)
command_registry.register(WestCommand)
command_registry.register(UpCommand)
command_registry.register(DownCommand)
command_registry.register(GoCommand)
