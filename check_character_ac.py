from app import models
from app.database import get_db_context


def check_character_ac(character_name):
    """Check the AC calculation for a specific character."""
    with get_db_context() as db:
        # Find the character by name
        character = (
            db.query(models.Character)
            .filter(models.Character.name == character_name)
            .first()
        )

        if not character:
            print(f"Character '{character_name}' not found")
            return

        print(f"Checking AC for character: {character.name}")
        print(f"Race: {character.race}, Class: {character.character_class}")
        print(f"Current armor class: {character.armor_class}")

        # Check dexterity modifier
        dex_score = character.dexterity
        print(f"Dexterity: {dex_score}")

        # Calculate dex modifier
        if dex_score == 3:
            dex_mod = -3
        elif 4 <= dex_score <= 5:
            dex_mod = -2
        elif 6 <= dex_score <= 8:
            dex_mod = -1
        elif 9 <= dex_score <= 12:
            dex_mod = 0
        elif 13 <= dex_score <= 15:
            dex_mod = 1
        elif 16 <= dex_score <= 17:
            dex_mod = 2
        elif dex_score == 18:
            dex_mod = 3
        else:
            dex_mod = 0

        print(f"Dexterity modifier: {dex_mod}")

        # Check equipped items
        print("\nEquipped items:")
        equipment = character.equipment or {}

        if not equipment:
            print("No equipment found.")
            return

        for slot, item_id in equipment.items():
            item = db.query(models.Item).filter(models.Item.id == item_id).first()
            if item:
                print(f"Slot: {slot}, Item: {item.name}, Type: {item.item_type}")
                print(f"  - Properties: {item.properties}")

                # Check AC value
                if item.item_type.value == "armor":
                    print("  - This is armor, should affect base AC")
                    if "ac_bonus" in item.properties:
                        print(f"  - AC from ac_bonus: {item.properties['ac_bonus']}")
                    elif "armor_class" in item.properties:
                        print(
                            f"  - AC from armor_class: {item.properties['armor_class']}"
                        )
                    else:
                        print("  - No AC information found in properties!")

                elif item.item_type.value == "shield":
                    print("  - This is a shield, should provide AC bonus")
                    if "ac_bonus" in item.properties:
                        print(f"  - AC bonus: {item.properties['ac_bonus']}")
                    else:
                        print("  - No AC bonus information found in properties!")

        # Check inventory for the equipped items
        print("\nInventory check for equipped items:")
        inventory = character.inventory or {}

        for item_id_str, item_data in inventory.items():
            if item_data.get("equipped", False):
                item = (
                    db.query(models.Item)
                    .filter(models.Item.id == int(item_id_str))
                    .first()
                )
                if item:
                    print(
                        f"Item: {item.name} is marked as equipped in slot: {item_data.get('slot')}"
                    )

        # Calculate what the AC should be
        base_ac = 10  # Default base AC
        for slot, item_id in equipment.items():
            item = db.query(models.Item).filter(models.Item.id == item_id).first()
            if item and item.properties:
                if slot == "body" and item.item_type.value == "armor":
                    # Get AC value from either property
                    if "ac_bonus" in item.properties:
                        base_ac = item.properties["ac_bonus"]
                    elif "armor_class" in item.properties:
                        base_ac = item.properties["armor_class"]

                elif slot == "off_hand" and item.item_type.value == "shield":
                    if "ac_bonus" in item.properties:
                        base_ac += item.properties["ac_bonus"]  # Higher is better in ascending AC

        # Apply dex modifier
        expected_ac = base_ac + dex_mod

        print(f"\nExpected AC calculation:")
        print(f"Base AC from equipment: {base_ac}")
        print(f"Dexterity modifier: {dex_mod}")
        print(f"Expected final AC: {expected_ac}")
        print(f"Actual AC in database: {character.armor_class}")

        if expected_ac == character.armor_class:
            print("\nAC calculation is CORRECT! ✓")
        else:
            print("\nAC calculation is INCORRECT! ✗")


if __name__ == "__main__":
    check_character_ac("Skilrok")  # Replace with your character's name
