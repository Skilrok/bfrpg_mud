# REMOVED: import asyncio
import json
import logging
from typing import Any, Dict, List, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# REMOVED: from sqlalchemy.orm import Session

from app.commands.base import CommandContext
from app.commands.registry import command_registry

# REMOVED: from app.database import get_db
from app.models import Character, CharacterLocation, User

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages websocket connections and provides broadcast capabilities
    """

    def __init__(self):
        # Map of active connections by type
        self.active_connections: Dict[str, List[WebSocket]] = {
            "command": [],
            "chat": [],
            "system": [],
        }

        # Map of user IDs to connection info
        self.user_connections: Dict[int, Set[WebSocket]] = {}

        # Map of character IDs to connection info
        self.character_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conn_type: str = "command"):
        """
        Accept connection and add to connection pools

        Args:
            websocket: The WebSocket connection
            conn_type: Type of connection (command, chat, system)
        """
        await websocket.accept()

        if conn_type not in self.active_connections:
            self.active_connections[conn_type] = []

        self.active_connections[conn_type].append(websocket)
        logger.info(f"New {conn_type} connection established")

    def disconnect(self, websocket: WebSocket, conn_type: str = "command"):
        """Remove connection from all pools"""
        if conn_type in self.active_connections:
            if websocket in self.active_connections[conn_type]:
                self.active_connections[conn_type].remove(websocket)

        # Remove from user connections
        for user_id, connections in list(self.user_connections.items()):
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.user_connections[user_id]
                break

        # Remove from character connections
        for char_id, connections in list(self.character_connections.items()):
            if websocket in connections:
                connections.remove(websocket)
                if not connections:
                    del self.character_connections[char_id]
                break

        logger.info(f"{conn_type.capitalize()} connection closed")

    def register_user(self, websocket: WebSocket, user_id: int):
        """Register a connection with a user ID"""
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

    def register_character(self, websocket: WebSocket, character_id: int):
        """Register a connection with a character ID"""
        if character_id not in self.character_connections:
            self.character_connections[character_id] = set()
        self.character_connections[character_id].add(websocket)

    async def broadcast(self, message: Any, conn_type: str = "command"):
        """Broadcast a message to all connections of a type"""
        if conn_type not in self.active_connections:
            return

        # Convert to JSON string if needed
        if not isinstance(message, str):
            message = json.dumps(message)

        # Send to all connections of this type
        disconnected = []
        for connection in self.active_connections[conn_type]:
            try:
                await connection.send_text(message)
            except Exception:
                # Mark for removal
                disconnected.append(connection)

        # Remove disconnected
        for conn in disconnected:
            self.disconnect(conn, conn_type)

    async def send_to_user(self, user_id: int, message: Any):
        """Send a message to all connections for a user"""
        if user_id not in self.user_connections:
            return

        # Convert to JSON string if needed
        if not isinstance(message, str):
            message = json.dumps(message)

        # Send to all connections for this user
        disconnected = []
        for connection in self.user_connections[user_id]:
            try:
                await connection.send_text(message)
            except Exception:
                # Mark for removal
                disconnected.append(connection)

        # Remove disconnected
        for conn in disconnected:
            self.disconnect(conn)

    async def send_to_character(self, character_id: int, message: Any):
        """Send a message to all connections for a character"""
        if character_id not in self.character_connections:
            return

        # Convert to JSON string if needed
        if not isinstance(message, str):
            message = json.dumps(message)

        # Send to all connections for this character
        disconnected = []
        for connection in self.character_connections[character_id]:
            try:
                await connection.send_text(message)
            except Exception:
                # Mark for removal
                disconnected.append(connection)

        # Remove disconnected
        for conn in disconnected:
            self.disconnect(conn)


class WebSocketManager:
    """
    Manages WebSocket endpoints for the application
    """

    def __init__(self, app: FastAPI):
        self.app = app
        self.manager = ConnectionManager()

        # Register WebSocket endpoints
        self._register_endpoints()

    def _register_endpoints(self):
        """Register WebSocket endpoints with the FastAPI app"""

        @self.app.websocket("/ws/commands")
        async def commands_websocket(websocket: WebSocket):
            await self.manager.connect(websocket, "command")

            # Initialize session data
            session_id = None
            user_id = None
            character_id = None

            try:
                # Get initial connection data with authentication
                auth_data = await websocket.receive_json()

                # Validate token
                token = auth_data.get("token")
                session_id = auth_data.get("session_id")

                if not token:
                    await websocket.send_json(
                        {"success": False, "message": "Authentication required"}
                    )
                    return

                # Get database session
                # We need to create a new db session for each request since we're in an async context
                from jose import JWTError, jwt

                from app.database import SessionLocal
                from app.utils import ALGORITHM, SECRET_KEY

                db = SessionLocal()
                try:
                    # Verify token and get user ID
                    try:
                        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                        user_id = None

                        # Handle both formats - username as "sub" and direct user ID
                        subject = payload.get("sub")
                        if subject is not None:
                            # Try to convert to int if it's a user ID
                            try:
                                user_id = int(subject)
                                logger.info(
                                    f"Found numeric user ID in token: {user_id}"
                                )
                            except (ValueError, TypeError):
                                # It's a username, look it up
                                logger.info(f"Found username in token: {subject}")
                                user = (
                                    db.query(User)
                                    .filter(User.username == subject)
                                    .first()
                                )
                                if user:
                                    user_id = user.id

                        if not user_id:
                            await websocket.send_json(
                                {
                                    "success": False,
                                    "message": "Invalid token payload or user not found",
                                }
                            )
                            return
                    except JWTError as e:
                        logger.error(f"JWT decode error: {str(e)}")
                        await websocket.send_json(
                            {"success": False, "message": "Invalid or expired token"}
                        )
                        return

                    # Get user
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        await websocket.send_json(
                            {"success": False, "message": "User not found"}
                        )
                        return

                    # Get active character ID if provided
                    character_id = auth_data.get("character_id")
                    character = None

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
                                    "message": "Character not found or not owned by user",
                                }
                            )
                            return

                        # Ensure character has a location in the starting room
                        from app.services.character_service import (
                            ensure_room_exists,
                            set_character_starting_location,
                        )

                        # Make sure room 1 exists
                        starter_room = ensure_room_exists(db, 1)
                        if not starter_room:
                            logger.error(
                                f"Failed to ensure starter room exists for character {character_id}"
                            )

                        # Set character location
                        location_success = set_character_starting_location(
                            db, character_id
                        )
                        if not location_success:
                            logger.warning(
                                f"Failed to set starting location for character {character_id}"
                            )

                        # Refresh character after location is set
                        db.refresh(character)

                    # Register the websocket with the manager
                    self.manager.register_user(websocket, user_id)
                    if character_id:
                        self.manager.register_character(websocket, character_id)

                    # Send successful connection message
                    await websocket.send_json(
                        {
                            "success": True,
                            "message": "Connected to command websocket",
                            "user_id": user_id,
                            "character_id": character_id,
                        }
                    )

                    # Main command processing loop
                    while True:
                        # Wait for commands
                        data = await websocket.receive_json()
                        command_text = data.get("command", "").strip()

                        if not command_text:
                            await websocket.send_json(
                                {"success": False, "message": "Empty command"}
                            )
                            continue

                        # Get character ID from the data payload if available
                        cmd_character_id = data.get("character_id")
                        if cmd_character_id:
                            character_id = cmd_character_id
                            logger.info(
                                f"Using character ID from command payload: {character_id}"
                            )

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
                                from app.services.character_service import (
                                    set_character_starting_location,
                                )

                                location_success = set_character_starting_location(
                                    db, character_id
                                )
                                if location_success:
                                    # Get the new location
                                    character_location = (
                                        db.query(CharacterLocation)
                                        .filter(
                                            CharacterLocation.character_id
                                            == character_id
                                        )
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
                        logger.info(
                            f"Command: {cmd}, Args: {args}, Character: {character_id}, Room: {room_id}"
                        )

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
                                "character_id": character_id,  # Explicitly include character_id in data
                            },
                        )

                        try:
                            # Execute command
                            response = await command_registry.execute_command(ctx)

                            # Log the response for debugging
                            logger.info(
                                f"Command response: success={response.success}, message_length={len(response.message) if response.message else 0}"
                            )

                            # Send response back to client
                            await websocket.send_json(
                                {
                                    "success": response.success,
                                    "message": response.message,
                                    "errors": response.errors or [],
                                    "data": response.data or {},
                                    "command": {
                                        "raw": command_text,
                                        "name": cmd,
                                        "args": args,
                                    },
                                }
                            )
                        except Exception as e:
                            # Log and handle errors in command execution
                            import traceback

                            logger.error(f"Error executing command: {str(e)}")
                            logger.error(traceback.format_exc())

                            await websocket.send_json(
                                {
                                    "success": False,
                                    "message": f"Error executing command: {str(e)}",
                                    "errors": [str(e)],
                                    "command": {"raw": command_text},
                                }
                            )

                finally:
                    db.close()

            except WebSocketDisconnect:
                self.manager.disconnect(websocket, "command")
            except Exception as e:
                logger.exception(f"Error in command websocket: {str(e)}")
                self.manager.disconnect(websocket, "command")

        @self.app.websocket("/ws/chat")
        async def chat_websocket(websocket: WebSocket):
            await self.manager.connect(websocket, "chat")

            try:
                # Chat implementation
                pass  # TODO: Implement chat websocket
            except WebSocketDisconnect:
                self.manager.disconnect(websocket, "chat")
