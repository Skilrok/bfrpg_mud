from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session

from app.commands.base import CommandHandler, CommandContext, CommandResponse
from app.commands.registry import command_registry

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
            # Get exits description
            exits = room.exits or {}
            exits_desc = "Exits: " + (", ".join(exits.keys()) if exits else "none")
            
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
            
            return CommandResponse(
                success=True,
                message=full_desc,
                data={
                    "room_id": room.id,
                    "room_name": room.name,
                    "exits": list(exits.keys()),
                    "characters": [c.character_id for c in other_characters] if other_characters else [],
                    "items": [i.item_id for i in items] if items else []
                }
            )
        
        # Look at a specific target
        target = " ".join(ctx.args).lower()
        
        # Check if target is an exit
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