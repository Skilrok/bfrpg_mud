from typing import List, Tuple, Dict, Any, Optional
import shlex
import re

class CommandParser:
    """
    Parser for command input from users.
    Handles splitting commands and arguments, handling quoted arguments, etc.
    """
    
    @staticmethod
    def parse(text: str) -> Tuple[str, List[str]]:
        """
        Parse command text into command and arguments
        
        Args:
            text: Raw command text
            
        Returns:
            Tuple of (command, args)
        """
        return parse_command(text)
    
    @staticmethod
    def extract_target(command: str, args: List[str]) -> Optional[str]:
        """
        Extract a target from command and arguments
        
        Args:
            command: Command name
            args: Command arguments
            
        Returns:
            Target string or None
        """
        return extract_target(command, args)
    
    @staticmethod
    def parse_direction(text: str) -> Optional[str]:
        """
        Parse a direction from text
        
        Args:
            text: Direction text
            
        Returns:
            Standardized direction
        """
        return parse_direction(text)

def parse_command(text: str) -> Tuple[str, List[str]]:
    """
    Parse a command string into a command name and list of arguments.
    
    Args:
        text: The raw command text from the user
        
    Returns:
        Tuple containing (command_name, list_of_arguments)
    """
    if not text or not text.strip():
        return ("", [])
    
    # Strip leading/trailing whitespace but don't lowercase yet
    text = text.strip()
    
    try:
        # Use shlex to handle quoted arguments properly
        parts = shlex.split(text)
    except ValueError:
        # If there's an error with quotes, fall back to simple splitting
        parts = text.split()
    
    if not parts:
        return ("", [])
    
    # Only lowercase the command, preserve case for arguments
    command = parts[0].lower()
    args = parts[1:] if len(parts) > 1 else []
    
    return (command, args)

def parse_direction(text: str) -> Optional[str]:
    """
    Parse a direction from text, handling various forms
    
    Args:
        text: Direction text to parse
        
    Returns:
        Standardized direction or None
    """
    directions = {
        "north": ["n", "north"],
        "south": ["s", "south"],
        "east": ["e", "east"],
        "west": ["w", "west"],
        "northeast": ["ne", "northeast"],
        "northwest": ["nw", "northwest"],
        "southeast": ["se", "southeast"],
        "southwest": ["sw", "southwest"],
        "up": ["u", "up", "climb"],
        "down": ["d", "down", "descend"]
    }
    
    text = text.lower().strip()
    
    for standard, variants in directions.items():
        if text in variants:
            return standard
            
    return None 

def extract_target(command: str, args: List[str]) -> Optional[str]:
    """
    Extract a potential target from command arguments
    
    Args:
        command: The command being executed
        args: List of command arguments
        
    Returns:
        Target string or None if no target found
    """
    if not args:
        return None
    
    # Common prepositions that might indicate a target
    prepositions = ["at", "to", "on", "with", "in", "from", "for"]
    
    # Check if any preposition exists in the arguments
    for i, arg in enumerate(args):
        if arg.lower() in prepositions and i + 1 < len(args):
            # Return everything after the preposition as the target
            return " ".join(args[i+1:])
    
    # If no preposition found, the entire args could be the target
    return " ".join(args) 