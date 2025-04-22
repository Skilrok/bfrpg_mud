import logging
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.commands import registry as command_registry_commands
from app.commands.base import CommandContext, CommandHandler, CommandResponse
from app.commands.registry import command_registry
from app.database import get_db_context
from app.models import Area, Exit, Item, Room, User

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
                    data={"command": handler.name, "help_text": handler.get_help()},
                )
            else:
                return CommandResponse(
                    success=False,
                    message=f"No help available: Command '{cmd_name}' not found.",
                    errors=[f"Command '{cmd_name}' not found"],
                )

        # Show general help (list of commands)
        commands = command_registry.get_command_list()
        commands_by_name = sorted(commands, key=lambda c: c.name)

        # Format command list
        help_text = "Available commands:\n"
        for cmd in commands_by_name:
            aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_text += f"- {cmd.name}{aliases}: {cmd.help_text.split('.')[0]}.\n"

        help_text += (
            "\nFor more information about a specific command, type: help <command>"
        )

        return CommandResponse(
            success=True,
            message=help_text,
            data={
                "commands": [
                    {"name": cmd.name, "help": cmd.help_text}
                    for cmd in commands_by_name
                ]
            },
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
                errors=["No active character"],
            )

        # TODO: Implement actual inventory retrieval
        return CommandResponse(
            success=True,
            message="You check your inventory. You're carrying nothing of interest.",
            data={"inventory": []},
        )


class ExamineCommand(CommandHandler):
    """Handler for the examine command"""

    name = "examine"
    aliases = ["exam", "ex", "x"]
    help_text = (
        "Examine an object, character, or feature closely. Usage: examine <target>"
    )

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # If no character is active, we can't examine
        if not ctx.character:
            return CommandResponse(
                success=False,
                message="You need an active character to examine things.",
                errors=["No active character"],
            )

        # Must have a target
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="What do you want to examine?",
                errors=["No target specified"],
            )

        target = " ".join(ctx.args).lower()

        # TODO: Implement object/NPC detailed examination
        return CommandResponse(
            success=True,
            message=f"You examine the {target} closely. This is a placeholder detailed description.",
            data={"target": target},
        )


# Register all command handlers
command_registry.register(HelpCommand)
command_registry.register(InventoryCommand)
command_registry.register(ExamineCommand)

# LookCommand removed from this file to avoid duplicate registration
# The implementation in look_commands.py will be used instead
