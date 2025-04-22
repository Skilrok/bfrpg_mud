#!/usr/bin/env python
"""
Test script to diagnose character location issues
"""
import json
import logging
import os
import sys
from datetime import datetime

import bcrypt
from passlib.context import CryptContext
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    text,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import and_, insert, select

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.database import SessionLocal, engine
from app.models import Character, User
from app.models.room import Area, CharacterLocation, Room, RoomType

# Set up password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


# Define the characters table
metadata = MetaData()
characters = Table(
    "characters",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("description", String),
    Column("level", Integer),
    Column("experience", Integer),
    Column("race", String),
    Column("character_class", String),
    Column("strength", Integer),
    Column("intelligence", Integer),
    Column("wisdom", Integer),
    Column("dexterity", Integer),
    Column("constitution", Integer),
    Column("charisma", Integer),
    Column("hit_points", Integer),
    Column("armor_class", Integer),
    Column("equipment", JSON),
    Column("inventory", JSON),
    Column("gold", Integer),
    Column("languages", String),
    Column("save_death_ray_poison", Integer),
    Column("save_magic_wands", Integer),
    Column("save_paralysis_petrify", Integer),
    Column("save_dragon_breath", Integer),
    Column("save_spells", Integer),
    Column("special_abilities", JSON),
    Column("spells_known", JSON),
    Column("thief_abilities", JSON),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
)


