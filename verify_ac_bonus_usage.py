import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def verify_equip_command():
    """
    Verify that the EquipCommand and UnequipCommand in app/commands/basic_commands.py
    have been updated to use the ac_bonus column.
    """
    try:
        # Path to the basic_commands.py file
        commands_file = Path("app/commands/basic_commands.py")

        if not commands_file.exists():
            logger.error(f"File not found: {commands_file}")
            return False

        # Read the current file content
        with open(commands_file, "r") as f:
            content = f.read()

        # Pattern to search for that indicates the code has been updated
        updated_pattern = r"if slot_db_item\.ac_bonus is not None"

        # Check if the updated code pattern exists
        if re.search(updated_pattern, content):
            logger.info("✅ EquipCommand has been updated to use ac_bonus column")
            return True
        else:
            logger.warning(
                "❌ EquipCommand has NOT been updated to use ac_bonus column"
            )
            return False

    except Exception as e:
        logger.error(f"Error verifying EquipCommand: {e}")
        return False


def verify_character_router():
    """
    Verify that the character router code in app/routers/characters.py
    has been updated to use the ac_bonus column.
    """
    try:
        # Path to the characters.py file
        router_file = Path("app/routers/characters.py")

        if not router_file.exists():
            logger.error(f"File not found: {router_file}")
            return False

        # Read the current file content
        with open(router_file, "r") as f:
            content = f.read()

        # Pattern to search for that indicates the code has been updated
        updated_pattern = r"if db_item\.ac_bonus is not None"

        # Check if the updated code pattern exists
        if re.search(updated_pattern, content):
            logger.info("✅ Character router has been updated to use ac_bonus column")
            return True
        else:
            logger.warning(
                "❌ Character router has NOT been updated to use ac_bonus column"
            )
            return False

    except Exception as e:
        logger.error(f"Error verifying character router: {e}")
        return False


def check_shield_item():
    """
    Check that the Shield item (ID 80) has the ac_bonus column populated.
    """
    try:
        from app.database import get_db_context
        from app.models.item import Item

        with get_db_context() as db:
            # Get the shield item with ID 80
            shield = db.query(Item).filter(Item.id == 80).first()

            if not shield:
                logger.error("Shield with ID 80 not found in the database")
                return False

            # Check if ac_bonus column is populated
            if shield.ac_bonus is not None:
                logger.info(
                    f"✅ Shield item (ID 80) has ac_bonus column populated with value: {shield.ac_bonus}"
                )
                return True
            else:
                logger.warning(
                    "❌ Shield item (ID 80) does NOT have ac_bonus column populated"
                )
                return False

    except Exception as e:
        logger.error(f"Error checking shield item: {e}")
        return False


def verify_updates():
    """Verify all updates."""
    logger.info("Starting verification of ac_bonus column usage")

    # Check code updates
    equip_updated = verify_equip_command()
    router_updated = verify_character_router()

    # Check database value
    shield_updated = check_shield_item()

    # Summary
    logger.info("\n--- VERIFICATION SUMMARY ---")

    if equip_updated:
        logger.info("✅ EquipCommand: Updated")
    else:
        logger.info("❌ EquipCommand: Not updated")

    if router_updated:
        logger.info("✅ Character Router: Updated")
    else:
        logger.info("❌ Character Router: Not updated")

    if shield_updated:
        logger.info("✅ Shield Item: ac_bonus column populated")
    else:
        logger.info("❌ Shield Item: ac_bonus column not populated")

    # Final assessment
    if equip_updated and router_updated and shield_updated:
        logger.info("\n✅ RESULT: All updates have been successfully applied")
    else:
        logger.info("\n❌ RESULT: Some updates were not successfully applied")


if __name__ == "__main__":
    verify_updates()
