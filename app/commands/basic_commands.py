from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session

from app.commands.base import CommandHandler, CommandContext, CommandResponse
from app.commands.registry import command_registry
from app.commands import registry as command_registry_commands
from app.models import Area, Room, Exit, Item, User
from app.database import get_db_context

logger = logging.getLogger(__name__)

class HelpCommand(CommandHandler):
    """Handler for the help command"""
    name = "help"
    aliases = ["?", "commands", "h"]
    help_text = "Display help information for available commands. Usage: help [command]"
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Show help for a specific command
        if ctx.args and len(ctx.args) > 0:
            cmd_name = ctx.args[0].lower()
            handler = command_registry.get_handler(cmd_name)
            
            if handler:
                return CommandResponse(
                    success=True,
                    message=f"Help for '{handler.name}':\n{handler.get_help()}",
                    data={"command": handler.name, "help_text": handler.get_help()}
                )
            else:
                return CommandResponse(
                    success=False,
                    message=f"No help available: Command '{cmd_name}' not found.",
                    errors=[f"Command '{cmd_name}' not found"]
                )
        
        # Show general help (list of commands)
        commands = command_registry.get_command_list()
        commands_by_name = sorted(commands, key=lambda c: c.name)
        
        # Format command list
        help_text = "Available commands:\n"
        for cmd in commands_by_name:
            aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_text += f"- {cmd.name}{aliases}: {cmd.help_text.split('.')[0]}.\n"
            
        help_text += "\nFor more information about a specific command, type: help <command>"
        
        return CommandResponse(
            success=True,
            message=help_text,
            data={"commands": [{"name": cmd.name, "help": cmd.help_text} for cmd in commands_by_name]}
        )

