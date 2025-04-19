"""
Area API Router

This module provides API endpoints for area management and retrieval.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user, get_current_admin_user

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()


@router.get("/{area_id}", response_model=schemas.AreaDetail)
async def get_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """
    Get detailed information about a specific area
    """
    try:
        # Check if area exists
        area = db.query(models.Area).filter(models.Area.id == area_id).first()
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Area with ID {area_id} not found",
            )

        # Get rooms in the area
        rooms = db.query(models.Room).filter(models.Room.area_id == area_id).all()
        room_count = len(rooms)
        
        # Create response with area details
        response = schemas.AreaDetail(
            id=area.id,
            name=area.name,
            description=area.description,
            level_range=area.level_range,
            is_dungeon=area.is_dungeon,
            properties=area.properties or {},
            created_at=area.created_at,
            updated_at=area.updated_at,
            room_count=room_count
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        logger.exception(f"Database error retrieving area {area_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving area",
        )


@router.get("/", response_model=List[schemas.Area])
async def list_areas(
    skip: int = 0,
    limit: int = 20,
    include_hidden: bool = False,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """
    List all areas
    """
    try:
        # Build query
        query = db.query(models.Area)
        
        # Filter out hidden areas unless specifically requested
        if not include_hidden:
            query = query.filter(models.Area.is_hidden == False)
            
        # Apply pagination
        areas = query.offset(skip).limit(limit).all()
        
        return [schemas.Area.from_orm(area) for area in areas]
    except SQLAlchemyError as e:
        logger.exception(f"Database error listing areas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while listing areas",
        )


@router.post("/", response_model=schemas.Area)
async def create_area(
    area: schemas.AreaCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Create a new area (admin only)
    """
    try:
        # Create area object
        db_area = models.Area(
            name=area.name,
            description=area.description,
            level_range=area.level_range,
            is_dungeon=area.is_dungeon,
            is_hidden=area.is_hidden,
            properties=area.properties,
        )
        
        # Save to database
        db.add(db_area)
        db.commit()
        db.refresh(db_area)
        
        return schemas.Area.from_orm(db_area)
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error creating area: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating area",
        )


@router.put("/{area_id}", response_model=schemas.Area)
async def update_area(
    area_id: int,
    area_update: schemas.AreaCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Update an existing area (admin only)
    """
    try:
        # Check if area exists
        db_area = db.query(models.Area).filter(models.Area.id == area_id).first()
        if not db_area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Area with ID {area_id} not found",
            )
            
        # Update area fields
        db_area.name = area_update.name
        db_area.description = area_update.description
        db_area.level_range = area_update.level_range
        db_area.is_dungeon = area_update.is_dungeon
        db_area.is_hidden = area_update.is_hidden
        db_area.properties = area_update.properties
        
        # Save changes
        db.commit()
        db.refresh(db_area)
        
        return schemas.Area.from_orm(db_area)
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error updating area {area_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating area",
        )


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_admin_user),
):
    """
    Delete an area (admin only)
    
    Note: This will fail if there are rooms associated with this area.
    Delete all rooms in the area first.
    """
    try:
        # Check if area exists
        db_area = db.query(models.Area).filter(models.Area.id == area_id).first()
        if not db_area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Area with ID {area_id} not found",
            )
        
        # Check if area has rooms
        room_count = db.query(models.Room).filter(models.Room.area_id == area_id).count()
        if room_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete area with {room_count} rooms. Delete all rooms first.",
            )
            
        # Delete area
        db.delete(db_area)
        db.commit()
        
        return None
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.exception(f"Database error deleting area {area_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while deleting area",
        )


@router.get("/{area_id}/rooms", response_model=List[schemas.Room])
async def get_area_rooms(
    area_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """
    Get all rooms in a specific area
    """
    try:
        # Check if area exists
        area = db.query(models.Area).filter(models.Area.id == area_id).first()
        if not area:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Area with ID {area_id} not found",
            )
            
        # Get rooms in the area
        rooms = db.query(models.Room).filter(
            models.Room.area_id == area_id
        ).offset(skip).limit(limit).all()
        
        return [schemas.Room.from_orm(room) for room in rooms]
    except SQLAlchemyError as e:
        logger.exception(f"Database error retrieving rooms for area {area_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while retrieving area rooms",
        ) 