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


def fix_character_equipment(character_name):
    """Fix character equipment inconsistencies."""
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

            # Display current equipment and inventory
            print("\n=== INITIAL STATE ===")
            equipment = character.equipment or {}
            print(f"Equipment: {json.dumps(equipment, indent=2)}")

            inventory = character.inventory or {}
            print(f"Inventory: {json.dumps(inventory, indent=2)}")

            # Fix inconsistencies in equipped items
            print("\n=== FIXING INCONSISTENCIES ===")
            fixed = False
            new_equipment = dict(equipment)

            # Check all inventory items that are marked as equipped
            for item_id_str, item_data in inventory.items():
                try:
                    if item_data.get("equipped", False):  # Only check equipped items
                        item_id = int(item_id_str)
                        item = (
                            db.query(models.Item)
                            .filter(models.Item.id == item_id)
                            .first()
                        )

                        if not item:
                            print(f"Item ID {item_id} not found in database")
                            continue

                        item_name = item.name
                        item_type = "unknown"
                        if hasattr(item, "item_type") and item.item_type:
                            if hasattr(item.item_type, "value"):
                                item_type = item.item_type.value
                            else:
                                item_type = str(item.item_type)

                        # Check if it's properly in equipment
                        is_in_equipment = False
                        for slot, equip_item_id in equipment.items():
                            if equip_item_id == item_id:
                                is_in_equipment = True
                                print(
                                    f"Item {item_id} ({item_name}) properly in equipment slot: {slot}"
                                )
                                break

                        # If not in equipment, add it to appropriate slot
                        if not is_in_equipment:
                            slot = item_data.get("slot")

                            # If no slot specified in inventory, determine appropriate slot
                            if not slot:
                                if item_type == "weapon":
                                    slot = "main_hand"
                                elif item_type == "armor":
                                    slot = "body"
                                elif item_type == "shield":
                                    slot = "off_hand"
                                elif item_type == "ring":
                                    slot = "ring_1"
                                elif item_type == "amulet":
                                    slot = "neck"
                                else:
                                    print(
                                        f"Cannot determine slot for item {item_id} ({item_name}) of type {item_type}"
                                    )
                                    continue

                            print(
                                f"Fixing: Adding {item_name} ({item_type}) to equipment in '{slot}' slot"
                            )
                            new_equipment[slot] = item_id
                            inventory[item_id_str]["slot"] = slot
                            fixed = True
                except Exception as e:
                    print(f"Error checking inventory item {item_id_str}: {str(e)}")

            # Also check for inconsistencies in the opposite direction
            # (items in equipment but not marked as equipped in inventory)
            for slot, item_id in equipment.items():
                item_id_str = str(item_id)
                if item_id_str in inventory and not inventory[item_id_str].get(
                    "equipped", False
                ):
                    print(
                        f"Item {item_id} in slot {slot} not marked as equipped in inventory"
                    )
                    inventory[item_id_str]["equipped"] = True
                    inventory[item_id_str]["slot"] = slot
                    fixed = True

            # Update the character in the database if fixes were made
            if fixed:
                print(f"Updated equipment: {json.dumps(new_equipment, indent=2)}")

                # Create a new equipment dictionary explicitly to ensure it's detected as changed
                character.equipment = new_equipment

                # Update inventory slots
                character.inventory = inventory

                # Recalculate armor class
                dex_mod = get_ability_modifier(character.dexterity)
                base_ac = 10

                # Look for armor and shield in equipment
                for slot, item_id in new_equipment.items():
                    item = (
                        db.query(models.Item).filter(models.Item.id == item_id).first()
                    )
                    if not item or not item.properties:
                        continue

                    if slot == "body" and item.item_type.value == "armor":
                        if "armor_class" in item.properties:
                            base_ac = item.properties["armor_class"]
                            print(f"Armor class from {item.name}: {base_ac}")
                        elif "ac_bonus" in item.properties:
                            armor_bonus = item.properties["ac_bonus"]
                            base_ac = armor_bonus  # Armor provides base AC
                            print(f"Armor base AC from {item.name}: {armor_bonus}")

                    if slot == "off_hand" and item.item_type.value == "shield":
                        if "ac_bonus" in item.properties:
                            shield_bonus = item.properties["ac_bonus"]
                            base_ac += shield_bonus  # Higher is better in ascending AC
                            print(f"Shield bonus from {item.name}: +{shield_bonus}")

                # Apply dexterity modifier
                total_ac = base_ac + dex_mod
                print(f"Dexterity modifier: +{dex_mod}")
                print(f"Recalculated AC: {total_ac}")

                character.armor_class = total_ac

                db.add(character)
                db.commit()
                db.refresh(character)

                print("\n=== AFTER FIXING ===")
                print(f"Final Armor Class: {character.armor_class}")
                print(f"Final Equipment: {json.dumps(character.equipment, indent=2)}")
                print("Database updated with fixed equipment and recalculated AC")

                return True
            else:
                print("No inconsistencies to fix")
                return False

        except Exception as e:
            print(f"Error fixing equipment: {str(e)}")
            import traceback

            traceback.print_exc()
            db.rollback()
            return False


if __name__ == "__main__":
    character_name = "Skilrok"  # Replace with your character name
    fix_character_equipment(character_name)
