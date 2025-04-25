import logging
import argparse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.character import Character
from app.models.character_item import CharacterItem
from app.models.item import Item

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_ability_modifier(score):
    """Calculate ability modifier based on score."""
    if score <= 3:
        return -3
    elif 4 <= score <= 5:
        return -2
    elif 6 <= score <= 8:
        return -1
    elif 9 <= score <= 12:
        return 0
    elif 13 <= score <= 15:
        return 1
    elif 16 <= score <= 17:
        return 2
    elif score >= 18:
        return 3

def fix_character_ac_calculations(check_only=False):
    """Update character AC based on equipped items and dexterity.
    
    Args:
        check_only: If True, only check for discrepancies without updating.
    """
    logger.info("Starting to fix AC calculations for all characters")
    
    # Create database session
    db = next(get_db())
    
    try:
        # Get all characters from the database
        characters = db.query(Character).all()
        logger.info(f"Found {len(characters)} characters to process")
        
        update_count = 0
        
        for character in characters:
            logger.info(f"Processing character {character.name} (ID: {character.id})")
            
            # Calculate dexterity modifier
            dex_modifier = get_ability_modifier(character.dexterity)
            logger.info(f"Character dexterity: {character.dexterity}, modifier: {dex_modifier}")
            
            # Get equipped items from CharacterItem table
            equipped_items = (
                db.query(CharacterItem)
                .filter(CharacterItem.character_id == character.id, CharacterItem.is_equipped == True)
                .all()
            )
            
            logger.info(f"Found {len(equipped_items)} equipped items")
            
            # Calculate AC based on equipped items
            base_ac = 10  # Default base AC
            shield_bonus = 0
            
            for char_item in equipped_items:
                # Get the actual item
                item = db.query(Item).filter(Item.id == char_item.item_id).first()
                
                if not item:
                    logger.warning(f"Item ID {char_item.item_id} not found in database")
                    continue
                
                logger.info(f"Checking item: {item.name} (ID: {item.id}) in slot: {char_item.equip_slot}")
                
                # Check if item is armor
                if item.item_type == "Armor" and char_item.equip_slot == "body":
                    armor_class = item.armor_class or 0
                    if armor_class > 0:
                        logger.info(f"Found armor with AC {armor_class}")
                        base_ac = armor_class
                    
                    ac_bonus = item.ac_bonus or 0
                    if ac_bonus > 0:
                        logger.info(f"Found armor with AC bonus {ac_bonus}")
                        base_ac += ac_bonus
                
                # Check if item is a shield
                elif item.item_type == "Armor" and char_item.equip_slot == "off_hand":
                    shield_ac = item.ac_bonus or 0
                    if shield_ac > 0:
                        logger.info(f"Found shield with AC bonus {shield_ac}")
                        shield_bonus = shield_ac
            
            # Calculate expected AC
            expected_ac = base_ac + shield_bonus + dex_modifier
            
            logger.info(f"Current AC: {character.armor_class}, Expected AC: {expected_ac}")
            
            # Update AC if necessary
            if character.armor_class != expected_ac:
                logger.info(f"Updating AC for {character.name} from {character.armor_class} to {expected_ac}")
                update_count += 1
                
                if not check_only:
                    character.armor_class = expected_ac
                    db.add(character)
        
        if update_count > 0:
            if check_only:
                logger.info(f"Found {update_count} characters with incorrect AC calculations")
            else:
                db.commit()
                logger.info(f"Updated AC for {update_count} characters")
        else:
            logger.info("All character AC calculations are correct")
            
    except Exception as e:
        logger.error(f"Error fixing AC calculations: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix character AC calculations")
    parser.add_argument("--check-only", action="store_true", 
                        help="Only check for AC discrepancies without updating")
    args = parser.parse_args()
    
    fix_character_ac_calculations(check_only=args.check_only)