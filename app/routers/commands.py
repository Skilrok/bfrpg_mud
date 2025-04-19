"""
Command API Router

This module provides API endpoints for processing game commands.
"""

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any, List, Optional
import logging
import json

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user, get_current_active_user
from ..commands.parser import parse_command
from ..commands.registry import command_registry
from ..commands.base import CommandContext, CommandResponse

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

@router.post("/", response_model=schemas.CommandResponse)
async def process_command(
    command_data: schemas.CommandRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Process a game command
    
    Request body should contain:
    - command: The command string to process
    - character_id: (Optional) ID of the character executing the command
    """
    # Validate input
    command_text = command_data.command.strip()
    if not command_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No command provided"
        )
    
    # Parse the command
    command_name, args = parse_command(command_text)
    
    # Get character if specified
    character = None
    if command_data.character_id:
        character = db.query(models.Character).filter(
            models.Character.id == command_data.character_id,
            models.Character.user_id == current_user.id
        ).first()
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {command_data.character_id} not found"
            )
    
    # Create command context
    ctx = CommandContext(
        user=current_user,
        character=character,
        room_id=None,  # Room tracking handled in command handlers now
        raw_input=command_text,
        command=command_name,
        args=args,
        data={"db": db}  # Include DB session in context
    )
    
    # Execute command
    try:
        response = await command_registry.execute_command(ctx)
        
        # Log command to database
        command_log = models.CommandHistory(
            user_id=current_user.id,
            character_id=character.id if character else None,
            command=command_text,
            response=response.message,
            success=response.success
        )
        db.add(command_log)
        db.commit()
        
        return schemas.CommandResponse(
            success=response.success,
            message=response.message,
            errors=response.errors,
            data=response.data,
            command={
                "raw": command_text,
                "name": command_name,
                "args": args
            }
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error processing command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while processing command"
        )
    except Exception as e:
        logger.exception(f"Error processing command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing command: {str(e)}"
        )

@router.websocket("/ws")
async def command_websocket(websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for processing commands
    
    Authentication is handled via token in the connection query parameters
    Format: /api/commands/ws?token=<jwt_token>
    """
    # TODO: Implement authentication for websockets
    await websocket.accept()
    
    try:
        # Simple echo for now, replace with actual command handling
        while True:
            data = await websocket.receive_text()
            command_data = json.loads(data)
            
            # Parse command
            command_text = command_data.get("command", "").strip()
            if not command_text:
                await websocket.send_json({
                    "success": False,
                    "message": "No command provided",
                    "errors": ["Empty command"]
                })
                continue
                
            command_name, args = parse_command(command_text)
            
            # TODO: Implement proper authentication and character validation
            # For now, just echo back
            await websocket.send_json({
                "success": True,
                "message": f"Received command: {command_text}",
                "data": {
                    "command": command_name,
                    "args": args
                }
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.exception(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011) 