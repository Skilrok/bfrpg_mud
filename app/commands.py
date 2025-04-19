"""
Command System for BFRPG MUD

This module implements a decorator-based command registry and parser system
to handle game commands. Commands are registered with metadata like:
- name: The primary name of the command
- aliases: Alternative names for the command
- help_text: Description of what the command does
- syntax: Usage syntax for the command
- category: Group the command belongs to (e.g., movement, inventory)
- permissions: Required permissions to use the command
"""

from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Any, Union
from pydantic import BaseModel
import re
import inspect
import logging
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)


class CommandCategory(str, Enum):
    """Categories for organizing commands"""
    MOVEMENT = "movement"
    INVENTORY = "inventory"
    INTERACTION = "interaction"
    COMBAT = "combat"
    COMMUNICATION = "communication"
    INFORMATION = "information"
    ADMIN = "admin"
    SYSTEM = "system"


class CommandRequirement(str, Enum):
    """Special requirements for commands"""
    NONE = "none"
    LOGGED_IN = "logged_in"
    IN_ROOM = "in_room"
    HAS_CHARACTER = "has_character"
    ADMIN = "admin"


class CommandResult(BaseModel):
    """Structured result of a command execution"""
    success: bool = True
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CommandRegistry:
    """Registry for game commands"""
    
    def __init__(self):
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.aliases: Dict[str, str] = {}
    
    def register(
        self,
        name: str,
        handler: Callable,
        aliases: Optional[List[str]] = None,
        help_text: str = "No help available.",
        syntax: str = "",
        category: CommandCategory = CommandCategory.SYSTEM,
        requirements: List[CommandRequirement] = [CommandRequirement.LOGGED_IN],
    ) -> None:
        """Register a command with the system"""
        if name in self.commands:
            logger.warning(f"Overwriting existing command: {name}")
        
        cmd_info = {
            "name": name,
            "handler": handler,
            "aliases": aliases or [],
            "help_text": help_text,
            "syntax": syntax,
            "category": category,
            "requirements": requirements,
        }
        
        self.commands[name] = cmd_info
        
        # Register aliases
        if aliases:
            for alias in aliases:
                if alias in self.aliases or alias in self.commands:
                    logger.warning(f"Alias '{alias}' already exists, skipping")
                    continue
                self.aliases[alias] = name
    
    def get_command(self, cmd_name: str) -> Optional[Dict[str, Any]]:
        """Get a command by name or alias"""
        if cmd_name in self.commands:
            return self.commands[cmd_name]
        
        if cmd_name in self.aliases:
            return self.commands[self.aliases[cmd_name]]
        
        return None
    
    def list_commands(self, category: Optional[CommandCategory] = None) -> List[Dict[str, Any]]:
        """List all registered commands, optionally filtered by category"""
        if category:
            return [cmd for cmd in self.commands.values() if cmd["category"] == category]
        return list(self.commands.values())


# Global command registry
command_registry = CommandRegistry()


