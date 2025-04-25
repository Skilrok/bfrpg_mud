#!/usr/bin/env python3
"""
Script to check characters directly from the database without using the ORM.
"""

import json
import logging
import traceback

from sqlalchemy import text

from app.database import get_db_context

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_characters_direct():
    """Check characters directly using SQL instead of ORM"""
    logger.info("Checking characters directly from database")

    with get_db_context() as db:
        try:
            # Get all characters
            chars = db.execute(
                text(
                    """
                SELECT id, name, race, character_class, inventory, equipment
                FROM characters
            """
                )
            ).fetchall()

            logger.info(f"Found {len(chars)} characters in the database")

            total_items = 0

            # Process each character
            for char_row in chars:
                char_id, char_name, race, char_class, inventory_json, equipment_json = (
                    char_row
                )
                logger.info(
                    f"Character: {char_name} (ID: {char_id}, Race: {race}, Class: {char_class})"
                )

                # Parse JSON fields
                try:
                    inventory = (
                        json.loads(inventory_json)
                        if inventory_json and not isinstance(inventory_json, dict)
                        else inventory_json or {}
                    )
                    equipment = (
                        json.loads(equipment_json)
                        if equipment_json and not isinstance(equipment_json, dict)
                        else equipment_json or {}
                    )
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON data for character {char_name}")
                    continue

                # Count inventory items
                inventory_count = len(inventory) if isinstance(inventory, dict) else 0
                logger.info(f"  Inventory: {inventory_count} items")

                # Count equipped items
                equipment_count = len(equipment) if isinstance(equipment, dict) else 0
                logger.info(f"  Equipment: {equipment_count} equipped items")

                # Get character items
                char_items = db.execute(
                    text(
                        """
                    SELECT item_id, quantity, is_equipped, equip_slot
                    FROM character_items
                    WHERE character_id = :char_id
                """
                    ),
                    {"char_id": char_id},
                ).fetchall()

                # Count character items
                char_items_count = len(char_items)
                equipped_count = sum(1 for item in char_items if item[2])  # is_equipped
                logger.info(
                    f"  Character items: {char_items_count} total, {equipped_count} equipped"
                )

                # Show some items
                for i, (item_id, quantity, is_equipped, equip_slot) in enumerate(
                    char_items[:3]
                ):
                    # Get item name
                    item_name = (
                        db.execute(
                            text(
                                """
                        SELECT name FROM items WHERE id = :item_id
                    """
                            ),
                            {"item_id": item_id},
                        ).scalar()
                        or f"Item ID: {item_id}"
                    )

                    equipped_str = (
                        f"equipped in {equip_slot}" if is_equipped else "not equipped"
                    )
                    logger.info(
                        f"  Item {i+1}: {item_name} (quantity: {quantity}, {equipped_str})"
                    )

                # Verify inventory vs character_items consistency
                if inventory_count != char_items_count:
                    logger.warning(
                        f"  ⚠️ Inconsistency: {inventory_count} items in inventory JSON vs {char_items_count} in character_items table"
                    )

                if equipment_count != equipped_count:
                    logger.warning(
                        f"  ⚠️ Inconsistency: {equipment_count} items in equipment JSON vs {equipped_count} equipped in character_items table"
                    )

                total_items += char_items_count

            # Calculate average
            if chars:
                avg_items = total_items / len(chars)
                logger.info(f"Average items per character: {avg_items:.1f}")

            return True

        except Exception as e:
            logger.error(f"Error checking characters: {str(e)}")
            traceback.print_exc()
            return False


def run_migrate_verify():
    """Run the original migration verification script with direct SQL"""
    logger.info("Running migration verification with direct SQL")

    with get_db_context() as db:
        try:
            # Get all characters
            characters_raw = db.execute(
                text(
                    """
                SELECT id, name, inventory, equipment FROM characters
            """
                )
            ).fetchall()

            logger.info(f"Found {len(characters_raw)} characters to verify")

            total_success = 0
            total_failure = 0

            for char_row in characters_raw:
                char_id, char_name, inventory_json, equipment_json = char_row

                # Parse JSON fields
                try:
                    old_inventory = (
                        json.loads(inventory_json)
                        if inventory_json and not isinstance(inventory_json, dict)
                        else inventory_json or {}
                    )
                    old_equipment = (
                        json.loads(equipment_json)
                        if equipment_json and not isinstance(equipment_json, dict)
                        else equipment_json or {}
                    )
                except json.JSONDecodeError:
                    logger.warning(
                        f"Invalid JSON data for character {char_name} (ID: {char_id})"
                    )
                    continue

                # Get new character items
                char_items_raw = db.execute(
                    text(
                        """
                    SELECT item_id, quantity, is_equipped, equip_slot
                    FROM character_items
                    WHERE character_id = :char_id
                """
                    ),
                    {"char_id": char_id},
                ).fetchall()

                # Reconstruct inventory and equipment from character_items
                new_inventory = {}
                new_equipment = {}

                for item_row in char_items_raw:
                    item_id, quantity, is_equipped, equip_slot = item_row

                    # Add to new inventory
                    new_inventory[str(item_id)] = {
                        "item_id": item_id,
                        "quantity": quantity,
                        "equipped": is_equipped,
                        "slot": equip_slot,
                    }

                    # Add to new equipment if equipped
                    if is_equipped and equip_slot:
                        new_equipment[equip_slot] = item_id

                # Compare old and new
                inventory_match = True
                equipment_match = True

                # Check if all old equipment items are in new equipment
                if isinstance(old_equipment, dict):
                    for slot, item_id in old_equipment.items():
                        if slot not in new_equipment or new_equipment[slot] != item_id:
                            equipment_match = False
                            logger.warning(
                                f"Equipment slot {slot} mismatch for character {char_name}"
                            )
                            logger.warning(f"  Expected: {slot} -> (ID: {item_id})")
                            if slot in new_equipment:
                                logger.warning(
                                    f"  Actual: {slot} -> (ID: {new_equipment[slot]})"
                                )
                            else:
                                logger.warning(f"  Actual: {slot} -> Not equipped")

                if inventory_match and equipment_match:
                    logger.info(
                        f"Verification successful for character {char_name} (ID: {char_id})"
                    )
                    total_success += 1
                else:
                    logger.error(
                        f"Verification failed for character {char_name} (ID: {char_id})"
                    )
                    total_failure += 1

            logger.info(
                f"Verification complete: {total_success} successful, {total_failure} failed"
            )
            return total_failure == 0

        except Exception as e:
            logger.error(f"Error during verification: {str(e)}")
            traceback.print_exc()
            return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Check characters directly from database"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Run verification of migration"
    )
    args = parser.parse_args()

    if args.verify:
        run_migrate_verify()
    else:
        check_characters_direct()
