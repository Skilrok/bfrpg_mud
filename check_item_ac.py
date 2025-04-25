import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.character import Character
from app.models.character_item import CharacterItem
from app.models.item import Item
from app.db.context import get_db_context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_ability_modifier(score):
    """Calculate ability modifier based on score."""
    if score == 3:
        return -3
    elif score in (4, 5):
        return -2
    elif score in (6, 7, 8):
        return -1
    elif score in (9, 10, 11, 12):
        return 0
    elif score in (13, 14, 15):
        return 1
    elif score in (16, 17):
        return 2
    elif score == 18:
        return 3
    else:
        return 0


def check_character_ac():
    """Check if the character's AC calculation is correct."""
    # Get database session
    db_context = get_db_context()
    session = Session(db_context["engine"])

    try:
        # Get the character with ID 20
        character_id = 20
        character = session.scalars(
            select(Character).where(Character.id == character_id)
        ).first()

        if not character:
            logger.error(f"Character with ID {character_id} not found.")
            return

        # Print character details
        logger.info(f"Character: {character.name}")
        logger.info(f"Current AC: {character.armor_class}")
        logger.info(f"Race: {character.race}")
        logger.info(f"Class: {character.character_class}")
        logger.info(f"Dexterity: {character.dexterity}")

        # Calculate dexterity modifier
        dex_mod = get_ability_modifier(character.dexterity)
        logger.info(f"Dexterity Modifier: {dex_mod}")

        # Get equipped items
        equipped_items = session.scalars(
            select(CharacterItem).where(
                CharacterItem.character_id == character.id,
                CharacterItem.equipped
            )
        ).all()

        logger.info("Equipped items:")
        base_ac = 10
        shield_bonus = 0

        # Check for armor and shield
        for char_item in equipped_items:
            item = session.scalars(
                select(Item).where(Item.id == char_item.item_id)
            ).first()

            if not item:
                logger.warning(f"Item with ID {char_item.item_id} not found")
                continue

            logger.info(f"Item: {item.name} (ID: {item.id})")
            logger.info(f"  Slot: {char_item.slot}")
            logger.info(f"  Type: {item.type}")
            logger.info(f"  AC: {item.armor_class}")
            logger.info(f"  AC Bonus: {item.ac_bonus}")

            # Check if it's armor (worn on body) and has armor_class
            if item.type == "armor" and char_item.slot == "body":
                if item.armor_class:
                    base_ac = item.armor_class
                    logger.info(f"Using armor_class {base_ac} from {item.name}")
                if item.properties:
                    logger.info("Item properties: {item.properties}")

            # Check if it's a shield
            elif item.type == "shield" and char_item.slot == "off_hand":
                if item.ac_bonus:
                    shield_bonus = item.ac_bonus
                    logger.info(f"Using shield bonus {shield_bonus} from {item.name}")
                if item.properties:
                    logger.info("Item properties: {item.properties}")
            
            # Check for other items with ac_bonus
            elif item.ac_bonus:
                shield_bonus += item.ac_bonus
                logger.info(
                    f"Adding AC bonus {item.ac_bonus} from {item.name} in slot {char_item.slot}"
                )

        # Print equipment from JSON field for comparison
        logger.info("Equipment from JSON field:")
        if character.equipment:
            for slot, item_id in character.equipment.items():
                if item_id:
                    item = session.scalars(
                        select(Item).where(Item.id == item_id)
                    ).first()
                    item_name = item.name if item else "Unknown"
                    logger.info(
                        f"  {slot}: {item_name} (ID: {item_id})"
                    )
                else:
                    logger.info(f"  {slot}: Empty")

        # Calculate expected armor class
        expected_ac = base_ac + shield_bonus + dex_mod
        logger.info(
            f"AC calculation: {base_ac} (base AC) + "
            f"{shield_bonus} (shield) + {dex_mod} (DEX mod) = {expected_ac}"
        )

        # Check if AC is correct
        if character.armor_class == expected_ac:
            logger.info("✓ Armor class is correct!")
        else:
            logger.error(
                f"✗ Armor class should be {expected_ac}, but it's {character.armor_class}"
            )
            logger.info("To fix this, you can run:")
            logger.info(
                "python -c \"from app.models.character import Character; "
                "from app.db.context import get_db_context; "
                "from sqlalchemy.orm import Session; "
                f"db = get_db_context(); "
                f"session = Session(db['engine']); "
                f"character = session.get(Character, {character_id}); "
                f"character.armor_class = {expected_ac}; "
                f"session.commit(); "
                f"print('Updated AC for {character.name} from {character.armor_class} to {expected_ac}');\""
            )

    finally:
        session.close()


if __name__ == "__main__":
    check_character_ac()
