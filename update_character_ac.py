from app import models
from app.database import get_db_context
from app.routers.characters import get_ability_modifier


def update_character_ac(character_name):
    """Update the armor class for a specific character based on equipped items."""
    with get_db_context() as db:
        try:
            # Find the character by name
            character = (
                db.query(models.Character)
                .filter(models.Character.name == character_name)
                .first()
            )

            if not character:
                print(f"Character '{character_name}' not found")
                return

            print(f"Updating AC for character: {character.name}")
            print(f"Current armor class: {character.armor_class}")

            # Calculate dexterity modifier
            dex_mod = get_ability_modifier(character.dexterity)
            print(f"Dexterity modifier: {dex_mod}")

            # Start with base AC of 10
            base_ac = 10

            # Check equipped items
            equipment = character.equipment or {}
            if not equipment:
                print("No equipment found.")
                return

            # Calculate AC from equipped items
            for slot, item_id in equipment.items():
                item = db.query(models.Item).filter(models.Item.id == item_id).first()
                if item and item.properties:
                    # Handle armor
                    if slot == "body" and item.item_type.value == "armor":
                        if "ac_bonus" in item.properties:
                            base_ac = item.properties["ac_bonus"]
                            print(f"Using armor AC from ac_bonus: {base_ac}")
                        elif "armor_class" in item.properties:
                            base_ac = item.properties["armor_class"]
                            print(f"Using armor AC from armor_class: {base_ac}")

                    # Handle shield
                    elif slot == "off_hand" and item.item_type.value == "shield":
                        if "ac_bonus" in item.properties:
                            shield_bonus = item.properties["ac_bonus"]
                            base_ac -= shield_bonus  # Lower is better in BFRPG
                            print(f"Applied shield bonus: -{shield_bonus}")

            # Apply dexterity modifier
            new_ac = base_ac - dex_mod

            print(f"\nCalculated new AC: {new_ac}")
            print(f"Old AC in database: {character.armor_class}")

            # Update the character's AC
            character.armor_class = new_ac
            db.add(character)
            db.commit()

            # Verify the update
            db.refresh(character)
            print(f"Updated AC in database: {character.armor_class}")

            print("\nCharacter AC updated successfully! ✓")

        except Exception as e:
            print(f"Error updating character AC: {str(e)}")
            db.rollback()
            raise


if __name__ == "__main__":
    character_name = "Skilrok"  # Replace with your character's name
    update_character_ac(character_name)
