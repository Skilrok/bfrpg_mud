#!/usr/bin/env python3
"""
Script to check character and character item tables
"""

import logging
import traceback

from sqlalchemy import inspect, text

from app.database import get_db, get_db_context
from app.models import Character, CharacterItem, User

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_database():
    """Check the database for characters and character items"""
    logger.info("Checking database records")

    # Get database session
    with get_db_context() as db:
        try:
            # Check tables using raw SQL to avoid ORM mapping issues
            # Get character count
            char_count = db.execute(text("SELECT COUNT(*) FROM characters")).scalar()
            logger.info(f"Total characters: {char_count}")

            # Check if character_items table exists
            try:
                item_count = db.execute(
                    text("SELECT COUNT(*) FROM character_items")
                ).scalar()
                logger.info(f"Total character items: {item_count}")

                # Get average items per character
                if char_count > 0:
                    avg_items = item_count / char_count
                    logger.info(f"Average items per character: {avg_items:.1f}")

                # Get first character details
                char = db.execute(
                    text("SELECT id, name FROM characters LIMIT 1")
                ).first()
                if char:
                    char_id, char_name = char
                    logger.info(f"First character: {char_name} (ID: {char_id})")

                    # Get items for this character
                    items = db.execute(
                        text(
                            " +
            "SELECT item_id, is_equipped, equip_slot FROM"character_items WHERE character_id = :char_id"
                        ),
                        {"char_id": char_id},
                    ).fetchall()

                    logger.info(f"Character has {len(items)} items")

                    # Show equipped items
                    equipped = [item for item in items if item[1]]  # is_equipped = True
                    logger.info(f"Equipped items: {len(equipped)}")

                    # Show a few items
                    for i, (item_id, is_equipped, equip_slot) in enumerate(items[:5]):
                        # Try to get item name
                        try:
                            item_name = (
                                db.execute(
                                    text("SELECT name FROM items WHERE id = :item_id"),
                                    {"item_id": item_id},
                                ).scalar()
                                or "unknown"
                            )
                        except Exception:
                            item_name = "unknown"

                        logger.info(
                            f"  Item {i+1}: ID {item_id} - {item_name} (equipped: {is_equipped}, slot: {equip_slot})"
                        )
                else:
                    logger.warning("No characters found in database")

            except Exception as e:
                logger.error(f"Error checking character_items table: {str(e)}")
                logger.info(
                    " +
            "The character_items table may not exist yet - run the"migration first"
                )

        except Exception as e:
            logger.error(f"Error checking database: {str(e)}")
            traceback.print_exc()

    # Check characters
    try:
        character_count = db.query(Character).count()
        logger.info(f"Total characters: {character_count}")

        # Check character details
        characters = db.query(Character).all()
        logger.info("\nCharacter details:")
        for char in characters:
            logger.info(
                f"ID: {char.id}, Name: {char.name}, Race: {char.race}, Class: {char.character_class}"
            )
            logger.info(f"  Owner/User ID: {char.user_id}")
            if char.user:
                logger.info(f"  Owner Username: {char.user.username}")

            # Check if owner property works
            assert char.owner is char.user, "Owner property doesn't match user property"

        # Check character items
        item_count = db.query(CharacterItem).count()
        logger.info(f"\nTotal character items: {item_count}")

        logger.info("\nDatabase integrity check completed successfully!")

    except Exception as e:
        logger.error(f"Error during database check: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    check_database()
