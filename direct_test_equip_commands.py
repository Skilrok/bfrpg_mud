import asyncio
import json

from app.commands.base import CommandContext, CommandResponse
from app.commands.basic_commands import EquipCommand, UnequipCommand
from app.database import SessionLocal
from app.models import Character, Item


async def execute_command_directly(handler, character, args):
    """Execute a command directly with the handler"""
    db = SessionLocal()
    try:
        # Get fresh character from DB
        fresh_character = (
            db.query(Character).filter(Character.id == character.id).first()
        )

        # Create command context
        ctx = CommandContext(
            user=None,
            character=fresh_character,
            room_id=None,
            session_id=None,
            raw_input=f"{handler.name} {' '.join(args)}",
            command=handler.name,
            args=args,
            data={"db": db},
        )

        # Execute command
        result = await handler.execute(ctx)
        return result
    finally:
        db.close()


async def test_equipment_commands(character_name="EquipmentTest"):
    """Test equip and unequip commands directly with handlers"""
    db = SessionLocal()
    try:
        # Get character
        character = db.query(Character).filter(Character.name == character_name).first()
        if not character:
            print(f"Character {character_name} not found")
            return

        print(f"Testing equipment commands for character: {character.name}")
        print(f"Character ID: {character.id}")

        # Get Hand Axe
        hand_axe = db.query(Item).filter(Item.name == "Hand Axe").first()
        if not hand_axe:
            print("Hand Axe not found in database")
            return

        print(f"Found Hand Axe: ID {hand_axe.id}")

        # Ensure Hand Axe is in inventory
        if not character.inventory or str(hand_axe.id) not in character.inventory:
            print("Adding Hand Axe to inventory...")
            if not character.inventory:
                character.inventory = {}

            character.inventory[str(hand_axe.id)] = {
                "item_id": hand_axe.id,
                "quantity": 1,
                "equipped": False,
                "slot": None,
            }
            db.add(character)
            db.commit()
            db.refresh(character)

        # Make sure Hand Axe is not already equipped
        if character.equipment and any(
            item_id == hand_axe.id for item_id in character.equipment.values()
        ):
            print("Hand Axe already equipped, clearing equipment...")
            character.equipment = {}

            # Update inventory to show as unequipped
            if str(hand_axe.id) in character.inventory:
                character.inventory[str(hand_axe.id)]["equipped"] = False
                character.inventory[str(hand_axe.id)]["slot"] = None

            db.add(character)
            db.commit()
            db.refresh(character)

        # Show initial state
        print("\nInitial Character State:")
        print(f"  Equipment: {json.dumps(character.equipment)}")
        print(f"  Inventory: {json.dumps(character.inventory)}")

        # Test equip command
        print("\nTesting Equip Command...")
        equip_cmd = EquipCommand()
        result = await execute_command_directly(equip_cmd, character, ["Hand", "Axe"])

        print(f"Equip Result: {result.message}")
        print(f"Success: {result.success}")

        # Refresh character and show state after equip
        db.refresh(character)
        print("\nAfter Equip Command:")
        print(f"  Equipment: {json.dumps(character.equipment)}")
        print(f"  Inventory: {json.dumps(character.inventory)}")

        # Test unequip command
        print("\nTesting Unequip Command...")
        unequip_cmd = UnequipCommand()
        result = await execute_command_directly(unequip_cmd, character, ["Hand", "Axe"])

        print(f"Unequip Result: {result.message}")
        print(f"Success: {result.success}")

        # Refresh character and show final state
        db.refresh(character)
        print("\nFinal Character State:")
        print(f"  Equipment: {json.dumps(character.equipment)}")
        print(f"  Inventory: {json.dumps(character.inventory)}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_equipment_commands())
