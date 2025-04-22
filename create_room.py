"""
Create a starting area and room for new character placement
"""

import logging
import os
import sys

from sqlalchemy import text
from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models.room import Area, Room, RoomType


def create_starter_area():
    """Create the starter area and initial room"""
    db = SessionLocal()

    try:
        # Check if starting area already exists
        try:
            # Manually construct the query to avoid schema mismatch
            areas = db.execute(
                text(
                    "SELECT id, name FROM areas WHERE name = 'Starting Village' LIMIT 1"
                )
            ).fetchall()
            if areas:
                starting_area_id = areas[0][0]
                starting_area_name = areas[0][1]
                logger.info(
                    f"Starting area already exists: {starting_area_name} (ID: {starting_area_id})"
                )
            else:
                logger.info("Creating starting area...")
                # Insert the area with direct SQL
                insert_sql = text(
                    "INSERT INTO areas (name, description, level_range, is_dungeon, is_hidden, properties, created_at, updated_at) "
                    "VALUES ('Starting Village', 'A small village where adventures begin', '1-3', 0, 0, '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) "
                    "RETURNING id"
                )
                result = db.execute(insert_sql)
                starting_area_id = result.fetchone()[0]
                db.commit()
                logger.info(f"Created area: Starting Village (ID: {starting_area_id})")

            # Check if starting room exists
            rooms = db.execute(
                text("SELECT id, name FROM rooms WHERE id = 1 LIMIT 1")
            ).fetchall()
            if rooms:
                starting_room_id = rooms[0][0]
                starting_room_name = rooms[0][1]
                logger.info(
                    f"Starting room already exists: {starting_room_name} (ID: {starting_room_id})"
                )
            else:
                logger.info("Creating starting room...")
                # Insert the room with direct SQL
                room_insert_sql = text(
                    "INSERT INTO rooms (id, name, description, room_type, area_id, x, y, z, is_dark, exits, properties, created_at, updated_at) "
                    f"VALUES (1, 'Village Square', 'The central square of the starting village. Paths lead in all directions.', '{RoomType.TOWN}', {starting_area_id}, 0, 0, 0, 0, '{{}}', '{{}}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                )
                db.execute(room_insert_sql)
                db.commit()
                logger.info(f"Created room: Village Square (ID: 1)")

            logger.info("Starter area setup complete.")
        except Exception as e:
            db.rollback()
            logger.error(f"Database operation error: {e}")

    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_starter_area()
