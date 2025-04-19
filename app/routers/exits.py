"""
Exit API Router

This module provides API endpoints for managing exits between rooms.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user, get_current_admin_user

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()


@router.get("/{exit_id}", response_model=schemas.ExitDetail)
async def get_exit(
    exit_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """
    Get detailed information about a specific exit
    """
    try:
        # Check if exit exists
        exit = db.query(models.Exit).filter(models.Exit.id == exit_id).first()
        if not exit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exit with ID {exit_id} not found",
            )
        
        # Get source and destination room info
        source_room = db.query(models.Room).filter(models.Room.id == exit.source_room_id).first()
        destination_room = db.query(models.Room).filter(models.Room.id == exit.destination_room_id).first()
        
        if not source_room or not destination_room:
            logger.error(f"Exit {exit_id} has invalid source or destination room references")
            
        return schemas.ExitDetail(
            id=exit.id,
            direction=exit.direction,
            name=exit.name,
            description=exit.description,
            is_hidden=exit.is_hidden,
            is_locked=exit.is_locked,
            key_id=exit.key_id,
            source_room_id=exit.source_room_id,
            destination_room_id=exit.destination_room_id,
            source_room=schemas.RoomBrief.from_orm(source_room) if source_room else None,
            destination_room=schemas.RoomBrief.from_orm(destination_room) if destination_room else None,
            properties=exit.properties or {},
            created_at=exit.created_at,
            updated_at=exit.updated_at
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.exception(f"Database error retrieving exit {exit_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving exit",
        )


@router.get("/", response_model=List[schemas.Exit])
async def list_exits(
    source_room_id: Optional[int] = None,
    destination_room_id: Optional[int] = None,
    direction: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    List exits with optional filtering (admin only)
    """
    try:
        # Build query
        query = db.query(models.Exit)
        
        # Apply filters if provided
        if source_room_id is not None:
            query = query.filter(models.Exit.source_room_id == source_room_id)
        if destination_room_id is not None:
            query = query.filter(models.Exit.destination_room_id == destination_room_id)
        if direction is not None:
            query = query.filter(models.Exit.direction == direction)
            
        # Apply pagination
        exits = query.offset(skip).limit(limit).all()
        
        return [schemas.Exit.from_orm(exit) for exit in exits]
    except SQLAlchemyError as e:
        logger.exception(f"Database error listing exits: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while listing exits",
        )


