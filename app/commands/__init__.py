from .base import CommandResult
from .parser import CommandParser, parse_command
from .registry import CommandCategory, CommandRegistry, CommandRequirement, command

# Initialize the global command registry
registry = CommandRegistry()

# Import all commands to register them
from .basic_commands import *
from .character_commands import *
from .look_commands import *
from .movement_commands import *
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
]

# Import debug command
import app.commands.debug_command
