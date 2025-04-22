import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_websocket_indentation():
    """Fix a critical indentation issue in the WebSocket command loop"""
    try:
        # Find the websocket manager implementation
        websocket_file = os.path.join("app", "websockets", "__init__.py")
        
        # Check if file exists
        if not os.path.exists(websocket_file):
            logger.error(f"WebSocket file not found: {websocket_file}")
            return False
            
        # Read the current file
        with open(websocket_file, "r") as f:
            content = f.readlines()
        
        # Look for the indentation issue in the command loop section
        fixed_content = []
        in_command_section = False
        found_issue = False
        
        for line in content:
            # Detect the command section with the refresh character information on each command
            if "# Refresh the character information on each command" in line:
                in_command_section = True
                # This line is indented too far - it's inside the 'if not command_text' block
                # which means it never executes for valid commands
                fixed_content.append(line.replace("            # Refresh", "        # Refresh"))
                found_issue = True
                continue
                
            # Fix all indentation in this section until we reach the command execution
            if in_command_section and "# Execute command" in line:
                in_command_section = False
                fixed_content.append(line)
                continue
                
            # Fix indentation for all lines in the problematic section
            if in_command_section and line.startswith("            "):
                # Reduce indentation by one level (4 spaces)
                fixed_content.append(line.replace("            ", "        ", 1))
                found_issue = True
            else:
                fixed_content.append(line)
        
        if not found_issue:
            logger.info("No indentation issue found or already fixed")
            return False
            
        # Write fixed content back to file
        with open(websocket_file, "w") as f:
            f.writelines(fixed_content)
            
        logger.info("Fixed WebSocket indentation issue")
        return True
            
    except Exception as e:
        logger.error(f"Error fixing WebSocket indentation: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("Attempting to fix WebSocket command processing issue...")
    result = fix_websocket_indentation()
    
    if result:
        print("SUCCESS: Fixed indentation issue in WebSocket command processing")
        print("Please restart the server for changes to take effect")
        sys.exit(0)
    else:
        print("FAILED: Could not fix the WebSocket command processing issue")
        print("Please contact support for assistance")
        sys.exit(1) 