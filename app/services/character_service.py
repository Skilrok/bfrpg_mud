"""
Character Service Module

This module provides helper functions for character management, 
including placing characters in the starting room.
"""

import logging
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Character, CharacterLocation, Room, Area

logger = logging.getLogger(__name__)


def set_character_starting_location(db: Session, character_id: int) -> bool:
    """
    Place a character in the starting room.
    
    Returns True if successful, False otherwise.
    """
    try:
        # Find the character
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            logger.error(f"Character {character_id} not found")
            return False
            
        # Check if character already has a location
        existing_location = db.query(CharacterLocation).filter(
            CharacterLocation.character_id == character_id
        ).first()
        
        if existing_location and existing_location.room_id:
            logger.info(f"Character {character_id} already has location, skipping initialization")
            return True
            
        # Find the starting area (Village)
        starting_area = db.query(Area).filter(Area.name == "Starting Village").first()
        
        if not starting_area:
            logger.warning("Starting area not found, looking for any room")
            # If no starting area is set up, just pick the first room available
            starting_room = db.query(Room).first()
        else:
            # Find the room marked as spawn point in the starting area
            starting_room = db.query(Room).filter(
                Room.area_id == starting_area.id,
                Room.properties.contains({"is_spawn_point": True})
            ).first()
            
            # If no spawn point is specifically marked, use the first room in the area
            if not starting_room:
                starting_room = db.query(Room).filter(
                    Room.area_id == starting_area.id
                ).first()
        
        if not starting_room:
            logger.error("No rooms found in the database")
            return False
            
        # Create or update character location
        if existing_location:
            existing_location.room_id = starting_room.id
            existing_location.x = None
            existing_location.y = None
        else:
            location = CharacterLocation(
                character_id=character_id,
                room_id=starting_room.id
            )
            db.add(location)
            
        db.commit()
        logger.info(f"Set character {character_id} starting location to room {starting_room.id} ({starting_room.name})")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error setting character location: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error setting character location: {str(e)}")
        return False 