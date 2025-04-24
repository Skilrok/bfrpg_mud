import json

from app.database import SessionLocal
from app.models import Character, Item


def fix_character_inventory(character_name, force_update=False):
    """Fix character inventory data structure issues"""
    db = SessionLocal()

    try:
        # Find the character
        character = db.query(Character).filter(Character.name == character_name).first()

        if not character:
            print(f"Character '{character_name}' not found")
            return

        print(f"Character: {character.name}")
        print(f"Class: {character.character_class.value}")

        # Print raw inventory and equipment data
        print("\nOriginal Raw Inventory Data:")
        print(json.dumps(character.inventory, indent=2))
        print("\nOriginal Raw Equipment Data:")
        print(json.dumps(character.equipment, indent=2))

        # Get Hand Axe for testing
        hand_axe = db.query(Item).filter(Item.name == "Hand Axe").first()

        if not hand_axe:
            print("\nHand Axe not found in database")
            return

        print(f"\nHand Axe found: ID: {hand_axe.id}, Type: {hand_axe.item_type.value}")

        # Check if we need to fix the inventory structure
        needs_fix = (
            force_update
            or not character.inventory
            or str(hand_axe.id) not in character.inventory
        )

        if needs_fix:
            print("\nFixing inventory structure...")
            # Make a copy of the current inventory
            current_inventory = character.inventory or {}

            # Update with hand axe
            current_inventory[str(hand_axe.id)] = {
                "item_id": hand_axe.id,
                "quantity": 1,
                "equipped": False,
                "slot": None,
            }

            # Update character with new inventory data
            print("Setting inventory...")
            character.inventory = current_inventory

            # Commit the changes
            db.add(character)
            db.commit()

            # Fetch the character again to see if changes persisted
            db.refresh(character)

            print("\nVerifying changes...")
            print("Updated Raw Inventory Data:")
            print(json.dumps(character.inventory, indent=2))

            if str(hand_axe.id) in character.inventory:
                print("Hand Axe successfully added to inventory!")
            else:
                print(
                    "ERROR: Hand Axe NOT added to inventory! This indicates a JSON serialization issue."
                )

                # Try an alternative approach with explicit type casting
                print("\nTrying alternative approach...")
                # Reload the character
                db.expire(character)
                character = (
                    db.query(Character).filter(Character.name == character_name).first()
                )

                # Create a new inventory object
                new_inventory = dict(character.inventory) if character.inventory else {}
                new_inventory[str(hand_axe.id)] = {
                    "item_id": hand_axe.id,
                    "quantity": 1,
                    "equipped": False,
                    "slot": None,
                }

                # Force type
                character.inventory = dict(new_inventory)
                db.add(character)
                db.commit()
                db.refresh(character)

                print("\nAfter alternative approach:")
                print(json.dumps(character.inventory, indent=2))

                if str(hand_axe.id) in character.inventory:
                    print("Alternative approach SUCCESS!")
                else:
                    print("Alternative approach FAILED!")
        else:
            print("Inventory already contains Hand Axe, no fix needed")

        # Also check the equip command functionality
        print("\n=== Testing Equip Functionality ===")
        if str(hand_axe.id) in character.inventory:
            # Simulate the equip command logic
            print("Simulating equip command...")

            # Get inventory and equipment
            inventory = character.inventory or {}
            equipment = character.equipment or {}

            # Equip the hand axe to main_hand
            slot = "main_hand"

            # Check if something is already in that slot
            old_item_name = None
            if slot in equipment:
                old_item_id = equipment[slot]
                old_item_id_str = str(old_item_id)

                if old_item_id_str in inventory:
                    old_db_item = db.query(Item).filter(Item.id == old_item_id).first()
                    if old_db_item:
                        old_item_name = old_db_item.name
                        inventory[old_item_id_str]["equipped"] = False
                        inventory[old_item_id_str]["slot"] = None

            # Equip the new item
            equipment[slot] = hand_axe.id
            inventory[str(hand_axe.id)]["equipped"] = True
            inventory[str(hand_axe.id)]["slot"] = slot

            # Update the character
            character.equipment = equipment
            character.inventory = inventory

            # Save changes
            db.add(character)
            db.commit()
            db.refresh(character)

            print("\nAfter equip simulation:")
            print("Raw Inventory Data:")
            print(json.dumps(character.inventory, indent=2))
            print("\nRaw Equipment Data:")
            print(json.dumps(character.equipment, indent=2))

            if (
                str(hand_axe.id) in character.inventory
                and character.inventory[str(hand_axe.id)].get("equipped", False)
                and "main_hand" in character.equipment
                and character.equipment["main_hand"] == hand_axe.id
            ):
                print("\nEquip simulation SUCCESS!")
            else:
                print("\nEquip simulation FAILED!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    character_name = "EquipmentTest"
    fix_character_inventory(character_name, force_update=True)
