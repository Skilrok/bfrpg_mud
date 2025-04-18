from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CommandRequest(BaseModel):
    """Schema for command request from client"""
    command: str = Field(..., title="Command text", description="The command text to execute")
    character_id: Optional[int] = Field(None, title="Character ID", description="ID of the character executing the command")

class CommandInfo(BaseModel):
    """Information about the executed command"""
    raw: str = Field(..., title="Raw command", description="The raw command text as entered by the user")
    name: str = Field(..., title="Command name", description="The parsed command name")
    args: List[str] = Field(default_factory=list, title="Command arguments", description="Arguments parsed from the command")

class CommandResponse(BaseModel):
    """Schema for command execution response"""
    success: bool = Field(..., title="Success status", description="Whether the command was executed successfully")
    message: str = Field(..., title="Response message", description="The text response to the command")
    errors: List[str] = Field(default_factory=list, title="Errors", description="List of error messages if any")
    data: Dict[str, Any] = Field(default_factory=dict, title="Response data", description="Additional structured data from the command")
    command: CommandInfo = Field(..., title="Command info", description="Information about the executed command") 