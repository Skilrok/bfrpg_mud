import logging
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import text
# REMOVED: from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.commands.base import CommandContext, CommandHandler, CommandResponse
# REMOVED: from app.commands.movement_commands import get_character_location
from app.commands.registry import command_registry
from app.models import Character, CharacterLocation, Room, RoomItem
from app.services.character_service import set_character_starting_location

logger = logging.getLogger(__name__)


class LookCommand(CommandHandler):
    """Handler for the look command"""

    name = "look"
    aliases = ["l", "debuglook"]
    help_text = "Look at your surroundings or examine something specific"

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        """Simple debug implementation of look command"""
        logger.info("Look command executed")

        # Get DB session
        db = ctx.data.get("db")
        if not db:
            return CommandResponse(
                success=False,
                message="Error: Database unavailable",
                errors=["No database"],
            )

        # Get character ID - log more details to diagnose issue
        character_id = None
        if ctx.character:
            character_id = ctx.character.id
            logger.info(f"Using character ID from ctx.character: {character_id}")
        else:
            character_id = ctx.data.get("character_id")
            logger.info(f"Using character ID from ctx.data: {character_id}")

        if not character_id:
            logger.error("No character ID found in ctx.character or ctx.data!")
            return CommandResponse(
                success=False,
                message="You need an active character to look around.",
                errors=["No active character"],
            )

        # Try to verify the character exists in the database
        try:
            char_exists = db.execute(
                text("SELECT id FROM characters WHERE id = :char_id"),
                {"char_id": character_id},
            ).fetchone()

            if not char_exists:
                logger.error(
                    f"Character with ID {character_id} does not exist in the database!"
                )
                return CommandResponse(
                    success=False,
                    message="Character not found. Please select a valid character.",
                    errors=["Character not found"],
                )
            logger.info(f"Verified character {character_id} exists in database")
        except Exception as e:
            logger.error(f"Error verifying character existence: {str(e)}")
            # Continue anyway - this is just an extra check

        logger.info(f"Looking at room for character {character_id}")

        # Check if we're looking at something specific
        if ctx.args:
            target = " ".join(ctx.args).lower()
            logger.info(f"Looking at target: {target}")
            return await self._look_at_target(db, character_id, target)
        else:
            # No target specified, look at the room
            logger.info("No target specified, looking at room")
            return await self._look_at_room(db, character_id)

    async def _look_at_room(
        # ADDED DEBUG INFO FOR LOOK
        self,
        db: Session,
        character_id: int,
    ) -> CommandResponse:
        try:
            # Add debug logging
            logger.info(f"Looking at room for character {character_id}")
            # Get character's current location using direct SQL
            location_data = db.execute(
                text(
                    "SELECT room_id FROM character_locations WHERE character_id = :char_id"
                ),
                {"char_id": character_id},
            ).fetchone()

            if not location_data:
                # Try to set starting location
                success = set_character_starting_location(db, character_id)
                if not success:
                    logger.info("Returning room description")
                    return CommandResponse(
                        success=False,
                        message="You aren't anywhere in the game world yet.",
                        errors=["No location found"],
                    )

            room_id = location_data[0]
            logger.info(f"Found room ID: {room_id}")
            logger.info(f"Found room_id: {room_id}")

            # Get room data using direct SQL to avoid ORM issues
            room_data = db.execute(
                text(
                    "SELECT id, name, description, room_type, area_id, is_dark, exits FROM rooms WHERE id = :room_id"
                ),
                {"room_id": room_id},
            ).fetchone()

            if not room_data:
                logger.info("Returning room description")
                return CommandResponse(
                    success=False,
                    message="The room you're in seems to have vanished!",
                    errors=["Room not found"],
                )

            room_name = room_data[1]
            logger.info(f"Room name: {room_name}")
            room_description = room_data[2]

            # Get room items using direct SQL
            items_data = db.execute(
                text(
                    """
                SELECT ri.id, ri.quantity, i.name, i.description 
                FROM room_items ri 
                JOIN items i ON ri.item_id = i.id 
                WHERE ri.room_id = :room_id
                """
                ),
                {"room_id": room_id},
            ).fetchall()

            # Get NPCs in the room using direct SQL
            npcs_data = db.execute(
                text(
                    """
                SELECT rn.id, n.name, n.description 
                FROM room_npcs rn 
                JOIN npcs n ON rn.npc_id = n.id 
                WHERE rn.room_id = :room_id
                """
                ),
                {"room_id": room_id},
            ).fetchall()

            # Get other characters in the room using direct SQL
            characters_data = db.execute(
                text(
                    """
                SELECT cl.character_id, c.name 
                FROM character_locations cl 
                JOIN characters c ON cl.character_id = c.id 
                WHERE cl.room_id = :room_id AND cl.character_id != :char_id
                """
                ),
                {"room_id": room_id, "char_id": character_id},
            ).fetchall()

            # Get available exits using direct SQL
            exits_data = db.execute(
                text(
                    """
                SELECT direction, destination_room_id, name 
                FROM exits 
                WHERE source_room_id = :room_id AND is_hidden = 0
                """
                ),
                {"room_id": room_id},
            ).fetchall()

            # Build a nicely formatted room description
            # Add a horizontal rule and room name in a centered format
            room_width = min(
                max(len(room_name) + 10, 60), 80
            )  # Width between 60-80 chars
            description = f"\n{'-' * room_width}\n"
            description += f"{room_name.center(room_width)}\n"
            description += f"{'-' * room_width}\n\n"
            description += f"{room_description}\n"

            # Format exits in a nice compass-like display
            exits_by_direction = {
                exit_data[0]: (exit_data[1], exit_data[2]) for exit_data in exits_data
            }

            # Also check legacy exits
            if room_data[6]:  # exits field
                import json

                try:
                    # Add debug logging
                    logger.info(f"Looking at room for character {character_id}")
                    exits_json = json.loads(room_data[6])
                    if exits_json:
                        for direction, dest_id in exits_json.items():
                            if direction not in exits_by_direction:
                                exits_by_direction[direction] = (dest_id, None)
                except Exception:
                    pass

            # Build an ASCII compass for the cardinal directions
            if exits_by_direction:
                description += "\n\nExits:\n"

                # Create compass display for N, S, E, W directions
                compass = ["    {N}    ", " {W}     {E} ", "    {S}    "]

                # Replace placeholders with exits or spaces
                direction_symbols = {
                    "north": "N",
                    "south": "S",
                    "east": "E",
                    "west": "W",
                    "n": "N",
                    "s": "S",
                    "e": "E",
                    "w": "W",
                }

                for i, row in enumerate(compass):
                    for direction, symbol in direction_symbols.items():
                        if direction in exits_by_direction:
                            # If there's an exit name, use it
                            exit_name = exits_by_direction[direction][1]
                            if exit_name:
                                direction_text = f"[{symbol}:{exit_name}]"
                            else:
                                direction_text = f"[{symbol}]"
                            compass[i] = compass[i].replace(
                                f"{{{symbol}}}", direction_text
                            )
                        else:
                            compass[i] = compass[i].replace(f"{{{symbol}}}", " ")

                # Add the compass to the description
                description += "\n".join(compass)

                # List all available exits with their destination names
                description += "\n"
                for direction, (dest_id, exit_name) in exits_by_direction.items():
                    # Get destination room name
                    dest_data = db.execute(
                        text("SELECT name FROM rooms WHERE id = :room_id"),
                        {"room_id": dest_id},
                    ).fetchone()

                    dest_name = "unknown"
                    if dest_data:
                        dest_name = dest_data[0]

                    if exit_name:
                        description += f"\n- {direction}: {exit_name} (to {dest_name})"
                    else:
                        description += f"\n- {direction}: to {dest_name}"

                # Add other non-cardinal directions
                other_dirs = [
                    d for d in exits_by_direction if d not in direction_symbols.keys()
                ]
                if other_dirs:
                    for direction in other_dirs:
                        dest_id, exit_name = exits_by_direction[direction]
                        dest_data = db.execute(
                            text("SELECT name FROM rooms WHERE id = :room_id"),
                            {"room_id": dest_id},
                        ).fetchone()

                        dest_name = "unknown"
                        if dest_data:
                            dest_name = dest_data[0]

                        if exit_name:
                            description += (
                                f"\n- {direction}: {exit_name} (to {dest_name})"
                            )
                        else:
                            description += f"\n- {direction}: to {dest_name}"
            else:
                description += "\n\nThere are no obvious exits."

            # Add items with a nice header
            if items_data:
                description += "\n\n" + "Items".center(room_width, "-") + "\n"
                for item in items_data:
                    quantity = item[1]
                    name = item[2]
                    if quantity > 1:
                        description += f"- {quantity}x {name}\n"
                    else:
                        description += f"- {name}\n"

            # Add NPCs and characters with a nice header
            if npcs_data or characters_data:
                description += "\n" + "Characters".center(room_width, "-") + "\n"

                # Add NPCs
                for npc in npcs_data:
                    name = npc[1]
                    description += f"- {name}\n"

                # Add other players
                for character in characters_data:
                    name = character[1]
                    description += f"- {name}\n"

            # Close with a horizontal rule
            description += f"\n{'-' * room_width}"

            # Return full description
            logger.info("Returning room description")
            return CommandResponse(
                success=True,
                message=description,
                data={
                    "room_id": room_id,
                    "room_name": room_name,
                    "items": [
                        {"id": item[0], "name": item[2], "quantity": item[1]}
                        for item in items_data
                    ],
                    "npcs": [{"id": npc[0], "name": npc[1]} for npc in npcs_data],
                    "characters": [
                        {"id": char[0], "name": char[1]} for char in characters_data
                    ],
                    "exits": [
                        {"direction": exit[0], "destination": exit[1], "name": exit[2]}
                        for exit in exits_data
                    ],
                },
            )
        except Exception as e:
            logger.error(f"Error in look command: {str(e)}")
            logger.info("Returning room description")
            return CommandResponse(
                success=False,
                message=f"Error looking around: {str(e)}",
                errors=[str(e)],
            )

    async def _look_at_target(
        self, db: Session, character_id: int, target: str
    ) -> CommandResponse:
        # Implementation for looking at specific targets
        # This could examine items, NPCs, or features in the room

        # Get character's location
        location_data = db.execute(
            text(
                "SELECT room_id FROM character_locations WHERE character_id = :char_id"
            ),
            {"char_id": character_id},
        ).fetchone()

        if not location_data:
            logger.info("Returning room description")
            return CommandResponse(
                success=False,
                message="You need to be somewhere to look at things.",
                errors=["No location"],
            )

        room_id = location_data[0]
        logger.info(f"Found room ID: {room_id}")
        logger.info(f"Found room_id: {room_id}")

        # First, check if target is an item in the room
        item_data = db.execute(
            text(
                """
            SELECT i.name, i.description, ri.quantity
            FROM room_items ri 
            JOIN items i ON ri.item_id = i.id 
            WHERE ri.room_id = :room_id AND lower(i.name) = :target
            """
            ),
            {"room_id": room_id, "target": target},
        ).fetchone()

        if item_data:
            item_name = item_data[0]
            item_description = item_data[1]
            quantity = item_data[2]

            description = f"{item_name}: {item_description}"
            if quantity > 1:
                description = f"({quantity}) {description}"

            logger.info("Returning room description")
            return CommandResponse(
                success=True,
                message=description,
                data={"item_name": item_name, "item_description": item_description},
            )

        # Check if target is an NPC
        npc_data = db.execute(
            text(
                """
            SELECT n.name, n.description
            FROM room_npcs rn 
            JOIN npcs n ON rn.npc_id = n.id 
            WHERE rn.room_id = :room_id AND lower(n.name) = :target
            """
            ),
            {"room_id": room_id, "target": target},
        ).fetchone()

        if npc_data:
            npc_name = npc_data[0]
            npc_description = npc_data[1]

            logger.info("Returning room description")
            return CommandResponse(
                success=True,
                message=f"{npc_name}: {npc_description}",
                data={"npc_name": npc_name, "npc_description": npc_description},
            )

        # Check if target is another player
        character_data = db.execute(
            text(
                """
            SELECT c.name, c.description 
            FROM character_locations cl 
            JOIN characters c ON cl.character_id = c.id 
            WHERE cl.room_id = :room_id AND cl.character_id != :char_id AND lower(c.name) = :target
            """
            ),
            {"room_id": room_id, "char_id": character_id, "target": target},
        ).fetchone()

        if character_data:
            player_name = character_data[0]
            player_description = character_data[1]

            logger.info("Returning room description")
            return CommandResponse(
                success=True,
                message=f"{player_name}: {player_description}",
                data={
                    "player_name": player_name,
                    "player_description": player_description,
                },
            )

        # Check if target is a direction
        directions = ["north", "south", "east", "west", "up", "down"]
        direction_aliases = {
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            "u": "up",
            "d": "down",
        }

        if target in directions or target in direction_aliases:
            # Normalize the direction
            if target in direction_aliases:
                direction = direction_aliases[target]
            else:
                direction = target

            # Check for exit in that direction
            exit_data = db.execute(
                text(
                    """
                SELECT e.name, e.description, r.name 
                FROM exits e
                JOIN rooms r ON e.destination_room_id = r.id
                WHERE e.source_room_id = :room_id AND e.direction = :direction AND e.is_hidden = 0
                """
                ),
                {"room_id": room_id, "direction": direction},
            ).fetchone()

            if exit_data:
                exit_name = exit_data[0] or "exit"
                exit_description = exit_data[1] or f"An exit leading {direction}."
                destination_name = exit_data[2]

                logger.info("Returning room description")
                return CommandResponse(
                    success=True,
                    message=f"{exit_name} ({direction} to {destination_name})\n\n{exit_description}",
                    data={
                        "exit_name": exit_name,
                        "exit_description": exit_description,
                        "direction": direction,
                        "destination_name": destination_name,
                    },
                )
            else:
                # Check legacy exits
                room_data = db.execute(
                    text("SELECT exits FROM rooms WHERE id = :room_id"),
                    {"room_id": room_id},
                ).fetchone()

                if room_data and room_data[0]:
                    import json

                    try:
                        # Add debug logging
                        logger.info(f"Looking at room for character {character_id}")
                        exits_json = json.loads(room_data[0])
                        if direction in exits_json:
                            destination_id = exits_json[direction]

                            dest_data = db.execute(
                                text("SELECT name FROM rooms WHERE id = :room_id"),
                                {"room_id": destination_id},
                            ).fetchone()

                            if dest_data:
                                destination_name = dest_data[0]
                                logger.info("Returning room description")
                                return CommandResponse(
                                    success=True,
                                    message=f"You see an exit leading {direction} to {destination_name}.",
                                    data={
                                        "direction": direction,
                                        "destination_name": destination_name,
                                    },
                                )
                    except Exception:
                        pass

                logger.info("Returning room description")
                return CommandResponse(
                    success=False,
                    message=f"You don't see an exit to the {direction}.",
                    errors=[f"No exit {direction}"],
                )

        # If we get here, the target wasn't found
        logger.info("Returning room description")
        return CommandResponse(
            success=False,
            message=f"You don't see '{target}' here.",
            errors=["Target not found"],
        )

    # DEBUG FUNCTION FOR LOOK COMMAND
    async def debug_look(self, ctx: CommandContext) -> CommandResponse:
        """Debug version of look command"""
        logger.info(f"DEBUG LOOK COMMAND EXECUTED")
        try:
            # Get DB session
            db = ctx.data.get("db")
            if not db:
                logger.info("Returning room description")
                return CommandResponse(
                    success=False,
                    message="Error: Database unavailable",
                    errors=["No database"],
                )

            # Get character ID
            character_id = None
            if ctx.character:
                character_id = ctx.character.id
            else:
                character_id = ctx.data.get("character_id")

            if not character_id:
                logger.info("Returning room description")
                return CommandResponse(
                    success=False,
                    message="You need an active character to look around.",
                    errors=["No active character"],
                )

            # Just call the execute method with debug logs
            logger.info(f"DEBUG look for character {character_id}")
            return await self.execute(ctx)

        except Exception as e:
            import traceback

            logger.error(f"Error in look command: {str(e)}")
            logger.error(traceback.format_exc())
            return CommandResponse(
                success=False,
                message=f"Error looking around: {str(e)}",
                errors=[str(e)],
            )


# Register the command - prevent duplicate registration
if "look" not in command_registry._commands:
    logger.info("Registering LookCommand for the first time")
    command_registry.register(LookCommand)
else:
    logger.warning("LookCommand already registered, not registering again")
