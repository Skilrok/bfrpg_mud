"""
Room API Router

This module provides API endpoints for managing rooms in the MUD game.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user, get_current_admin_user

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()


@router.get("/{room_id}", response_model=schemas.RoomDetail)
async def get_room(
    room_id: int,
    include_exits: bool = True,
    include_items: bool = True,
    include_npcs: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """
    Get detailed information about a specific room
    """
    try:
        # Check if room exists
        room = db.query(models.Room).filter(models.Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with ID {room_id} not found",
            )

        # Get exits if requested
        exits = []
        if include_exits:
            exits = db.query(models.Exit).filter(models.Exit.source_room_id == room_id).all()
            exits = [schemas.Exit.from_orm(exit) for exit in exits]

        # Get items if requested
        items = []
        if include_items:
            items = db.query(models.Item).filter(models.Item.room_id == room_id).all()
            items = [schemas.Item.from_orm(item) for item in items]

        # Get NPCs if requested
        npcs = []
        if include_npcs:
            npcs = db.query(models.NPC).filter(models.NPC.room_id == room_id).all()
            npcs = [schemas.NPC.from_orm(npc) for npc in npcs]

        # Get area information
        area = None
        if room.area_id:
            area = db.query(models.Area).filter(models.Area.id == room.area_id).first()
            if area:
                area = schemas.AreaBrief.from_orm(area)

        # Construct response
        return schemas.RoomDetail(
            id=room.id,
            name=room.name,
            description=room.description,
            area_id=room.area_id,
            area=area,
            is_dark=room.is_dark,
            coordinates=room.coordinates,
            properties=room.properties or {},
            exits=exits,
            items=items,
            npcs=npcs,
            created_at=room.created_at,
            updated_at=room.updated_at
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.exception(f"Database error retrieving room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving room",
        )


@router.get("/", response_model=List[schemas.Room])
async def list_rooms(
    area_id: Optional[int] = None,
    is_dark: Optional[bool] = None,
    name_contains: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    List rooms with optional filtering (admin only)
    """
    try:
        # Build query
        query = db.query(models.Room)

        # Apply filters if provided
        if area_id is not None:
            query = query.filter(models.Room.area_id == area_id)
        if is_dark is not None:
            query = query.filter(models.Room.is_dark == is_dark)
        if name_contains is not None:
            query = query.filter(models.Room.name.ilike(f"%{name_contains}%"))

        # Apply pagination
        rooms = query.offset(skip).limit(limit).all()

        return [schemas.Room.from_orm(room) for room in rooms]
    except SQLAlchemyError as e:
        logger.exception(f"Database error listing rooms: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while listing rooms",
        )


