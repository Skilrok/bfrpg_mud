#!/usr/bin/env python3
"""
Script to verify the character inventory migration using the ORM after relationship fixes.
"""

import json
import logging
import traceback

from app.database import get_db_context
from app.models.character import Character
from app.models.character_item import CharacterItem

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def verify_migration():
    """Verify the character inventory migration using the ORM"""
    logger.info("Verifying character inventory migration using ORM")

    with get_db_context() as db:
        try:
            # Get all characters
            characters = db.query(Character).all()
            logger.info(f"Found {len(characters)} characters in the database")

            total_success = 0
            total_items = 0
            failed_characters = []

            for character in characters:
                # Get character items through ORM relationship
                character_items = (
                    db.query(CharacterItem)
                    .filter(CharacterItem.character_id == character.id)
                    .all()
                )

                logger.info(
                    f"Character: {character.name} (ID: {character.id}) - {len(character_items)} items"
                )

                # Get equipped items
                equipped_items = [item for item in character_items if item.is_equipped]
                logger.info(f"  Equipped items: {len(equipped_items)}")

                # Show some item details
                for i, item in enumerate(character_items[:3]):  # Show first 3 items
                    item_name = (
                        item.item.name
                        if hasattr(item, "item") and item.item
                        else f"Item ID: {item.item_id}"
                    )
                    equipped_str = (
                        f"equipped in {item.equip_slot}"
                        if item.is_equipped
                        else "not equipped"
                    )
                    logger.info(f"  Item {i+1}: {item_name} ({equipped_str})")

                # Check backward compatibility properties
                logger.info("Testing backward compatibility properties:")

                # Check inventory property
                if hasattr(character, "inventory"):
                    inventory = character.inventory
                    logger.info(f"  inventory property: {len(inventory)} items")

                    # Verify inventory matches CharacterItems
                    if len(inventory) == len(character_items):
                        logger.info(
                            "  ✅ inventory property length matches CharacterItems count"
                        )
                    else:
                        logger.warning(
                            f"  ❌ inventory property length mismatch: {len(inventory)} vs {len(character_items)}"
                        )
                else:
                    logger.warning("  ❌ Character has no inventory property")

                # Check equipment property
                if hasattr(character, "equipment"):
                    equipment = character.equipment
                    logger.info(
                        f"  equipment property: {len(equipment)} equipped items"
                    )

                    # Verify equipment matches equipped CharacterItems
                    if len(equipment) == len(equipped_items):
                        logger.info(
                            "  ✅ equipment property length matches equipped CharacterItems count"
                        )
                    else:
                        logger.warning(
                            f"  ❌ equipment property length mismatch: {len(equipment)} vs {len(equipped_items)}"
                        )
                else:
                    logger.warning("  ❌ Character has no equipment property")

                # Track statistics
                total_success += 1
                total_items += len(character_items)

            # Calculate average items per character
            if total_success > 0:
                avg_items = total_items / total_success
                logger.info(f"Average items per character: {avg_items:.1f}")

            logger.info(f"Verification complete: {total_success} characters processed")
            return True

        except Exception as e:
            logger.error(f"Error during verification: {str(e)}")
            traceback.print_exc()
            return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify character inventory migration")
    args = parser.parse_args()

    verify_migration()
