from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session

from app.commands.base import CommandHandler, CommandContext, CommandResponse
from app.commands.registry import command_registry
from app.models import CharacterLocation, Room, NPC, RoomNPC, Character

logger = logging.getLogger(__name__)

class SayCommand(CommandHandler):
    """Handler for the say command"""
    name = "say"
    aliases = ["\"", "'"]
    help_text = "Say something to everyone in the room. Usage: say <message>"
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't speak
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to speak.",
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
            
        # Check if a message was specified
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="What do you want to say?",
                errors=["No message specified"]
            )
            
        # Get character's current location
        from app.commands.movement_commands import get_character_location
        location = await get_character_location(db, ctx.character.id)
        
        if not location or not location.room_id:
            return CommandResponse(
                success=False,
                message="You are not in a room.",
                errors=["No location found"]
            )
            
        # Get the message
        message = " ".join(ctx.args)
        
        # Check for NPC responses
        npcs = db.query(NPC).join(RoomNPC).filter(
            RoomNPC.room_id == location.room_id
        ).all()
        
        npc_responses = []
        for npc in npcs:
            # Check if NPC has dialogues
            if npc.dialogs and isinstance(npc.dialogs, dict):
                # Look for keywords in the message
                for keyword, response in npc.dialogs.items():
                    if keyword.lower() in message.lower():
                        npc_responses.append(f"{npc.name} says: \"{response}\"")
                        break
        
        # Format the say message
        say_message = f"You say: \"{message}\""
        if npc_responses:
            say_message += "\n\n" + "\n".join(npc_responses)
        
        # TODO: In a real multiplayer environment, broadcast to other players in the room
        
        return CommandResponse(
            success=True,
            message=say_message,
            data={"message": message, "npc_responses": npc_responses}
        )

class EmoteCommand(CommandHandler):
    """Handler for the emote command"""
    name = "emote"
    aliases = ["em", "me", ":"]
    help_text = "Perform an emote/action. Usage: emote <action>"
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't emote
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to perform actions.",
                errors=["No active character"]
            )
            
        # Check if an action was specified
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="What do you want to do?",
                errors=["No action specified"]
            )
            
        # Get the action text
        action = " ".join(ctx.args)
        
        # Format the emote message
        emote_message = f"* {ctx.character.name} {action}"
        
        # TODO: In a real multiplayer environment, broadcast to other players in the room
        
        return CommandResponse(
            success=True,
            message=emote_message,
            data={"action": action}
        )

class TalkCommand(CommandHandler):
    """Handler for talking to NPCs"""
    name = "talk"
    aliases = ["speak", "ask"]
    help_text = "Talk to an NPC. Usage: talk <npc> [about <topic>]"
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't talk
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to talk to NPCs.",
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
            
        # Check if an NPC was specified
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="Who do you want to talk to?",
                errors=["No NPC specified"]
            )
            
        # Get character's current location
        from app.commands.movement_commands import get_character_location
        location = await get_character_location(db, ctx.character.id)
        
        if not location or not location.room_id:
            return CommandResponse(
                success=False,
                message="You are not in a room.",
                errors=["No location found"]
            )
            
        # Parse the target NPC and topic
        target_npc = ctx.args[0].lower()
        topic = None
        
        # Check if there's a topic specified (format: talk npc about topic)
        if len(ctx.args) > 2 and ctx.args[1].lower() == "about":
            topic = " ".join(ctx.args[2:]).lower()
        
        # Find matching NPCs in the room
        npcs = db.query(NPC).join(RoomNPC).filter(
            RoomNPC.room_id == location.room_id,
            NPC.name.ilike(f"%{target_npc}%")
        ).all()
        
        if not npcs:
            return CommandResponse(
                success=False,
                message=f"You don't see anyone named '{target_npc}' here.",
                errors=["NPC not found"]
            )
            
        # Get the first matching NPC
        npc = npcs[0]
        
        # Get the NPC's response based on topic
        if topic and npc.dialogs and isinstance(npc.dialogs, dict):
            # Look for exact topic match
            if topic in npc.dialogs:
                response = npc.dialogs[topic]
            else:
                # Look for partial matches
                for key, value in npc.dialogs.items():
                    if key in topic or topic in key:
                        response = value
                        break
                else:
                    # Default response if no match found
                    response = npc.dialogs.get("greeting", "The NPC doesn't seem interested in that topic.")
        else:
            # Default to greeting if no topic specified
            response = npc.dialogs.get("greeting", "The NPC nods at you.") if npc.dialogs else "The NPC nods at you."
        
        return CommandResponse(
            success=True,
            message=f"{npc.name} says: \"{response}\"",
            data={"npc_id": npc.id, "npc_name": npc.name, "topic": topic, "response": response}
        )

# Register social commands
command_registry.register(SayCommand)
command_registry.register(EmoteCommand)
command_registry.register(TalkCommand) 