def command(
    name: str,
    aliases: Optional[List[str]] = None,
    help_text: str = "No help available.",
    syntax: str = "",
    category: CommandCategory = CommandCategory.SYSTEM,
    requirements: List[CommandRequirement] = [CommandRequirement.LOGGED_IN],
) -> Callable:
    """Decorator to register a function as a game command"""
    def decorator(func: Callable) -> Callable:
        command_registry.register(
            name=name,
            handler=func,
            aliases=aliases,
            help_text=help_text,
            syntax=syntax,
            category=category,
            requirements=requirements,
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class CommandParser:
    """Parser for command input"""
    
    @staticmethod
    def parse(command_string: str) -> tuple[str, List[str]]:
        """
        Parse a command string into command name and arguments
        
        Args:
            command_string: The raw command string from the user
            
        Returns:
            Tuple of (command_name, args)
        """
        parts = command_string.strip().split()
        if not parts:
            return ("", [])
        
        cmd_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return (cmd_name, args)
    
    @staticmethod
    def parse_with_quotes(command_string: str) -> tuple[str, List[str]]:
        """
        Parse a command string, preserving quoted arguments
        
        Args:
            command_string: The raw command string from the user
            
        Returns:
            Tuple of (command_name, args)
        """
        # Match the command name as everything up to the first whitespace
        # Then match arguments, handling quoted strings as single arguments
        pattern = r'^(\S+)(?:\s+(.*))?$'
        match = re.match(pattern, command_string.strip())
        
        if not match:
            return ("", [])
        
        cmd_name = match.group(1).lower()
        args_str = match.group(2) or ""
        
        # Parse arguments, respecting quotes
        args = []
        if args_str:
            # This regex will match:
            # - Quoted strings (preserving content inside quotes)
            # - Non-quoted words (separated by whitespace)
            arg_pattern = r'"([^"]*)"|\S+'
            args = [
                m.group(1) if m.group(1) is not None else m.group(0)
                for m in re.finditer(arg_pattern, args_str)
            ]
        
        return (cmd_name, args)


class CommandExecutor:
    """Executes commands from the registry after checking requirements"""
    
    @staticmethod
    def check_requirements(requirements: List[CommandRequirement], context: Dict[str, Any]) -> tuple[bool, str]:
        """
        Check if all requirements for a command are met
        
        Args:
            requirements: List of command requirements
            context: Information about the current user/character/state
            
        Returns:
            Tuple of (requirements_met, error_message)
        """
        if CommandRequirement.NONE in requirements:
            return (True, "")
        
        if CommandRequirement.LOGGED_IN in requirements and not context.get("user_id"):
            return (False, "You must be logged in to use this command.")
        
        if CommandRequirement.HAS_CHARACTER in requirements and not context.get("character_id"):
            return (False, "You need a character to use this command.")
        
        if CommandRequirement.IN_ROOM in requirements and not context.get("room_id"):
            return (False, "You need to be in a room to use this command.")
        
        if CommandRequirement.ADMIN in requirements and not context.get("is_admin", False):
            return (False, "This command requires administrator privileges.")
        
        return (True, "")
    
    @staticmethod
    async def execute(
        cmd_name: str,
        args: List[str],
        context: Dict[str, Any]
    ) -> CommandResult:
        """
        Execute a command with the given arguments and context
        
        Args:
            cmd_name: Name of the command to execute
            args: List of arguments for the command
            context: Information about the current user/character/state
            
        Returns:
            CommandResult object with the outcome
        """
        # Find the command
        cmd_info = command_registry.get_command(cmd_name)
        if not cmd_info:
            return CommandResult(
                success=False,
                message=f"Unknown command: {cmd_name}",
                error="COMMAND_NOT_FOUND"
            )
        
        # Check requirements
        requirements_met, error_message = CommandExecutor.check_requirements(
            cmd_info["requirements"], context
        )
        
        if not requirements_met:
            return CommandResult(
                success=False,
                message=error_message,
                error="REQUIREMENTS_NOT_MET"
            )
        
        # Execute the command
        handler = cmd_info["handler"]
        try:
            # Check if the handler is an async function
            if inspect.iscoroutinefunction(handler):
                result = await handler(args, context)
            else:
                result = handler(args, context)
            
            # If the handler returned a string, wrap it in a CommandResult
            if isinstance(result, str):
                return CommandResult(success=True, message=result)
            # If it already returned a CommandResult, use that
            elif isinstance(result, CommandResult):
                return result
            # For any other return type, convert to a generic success result
            else:
                return CommandResult(
                    success=True,
                    message="Command executed successfully.",
                    data={"result": result} if result is not None else None
                )
                
        except Exception as e:
            logger.exception(f"Error executing command {cmd_name}: {str(e)}")
            return CommandResult(
                success=False,
                message=f"Error executing command: {str(e)}",
                error="EXECUTION_ERROR"
            ) 