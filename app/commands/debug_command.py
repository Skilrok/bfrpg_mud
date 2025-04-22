import logging
from datetime import datetime
from typing import List, Optional
from app.commands.base import CommandContext, CommandHandler, CommandResponse
from app.commands.registry import command_registry

logger = logging.getLogger(__name__)

class DebugCommand(CommandHandler):
    """A simple debug command for testing"""
    
    name = "debug"
    aliases = ["dbg", "test"]
    help_text = "A debug command to test the command system"
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        logger.info(f"Debug command executed with args: {ctx.args}")
        
        # Log context data
        logger.info(f"Context data: {ctx.data}")
        
        # Check if character exists
        if ctx.character:
            logger.info(f"Character: {ctx.character.name} (ID: {ctx.character.id})")
        else:
            logger.warning("No character in context")
            
        # Enhanced debug command
        # Return a more detailed response with useful debugging info
        room_id = None
        room_name = None
        if ctx.data and 'db' in ctx.data and ctx.character:
            db = ctx.data['db']
            from app.commands.movement_commands import get_character_location
            try:
                location = await get_character_location(db, ctx.character.id)
                if location and location.room_id:
                    room_id = location.room_id
                    from app.models import Room
                    room = db.query(Room).filter(Room.id == room_id).first()
                    if room:
                        room_name = room.name
            except Exception as e:
                logger.error(f"Error getting location: {str(e)}")
        
        return CommandResponse(
            success=True,
            message=f"Debug command executed successfully at {datetime.now().strftime('%H:%M:%S')}! The command system is working.\n" +
                    f"Character: {ctx.character.name if ctx.character else 'None'}\n" +
                    f"Location: {room_name or 'Unknown'} (ID: {room_id or 'Unknown'})\n" +
                    f"Args: {ctx.args}\n" +
                    f"WebSocket is operational.",
            data={
                "args": ctx.args,
                "character_id": ctx.character.id if ctx.character else None,
                "character_name": ctx.character.name if ctx.character else None,
                "room_id": room_id,
                "room_name": room_name,
                "timestamp": datetime.now().isoformat()
            }
        )

# Register the command
command_registry.register(DebugCommand)
logger.info("Debug command registered")