async def create_test_user(session: AsyncSession) -> int:
    """Create a test user if it doesn't exist."""
    try:
        # Check if test user already exists
        result = await session.execute(
            text("SELECT id FROM users WHERE username = 'testuser' LIMIT 1")
        )
        user = result.scalar_one_or_none()

        if not user:
            logger.info("Creating test user")

            # Hash password
            hashed_password = bcrypt.hashpw(
                "testpassword".encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # Create user
            result = await session.execute(
                text(
                    """
                    INSERT INTO users (username, password_hash, email, is_admin, created_at, updated_at)
                    VALUES (:username, :password_hash, :email, :is_admin, :created_at, :updated_at)
                    RETURNING id
                """
                ),
                {
                    "username": "testuser",
                    "password_hash": hashed_password,
                    "email": "test@example.com",
                    "is_admin": False,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            )
            user_id = result.scalar_one()
            logger.info(f"Created test user with ID: {user_id}")
        else:
            user_id = user
            logger.info(f"Found existing test user with ID: {user_id}")

        await session.commit()
        return user_id
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating test user: {e}")
        raise


async def create_test_character(session: AsyncSession, user_id: int) -> int:
    """Create a test character for the user if it doesn't exist."""
    try:
        # Check if the test character already exists
        result = await session.execute(
            text(
                "SELECT id FROM characters WHERE user_id = :user_id AND name = 'TestChar' LIMIT 1"
            ),
            {"user_id": user_id},
        )
        character = result.scalar_one_or_none()

        if not character:
            logger.info("Creating test character")

            # Create character
            result = await session.execute(
                text(
                    """
                    INSERT INTO characters (
                        user_id, name, race, character_class, level,
                        strength, dexterity, constitution, intelligence, wisdom, charisma,
                        hit_points, max_hit_points, armor_class,
                        experience_points, gold, room_id, properties, inventory,
                        created_at, updated_at
                    )
                    VALUES (
                        :user_id, 'TestChar', 'HUMAN', 'FIGHTER', 1,
                        10, 10, 10, 10, 10, 10,
                        8, 8, 10,
                        0, 100, 1, '{}', '[]',
                        :created_at, :updated_at
                    )
                    RETURNING id
                """
                ),
                {
                    "user_id": user_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            )
            character_id = result.scalar_one()
            logger.info(f"Created test character with ID: {character_id}")
        else:
            character_id = character
            logger.info(f"Found existing test character with ID: {character_id}")

        await session.commit()
        return character_id
    except Exception as e:
        await session.rollback()
        logger.error(f"Error creating test character: {e}")
        raise


async def ensure_starting_area_and_room(session: AsyncSession) -> int:
    """Make sure the starting area and room exist."""
    try:
        # Check if the starting area exists
        result = await session.execute(
            text("SELECT id FROM areas WHERE name = 'Starting Village' LIMIT 1")
        )
        area = result.scalar_one_or_none()

        if not area:
            logger.info("Creating starting area")

            # Create area
            result = await session.execute(
                text(
                    """
                    INSERT INTO areas (name, description, is_dungeon, is_hidden, properties, created_at, updated_at)
                    VALUES (:name, :description, :is_dungeon, :is_hidden, :properties, :created_at, :updated_at)
                    RETURNING id
                """
                ),
                {
                    "name": "Starting Village",
                    "description": "A peaceful village where adventures begin.",
                    "is_dungeon": False,
                    "is_hidden": False,
                    "properties": "{}",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            )
            area_id = result.scalar_one()
            logger.info(f"Created starting area with ID: {area_id}")
        else:
            area_id = area
            logger.info(f"Found existing starting area with ID: {area_id}")

        # Check if room 1 exists
        result = await session.execute(
            text("SELECT id FROM rooms WHERE id = 1 LIMIT 1")
        )
        room = result.scalar_one_or_none()

        if not room:
            logger.info("Creating starting room")

            # Create room
            await session.execute(
                text(
                    """
                    INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark, properties, created_at, updated_at)
                    VALUES (:id, :name, :description, :room_type, :area_id, :x, :y, :z, :is_dark, :properties, :created_at, :updated_at)
                """
                ),
                {
                    "id": 1,
                    "name": "Village Square",
                    "description": "The central square of the starting village.",
                    "room_type": "TOWN",
                    "area_id": area_id,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "is_dark": False,
                    "properties": "{}",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            )
            logger.info("Created starting room with ID: 1")
        else:
            logger.info("Found existing starting room with ID: 1")

        await session.commit()
        return 1  # Return the room ID
    except Exception as e:
        await session.rollback()
        logger.error(f"Error ensuring starting area and room: {e}")
        raise


def test_character_location(character_id):
    """Test character location functionality with direct SQL"""
    db = SessionLocal()
    try:
        # Check if character already has a location
        location_data = db.execute(
            text(
                "SELECT id, room_id FROM character_locations WHERE character_id = :char_id"
            ),
            {"char_id": character_id},
        ).fetchone()

        if location_data:
            logger.info(
                f"Character {character_id} already has location {location_data[0]} in room {location_data[1]}"
            )

            # Update to room 1 to verify update works
            db.execute(
                text(
                    "UPDATE character_locations SET room_id = 1 WHERE character_id = :char_id"
                ),
                {"char_id": character_id},
            )
            db.commit()
            logger.info(f"Updated character {character_id} location to room 1")
        else:
            # Create new location entry with direct SQL
            logger.info(f"Creating new location for character {character_id}")
            db.execute(
                text(
                    """
                INSERT INTO character_locations (character_id, room_id, created_at, updated_at)
                VALUES (:char_id, :room_id, :created_at, :updated_at)
                """
                ),
                {
                    "char_id": character_id,
                    "room_id": 1,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                },
            )
            db.commit()
            logger.info(f"Created new location for character {character_id} in room 1")

        # Verify location was created/updated
        verify_data = db.execute(
            text(
                "SELECT id, room_id FROM character_locations WHERE character_id = :char_id"
            ),
            {"char_id": character_id},
        ).fetchone()

        if verify_data and verify_data[1] == 1:
            logger.info(f"Verified character {character_id} is in room 1")
            return True
        else:
            logger.error(
                f"Failed to verify character {character_id} location in room 1"
            )
            return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error testing character location: {str(e)}")
        return False
    finally:
        db.close()


def test_character_location_in_look_command(character_id):
    """Test how the look command retrieves character location"""
    db = SessionLocal()
    try:
        # Print character location with direct SQL
        location_data = db.execute(
            text(
                "SELECT room_id FROM character_locations WHERE character_id = :char_id"
            ),
            {"char_id": character_id},
        ).fetchone()

        if location_data:
            logger.info(
                f"Character {character_id} is in room {location_data[0]} (direct SQL)"
            )
        else:
            logger.info(f"Character {character_id} has no location (direct SQL)")

        # Try to get room data
        if location_data:
            room_data = db.execute(
                text("SELECT id, name, description FROM rooms WHERE id = :room_id"),
                {"room_id": location_data[0]},
            ).fetchone()

            if room_data:
                logger.info(f"Room data: ID={room_data[0]}, Name={room_data[1]}")
            else:
                logger.error(f"Room with ID {location_data[0]} not found")

        # Get location using ORM for comparison
        char_location = (
            db.query(CharacterLocation)
            .filter(CharacterLocation.character_id == character_id)
            .first()
        )

        if char_location:
            logger.info(
                f"Character {character_id} is in room {char_location.room_id} (ORM)"
            )

            # Try to get room through relationship
            if char_location.room:
                logger.info(
                    f"Room through relationship: ID={char_location.room.id}, Name={char_location.room.name}"
                )
            else:
                logger.error("Room relationship is None")
        else:
            logger.info(f"Character {character_id} has no location (ORM)")

        return True
    except Exception as e:
        logger.error(f"Error testing look command location: {str(e)}")
        return False
    finally:
        db.close()


async def test_character_location():
    """Test character location functionality."""
    try:
        async with engine.begin() as conn:
            session = AsyncSession(conn)

            # Ensure the starting area and room exist
            await ensure_starting_area_and_room(session)

            # Create a test user if needed
            user_id = await create_test_user(session)

            # Create a test character if needed
            character_id = await create_test_character(session, user_id)

            if not character_id:
                logger.error("Failed to create test character")
                return

            # Test setting and getting character location
            area_id = 1
            room_id = 1
            await session.execute(
                text(
                    """
                    INSERT INTO character_locations (character_id, room_id, area_id, x, y, z, created_at, updated_at)
                    VALUES (:character_id, :room_id, :area_id, 0, 0, 0, :created_at, :updated_at)
                    ON CONFLICT (character_id) DO UPDATE
                    SET room_id = :room_id, area_id = :area_id, x = 0, y = 0, z = 0, updated_at = :updated_at
                    """
                ),
                {
                    "character_id": character_id,
                    "room_id": room_id,
                    "area_id": area_id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                },
            )
            await session.commit()

            # Now retrieve the character location
            result = await session.execute(
                text(
                    """
                    SELECT cl.character_id, cl.room_id, cl.area_id, r.name as room_name, a.name as area_name
                    FROM character_locations cl
                    JOIN rooms r ON cl.room_id = r.id
                    JOIN areas a ON cl.area_id = a.id
                    WHERE cl.character_id = :character_id
                    """
                ),
                {"character_id": character_id},
            )

            location = result.mappings().one_or_none()
            if location:
                logger.info(
                    f"Character ID: {location['character_id']} is in "
                    f"Room: {location['room_name']} (ID: {location['room_id']}) in "
                    f"Area: {location['area_name']} (ID: {location['area_id']})"
                )
            else:
                logger.error(
                    f"Character location not found for character ID: {character_id}"
                )

            # Test look command with the character
            await test_character_location_in_look_command(character_id)

    except Exception as e:
        logger.error(f"Error in test_character_location: {e}")
        raise


async def test_character_location_in_look_command(session, character_id):
    """Test character location through the look command."""
    try:
        # Get character's current room
        result = await session.execute(
            text(
                """
                SELECT r.id, r.name, r.description
                FROM character_locations cl
                JOIN rooms r ON cl.room_id = r.id
                WHERE cl.character_id = :character_id
                """
            ),
            {"character_id": character_id},
        )

        room = result.mappings().one_or_none()
        if room:
            logger.info(f"Character is in room: {room['name']} - {room['description']}")

            # Get character information
            result = await session.execute(
                text(
                    """
                    SELECT name, race, character_class
                    FROM characters
                    WHERE id = :character_id
                    """
                ),
                {"character_id": character_id},
            )

            character = result.mappings().one_or_none()
            if character:
                logger.info(
                    f"Character info: {character['name']} - "
                    f"{character['race']} {character['character_class']}"
                )
            else:
                logger.error(f"Character not found with ID: {character_id}")
        else:
            logger.error(f"Room not found for character ID: {character_id}")

    except Exception as e:
        logger.error(f"Error in test_character_location_in_look_command: {e}")
        raise


# Execute the test
if __name__ == "__main__":
    import asyncio

    asyncio.run(test_character_location())
