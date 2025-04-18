from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Dict, List, Optional
import json
import logging
from app.utils import verify_token
from app.database import get_db
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active connections by room
class ConnectionManager:
    def __init__(self):
        # Structure: {room_id: {user_id: WebSocket}}
        self.active_connections: Dict[str, Dict[int, WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket
        logger.info(f"User {user_id} connected to room {room_id}")
        
    def disconnect(self, user_id: int, room_id: str):
        if room_id in self.active_connections and user_id in self.active_connections[room_id]:
            del self.active_connections[room_id][user_id]
            logger.info(f"User {user_id} disconnected from room {room_id}")
            
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
            
    async def broadcast_to_room(self, message: dict, room_id: str, exclude_user: Optional[int] = None):
        if room_id in self.active_connections:
            for user_id, connection in self.active_connections[room_id].items():
                if exclude_user is None or user_id != exclude_user:
                    await connection.send_json(message)
                    
    def get_active_users_in_room(self, room_id: str) -> List[int]:
        if room_id in self.active_connections:
            return list(self.active_connections[room_id].keys())
        return []

# Create a manager instance
manager = ConnectionManager()

@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: str, 
    user_id: int, 
    token: str = Query(None),
    db = Depends(get_db)
):
    # Verify token (basic auth check)
    if token and not verify_token(token, user_id):
        logger.warning(f"Invalid token for user {user_id}")
        await websocket.close(code=1008)  # Policy violation
        return
        
    # Connect to the WebSocket
    await manager.connect(websocket, user_id, room_id)
    
    # Notify other users in the room
    user = db.query(User).filter(User.id == user_id).first()
    username = user.username if user else f"User-{user_id}"
    
    await manager.broadcast_to_room(
        {
            "type": "system",
            "message": f"{username} has joined the room"
        },
        room_id
    )
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message_type = message_data.get("type", "")
            
            if message_type == "chat":
                # Process chat message
                await manager.broadcast_to_room(
                    {
                        "type": "chat",
                        "user_id": user_id,
                        "username": username,
                        "message": message_data.get("message", "")
                    },
                    room_id
                )
            elif message_type == "command":
                # Process game command (placeholder for game logic)
                command = message_data.get("command", "")
                logger.info(f"User {user_id} sent command: {command}")
                
                # Send response only to the user who sent the command
                await manager.send_personal_message(
                    {
                        "type": "command_result",
                        "command": command,
                        "result": f"You executed: {command}"
                    },
                    websocket
                )
                
                # If command would affect others (e.g. movement), notify them
                if command.startswith(("move", "say", "emote")):
                    await manager.broadcast_to_room(
                        {
                            "type": "game_update",
                            "user_id": user_id,
                            "username": username,
                            "action": command
                        },
                        room_id,
                        exclude_user=user_id
                    )
                
    except WebSocketDisconnect:
        # Handle disconnect
        manager.disconnect(user_id, room_id)
        await manager.broadcast_to_room(
            {
                "type": "system",
                "message": f"{username} has left the room"
            },
            room_id
        )
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(user_id, room_id) 