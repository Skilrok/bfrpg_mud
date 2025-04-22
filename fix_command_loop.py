import logging
import os
import re
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def replace_command_loop():
    """Replace the entire command loop with a corrected version"""
    try:
        # Find the websocket manager implementation
        websocket_file = os.path.join("app", "websockets", "__init__.py")

        # Check if file exists
        if not os.path.exists(websocket_file):
            logger.error(f"WebSocket file not found: {websocket_file}")
            return False

        # Read the current file
        with open(websocket_file, "r") as f:
            content = f.read()

        # Find the main command processing loop
        command_loop_pattern = re.compile(
            r'# Main command processing loop.*?while True:.*?# Wait for commands.*?data = await websocket\.receive_json\(\).*?command_text = data\.get\("command", ""\)\.strip\(\).*?if not command_text:.*?await websocket\.send_json\(.*?continue',
            re.DOTALL,
        )

        match = command_loop_pattern.search(content)
        if not match:
            logger.error("Could not find command loop pattern in WebSocket file")
            return False

        old_loop = match.group(0)

        # Create a replacement command loop with correct structure and indentation
        new_loop = """                    # Main command processing loop
                    while True:
                        # Wait for commands
                        try:
                            data = await websocket.receive_json()
                            command_text = data.get("command", "").strip()

                            logger.info(f"Received command: {command_text}")

                            if not command_text:
                                await websocket.send_json(
                                    {"success": False, "message": "Empty command"}
                                )
                                continue

                            # Refresh character object on each command
                            if character_id:
                                character = (
                                    db.query(Character)
                                    .filter(
                                        Character.id == character_id,
                                        Character.user_id == user_id,
                                    )
                                    .first()
                                )

                                if not character:
                                    await websocket.send_json(
                                        {
                                            "success": False,
                                            "message": "Character not found or not owned by user. Please select a character.",
                                        }
                                    )
                                    continue

                            # Get character location if it exists
                            character_location = None
                            room_id = None
                            if character_id:
                                character_location = (
                                    db.query(CharacterLocation)
                                    .filter(CharacterLocation.character_id == character_id)
                                    .first()
                                )

                                if character_location:
                                    room_id = character_location.room_id

                                if not character_location:
                                    # Try to set character location if it doesn't exist
                                    from app.services.character_service import set_character_starting_location
                                    location_success = set_character_starting_location(db, character_id)
                                    if location_success:
                                        # Get the new location
                                        character_location = (
                                            db.query(CharacterLocation)
                                            .filter(CharacterLocation.character_id == character_id)
                                            .first()
                                        )
                                        if character_location:
                                            room_id = character_location.room_id

                                    # Refresh character after location update
                                    if character:
                                        db.refresh(character)

                            # Parse the command
                            from app.commands.parser import parse_command

                            cmd, args = parse_command(command_text)

                            # Log to help debug
                            logger.info(f"Processing command: {cmd}, Args: {args}, Character: {character_id}, Room: {room_id}")

                            # Create command context
                            ctx = CommandContext(
                                user=user,
                                character=character,
                                room_id=room_id,
                                session_id=session_id,
                                raw_input=command_text,
                                command=cmd,
                                args=args,
                                data={
                                    "db": db,
                                    "character_id": character_id  # Explicitly include character_id in data
                                },
                            )

                            # Execute command and send response
                            try:
                                # Execute command
                                response = await command_registry.execute_command(ctx)

                                # Log response for debugging
                                logger.info(f"Command response: success={response.success}, message={response.message[:50] if response.message else 'None'}...")

                                # Prepare response data
                                response_data = {
                                    "success": response.success,
                                    "message": response.message,
                                    "errors": response.errors or [],
                                    "data": response.data or {},
                                    "command": {
                                        "raw": command_text,
                                        "name": cmd,
                                        "args": args
                                    }
                                }

                                # Send response back to client
                                await websocket.send_json(response_data)
                                logger.info(f"Response sent to client for command: {cmd}")
                            except Exception as e:
                                # Log and handle exceptions
                                import traceback
                                logger.error(f"Error executing command {cmd}: {str(e)}")
                                logger.error(traceback.format_exc())

                                # Send error response to client
                                await websocket.send_json({
                                    "success": False,
                                    "message": f"Error executing command: {str(e)}",
                                    "errors": [str(e)],
                                    "command": {
                                        "raw": command_text,
                                        "name": cmd,
                                        "args": args
                                    }
                                })
                        except Exception as e:
                            logger.error(f"Error in command loop: {str(e)}")
                            import traceback
                            logger.error(traceback.format_exc())
                            try:
                                await websocket.send_json({
                                    "success": False,
                                    "message": f"Server error: {str(e)}",
                                    "errors": [str(e)]
                                })
                            except:
                                pass"""

        # Replace the old loop with the new one
        updated_content = content.replace(old_loop, new_loop)

        # Write updated content back to file
        with open(websocket_file, "w") as f:
            f.write(updated_content)

        logger.info("Fixed WebSocket command loop")
        return True

    except Exception as e:
        logger.error(f"Error fixing WebSocket command loop: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("Attempting to fix WebSocket command processing...")
    result = replace_command_loop()

    if result:
        print("SUCCESS: Fixed WebSocket command processing")
        print("Please restart the server for changes to take effect")
        sys.exit(0)
    else:
        print("FAILED: Could not fix the WebSocket command processing")
        print("Please check logs for details")
        sys.exit(1)
