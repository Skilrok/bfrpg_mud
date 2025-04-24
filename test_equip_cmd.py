import json

from app.commands.base import CommandContext
from app.commands.basic_commands import EquipCommand, UnequipCommand, get_db_context
from app.database import SessionLocal
from app.models import Character, Item


async def test_equip_unequip_commands(character_name, item_name):
    """Test equip and unequip commands directly"""
    db = SessionLocal()

    try:
        # Find the character
        character = db.query(Character).filter(Character.name == character_name).first()

        if not character:
            print(f"Character '{character_name}' not found")
            return

        # Find the item
        item = db.query(Item).filter(Item.name == item_name).first()

        if not item:
            print(f"Item '{item_name}' not found")
            return

        print(
            f"Testing with character: {character.name} and item: {item.name} (ID: {item.id})"
        )

        # First make sure the item is in the character's inventory
        if not character.inventory or str(item.id) not in character.inventory:
            print("Adding item to inventory first...")
            inventory = character.inventory or {}
            inventory[str(item.id)] = {
                "item_id": item.id,
                "quantity": 1,
                "equipped": False,
                "slot": None,
            }
            character.inventory = dict(inventory)
            db.add(character)
            db.commit()
            db.refresh(character)

        # Print initial state
        print("\nInitial State:")
        print("Inventory:", json.dumps(character.inventory, indent=2))
        print("Equipment:", json.dumps(character.equipment, indent=2))

        # Make sure the item is not already equipped
        if character.equipment and any(
            item_id == item.id for item_id in character.equipment.values()
        ):
            print("Item is already equipped, removing it first...")
            # Create a fresh equipment dictionary without this item
            new_equipment = {}
            for slot, equipped_item_id in character.equipment.items():
                if equipped_item_id != item.id:
                    new_equipment[slot] = equipped_item_id

            character.equipment = new_equipment

            # Update inventory to show as unequipped
            if str(item.id) in character.inventory:
                inventory = dict(character.inventory)
                inventory[str(item.id)]["equipped"] = False
                inventory[str(item.id)]["slot"] = None
                character.inventory = inventory

            db.add(character)
            db.commit()
            db.refresh(character)

            print("After resetting equipment:")
            print("Inventory:", json.dumps(character.inventory, indent=2))
            print("Equipment:", json.dumps(character.equipment, indent=2))

        # Create command context for equip
        print("\nExecuting equip command...")

        # Use a fresh database session for the command
        db_context = SessionLocal()

        # Reload character with fresh session
        fresh_character = (
            db_context.query(Character).filter(Character.name == character_name).first()
        )

        ctx = CommandContext(
            user=None,
            character=fresh_character,
            room_id=None,
            session_id=None,
            raw_input=f"equip {item_name}",
            command="equip",
            args=[item_name],
            data={"db": db_context},  # This won't be used anyway
        )

        # Execute equip command
        equip_cmd = EquipCommand()
        equip_result = await equip_cmd.execute(ctx)
        print(f"Result: {equip_result.message}")
        print(f"Success: {equip_result.success}")

        # Refresh our main db session to see changes
        db.refresh(character)

        # Print state after equip
        print("\nAfter Equip:")
        print("Inventory:", json.dumps(character.inventory, indent=2))
        print("Equipment:", json.dumps(character.equipment, indent=2))

        # Now test unequip with a fresh session
        print("\nExecuting unequip command...")

        # Use a fresh database session for the command
        db_context = SessionLocal()

        # Reload character with fresh session
        fresh_character = (
            db_context.query(Character).filter(Character.name == character_name).first()
        )

        ctx = CommandContext(
            user=None,
            character=fresh_character,
            room_id=None,
            session_id=None,
            raw_input=f"unequip {item_name}",
            command="unequip",
            args=[item_name],
            data={"db": db_context},  # This won't be used anyway
        )

        # Execute unequip command
        unequip_cmd = UnequipCommand()
        unequip_result = await unequip_cmd.execute(ctx)
        print(f"Result: {unequip_result.message}")
        print(f"Success: {unequip_result.success}")

        # Refresh character from DB to see the changes
        db.refresh(character)

        # Print final state
        print("\nFinal State:")
        print("Inventory:", json.dumps(character.inventory, indent=2))
        print("Equipment:", json.dumps(character.equipment, indent=2))

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_equip_unequip_commands("EquipmentTest", "Hand Axe"))
