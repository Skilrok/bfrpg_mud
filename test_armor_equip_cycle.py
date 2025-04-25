import json
import logging

from app.database import get_db_context
from app.models.character import Character
from app.models.item import Item
from app.routers.characters import equip_item, unequip_item

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_armor_equip_cycle(character_name):
    """
    Test the full cycle of unequipping and equipping armor for a character.
    Verifies that the armor class (AC) is correctly updated during each operation.

    Args:
        character_name: The name of the character to test
    """
    # Create database session
    with get_db_context() as db:
        logger.info(
            f"Starting armor equip/unequip cycle test for character: {character_name}"
        )

        # Query the character
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            logger.error(f"Character '{character_name}' not found in database.")
            return

        # Store initial state
        initial_ac = character.armor_class
        initial_equipment = json.loads(json.dumps(character.equipment))
        initial_inventory = json.loads(json.dumps(character.inventory))

        logger.info(
            f"Initial character state - AC: {initial_ac}, Equipment: {initial_equipment}"
        )

        # Check if armor is currently equipped
        armor_slot = character.equipment.get("armor")
        has_equipped_armor = armor_slot is not None

        if has_equipped_armor:
            # Get the equipped armor's details
            armor_id = armor_slot.get("id")
            armor_item = db.query(Item).filter(Item.id == armor_id).first()
            armor_ac_bonus = armor_item.properties.get("ac_bonus", 0)

            logger.info(
                f"Found equipped armor: {armor_item.name} with AC bonus: {armor_ac_bonus}"
            )

            # Calculate expected AC after unequipping
            shield_bonus = 0
            if character.equipment.get("shield"):
                shield_id = character.equipment.get("shield").get("id")
                shield_item = db.query(Item).filter(Item.id == shield_id).first()
                shield_bonus = shield_item.properties.get("ac_bonus", 0)

            # Calculate dexterity modifier
            dex_mod = (character.abilities["dexterity"] - 10) // 2
            expected_ac_unequipped = 10 + dex_mod + shield_bonus

            logger.info(
                f"Unequipping armor. Expected AC will be: {expected_ac_unequipped}"
            )

            # Unequip the armor
            unequip_item(character=character, slot="armor", db=db)
            db.commit()
            db.refresh(character)

            # Verify AC after unequipping
            logger.info(
                f"After unequipping - AC: {character.armor_class}, Expected: {expected_ac_unequipped}"
            )
            if character.armor_class != expected_ac_unequipped:
                logger.error(
                    f"AC mismatch after unequipping: Got {character.armor_class}, Expected {expected_ac_unequipped}"
                )

            # Now re-equip the armor
            # First find the armor in inventory
            armor_in_inventory = False
            armor_inventory_index = None

            for idx, item in enumerate(character.inventory):
                if item.get("id") == armor_id:
                    armor_in_inventory = True
                    armor_inventory_index = idx
                    break

            if armor_in_inventory:
                logger.info(
                    f"Found armor in inventory at position {armor_inventory_index}, re-equipping"
                )

                # Expected AC after re-equipping
                expected_ac_reequipped = expected_ac_unequipped + armor_ac_bonus
                logger.info(
                    f"Re-equipping armor. Expected AC will be: {expected_ac_reequipped}"
                )

                # Re-equip the armor
                equip_item(
                    character=character, inventory_index=armor_inventory_index, db=db
                )
                db.commit()
                db.refresh(character)

                # Verify AC after re-equipping
                logger.info(
                    f"After re-equipping - AC: {character.armor_class}, Expected: {expected_ac_reequipped}"
                )
                if character.armor_class != expected_ac_reequipped:
                    logger.error(
                        f"AC mismatch after re-equipping: Got {character.armor_class}, Expected {expected_ac_reequipped}"
                    )
            else:
                logger.error(
                    f"Could not find the unequipped armor in inventory to re-equip"
                )
        else:
            logger.info(
                "No armor currently equipped. Checking inventory for armor to equip."
            )

            # Find armor in inventory to equip
            armor_found = False
            armor_inventory_index = None
            armor_item = None

            for idx, item_data in enumerate(character.inventory):
                item_id = item_data.get("id")
                item = db.query(Item).filter(Item.id == item_id).first()
                if item and item.type == "armor" and item.subtype != "shield":
                    armor_found = True
                    armor_inventory_index = idx
                    armor_item = item
                    break

            if armor_found:
                logger.info(
                    f"Found armor in inventory: {armor_item.name} at position {armor_inventory_index}"
                )

                # Calculate dexterity modifier
                dex_mod = (character.abilities["dexterity"] - 10) // 2

                # Calculate shield bonus if any
                shield_bonus = 0
                if character.equipment.get("shield"):
                    shield_id = character.equipment.get("shield").get("id")
                    shield_item = db.query(Item).filter(Item.id == shield_id).first()
                    shield_bonus = shield_item.properties.get("ac_bonus", 0)

                # Calculate expected AC after equipping
                armor_ac_bonus = armor_item.properties.get("ac_bonus", 0)
                expected_ac_equipped = 10 + dex_mod + shield_bonus + armor_ac_bonus

                logger.info(
                    f"Equipping armor. Expected AC will be: {expected_ac_equipped}"
                )

                # Equip the armor
                equip_item(
                    character=character, inventory_index=armor_inventory_index, db=db
                )
                db.commit()
                db.refresh(character)

                # Verify AC after equipping
                logger.info(
                    f"After equipping - AC: {character.armor_class}, Expected: {expected_ac_equipped}"
                )
                if character.armor_class != expected_ac_equipped:
                    logger.error(
                        f"AC mismatch after equipping: Got {character.armor_class}, Expected {expected_ac_equipped}"
                    )

                # Now unequip the armor to test full cycle
                logger.info(f"Now unequipping the armor to complete the test cycle")
                expected_ac_unequipped = 10 + dex_mod + shield_bonus

                # Unequip the armor
                unequip_item(character=character, slot="armor", db=db)
                db.commit()
                db.refresh(character)

                # Verify AC after unequipping
                logger.info(
                    f"After unequipping - AC: {character.armor_class}, Expected: {expected_ac_unequipped}"
                )
                if character.armor_class != expected_ac_unequipped:
                    logger.error(
                        f"AC mismatch after unequipping: Got {character.armor_class}, Expected {expected_ac_unequipped}"
                    )
            else:
                logger.error("No suitable armor found in inventory to test equipping.")

        # Test completed, log results
        logger.info(f"Armor equip/unequip cycle test completed for {character_name}")


# Run the test for Skilrok
if __name__ == "__main__":
    test_armor_equip_cycle("Skilrok")
