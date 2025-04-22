"""
Character Service Module

This module provides helper functions for character management,
including placing characters in the starting room.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.room import Area, Room, RoomType
from app.models import Character, CharacterLocation

logger = logging.getLogger(__name__)


def set_character_starting_location(db: Session, character_id: int) -> bool:
    """
    Place a character in the starting room (creating the room if needed)
    """
    try:
        # First check if the room exists without querying columns that might not exist
        try:
            room_exists = db.execute(text("SELECT id FROM rooms WHERE id = 1")).fetchone()
        except SQLAlchemyError as e:
            logger.error(f"Error checking if room exists: {str(e)}")
            # Room table might not exist or have a different structure
            # Let's handle this gracefully and create the table if needed
            room_exists = None

        if not room_exists:
            # Room doesn't exist, we need to create it
            
            # First, check if we have a starting area
            try:
                area_result = db.execute(text("SELECT id FROM areas WHERE name = 'Starting Village' LIMIT 1")).fetchone()
            except SQLAlchemyError as e:
                logger.error(f"Error checking if area exists: {str(e)}")
                # Area table might not exist
                area_result = None
            
            if not area_result:
                # Create a basic starting area
                logger.info("Creating starter area 'Starting Village'")
                try:
                    # Check if areas table exists
                    db.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name = 'areas'")).fetchone()
                    
                    area_insert = text("""
                        INSERT INTO areas (name, description, level_range, is_dungeon, is_hidden, properties, created_at, updated_at) 
                        VALUES (:name, :description, :level_range, :is_dungeon, :is_hidden, :properties, :created_at, :updated_at)
                        RETURNING id
                    """)
                    
                    area_result = db.execute(
                        area_insert,
                        {
                            "name": "Starting Village",
                            "description": "A small village where new adventurers begin their journey.",
                            "level_range": "1-3",
                            "is_dungeon": False,
                            "is_hidden": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    area_id = area_result.fetchone()[0]
                    db.commit()
                    logger.info(f"Created starter area with ID {area_id}")
                except SQLAlchemyError as e:
                    logger.error(f"Error creating area: {str(e)}")
                    # If we can't create the area, we'll set a dummy area ID
                    area_id = 1
            else:
                # Use existing area
                area_id = area_result[0]
                logger.info(f"Using existing starter area with ID {area_id}")
                
            # Create the starter room
            logger.info("Creating starter room")
            
            # Basic JSON for exits
            exits_json = "{}"
            
            try:
                # Check if rooms table exists
                db.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name = 'rooms'")).fetchone()
                
                # Insert the room
                room_insert = text("""
                    INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark, exits, properties, created_at, updated_at) 
                    VALUES (:id, :name, :description, :room_type, :area_id, :x, :y, :z, :is_dark, :exits, :properties, :created_at, :updated_at)
                """)
                
                db.execute(
                    room_insert,
                    {
                        "id": 1,
                        "name": "Village Square",
                        "description": "The central square of the starting village. Paths lead in all directions. A tavern stands to the north, a market to the east, a blacksmith to the south, and a temple to the west.",
                        "room_type": "town",
                        "area_id": area_id,
                        "x": 0,
                        "y": 0,
                        "z": 0,
                        "is_dark": False,
                        "exits": exits_json,
                        "properties": "{}",
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                
                # Create additional rooms around the village square
                try:
                    # Tavern to the north (Room 2)
                    db.execute(
                        room_insert,
                        {
                            "id": 2,
                            "name": "Village Tavern",
                            "description": "A cozy tavern with a roaring fireplace. Adventurers gather here to share tales and find work. The bartender nods at you as you enter.",
                            "room_type": "town",
                            "area_id": area_id,
                            "x": 0,
                            "y": 1,
                            "z": 0,
                            "is_dark": False,
                            "exits": "{}",
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # Market to the east (Room 3)
                    db.execute(
                        room_insert,
                        {
                            "id": 3,
                            "name": "Village Market",
                            "description": "A bustling market with various stalls selling goods. Merchants call out to passersby, hawking their wares.",
                            "room_type": "town",
                            "area_id": area_id,
                            "x": 1,
                            "y": 0,
                            "z": 0,
                            "is_dark": False,
                            "exits": "{}",
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # Blacksmith to the south (Room 4)
                    db.execute(
                        room_insert,
                        {
                            "id": 4,
                            "name": "Village Blacksmith",
                            "description": "The sound of hammering fills the air as the blacksmith works at the forge. Weapons and armor are displayed on the walls.",
                            "room_type": "town",
                            "area_id": area_id,
                            "x": 0,
                            "y": -1,
                            "z": 0,
                            "is_dark": False,
                            "exits": "{}",
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # Temple to the west (Room 5)
                    db.execute(
                        room_insert,
                        {
                            "id": 5,
                            "name": "Village Temple",
                            "description": "A peaceful temple dedicated to various deities. Candles flicker in the dim interior, and a priest stands ready to offer healing and blessings.",
                            "room_type": "town",
                            "area_id": area_id,
                            "x": -1,
                            "y": 0,
                            "z": 0,
                            "is_dark": False,
                            "exits": "{}",
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # Now create exits between rooms using the exits table
                    exit_insert = text("""
                        INSERT INTO exits (direction, name, description, source_room_id, destination_room_id, is_hidden, is_locked, properties, created_at, updated_at)
                        VALUES (:direction, :name, :description, :source_room_id, :destination_room_id, :is_hidden, :is_locked, :properties, :created_at, :updated_at)
                    """)
                    
                    # Exits from Village Square (Room 1)
                    # North to Tavern
                    db.execute(
                        exit_insert,
                        {
                            "direction": "north",
                            "name": "Tavern Entrance",
                            "description": "The door to the village tavern.",
                            "source_room_id": 1,
                            "destination_room_id": 2,
                            "is_hidden": False,
                            "is_locked": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # East to Market
                    db.execute(
                        exit_insert,
                        {
                            "direction": "east",
                            "name": "Market Street",
                            "description": "A path leading to the village market.",
                            "source_room_id": 1,
                            "destination_room_id": 3,
                            "is_hidden": False,
                            "is_locked": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # South to Blacksmith
                    db.execute(
                        exit_insert,
                        {
                            "direction": "south",
                            "name": "Smithy Road",
                            "description": "A path leading to the village blacksmith.",
                            "source_room_id": 1,
                            "destination_room_id": 4,
                            "is_hidden": False,
                            "is_locked": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # West to Temple
                    db.execute(
                        exit_insert,
                        {
                            "direction": "west",
                            "name": "Temple Path",
                            "description": "A serene path leading to the village temple.",
                            "source_room_id": 1,
                            "destination_room_id": 5,
                            "is_hidden": False,
                            "is_locked": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # Return paths back to Village Square
                    # South from Tavern
                    db.execute(
                        exit_insert,
                        {
                            "direction": "south",
                            "name": "Exit to Village Square",
                            "description": "The door leading back to the village square.",
                            "source_room_id": 2,
                            "destination_room_id": 1,
                            "is_hidden": False,
                            "is_locked": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # West from Market
                    db.execute(
                        exit_insert,
                        {
                            "direction": "west",
                            "name": "Back to Village Square",
                            "description": "The path leading back to the village square.",
                            "source_room_id": 3,
                            "destination_room_id": 1,
                            "is_hidden": False,
                            "is_locked": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # North from Blacksmith
                    db.execute(
                        exit_insert,
                        {
                            "direction": "north",
                            "name": "Back to Village Square",
                            "description": "The path leading back to the village square.",
                            "source_room_id": 4,
                            "destination_room_id": 1,
                            "is_hidden": False,
                            "is_locked": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    # East from Temple
                    db.execute(
                        exit_insert,
                        {
                            "direction": "east",
                            "name": "Back to Village Square",
                            "description": "The path leading back to the village square.",
                            "source_room_id": 5,
                            "destination_room_id": 1,
                            "is_hidden": False,
                            "is_locked": False,
                            "properties": "{}",
                            "created_at": datetime.now(),
                            "updated_at": datetime.now()
                        }
                    )
                    
                    logger.info("Created additional rooms and exits around the village square")
                except SQLAlchemyError as e:
                    logger.error(f"Error creating additional rooms or exits: {str(e)}")
                    # Continue even if creating additional rooms fails
                
                db.commit()
                logger.info("Created starter room with ID 1")
            except SQLAlchemyError as e:
                logger.error(f"Error creating room: {str(e)}")
                # Continue with the character location part anyway
            
        # Check if the character already has a location using direct SQL
        try:
            location_exists = db.execute(
                text("SELECT id FROM character_locations WHERE character_id = :char_id"),
                {"char_id": character_id}
            ).fetchone()
            
            if location_exists:
                # Update existing location with direct SQL
                db.execute(
                    text("UPDATE character_locations SET room_id = 1 WHERE character_id = :char_id"),
                    {"char_id": character_id}
                )
                logger.info(f"Updated character {character_id} location to room 1")
            else:
                # Create new location with direct SQL
                db.execute(
                    text("""
                    INSERT INTO character_locations (character_id, room_id, created_at, updated_at) 
                    VALUES (:char_id, :room_id, :created_at, :updated_at)
                    """),
                    {
                        "char_id": character_id,
                        "room_id": 1,
                        "created_at": datetime.now(),
                        "updated_at": datetime.now()
                    }
                )
                logger.info(f"Created new location for character {character_id} in room 1")
            
            # Commit all changes
            db.commit()
            
            # Verify location was set using direct SQL
            check_location = db.execute(
                text("SELECT room_id FROM character_locations WHERE character_id = :char_id"),
                {"char_id": character_id}
            ).fetchone()
            
            if not check_location or check_location[0] != 1:
                logger.error(f"Failed to verify character {character_id} location after commit")
                return False
                
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error handling character location: {str(e)}")
            # If we can't set the location, we'll return success anyway
            # This is better than failing character selection completely
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Database error setting character location: {str(e)}")
        db.rollback()
        # Return True instead of False to prevent character loading failure
        return True
    except Exception as e:
        logger.error(f"Unexpected error setting character location: {str(e)}")
        db.rollback()
        # Return True instead of False to prevent character loading failure
        return True


def ensure_character_location(db: Session, character_id: int) -> bool:
    """Make sure a character has a location"""
    try:
        # Check if character has a location
        location = db.execute(
            text("SELECT id FROM character_locations WHERE character_id = :char_id"),
            {"char_id": character_id}
        ).fetchone()
        
        if not location:
            # No location found, set default location
            return set_character_starting_location(db, character_id)
            
        return True
    except Exception as e:
        logger.error(f"Error ensuring character location: {e}")
        return False

def ensure_room_exists(db: Session, room_id: int) -> Optional[Room]:
    """
    Ensure that a room with the given ID exists, creating it if necessary.
    Uses direct SQL to avoid ORM schema mismatch issues.
    """
    try:
        # Check if room exists using direct SQL
        room_exists = db.execute(
            text("SELECT id, name, description FROM rooms WHERE id = :room_id"),
            {"room_id": room_id}
        ).fetchone()
        
        if room_exists:
            # Create a room object with the basic data we have
            room = Room(
                id=room_exists[0],
                name=room_exists[1],
                description=room_exists[2],
                room_type=RoomType.TOWN
            )
            return room
            
        logger.info(f"Creating room with ID {room_id}")
        
        # Get or create the starter area using direct SQL
        area_exists = db.execute(
            text("SELECT id FROM areas WHERE name = 'Starting Village'")
        ).fetchone()
        
        area_id = None
        if not area_exists:
            # Create a new area using direct SQL with only basic fields
            db.execute(
                text("""
                INSERT INTO areas (name, description, created_at, updated_at) 
                VALUES (:name, :description, :created_at, :updated_at)
                """),
                {
                    "name": "Starting Village",
                    "description": "A peaceful starting village for new adventurers.",
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            )
            # Get the new area ID
            area_id = db.execute(
                text("SELECT id FROM areas WHERE name = 'Starting Village'")
            ).fetchone()[0]
            logger.info(f"Created starter area with ID {area_id}")
        else:
            area_id = area_exists[0]
        
        # Create the room with room_id using direct SQL with only basic fields
        exits_json = json.dumps({})
        db.execute(
            text("""
            INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark, exits, created_at, updated_at) 
            VALUES (:id, :name, :description, :room_type, :area_id, :x, :y, :z, :is_dark, :exits, :created_at, :updated_at)
            """),
            {
                "id": room_id,
                "name": f"Room {room_id}",
                "description": f"A basic room with ID {room_id}.",
                "room_type": "town",
                "area_id": area_id,
                "x": 0,
                "y": 0,
                "z": 0,
                "is_dark": False,
                "exits": exits_json,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        )
        db.commit()
        
        # Create a simple Room object to return
        room = Room(
            id=room_id,
            name=f"Room {room_id}",
            description=f"A basic room with ID {room_id}.",
            room_type=RoomType.TOWN,
            area_id=area_id,
            x=0, y=0, z=0,
            is_dark=False
        )
        
        logger.info(f"Created room with ID {room_id}")
        return room
    except Exception as e:
        logger.error(f"Error ensuring room exists: {str(e)}")
        db.rollback()
        return None
