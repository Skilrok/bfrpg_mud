import logging

from app.database import get_db
from app.models.character import Character
from app.models.character_item import CharacterItem
from app.models.item import Item

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_shield_equipment():
    """
    Check which characters have shield (item ID 80) in their equipment.
    """
    try:
        # Get database session
        db = next(get_db())

        # Query all character items for item ID 80
        character_items = (
            db.query(CharacterItem).filter(CharacterItem.item_id == 80).all()
        )

        if not character_items:
            logger.info(
                "No characters have shield (item ID 80) in their inventory or equipment"
            )
            return

        logger.info(f"Found {len(character_items)} characters with shield (item ID 80)")

        # Check each character's equipment status for the shield
        for char_item in character_items:
            character = (
                db.query(Character)
                .filter(Character.id == char_item.character_id)
                .first()
            )
            if not character:
                logger.warning(
                    f"Character {char_item.character_id} not found but has shield item"
                )
                continue

            logger.info(f"Character: {character.name} (ID: {character.id}) has shield")
            logger.info(f"  Is equipped: {char_item.is_equipped}")
            logger.info(f"  Equipment slot: {char_item.equip_slot}")

            # Check if character has equipment JSON field and if shield is in it
            if character.equipment:
                for slot, item_id in character.equipment.items():
                    if item_id == 80:
                        logger.warning(
                            f"  Shield found in equipment JSON field in slot: {slot}"
                        )

    except Exception as e:
        logger.error(f"Error checking shield equipment: {str(e)}")


if __name__ == "__main__":
    check_shield_equipment()
