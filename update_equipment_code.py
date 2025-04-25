import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def update_equip_command():
    """
    Update the EquipCommand and UnequipCommand in app/commands/basic_commands.py
    to use the ac_bonus column instead of accessing the properties dictionary.
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

        # Pattern to find in EquipCommand for shield AC calculation
        equip_pattern = r"""if \(
                                slot_db_item
                                and slot_db_item\.properties
                                and "ac_bonus" in slot_db_item\.properties
                            \):
                                ac_bonus = slot_db_item\.properties\["ac_bonus"\]"""

        # Replacement that uses the ac_bonus column with a fallback to properties
        equip_replacement = r"""if slot_db_item:
                                # First try to use the ac_bonus column
                                if slot_db_item.ac_bonus is not None:
                                    ac_bonus = slot_db_item.ac_bonus
                                    logger.debug(f"Using ac_bonus column value: {ac_bonus}")
                                # Fall back to properties if column is None
                                elif slot_db_item.properties and "ac_bonus" in slot_db_item.properties:
                                    ac_bonus = slot_db_item.properties["ac_bonus"]
                                    logger.debug(f"Using properties ac_bonus value: {ac_bonus}")"""

        # Update EquipCommand
        updated_content = re.sub(equip_pattern, equip_replacement, content)

        # Similar update for UnequipCommand
        unequip_pattern = r"""if \(
                                slot_db_item
                                and slot_db_item\.properties
                                and "ac_bonus" in slot_db_item\.properties
                            \):
                                ac_bonus = slot_db_item\.properties\["ac_bonus"\]"""

        updated_content = re.sub(unequip_pattern, equip_replacement, updated_content)

        # Write the updated content back to the file
        if content != updated_content:
            with open(commands_file, "w") as f:
                f.write(updated_content)
            logger.info(f"Updated {commands_file} to use the ac_bonus column")
            return True
        else:
            logger.info(f"No changes needed in {commands_file}")
            return False

    except Exception as e:
        logger.error(f"Error updating EquipCommand: {e}")
        return False


def update_character_router():
    """
    Update the character router code in app/routers/characters.py
    to use the ac_bonus column instead of accessing the properties dictionary.
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

        # Pattern to find in character router
        router_pattern = r"""if \(
                        db_item
                        and db_item\.properties
                        and "ac_bonus" in db_item\.properties
                    \):
                        ac_bonus = db_item\.properties\["ac_bonus"\]"""

        # Replacement that uses the ac_bonus column with a fallback to properties
        router_replacement = r"""if db_item:
                        # First try to use the ac_bonus column
                        if db_item.ac_bonus is not None:
                            ac_bonus = db_item.ac_bonus
                            logger.debug(f"Using ac_bonus column value: {ac_bonus}")
                        # Fall back to properties if column is None
                        elif db_item.properties and "ac_bonus" in db_item.properties:
                            ac_bonus = db_item.properties["ac_bonus"]
                            logger.debug(f"Using properties ac_bonus value: {ac_bonus}")"""

        # Update the character router
        updated_content = re.sub(router_pattern, router_replacement, content)

        # Write the updated content back to the file
        if content != updated_content:
            with open(router_file, "w") as f:
                f.write(updated_content)
            logger.info(f"Updated {router_file} to use the ac_bonus column")
            return True
        else:
            logger.info(f"No changes needed in {router_file}")
            return False

    except Exception as e:
        logger.error(f"Error updating character router: {e}")
        return False


def run_updates():
    """Run all update functions."""
    logger.info("Starting code updates to use ac_bonus column")

    equip_updated = update_equip_command()
    router_updated = update_character_router()

    if equip_updated or router_updated:
        logger.info("Successfully updated code to use the ac_bonus column")
    else:
        logger.info("No files were updated")


if __name__ == "__main__":
    run_updates()