@router.post("/", response_model=schemas.Room)
async def create_room(
    room_create: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Create a new room (admin only)
    """
    try:
        # If area_id is provided, verify that the area exists
        if room_create.area_id:
            area = db.query(models.Area).filter(models.Area.id == room_create.area_id).first()
            if not area:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Area with ID {room_create.area_id} not found",
                )

        # Create room object
        db_room = models.Room(
            name=room_create.name,
            description=room_create.description,
            area_id=room_create.area_id,
            is_dark=room_create.is_dark or False,
            coordinates=room_create.coordinates,
            properties=room_create.properties,
        )

        # Save to database
        db.add(db_room)
        db.commit()
        db.refresh(db_room)

        return schemas.Room.from_orm(db_room)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error creating room: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating room",
        )


@router.put("/{room_id}", response_model=schemas.Room)
async def update_room(
    room_id: int,
    room_update: schemas.RoomUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Update an existing room (admin only)
    """
    try:
        # Check if room exists
        db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
        if not db_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with ID {room_id} not found",
            )

        # Update fields if provided (handle optional fields properly)
        if room_update.name is not None:
            db_room.name = room_update.name
        if room_update.description is not None:
            db_room.description = room_update.description
        if room_update.area_id is not None:
            # Verify that area exists
            if room_update.area_id:
                area = db.query(models.Area).filter(models.Area.id == room_update.area_id).first()
                if not area:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Area with ID {room_update.area_id} not found",
                    )
            db_room.area_id = room_update.area_id
        if room_update.is_dark is not None:
            db_room.is_dark = room_update.is_dark
        if room_update.coordinates is not None:
            db_room.coordinates = room_update.coordinates
        if room_update.properties is not None:
            db_room.properties = room_update.properties

        # Save changes
        db.commit()
        db.refresh(db_room)

        return schemas.Room.from_orm(db_room)
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error updating room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating room",
        )


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Delete a room (admin only)
    
    By default, deletion will fail if the room has associated exits, items, or NPCs.
    If force=True, all associated entities will be deleted as well.
    """
    try:
        # Check if room exists
        db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
        if not db_room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with ID {room_id} not found",
            )

        # Check for dependencies if not force deleting
        if not force:
            # Check for outgoing exits
            outgoing_exits = db.query(models.Exit).filter(models.Exit.source_room_id == room_id).count()
            if outgoing_exits > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room has {outgoing_exits} outgoing exits. Use force=true to delete anyway.",
                )

            # Check for incoming exits
            incoming_exits = db.query(models.Exit).filter(models.Exit.destination_room_id == room_id).count()
            if incoming_exits > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room has {incoming_exits} incoming exits. Use force=true to delete anyway.",
                )

            # Check for items in the room
            items = db.query(models.Item).filter(models.Item.room_id == room_id).count()
            if items > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room has {items} items. Use force=true to delete anyway.",
                )

            # Check for NPCs in the room
            npcs = db.query(models.NPC).filter(models.NPC.room_id == room_id).count()
            if npcs > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room has {npcs} NPCs. Use force=true to delete anyway.",
                )

            # Check for players in the room
            characters = db.query(models.Character).filter(models.Character.room_id == room_id).count()
            if characters > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room has {characters} characters. Cannot delete room with characters present.",
                )
        else:
            # Force delete associated entities
            logger.warning(f"Force deleting room {room_id} with all associated entities")
            
            # Delete outgoing exits
            outgoing_exits = db.query(models.Exit).filter(models.Exit.source_room_id == room_id).all()
            for exit in outgoing_exits:
                db.delete(exit)
                
            # Delete incoming exits
            incoming_exits = db.query(models.Exit).filter(models.Exit.destination_room_id == room_id).all()
            for exit in incoming_exits:
                db.delete(exit)
                
            # Delete items
            items = db.query(models.Item).filter(models.Item.room_id == room_id).all()
            for item in items:
                db.delete(item)
                
            # Delete NPCs
            npcs = db.query(models.NPC).filter(models.NPC.room_id == room_id).all()
            for npc in npcs:
                db.delete(npc)
                
            # Check for players in the room (can't force delete if characters present)
            characters = db.query(models.Character).filter(models.Character.room_id == room_id).count()
            if characters > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Room has {characters} characters. Cannot delete room with characters present, even with force=true.",
                )

        # Delete room
        db.delete(db_room)
        db.commit()
        
        return None
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error deleting room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting room",
        )


@router.get("/{room_id}/exits", response_model=List[schemas.ExitDetail])
async def get_room_exits(
    room_id: int,
    include_hidden: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """
    Get all exits from a specific room
    """
    try:
        # Check if room exists
        room = db.query(models.Room).filter(models.Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with ID {room_id} not found",
            )
        
        # Query exits
        exits_query = db.query(models.Exit).filter(models.Exit.source_room_id == room_id)
        
        # Filter hidden exits if not admin and not requested
        is_admin = False
        try:
            get_current_admin_user(current_user)
            is_admin = True
        except:
            pass
            
        if not include_hidden and not is_admin:
            exits_query = exits_query.filter(models.Exit.is_hidden == False)
            
        exits = exits_query.all()
        
        # Get destination room info for each exit
        result = []
        for exit in exits:
            destination_room = db.query(models.Room).filter(models.Room.id == exit.destination_room_id).first()
            
            exit_detail = schemas.ExitDetail(
                id=exit.id,
                direction=exit.direction,
                name=exit.name,
                description=exit.description,
                is_hidden=exit.is_hidden,
                is_locked=exit.is_locked,
                key_id=exit.key_id,
                source_room_id=exit.source_room_id,
                destination_room_id=exit.destination_room_id,
                destination_room=schemas.RoomBrief.from_orm(destination_room) if destination_room else None,
                properties=exit.properties or {},
                created_at=exit.created_at,
                updated_at=exit.updated_at
            )
            result.append(exit_detail)
            
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.exception(f"Database error retrieving exits for room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving room exits",
        )


@router.get("/{room_id}/items", response_model=List[schemas.Item])
async def get_room_items(
    room_id: int,
    include_hidden: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """
    Get all items in a specific room
    """
    try:
        # Check if room exists
        room = db.query(models.Room).filter(models.Room.id == room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room with ID {room_id} not found",
            )
        
        # Query items
        items_query = db.query(models.Item).filter(models.Item.room_id == room_id)
        
        # Filter hidden items if not admin and not requested
        is_admin = False
        try:
            get_current_admin_user(current_user)
            is_admin = True
        except:
            pass
            
        if not include_hidden and not is_admin:
            items_query = items_query.filter(models.Item.is_hidden == False)
            
        items = items_query.all()
        
        return [schemas.Item.from_orm(item) for item in items]
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.exception(f"Database error retrieving items for room {room_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving room items",
        ) 