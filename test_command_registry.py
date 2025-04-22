import logging
import sys
from app.commands.registry import command_registry

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_commands():
    """Test the command registry to make sure all commands are properly registered"""
    
    # List all available commands
    commands = command_registry.get_command_list()
    command_names = [cmd.name for cmd in commands]
    
    print(f"Found {len(commands)} registered commands:")
    for cmd in sorted(commands, key=lambda c: c.name):
        aliases = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
        print(f"- {cmd.name}{aliases}")
    
    # Check for specific important commands
    important_commands = ["look", "debug", "help", "create"]
    missing_commands = []
    
    for cmd_name in important_commands:
        if cmd_name not in command_names:
            missing_commands.append(cmd_name)
    
    if missing_commands:
        print(f"\nWARNING: Missing important commands: {', '.join(missing_commands)}")
        return False
    else:
        print("\nAll important commands are registered correctly.")
        
    # Try to get the look command specifically
    look_handler = command_registry.get_handler("look")
    if look_handler:
        print(f"\nLook command details:")
        print(f"  Name: {look_handler.name}")
        print(f"  Aliases: {look_handler.aliases}")
        print(f"  Help text: {look_handler.help_text}")
    else:
        print("\nERROR: Look command could not be retrieved from registry!")
        return False
        
    # Try to get the debug command specifically
    debug_handler = command_registry.get_handler("debug")
    if debug_handler:
        print(f"\nDebug command details:")
        print(f"  Name: {debug_handler.name}")
        print(f"  Aliases: {debug_handler.aliases}")
        print(f"  Help text: {debug_handler.help_text}")
    else:
        print("\nERROR: Debug command could not be retrieved from registry!")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing command registry...\n")
    success = check_commands()
    
    if success:
        print("\nCommand registry test PASSED")
        sys.exit(0)
    else:
        print("\nCommand registry test FAILED")
        sys.exit(1) 