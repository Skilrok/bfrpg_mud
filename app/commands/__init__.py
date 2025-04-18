from .registry import CommandRegistry, CommandCategory, CommandRequirement, command
from .parser import CommandParser, parse_command
from .base import CommandResult

# Initialize the global command registry
registry = CommandRegistry()

# Import all commands to register them
from .basic_commands import *
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
    "CommandResult"
] 