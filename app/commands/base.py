from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.models.character import Character
from app.models.user import User
from enum import Enum, auto

class CommandCategory(str, Enum):
    """Categories for organizing commands"""
    BASIC = "basic"
    INFORMATION = "information"
    MOVEMENT = "movement"
    COMBAT = "combat"
    SOCIAL = "social"
    COMMUNICATION = "communication"
    INVENTORY = "inventory"
    ADMIN = "admin"
    MISC = "misc"

class CommandRequirement(str, Enum):
    """Requirements for executing commands"""
    NONE = "none"  # No special requirements
    AUTHENTICATED = "authenticated"  # User must be logged in
    LOGGED_IN = "logged_in"  # Alias for AUTHENTICATED
    CHARACTER = "character"  # User must have a character
    HAS_CHARACTER = "has_character"  # Alias for CHARACTER
    IN_ROOM = "in_room"  # Character must be in a room
    ADMIN = "admin"  # User must have admin privileges

class CommandResult(BaseModel):
    """Result of a command execution"""
    success: bool
    message: str
    data: Dict[str, Any] = {}

class CommandContext(BaseModel):
    """
    Context for command execution, containing information about
    the current state at the time of command invocation.
    """
    user: Optional[User] = None
    character: Optional[Character] = None
    room_id: Optional[int] = None
    session_id: Optional[str] = None
    
    # Original input
    raw_input: str = ""
    
    # Data passed from the command parser
    command: str = ""
    args: List[str] = []
    
    # Additional context data
    data: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True

class CommandResponse(BaseModel):
    """
    Structure for command execution responses
    """
    success: bool = True
    message: str = ""
    errors: List[str] = []
    data: Dict[str, Any] = {}
    
    def add_error(self, error: str) -> None:
        """Add an error message and set success to False"""
        self.errors.append(error)
        self.success = False

class CommandHandler:
    """
    Base class for command handlers
    """
    name: str = ""
    aliases: List[str] = []
    help_text: str = ""
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        """
        Execute the command with the given context
        
        Args:
            ctx: The command context
            
        Returns:
            CommandResponse with the result of execution
        """
        raise NotImplementedError("Command handlers must implement execute()")
    
    def get_help(self) -> str:
        """
        Get help text for this command
        
        Returns:
            Formatted help text
        """
        return self.help_text or f"No help available for '{self.name}'" 