class LookCommand(CommandHandler):
    """Handler for the look command"""
    name = "look"
    aliases = ["l"]
    help_text = "Look at your surroundings or examine something specific. Usage: look [target]"
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't look
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to look around.",
                errors=["No active character"]
            )
            
        # Get DB session
        db = ctx.data.get("db")
        if not db:
            return CommandResponse(
                success=False,
                message="Database session not available.",
                errors=["No database session"]
            )
            
        # Get character's current location
        from app.commands.movement_commands import get_character_location
        location = await get_character_location(db, ctx.character.id)
        
        if not location or not location.room_id:
            return CommandResponse(
                success=False,
                message="You are not in a room yet. Try moving in a direction to get started.",
                errors=["No location found"]
            )
            
        # Get current room
        from app.models import Room, CharacterLocation, RoomItem, RoomNPC
        room = db.query(Room).filter(Room.id == location.room_id).first()
        
        if not room:
            return CommandResponse(
                success=False,
                message="You seem to be nowhere. This is a bug!",
                errors=["Room not found"]
            )
            
        # If no target specified, look at the room
        if not ctx.args:
            # Get exits description using both Exit model and legacy exits field
            from app.models import Exit
            
            # Get exits from Exit model
            model_exits = db.query(Exit).filter(
                Exit.source_room_id == room.id,
                Exit.is_hidden == False  # Only visible exits
            ).all()
            
            # Organize directions
            exit_directions = []
            
            # Add exits from Exit model
            for exit in model_exits:
                exit_directions.append(exit.direction)
            
            # Add exits from legacy field if they don't overlap with model exits
            legacy_exits = room.exits or {}
            for direction in legacy_exits.keys():
                if direction not in exit_directions:
                    exit_directions.append(direction)
            
            # Create exits description
            exits_desc = "Exits: " + (", ".join(sorted(exit_directions)) if exit_directions else "none")
            
            # Add detailed exit descriptions if available from Exit model
            exit_details = []
            for exit in model_exits:
                if exit.name or exit.description:
                    detail = f"The {exit.direction} exit"
                    if exit.name:
                        detail += f" leads to {exit.name}"
                    if exit.description:
                        detail += f". {exit.description}"
                    exit_details.append(detail)
            
            if exit_details:
                exits_desc += "\n" + "\n".join(exit_details)
            
            # Get characters in room
            other_characters = db.query(CharacterLocation).filter(
                CharacterLocation.room_id == room.id,
                CharacterLocation.character_id != ctx.character.id
            ).all()
            
            characters_desc = ""
            if other_characters:
                # Get character names
                character_ids = [cl.character_id for cl in other_characters]
                from app.models import Character
                chars = db.query(Character).filter(Character.id.in_(character_ids)).all()
                if chars:
                    characters_desc = "\n\nYou see:\n" + "\n".join([f"- {char.name}" for char in chars])
            
            # Get items in room
            items = db.query(RoomItem).filter(RoomItem.room_id == room.id).all()
            items_desc = ""
            if items:
                # Get item details
                item_ids = [ri.item_id for ri in items]
                from app.models import Item
                room_items = db.query(Item).filter(Item.id.in_(item_ids)).all()
                if room_items:
                    items_desc = "\n\nItems here:\n" + "\n".join([f"- {item.name}" for item in room_items])
            
            # Combine all descriptions
            full_desc = f"{room.name}\n\n{room.description}\n\n{exits_desc}{characters_desc}{items_desc}"
            
            # Create a list of exit information including both model and legacy exits
            exit_info = []
            
            # Add Exit model exits
            for exit in model_exits:
                exit_info.append({
                    "direction": exit.direction,
                    "exit_id": exit.id,
                    "destination_room_id": exit.destination_room_id,
                    "name": exit.name,
                    "is_locked": exit.is_locked
                })
            
            # Add legacy exits
            for direction, dest_id in legacy_exits.items():
                # Check if this direction is already covered by a model exit
                if not any(e["direction"] == direction for e in exit_info):
                    exit_info.append({
                        "direction": direction,
                        "exit_id": None,
                        "destination_room_id": dest_id
                    })
            
            return CommandResponse(
                success=True,
                message=full_desc,
                data={
                    "room_id": room.id,
                    "room_name": room.name,
                    "exits": exit_info,
                    "legacy_exits": list(legacy_exits.keys()),
                    "characters": [c.character_id for c in other_characters] if other_characters else [],
                    "items": [i.item_id for i in items] if items else []
                }
            )
        
        # Look at a specific target
        target = " ".join(ctx.args).lower()
        
        # Check if target is an exit (including Exit model exits)
        from app.models import Exit
        
        # First check Exit model exits
        model_exit = db.query(Exit).filter(
            Exit.source_room_id == room.id,
            Exit.is_hidden == False,
            Exit.direction == target
        ).first()
        
        if model_exit:
            # Build description
            exit_desc = f"You look {target}."
            if model_exit.name:
                exit_desc += f" It leads to {model_exit.name}."
            if model_exit.description:
                exit_desc += f" {model_exit.description}"
            
            return CommandResponse(
                success=True,
                message=exit_desc,
                data={
                    "direction": target,
                    "exit_id": model_exit.id,
                    "destination_room_id": model_exit.destination_room_id
                }
            )
        
        # Then check legacy exits
        exits = room.exits or {}
        for direction, _ in exits.items():
            if target == direction:
                return CommandResponse(
                    success=True,
                    message=f"You look {direction}. The path continues that way.",
                    data={"direction": direction}
                )
                
        # Check if target is a character in the room
        from app.models import Character
        characters = db.query(Character).join(CharacterLocation).filter(
            CharacterLocation.room_id == room.id,
            Character.name.ilike(f"%{target}%")
        ).all()
        
        if characters:
            char = characters[0]  # Take the first matching character
            return CommandResponse(
                success=True,
                message=f"You see {char.name}, a level {char.level} {char.race} {char.character_class}.",
                data={"character_id": char.id, "character_name": char.name}
            )
            
        # Check if target is an item in the room
        from app.models import Item
        items = db.query(Item).join(RoomItem).filter(
            RoomItem.room_id == room.id,
            Item.name.ilike(f"%{target}%")
        ).all()
        
        if items:
            item = items[0]  # Take the first matching item
            return CommandResponse(
                success=True,
                message=f"You see {item.name}: {item.description}",
                data={"item_id": item.id, "item_name": item.name}
            )
                
        # Target not found
        return CommandResponse(
            success=False,
            message=f"You don't see '{target}' here.",
            errors=["Target not found"]
        )

class InventoryCommand(CommandHandler):
    """Handler for the inventory command"""
    name = "inventory"
    aliases = ["inv", "i"]
    help_text = "Check your character's inventory. Usage: inventory"
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't check inventory
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to check inventory.",
                errors=["No active character"]
            )
            
        # TODO: Implement actual inventory retrieval
        return CommandResponse(
            success=True,
            message="You check your inventory. You're carrying nothing of interest.",
            data={"inventory": []}
        )

class ExamineCommand(CommandHandler):
    """Handler for the examine command"""
    name = "examine"
    aliases = ["exam", "ex", "x"]
    help_text = "Examine an object, character, or feature closely. Usage: examine <target>"
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't examine
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to examine things.",
                errors=["No active character"]
            )
            
        # Must have a target
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="What do you want to examine?",
                errors=["No target specified"]
            )
            
        target = " ".join(ctx.args).lower()
        
        # TODO: Implement object/NPC detailed examination
        return CommandResponse(
            success=True,
            message=f"You examine the {target} closely. This is a placeholder detailed description.",
            data={"target": target}
        )

# Register all command handlers
command_registry.register(HelpCommand)
command_registry.register(LookCommand)
command_registry.register(InventoryCommand)
command_registry.register(ExamineCommand)

