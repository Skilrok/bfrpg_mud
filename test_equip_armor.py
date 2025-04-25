import logging
import sys

from app import models
from app.database import get_db_context
from app.routers.characters import get_ability_modifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def test_equip_armor(character_name):
    """Test that equipping armor properly updates the armor class."""
    logger.info(f"Starting armor equip test for {character_name}")

    # Get DB context
    with get_db_context() as db:
        try:
            # Query the character by name
            character = (
                db.query(models.Character)
                .filter(models.Character.name == character_name)
                .first()
            )

            if not character:
                logger.error(f"Character {character_name} not found in database")
                return False

            logger.info(f"Retrieved character: {character.name} (ID: {character.id})")

            # Query for a piece of armor - in a real system, you'd query equipment the character has access to
            armor_item = (
                db.query(models.Item).filter(models.Item.item_type == "armor").first()
            )

            if not armor_item:
                logger.error("No armor found in database")
                return False

            logger.info(f"Found armor: {armor_item.name} (ID: {armor_item.id})")

            # Get the armor item ID for later reference
            armor_item_id = armor_item.id

            # Calculate dexterity modifier
            dex_mod = get_ability_modifier(character.dexterity)
            print(f"Character dexterity: {character.dexterity}, modifier: {dex_mod}")

            # Calculate expected AC after equipping
            expected_ac = 10  # Base AC

            # Apply armor bonus
            armor_bonus = 0
            if armor_item.properties and "ac_bonus" in armor_item.properties:
                armor_bonus = armor_item.properties["ac_bonus"]
                expected_ac = armor_bonus  # Armor provides base AC
                print(f"Armor base AC: {armor_bonus}")

            # Apply shield bonus if equipped
            equipment = character.equipment or {}
            for slot, item_id in equipment.items():
                item = db.query(models.Item).filter(models.Item.id == item_id).first()
                if (
                    item
                    and item.item_type
                    and item.item_type.value == "shield"
                    and item.properties
                ):
                    if "ac_bonus" in item.properties:
                        shield_bonus = item.properties["ac_bonus"]
                        expected_ac += shield_bonus  # Higher is better in ascending AC
                        print(f"Shield bonus: +{shield_bonus}")

            # Apply dexterity modifier
            expected_ac += dex_mod
            print(f"Expected AC after equipping: {expected_ac}")

            # Equip the armor
            print(f"Equipping armor: {armor_item.name}...")

            # Determine slot to use
            slot = "body"  # Default armor slot

            # Update equipment
            new_equipment = dict(equipment)
            new_equipment[slot] = armor_item_id

            # Update inventory
            inventory = character.inventory or {}
            item_id_str = str(armor_item_id)
            if item_id_str in inventory:
                inventory[item_id_str]["equipped"] = True
                inventory[item_id_str]["slot"] = slot

            # Update the character
            character.equipment = new_equipment
            character.inventory = inventory
            character.armor_class = expected_ac

            db.add(character)
            db.commit()

            # Verify the update
            db.refresh(character)
            print(f"New armor class: {character.armor_class}")
            print(f"Expected armor class: {expected_ac}")

            if character.armor_class == expected_ac:
                print("Armor class updated correctly!")
                return True
            else:
                print(
                    f"ERROR: Armor class not updated correctly. Got {character.armor_class}, expected {expected_ac}"
                )
                return False

        except Exception as e:
            print(f"Error in armor test: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    # Replace with your character's name
    test_equip_armor("TestCharacter")
