"""
Basic Command Handlers - STUB FILE FOR TESTS

This is a stub file to resolve import dependencies for tests.
"""

from typing import List, Dict, Any
from .commands import (
    command, 
    CommandCategory, 
    CommandRequirement,
    CommandResult
)

# Stub functions for testing
def cmd_help(args: List[str], context: Dict[str, Any]) -> CommandResult:
    """Stub help command"""
    return CommandResult(success=True, message="Help info")

def cmd_look(args: List[str], context: Dict[str, Any]) -> CommandResult:
    """Stub look command"""
    return CommandResult(success=True, message="You look around")

def cmd_examine(args: List[str], context: Dict[str, Any]) -> CommandResult:
    """Stub examine command"""
    if not args:
        return CommandResult(success=False, message="Examine what?")
    return CommandResult(success=True, message=f"You examine the {args[0]}")

def cmd_inventory(args: List[str], context: Dict[str, Any]) -> CommandResult:
    """Stub inventory command"""
    return CommandResult(success=True, message="Your inventory is empty") 