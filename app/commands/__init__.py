from .base import CommandResult
from .parser import CommandParser, parse_command
from .registry import CommandCategory, CommandRegistry, CommandRequirement, command

# Initialize the global command registry
registry = CommandRegistry()

# Import all commands to register them
from .basic_commands import (
    EquipCommand,
    ExamineCommand,
    HelpCommand,
    InventoryCommand,
    StatsCommand,
    UnequipCommand,
)
from .character_commands import CreateCharacterCommand
from .look_commands import LookCommand
from .movement_commands import (
    DownCommand,
    EastCommand,
    GoCommand,
    NorthCommand,
    SouthCommand,
    UpCommand,
    WestCommand,
)
from .social_commands import *

__all__ = [
    "registry",
    "parse_command",
    "CommandParser",
    "CommandRegistry",
    "CommandCategory",
    "CommandRequirement",
    "command",
    "CommandResult",
    "CreateCharacterCommand",
    "HelpCommand",
    "InventoryCommand",
    "ExamineCommand",
    "EquipCommand",
    "UnequipCommand",
    "StatsCommand",
    "LookCommand",
    "NorthCommand",
    "SouthCommand",
    "EastCommand",
    "WestCommand",
    "UpCommand",
    "DownCommand",
    "GoCommand",
]

# Import debug command
import app.commands.debug_command