@router.post("/", response_model=schemas.Exit)
async def create_exit(
    exit_create: schemas.ExitCreate,
    create_reverse: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Create a new exit between rooms (admin only)
    
    Optionally create a reverse exit as well (bidirectional connection)
    """
    try:
        # Verify that source and destination rooms exist
        source_room = db.query(models.Room).filter(models.Room.id == exit_create.source_room_id).first()
        if not source_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source room with ID {exit_create.source_room_id} not found",
            )
            
        destination_room = db.query(models.Room).filter(models.Room.id == exit_create.destination_room_id).first()
        if not destination_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination room with ID {exit_create.destination_room_id} not found",
            )
            
        # Check if exit already exists
        existing_exit = db.query(models.Exit).filter(
            models.Exit.source_room_id == exit_create.source_room_id,
            models.Exit.direction == exit_create.direction
        ).first()
        
        if existing_exit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Exit already exists in direction {exit_create.direction} from room {exit_create.source_room_id}",
            )
        
        # Create exit object
        db_exit = models.Exit(
            source_room_id=exit_create.source_room_id,
            destination_room_id=exit_create.destination_room_id,
            direction=exit_create.direction,
            name=exit_create.name,
            description=exit_create.description,
            is_hidden=exit_create.is_hidden,
            is_locked=exit_create.is_locked,
            key_id=exit_create.key_id,
            properties=exit_create.properties,
        )
        
        # Save to database
        db.add(db_exit)
        
        # Create reverse exit if requested
        if create_reverse:
            reverse_direction = get_reverse_direction(exit_create.direction)
            if not reverse_direction:
                logger.warning(f"Could not determine reverse direction for '{exit_create.direction}'")
                
            else:
                # Check if reverse exit already exists
                existing_reverse = db.query(models.Exit).filter(
                    models.Exit.source_room_id == exit_create.destination_room_id,
                    models.Exit.direction == reverse_direction
                ).first()
                
                if existing_reverse:
                    logger.warning(f"Reverse exit already exists in direction {reverse_direction} from room {exit_create.destination_room_id}")
                else:
                    # Create reverse exit with similar properties
                    reverse_exit = models.Exit(
                        source_room_id=exit_create.destination_room_id,
                        destination_room_id=exit_create.source_room_id,
                        direction=reverse_direction,
                        name=exit_create.name,
                        description=exit_create.description,
                        is_hidden=exit_create.is_hidden,
                        is_locked=exit_create.is_locked,
                        key_id=exit_create.key_id,
                        properties=exit_create.properties,
                    )
                    db.add(reverse_exit)
        
        db.commit()
        db.refresh(db_exit)
        
        return schemas.Exit.from_orm(db_exit)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error creating exit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating exit",
        )


@router.put("/{exit_id}", response_model=schemas.Exit)
async def update_exit(
    exit_id: int,
    exit_update: schemas.ExitUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Update an existing exit (admin only)
    """
    try:
        # Check if exit exists
        db_exit = db.query(models.Exit).filter(models.Exit.id == exit_id).first()
        if not db_exit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exit with ID {exit_id} not found",
            )
        
        # Update fields if provided (handle optional fields properly)
        if exit_update.direction is not None:
            db_exit.direction = exit_update.direction
        if exit_update.name is not None:
            db_exit.name = exit_update.name
        if exit_update.description is not None:
            db_exit.description = exit_update.description
        if exit_update.is_hidden is not None:
            db_exit.is_hidden = exit_update.is_hidden
        if exit_update.is_locked is not None:
            db_exit.is_locked = exit_update.is_locked
        if exit_update.key_id is not None:
            db_exit.key_id = exit_update.key_id
        if exit_update.destination_room_id is not None:
            # Verify that destination room exists
            destination_room = db.query(models.Room).filter(models.Room.id == exit_update.destination_room_id).first()
            if not destination_room:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Destination room with ID {exit_update.destination_room_id} not found",
                )
            db_exit.destination_room_id = exit_update.destination_room_id
        if exit_update.properties is not None:
            db_exit.properties = exit_update.properties
            
        # Save changes
        db.commit()
        db.refresh(db_exit)
        
        return schemas.Exit.from_orm(db_exit)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error updating exit {exit_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating exit",
        )


@router.delete("/{exit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exit(
    exit_id: int,
    delete_reverse: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Delete an exit (admin only)
    
    Optionally delete the reverse exit as well
    """
    try:
        # Check if exit exists
        db_exit = db.query(models.Exit).filter(models.Exit.id == exit_id).first()
        if not db_exit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Exit with ID {exit_id} not found",
            )
        
        # If delete_reverse is true, try to find and delete the reverse exit
        if delete_reverse:
            reverse_direction = get_reverse_direction(db_exit.direction)
            if reverse_direction:
                reverse_exit = db.query(models.Exit).filter(
                    models.Exit.source_room_id == db_exit.destination_room_id,
                    models.Exit.destination_room_id == db_exit.source_room_id,
                    models.Exit.direction == reverse_direction
                ).first()
                
                if reverse_exit:
                    db.delete(reverse_exit)
                    logger.info(f"Deleted reverse exit {reverse_exit.id} ({reverse_direction}) from room {reverse_exit.source_room_id}")
        
        # Delete exit
        db.delete(db_exit)
        db.commit()
        
        return None
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error deleting exit {exit_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting exit",
        )


def get_reverse_direction(direction: str) -> Optional[str]:
    """
    Get the reverse direction for a given direction
    """
    direction_pairs = {
        "north": "south",
        "south": "north",
        "east": "west",
        "west": "east",
        "northeast": "southwest",
        "southwest": "northeast",
        "northwest": "southeast",
        "southeast": "northwest",
        "up": "down",
        "down": "up",
        "in": "out",
        "out": "in"
    }
    
    return direction_pairs.get(direction.lower()) 