# Commented out due to AttributeError with command_registry_commands.command
"""
@command_registry_commands.command(name="look", category="basic", description="Look around to see where you are")
async def look_command(user_id: int, character_id: int, args: Optional[str] = None) -> CommandResult:
    \"\"\"
    Look around the current room to see the description, exits, items, and other characters.
    
    Usage:
      look           - Look at the current room
      look [item]    - Look at a specific item in the room
      look [exit]    - Look at a specific exit
    \"\"\"
    try:
        with get_db_context() as db:
            # Get the character's current location
            from app.models import Character, CharacterLocation
            
            # Find character's location
            character_loc = db.query(CharacterLocation).filter(
                CharacterLocation.character_id == character_id
            ).first()
            
            if not character_loc or not character_loc.room_id:
                return CommandResult(
                    success=False,
                    message="You are lost in the void. There is nothing to see."
                )
            
            # If args provided, look at a specific object
            if args:
                return await look_at_target(character_id, character_loc.room_id, args)
            
            # Get the room details
            room = db.query(Room).filter(Room.id == character_loc.room_id).first()
            if not room:
                return CommandResult(
                    success=False,
                    message="The room you're in seems to have vanished from existence!"
                )
                
            # Get area information if available
            area_name = ""
            if room.area_id:
                area = db.query(Area).filter(Area.id == room.area_id).first()
                if area:
                    area_name = f"[{area.name}] "
            
            # Get visible exits
            exits = db.query(Exit).filter(
                Exit.source_room_id == room.id,
                Exit.is_hidden == False
            ).all()
            
            exit_str = ""
            if exits:
                exit_directions = [exit.direction for exit in exits]
                exit_str = f"Exits: {', '.join(exit_directions)}"
            else:
                exit_str = "There are no obvious exits."
            
            # Get items in the room
            items = db.query(Item).filter(
                Item.room_id == room.id,
                Item.is_hidden == False
            ).all()
            
            item_str = ""
            if items:
                item_names = [item.name for item in items]
                item_str = f"You see: {', '.join(item_names)}"
            
            # Get other characters in the room
            other_characters = db.query(Character).join(
                CharacterLocation, CharacterLocation.character_id == Character.id
            ).filter(
                CharacterLocation.room_id == room.id,
                Character.id != character_id
            ).all()
            
            character_str = ""
            if other_characters:
                character_names = [char.name for char in other_characters]
                character_str = f"Others here: {', '.join(character_names)}"
            
            # Compile the complete room description
            room_desc = f"{area_name}{room.name}\n\n{room.description}\n\n{exit_str}"
            
            if item_str:
                room_desc += f"\n\n{item_str}"
                
            if character_str:
                room_desc += f"\n\n{character_str}"
            
            return CommandResult(
                success=True,
                message=room_desc
            )
    
    except Exception as e:
        return CommandResult(
            success=False,
            message=f"Error examining surroundings: {str(e)}"
        )


async def look_at_target(character_id: int, room_id: int, target: str) -> CommandResult:
    \"\"\"Look at a specific item, exit, or character in the room\"\"\"
    try:
        target = target.lower().strip()
        with get_db_context() as db:
            # Check if it's an exit
            exits = db.query(Exit).filter(
                Exit.source_room_id == room_id,
                Exit.is_hidden == False
            ).all()
            
            for exit in exits:
                if exit.direction.lower() == target or (exit.name and exit.name.lower() == target):
                    # Get the destination room
                    dest_room = db.query(Room).filter(Room.id == exit.destination_room_id).first()
                    if dest_room:
                        return CommandResult(
                            success=True,
                            message=f"{exit.name.capitalize() if exit.name else exit.direction.capitalize()}: "
                                    f"{exit.description if exit.description else 'A path leading to ' + dest_room.name}"
                        )
            
            # Check if it's an item
            items = db.query(Item).filter(
                Item.room_id == room_id,
                Item.is_hidden == False
            ).all()
            
            for item in items:
                if item.name.lower() == target:
                    return CommandResult(
                        success=True,
                        message=f"{item.name}: {item.description}"
                    )
            
            # Check if it's another character
            from app.models import Character, CharacterLocation
            other_characters = db.query(Character).join(
                CharacterLocation, CharacterLocation.character_id == Character.id
            ).filter(
                CharacterLocation.room_id == room_id,
                Character.id != character_id
            ).all()
            
            for character in other_characters:
                if character.name.lower() == target:
                    return CommandResult(
                        success=True,
                        message=f"You see {character.name}, a level {character.level} {character.race} {character.character_class}."
                    )
            
            # If we get here, the target wasn't found
            return CommandResult(
                success=False,
                message=f"You don't see any '{target}' here."
            )
            
    except Exception as e:
        return CommandResult(
            success=False,
            message=f"Error examining {target}: {str(e)}"
        )
""" 