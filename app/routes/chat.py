from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    # TODO: Implement WebSocket chat functionality
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received in room {room_id}: {data}")

@router.get("/{room_id}/history")
def get_chat_history(room_id: int, db: Session = Depends(get_db)):
    # TODO: Implement chat history retrieval
    return {"message": f"Chat history for room {room_id}"} 