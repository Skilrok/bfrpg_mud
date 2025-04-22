import os

def replace_websocket_command_handler():
    """Replace the entire WebSocket command execution code with a correctly indented version"""
    websocket_file = os.path.join("app", "websockets", "__init__.py")
    
    if not os.path.exists(websocket_file):
        print(f"Error: WebSocket file not found: {websocket_file}")
        return False
    
    # Create the correctly indented command handler section
    correct_handler = """                    # Main command processing loop
                    while True:
                        # Wait for commands
                        data = await websocket.receive_json()
                        command_text = data.get("command", "").strip()

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
                                db.refresh(character)

                        # Parse the command
                        from app.commands.parser import parse_command

                        cmd, args = parse_command(command_text)
                        
                        # Log to help debug
                        logger.info(f"Command: {cmd}, Args: {args}, Character: {character_id}, Room: {room_id}")

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

                        # Execute command
                        response = await command_registry.execute_command(ctx)

                        # Send response back to client
                        await websocket.send_json(
                            {
                                "success": response.success,
                                "message": response.message,
                                "errors": response.errors,
                                "data": response.data,
                                "command": {
                                    "raw": command_text,
                                    "name": cmd,
                                    "args": args
                                }
                            }
                        )"""
    
    with open(websocket_file, "r") as f:
        content = f.read()
    
    # Look for the start of the command loop
    start_marker = "                    # Main command processing loop"
    end_marker = "                    db.close()"
    
    start_index = content.find(start_marker)
    end_index = content.find(end_marker)
    
    if start_index == -1 or end_index == -1:
        print("Could not locate the command loop in the file")
        return False
    
    # Replace the problematic section with our corrected version
    new_content = content[:start_index] + correct_handler + "\n\n" + content[end_index:]
    
    # Write the fixed content back to the file
    with open(websocket_file, "w") as f:
        f.write(new_content)
    
    print("WebSocket command handler replaced with correctly indented version")
    return True

if __name__ == "__main__":
    print("Fixing WebSocket command handler...")
    success = replace_websocket_command_handler()
    
    if success:
        print("WebSocket command handler fixed. You can now restart the server.")
    else:
        print("Failed to fix the WebSocket command handler.") 