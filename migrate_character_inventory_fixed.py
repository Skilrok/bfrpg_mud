#!/usr/bin/env python3
"""
Fixed migration script to transfer character inventory data from JSON fields to CharacterItem table
using direct SQL to avoid ORM relationship issues.
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


def verify_migration():
    """Verify that the migration was successful by comparing old and new data"""
    logger.info("Verifying migration results using direct SQL")

    with get_db_context() as db:
        try:
            # Get all characters using raw SQL to avoid ORM validation
            characters_raw = db.execute(
                text(
                    """
                SELECT id, name, inventory, equipment FROM characters
            """
                )
            ).fetchall()

            total_success = 0
            total_failure = 0
            failed_characters = []

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
                    logger.warning(f"Inventory JSON: {inventory_json}")
                    logger.warning(f"Equipment JSON: {equipment_json}")
                    continue

                # Get new character items using direct SQL
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

                            # Get item name for better logging
                            item_name_result = db.execute(
                                text(
                                    """
                                SELECT name FROM items WHERE id = :item_id
                            """
                                ),
                                {"item_id": item_id},
                            ).first()

                            item_name = (
                                item_name_result[0] if item_name_result else "Unknown"
                            )

                            logger.warning(
                                f"  Expected: {slot} -> {item_name} (ID: {item_id})"
                            )
                            if slot in new_equipment:
                                new_item_name_result = db.execute(
                                    text(
                                        """
                                    SELECT name FROM items WHERE id = :item_id
                                """
                                    ),
                                    {"item_id": new_equipment[slot]},
                                ).first()

                                new_item_name = (
                                    new_item_name_result[0]
                                    if new_item_name_result
                                    else "Unknown"
                                )
                                logger.warning(
                                    f"  Actual: {slot} -> {new_item_name} (ID: {new_equipment[slot]})"
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
                    if char_name not in failed_characters:
                        failed_characters.append(char_name)

                    # Log detailed differences
                    if not equipment_match:
                        logger.error(f"Old equipment: {old_equipment}")
                        logger.error(f"New equipment: {new_equipment}")

                        # Try to auto-fix the equipment issues
                        fix_character_equipment(db, char_id, char_name, old_equipment)

                    total_failure += 1

            logger.info(
                f"Verification complete: {total_success} successful, {total_failure} failed"
            )

            if total_failure > 0:
                logger.warning(f"Failed characters: {', '.join(failed_characters)}")

                # One last verification attempt after fixes
                if verify_again():
                    logger.info("All issues resolved after auto-fixes")
                    return True

                logger.warning(
                    "There were verification failures that couldn't be auto-fixed."
                )
                return False
            return True

        except Exception as e:
            logger.error(f"Error during verification: {str(e)}")
            traceback.print_exc()
            return False


def fix_character_equipment(db, char_id, char_name, old_equipment):
    """Fix equipment issues for a character using direct SQL"""
    logger.info(f"Attempting to fix equipment issues for {char_name} (ID: {char_id})")

    if not isinstance(old_equipment, dict):
        logger.warning(f"Invalid equipment format for {char_name}")
        return False

    try:
        # Get equipment details for logging
        equipment_details = {}
        for slot, item_id in old_equipment.items():
            item_result = db.execute(
                text(
                    """
                SELECT name FROM items WHERE id = :item_id
            """
                ),
                {"item_id": item_id},
            ).first()

            if item_result:
                equipment_details[slot] = f"{item_result[0]} (ID: {item_id})"
            else:
                equipment_details[slot] = f"Unknown (ID: {item_id})"

        logger.info(f"Equipment details to fix: {equipment_details}")

        # Fix each equipment slot
        for slot, item_id in old_equipment.items():
            # Check if the item exists first
            item_exists = db.execute(
                text(
                    """
                SELECT id FROM items WHERE id = :item_id
            """
                ),
                {"item_id": item_id},
            ).first()

            if not item_exists:
                logger.warning(f"Cannot fix: Item {item_id} not found in database")
                continue

            # Check if the character already has this item but not equipped correctly
            existing_item = db.execute(
                text(
                    """
                SELECT id, is_equipped, equip_slot
                FROM character_items
                WHERE character_id = :char_id AND item_id = :item_id
            """
                ),
                {"char_id": char_id, "item_id": item_id},
            ).first()

            if existing_item:
                # Update existing item
                item_id_in_db, is_equipped, current_slot = existing_item
                logger.info(
                    f"Updating existing item {item_id} to be equipped in slot {slot}"
                )

                db.execute(
                    text(
                        """
                    UPDATE character_items
                    SET is_equipped = 1, equip_slot = :slot
                    WHERE character_id = :char_id AND item_id = :item_id
                """
                    ),
                    {"char_id": char_id, "item_id": item_id, "slot": slot},
                )
            else:
                # Delete any existing item in this slot first
                db.execute(
                    text(
                        """
                    UPDATE character_items
                    SET is_equipped = 0, equip_slot = NULL
                    WHERE character_id = :char_id AND equip_slot = :slot
                """
                    ),
                    {"char_id": char_id, "slot": slot},
                )

                # Create new item
                logger.info(f"Creating new equipped item {item_id} in slot {slot}")
                db.execute(
                    text(
                        """
                    INSERT INTO character_items (character_id, item_id, quantity, is_equipped, equip_slot)
                    VALUES (:char_id, :item_id, 1, 1, :slot)
                """
                    ),
                    {"char_id": char_id, "item_id": item_id, "slot": slot},
                )

        # Commit changes
        db.commit()
        logger.info(f"Fixed equipment issues for {char_name}")

        # Verify the fixes worked
        verify_character_equipment(db, char_id, char_name, old_equipment)

        return True

    except Exception as e:
        logger.error(f"Error fixing equipment: {str(e)}")
        traceback.print_exc()
        db.rollback()
        return False


def verify_character_equipment(db, char_id, char_name, old_equipment):
    """Verify equipment fixes for a single character"""
    logger.info(f"Verifying equipment fixes for {char_name} (ID: {char_id})")

    try:
        # Get current equipment
        char_items = db.execute(
            text(
                """
            SELECT item_id, equip_slot
            FROM character_items
            WHERE character_id = :char_id AND is_equipped = 1
        """
            ),
            {"char_id": char_id},
        ).fetchall()

        new_equipment = {}
        for item_id, equip_slot in char_items:
            if equip_slot:
                new_equipment[equip_slot] = item_id

        # Check if all old equipment is properly set
        all_fixed = True
        for slot, item_id in old_equipment.items():
            if slot not in new_equipment or new_equipment[slot] != item_id:
                all_fixed = False
                logger.error(f"Still missing/wrong after fix: {slot} - {item_id}")

        if all_fixed:
            logger.info(f"All equipment issues fixed for {char_name}")
        else:
            logger.error(f"Failed to fix all equipment issues for {char_name}")
            logger.error(f"Original equipment: {old_equipment}")
            logger.error(f"Current equipment: {new_equipment}")

        return all_fixed

    except Exception as e:
        logger.error(f"Error verifying equipment fixes: {str(e)}")
        return False


def verify_again():
    """Perform one final verification pass after fixes"""
    logger.info("Performing final verification pass")

    with get_db_context() as db:
        try:
            # Get all characters using raw SQL
            characters_raw = db.execute(
                text(
                    """
                SELECT id, name, inventory, equipment FROM characters
            """
                )
            ).fetchall()

            all_success = True

            for char_row in characters_raw:
                char_id, char_name, inventory_json, equipment_json = char_row

                # Parse JSON fields
                try:
                    old_equipment = (
                        json.loads(equipment_json)
                        if equipment_json and not isinstance(equipment_json, dict)
                        else equipment_json or {}
                    )
                except json.JSONDecodeError:
                    continue

                if not isinstance(old_equipment, dict):
                    continue

                # We only care about equipment for the final check
                char_items = db.execute(
                    text(
                        """
                    SELECT item_id, equip_slot
                    FROM character_items
                    WHERE character_id = :char_id AND is_equipped = 1
                """
                    ),
                    {"char_id": char_id},
                ).fetchall()

                new_equipment = {}
                for item_id, equip_slot in char_items:
                    if equip_slot:
                        new_equipment[equip_slot] = item_id

                # Check for missing equipment
                for slot, item_id in old_equipment.items():
                    if slot not in new_equipment or new_equipment[slot] != item_id:
                        all_success = False
                        logger.error(
                            f"Still missing equipment for {char_name}: {slot} -> {item_id}"
                        )

            return all_success

        except Exception as e:
            logger.error(f"Error during final verification: {str(e)}")
            return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Verify character inventory migration")
    args = parser.parse_args()

    verify_migration()
