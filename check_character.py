import json

from app.database import SessionLocal
from app.models import Character, Item


def check_character_inventory(character_name):
    """Check a character's inventory and equipment"""
    db = SessionLocal()

    try:
        # Find the character
        character = db.query(Character).filter(Character.name == character_name).first()

        if not character:
            print(f"Character '{character_name}' not found")
            return

        print(f"Character: {character.name}")
        print(f"Class: {character.character_class.value}")
        print(f"Level: {character.level}")

        # Print raw inventory data
        print("\nRaw Inventory Data:")
        print(json.dumps(character.inventory, indent=2))

        # Print raw equipment data
        print("\nRaw Equipment Data:")
        print(json.dumps(character.equipment, indent=2))

        # Get Hand Axe id
        hand_axe = db.query(Item).filter(Item.name == "Hand Axe").first()
        if hand_axe:
            print(
                f"\nHand Axe found in database: ID: {hand_axe.id}, Type: {hand_axe.item_type.value}"
            )
            # Check if character has Hand Axe
            if str(hand_axe.id) in character.inventory:
                hand_axe_data = character.inventory[str(hand_axe.id)]
                print(f"Character has Hand Axe in inventory: {hand_axe_data}")
            else:
                print("Character does NOT have Hand Axe in inventory")

            # Add Hand Axe to the character's inventory for testing
            if str(hand_axe.id) not in character.inventory:
                print("Adding Hand Axe to inventory for testing...")
                character.inventory = character.inventory or {}
                character.inventory[str(hand_axe.id)] = {
                    "item_id": hand_axe.id,
                    "quantity": 1,
                    "equipped": False,
                    "slot": None,
                }
                db.add(character)
                db.commit()
                print("Hand Axe added to inventory")
                print("Updated inventory:")
                print(json.dumps(character.inventory, indent=2))
        else:
            print("\nHand Axe not found in database")

        # Print inventory
        print("\nInventory:")
        inventory = character.inventory or {}

        if not inventory:
            print("  Empty inventory")
        else:
            for item_id_str, item_data in inventory.items():
                try:
                    item_id = int(item_id_str)
                    db_item = db.query(Item).filter(Item.id == item_id).first()

                    if db_item:
                        equipped_str = (
                            " (equipped)" if item_data.get("equipped", False) else ""
                        )
                        slot_str = (
                            f" in {item_data.get('slot')}"
                            if item_data.get("slot")
                            else ""
                        )
                        qty_str = (
                            f" x{item_data.get('quantity', 1)}"
                            if item_data.get("quantity", 1) > 1
                            else ""
                        )

                        print(
                            f"  - {db_item.name}{qty_str}{equipped_str}{slot_str} (ID: {item_id}, Type: {db_item.item_type.value})"
                        )
                        print(f"    Properties: {db_item.properties}")
                    else:
                        print(f"  - Unknown item (ID: {item_id})")
                except Exception as e:
                    print(f"  - Error processing item {item_id_str}: {e}")

        # Print equipment
        print("\nEquipment:")
        equipment = character.equipment or {}

        if not equipment:
            print("  No equipment equipped")
        else:
            for slot, item_id in equipment.items():
                try:
                    db_item = db.query(Item).filter(Item.id == item_id).first()

                    if db_item:
                        print(
                            f"  - {slot}: {db_item.name} (ID: {item_id}, Type: {db_item.item_type.value})"
                        )
                    else:
                        print(f"  - {slot}: Unknown item (ID: {item_id})")
                except Exception as e:
                    print(f"  - Error processing equipment in slot {slot}: {e}")

    except Exception as e:
        print(f"Error checking character: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    character_name = "EquipmentTest"
    check_character_inventory(character_name)
