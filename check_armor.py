import json
import logging

from app import models
from app.database import get_db_context

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_character_inventory(character_name):
    """Check a character's inventory for armor and display equipment status."""
    print(f"Starting inventory check for character: {character_name}")

    with get_db_context() as db:
        try:
            # Find the character
            print(f"Querying database for character: {character_name}")
            character = (
                db.query(models.Character)
                .filter(models.Character.name == character_name)
                .first()
            )

            if not character:
                print(f"Character '{character_name}' not found")
                return False

            print(f"\n=== {character.name} ===")
            print(f"Armor Class: {character.armor_class}")
            print(f"Dexterity: {character.dexterity}")

            # Display equipment
            equipment = character.equipment or {}
            print("\n=== EQUIPPED ITEMS ===")
            print(f"Equipment data: {json.dumps(equipment, indent=2)}")

            if not equipment:
                print("No items equipped.")
            else:
                for slot, item_id in equipment.items():
                    item = (
                        db.query(models.Item).filter(models.Item.id == item_id).first()
                    )
                    if item:
                        item_type = (
                            item.item_type.value if item.item_type else "unknown"
                        )
                        properties = (
                            json.dumps(item.properties) if item.properties else "{}"
                        )
                        print(
                            f"Slot {slot}: {item.name} (ID: {item.id}, Type: {item_type}, Properties: {properties})"
                        )
                    else:
                        print(f"Slot {slot}: Unknown item (ID: {item_id})")

            # Check inventory for armor
            inventory = character.inventory or {}
            print("\n=== INVENTORY ITEMS ===")
            print(f"Inventory data: {json.dumps(inventory, indent=2)}")

            if not inventory:
                print("Inventory is empty.")
                return False

            armor_found = False

            for item_id_str, item_data in inventory.items():
                try:
                    item_id = int(item_id_str)
                    equipped = item_data.get("equipped", False)
                    print(f"Looking up item ID: {item_id}")
                    item = (
                        db.query(models.Item).filter(models.Item.id == item_id).first()
                    )

                    if item:
                        item_type = "unknown"
                        if hasattr(item, "item_type") and item.item_type:
                            if hasattr(item.item_type, "value"):
                                item_type = item.item_type.value
                            else:
                                item_type = str(item.item_type)

                        properties = (
                            json.dumps(item.properties) if item.properties else "{}"
                        )
                        status = "EQUIPPED" if equipped else "NOT EQUIPPED"

                        print(f"Item found: {item.name}, Type: {item_type}")

                        if item_type == "armor":
                            armor_found = True
                            print(
                                f"ARMOR: {item.name} (ID: {item.id}, Status: {status}, Properties: {properties})"
                            )
                        else:
                            print(
                                f"Item: {item.name} (ID: {item.id}, Type: {item_type}, Status: {status})"
                            )
                    else:
                        print(f"Item with ID {item_id} not found in database")
                except Exception as e:
                    print(f"Error processing item {item_id_str}: {str(e)}")

            if not armor_found:
                print("\nNo armor items found in inventory.")

            return True

        except Exception as e:
            print(f"Error checking inventory: {str(e)}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    character_name = "Skilrok"  # Replace with your character name
    print("Starting script")
    check_character_inventory(character_name)
    print("Script completed")
