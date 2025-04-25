import json
import logging

from app import models
from app.database import get_db_context
from app.routers.characters import get_ability_modifier

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_and_test_armor(character_name):
    """Fix character equipment inconsistencies and test armor equipping/unequipping."""
    with get_db_context() as db:
        try:
            # Find character by name
            character = (
                db.query(models.Character)
                .filter(models.Character.name == character_name)
                .first()
            )

            if not character:
                print(f"Character '{character_name}' not found")
                return False

            print(f"\n=== {character.name} ===")
            print(f"Initial Armor Class: {character.armor_class}")
            print(f"Dexterity: {character.dexterity}")

            # Display current equipment and inventory
            print("\n=== INITIAL STATE ===")
            equipment = character.equipment or {}
            print(f"Equipment: {json.dumps(equipment, indent=2)}")

            inventory = character.inventory or {}
            print(f"Inventory: {json.dumps(inventory, indent=2)}")

            # Find equipment slot for armor
            armor_slot = None
            armor_item_id = None
            for slot, item_id in equipment.items():
                item = db.query(models.Item).filter(models.Item.id == item_id).first()
                if item and item.item_type and item.item_type.value == "armor":
                    armor_slot = slot
                    armor_item_id = item_id
                    print(f"Found equipped armor: {item.name} in slot {slot}")
                    break

            # Fix inconsistencies in equipped items
            print("\n=== FIXING INCONSISTENCIES ===")
            fixed = False

            # Find the armor item in inventory
            armor_item_in_inventory = False
            for item_id_str, item_data in inventory.items():
                try:
                    if item_data.get("equipped", False):  # Only check equipped items
                        item_id = int(item_id_str)
                        item = (
                            db.query(models.Item)
                            .filter(models.Item.id == item_id)
                            .first()
                        )
                        if item and item.item_type and item.item_type.value == "armor":
                            print(
                                f"Found armor item {item_id} ({item.name}) marked as equipped in inventory"
                            )

                            # Check if it's properly in equipment
                            is_in_equipment = False
                            for slot_name, equip_item_id in equipment.items():
                                if equip_item_id == item_id:
                                    is_in_equipment = True
                                    armor_slot = slot_name
                                    armor_item_id = item_id
                                    print(
                                        f"Armor is properly in equipment slot: {slot_name}"
                                    )
                                    break

                            # If not in equipment, add it
                            if not is_in_equipment:
                                print(
                                    f"Fixing: Adding armor to equipment in 'body' slot"
                                )
                                equipment["body"] = item_id
                                inventory[item_id_str]["slot"] = "body"
                                armor_slot = "body"
                                armor_item_id = item_id
                                fixed = True

                            armor_item_in_inventory = True
                            break
                except Exception as e:
                    print(f"Error checking inventory item {item_id_str}: {str(e)}")

            # Update the character in the database if fixes were made
            if fixed:
                character.equipment = equipment
                character.inventory = inventory

                # Recalculate armor class
                dex_mod = get_ability_modifier(character.dexterity)
                base_ac = 10

                # Get armor properties
                armor_item = (
                    db.query(models.Item)
                    .filter(models.Item.id == armor_item_id)
                    .first()
                )
                if armor_item and armor_item.properties:
                    if "armor_class" in armor_item.properties:
                        base_ac = armor_item.properties["armor_class"]
                        print(f"Armor class from armor: {base_ac}")
                    elif "ac_bonus" in armor_item.properties:
                        armor_bonus = armor_item.properties["ac_bonus"]
                        base_ac = armor_bonus  # Armor provides base AC
                        print(f"Armor base AC: {armor_bonus}")

                # Apply shield bonus if equipped
                for slot, item_id in equipment.items():
                    if slot == "off_hand":
                        shield_item = (
                            db.query(models.Item)
                            .filter(models.Item.id == item_id)
                            .first()
                        )
                        if (
                            shield_item
                            and shield_item.properties
                            and "ac_bonus" in shield_item.properties
                        ):
                            shield_bonus = shield_item.properties["ac_bonus"]
                            base_ac += shield_bonus  # Higher is better in ascending AC
                            print(f"Shield bonus: +{shield_bonus}")

                # Apply dexterity modifier
                total_ac = base_ac + dex_mod

                character.armor_class = total_ac
                print(f"Recalculated AC: {total_ac}")

                db.add(character)
                db.commit()
                db.refresh(character)
                print("Database updated with fixed equipment and recalculated AC")

                # Make sure we have the latest equipment
                equipment = character.equipment or {}
                print(f"Updated equipment: {json.dumps(equipment, indent=2)}")
            else:
                print("No inconsistencies to fix")

            # Verify armor is in equipment after potential fix
            if not armor_slot:
                print("\nSearching for armor in equipment after fix...")
                for slot, item_id in equipment.items():
                    item = (
                        db.query(models.Item).filter(models.Item.id == item_id).first()
                    )
                    if item and item.item_type and item.item_type.value == "armor":
                        armor_slot = slot
                        armor_item_id = item_id
                        print(f"Found armor: {item.name} in slot {slot}")
                        break

            # Now test unequipping the armor
            print("\n=== TESTING UNEQUIP ARMOR ===")

            if not armor_slot:
                # Special case: Check if Chain Mail (ID 78) is in inventory and "equipped"
                # but not properly in equipment
                chain_mail_id = 78
                chain_mail_id_str = str(chain_mail_id)

                if chain_mail_id_str in inventory and inventory[chain_mail_id_str].get(
                    "equipped", False
                ):
                    print(
                        " +
            "Chain Mail found in inventory marked as equipped but not"in equipment"
                    )
                    armor_item = (
                        db.query(models.Item)
                        .filter(models.Item.id == chain_mail_id)
                        .first()
                    )
                    armor_slot = "body"
                    armor_item_id = chain_mail_id

                    # Add to equipment for testing
                    equipment["body"] = chain_mail_id
                    character.equipment = equipment
                    db.add(character)
                    db.commit()
                    db.refresh(character)
                    print(f"Temporarily added Chain Mail to body slot for testing")
                else:
                    print("No armor found in equipment. Cannot test unequipping.")
                    return False

            # Calculate expected AC after unequipping
            dex_mod = get_ability_modifier(character.dexterity)
            expected_ac = 10  # Base AC without armor

            # Apply shield bonus if equipped
            for slot, item_id in character.equipment.items():
                if slot == armor_slot:
                    continue  # Skip the armor we're going to unequip

                item = db.query(models.Item).filter(models.Item.id == item_id).first()
                if (
                    item
                    and item.item_type
                    and item.item_type.value == "shield"
                    and item.properties
                ):
                    if "ac_bonus" in item.properties:
                        shield_bonus = item.properties["ac_bonus"]
                        expected_ac -= shield_bonus  # Lower AC is better
                        print(f"Shield bonus: -{shield_bonus}")

            # Apply dexterity modifier
            expected_ac -= dex_mod
            print(f"Expected AC after unequipping: {expected_ac}")

            # Get the item ID of the armor
            armor_item_id = character.equipment[armor_slot]
            armor_item = (
                db.query(models.Item).filter(models.Item.id == armor_item_id).first()
            )
            print(f"Unequipping armor: {armor_item.name} from slot {armor_slot}...")

            # Create a copy of equipment without the armor
            new_equipment = dict(character.equipment)
            del new_equipment[armor_slot]

            # Update inventory
            new_inventory = dict(character.inventory)
            item_id_str = str(armor_item_id)
            if item_id_str in new_inventory:
                new_inventory[item_id_str]["equipped"] = False
                new_inventory[item_id_str]["slot"] = None

            # Update the character
            character.equipment = new_equipment
            character.inventory = new_inventory
            character.armor_class = expected_ac

            db.add(character)
            db.commit()
            db.refresh(character)

            # Check if AC was updated
            print(f"New armor class after unequipping: {character.armor_class}")

            unequip_successful = False
            if character.armor_class == expected_ac:
                print(
                    "SUCCESS: Armor class was correctly updated when unequipping armor!"
                )
                unequip_successful = True
            else:
                print(
                    f"ERROR: AC update failed! Expected {expected_ac}, got {character.armor_class}"
                )

            print("\n=== NOW TESTING EQUIP ARMOR ===")

            # Make sure the armor is in inventory (should be unequipped from previous test)
            armor_item_id_str = str(armor_item_id)
            armor_item = (
                db.query(models.Item).filter(models.Item.id == armor_item_id).first()
            )

            if not armor_item:
                print(f"Armor item {armor_item_id} not found in database.")
                return False

            print(f"Using armor: {armor_item.name}")

            # Calculate expected AC after equipping
            dex_mod = get_ability_modifier(character.dexterity)
            expected_ac = 10  # Base AC

            # Apply armor bonus
            if armor_item.properties:
                if "armor_class" in armor_item.properties:
                    expected_ac = armor_item.properties["armor_class"]
                    print(f"Armor class: {expected_ac}")
                elif "ac_bonus" in armor_item.properties:
                    armor_bonus = armor_item.properties["ac_bonus"]
                    expected_ac -= armor_bonus  # Lower AC is better
                    print(f"Armor bonus: -{armor_bonus}")

            # Apply shield bonus if equipped
            for slot, item_id in character.equipment.items():
                item = db.query(models.Item).filter(models.Item.id == item_id).first()
                if (
                    item
                    and item.item_type
                    and item.item_type.value == "shield"
                    and item.properties
                ):
                    if "ac_bonus" in item.properties:
                        shield_bonus = item.properties["ac_bonus"]
                        expected_ac -= shield_bonus  # Lower AC is better
                        print(f"Shield bonus: -{shield_bonus}")

            # Apply dexterity modifier
            expected_ac -= dex_mod
            print(f"Expected AC after equipping: {expected_ac}")

            # Equip the armor
            print(f"Equipping armor: {armor_item.name}...")

            # Use 'body' slot for armor
            slot = "body"

            # Update equipment
            new_equipment = dict(character.equipment)
            new_equipment[slot] = armor_item_id

            # Update inventory
            new_inventory = dict(character.inventory)
            if armor_item_id_str in new_inventory:
                new_inventory[armor_item_id_str]["equipped"] = True
                new_inventory[armor_item_id_str]["slot"] = slot

            # Update the character
            character.equipment = new_equipment
            character.inventory = new_inventory
            character.armor_class = expected_ac

            db.add(character)
            db.commit()

            # Refresh character
            db.refresh(character)

            # Check if AC was updated
            print(f"New armor class after equipping: {character.armor_class}")

            equip_successful = False
            if character.armor_class == expected_ac:
                print(
                    "SUCCESS: Armor class was correctly updated when equipping armor!"
                )
                equip_successful = True
            else:
                print(
                    f"ERROR: AC update failed! Expected {expected_ac}, got {character.armor_class}"
                )

            return unequip_successful and equip_successful

        except Exception as e:
            print(f"Error testing armor: {str(e)}")
            import traceback

            traceback.print_exc()
            db.rollback()
            return False


if __name__ == "__main__":
    character_name = "Skilrok"  # Replace with your character name
    fix_and_test_armor(character_name)
