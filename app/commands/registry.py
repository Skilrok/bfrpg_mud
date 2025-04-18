from typing import Dict, List, Type, Optional, Set, Callable, Any
import logging
from app.commands.base import CommandHandler, CommandContext, CommandResponse, CommandCategory, CommandRequirement
import functools

logger = logging.getLogger(__name__)

class CommandRegistry:
    """
    Registry for command handlers.
    Manages registration of commands and dispatching input to the appropriate handler.
    """
    
    def __init__(self):
        self._commands: Dict[str, CommandHandler] = {}
        self._command_aliases: Dict[str, str] = {}
        
    def register(self, handler_class: Type[CommandHandler]) -> None:
        """
        Register a command handler
        
        Args:
            handler_class: The command handler class to register
        """
        handler = handler_class()
        
        if not handler.name:
            logger.error(f"Cannot register command with empty name: {handler_class.__name__}")
            return
            
        # Register primary command name
        if handler.name in self._commands:
            logger.warning(f"Command '{handler.name}' already registered, overwriting")
            
        self._commands[handler.name] = handler
        
        # Register aliases
        for alias in handler.aliases:
            if alias in self._command_aliases:
                logger.warning(f"Command alias '{alias}' already registered, overwriting")
            self._command_aliases[alias] = handler.name
            
        logger.info(f"Registered command '{handler.name}' with aliases: {handler.aliases}")
        
    def get_handler(self, command_name: str) -> Optional[CommandHandler]:
        """
        Get a command handler by name or alias
        
        Args:
            command_name: The command name or alias
            
        Returns:
            The command handler, or None if not found
        """
        # Check if it's a direct command
        if command_name in self._commands:
            return self._commands[command_name]
            
        # Check if it's an alias
        if command_name in self._command_aliases:
            return self._commands[self._command_aliases[command_name]]
            
        return None
        
    async def execute_command(self, ctx: CommandContext) -> CommandResponse:
        """
        Execute a command from context
        
        Args:
            ctx: The command context with command and args
            
        Returns:
            CommandResponse with the result
        """
        if not ctx.command:
            return CommandResponse(
                success=False,
                message="No command specified",
                errors=["Empty command"]
            )
            
        handler = self.get_handler(ctx.command.lower())
        
        if not handler:
            return CommandResponse(
                success=False,
                message=f"Unknown command: {ctx.command}",
                errors=[f"Command '{ctx.command}' not found"]
            )
            
        try:
            return await handler.execute(ctx)
        except Exception as e:
            logger.exception(f"Error executing command '{ctx.command}': {e}")
            return CommandResponse(
                success=False,
                message="An error occurred while executing the command",
                errors=[str(e)]
            )
            
    def get_available_commands(self) -> Set[str]:
        """
        Get a set of all available command names
        
        Returns:
            Set of command names
        """
        return set(self._commands.keys())
        
    def get_command_list(self) -> List[CommandHandler]:
        """
        Get a list of all command handlers
        
        Returns:
            List of command handlers
        """
        return list(self._commands.values())

# Global command registry instance
command_registry = CommandRegistry()

def command(name: str, aliases: List[str] = None, help_text: str = "", 
            category: CommandCategory = CommandCategory.MISC,
            syntax: str = "",
            requirements: List[CommandRequirement] = None):
    """
    Decorator for registering command functions.
    
    Args:
        name: Primary command name
        aliases: Alternative command names
        help_text: Help text for the command
        category: Command category for organization
        syntax: Command syntax help
        requirements: List of requirements for executing this command
        
    Returns:
        Decorator function
    """
    if aliases is None:
        aliases = []
    if requirements is None:
        requirements = [CommandRequirement.NONE]
        
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
            
        # Create a dynamic CommandHandler class
        handler_name = f"{func.__name__.title()}CommandHandler"
        handler_class = type(handler_name, (CommandHandler,), {
            "name": name,
            "aliases": aliases,
            "help_text": help_text,
            "category": category,
            "requirements": requirements,
            "syntax": syntax,
            "execute": lambda self, ctx: func(ctx)
        })
        
        # Register the command
        command_registry.register(handler_class)
        
        return wrapper
    return decorator 