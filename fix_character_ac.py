import logging
import argparse
from app.models.character import Character
from app.models.character_item import CharacterItem
from app.models.item import Item
from app.database import get_db_context

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_ability_modifier(score):
    """Calculate ability score modifier based on D&D rules."""
    if score <= 3:
        return -3
    elif score <= 5:
        return -2
    elif score <= 8:
        return -1
    elif score <= 12:
        return 0
    elif score <= 15:
        return 1
    elif score <= 17:
        return 2
    else:
        return 3

def fix_character_ac_calculations(check_only=False):
    """Fix armor class calculations for all characters based on equipped items."""
    logger.info("Fixing AC calculations for all characters...")
    
    # Setup database session using context manager
    with get_db_context() as db:
        try:
            # Get all characters
            characters = db.query(Character).all()
            logger.info(f"Found {len(characters)} characters to process")
            
            updated_count = 0
            
            # Process each character
            for character in characters:
                logger.info(f"Processing {character.name} (ID: {character.id})")
                logger.info(f"Current AC: {character.armor_class}")
                logger.info(f"Dexterity: {character.dexterity}")
                
                # Calculate dexterity modifier
                dex_modifier = get_ability_modifier(character.dexterity)
                logger.info(f"Dexterity modifier: {dex_modifier}")
                
                # Get equipped items for this character
                equipped_items = db.query(CharacterItem).filter(
                    CharacterItem.character_id == character.id,
                    CharacterItem.is_equipped == True
                ).all()
                
                logger.info(f"Found {len(equipped_items)} equipped items")
                
                # Initialize AC calculation values
                base_ac = 10  # Default base AC
                shield_bonus = 0
                
                # Process each equipped item to determine AC effects
                for char_item in equipped_items:
                    # Get the item details
                    item = db.query(Item).filter(Item.id == char_item.item_id).first()
                    
                    if not item:
                        logger.warning(f"Item ID {char_item.item_id} not found in database")
                        continue
                    
                    logger.info(f"Checking item: {item.name} (ID: {item.id}) in slot: {char_item.equip_slot}")
                    
                    # Process armor (body slot items that affect base AC)
                    if item.item_type == "armor" and char_item.equip_slot == "body":
                        # Check if item has armor_class attribute
                        if item.armor_class is not None:
                            logger.info(f"Setting base AC to {item.armor_class} from armor")
                            base_ac = item.armor_class
                        # Also check properties for armor_class
                        elif item.properties and 'armor_class' in item.properties:
                            logger.info(f"Setting base AC to {item.properties['armor_class']} from armor properties")
                            base_ac = item.properties['armor_class']
                    
                    # Process shields (items that add AC bonus)
                    if item.item_type == "shield" or (item.properties and item.properties.get('is_shield')):
                        # Check ac_bonus attribute
                        if item.ac_bonus is not None:
                            logger.info(f"Adding shield bonus of {item.ac_bonus}")
                            shield_bonus += item.ac_bonus
                        # Also check properties for ac_bonus
                        elif item.properties and 'ac_bonus' in item.properties:
                            logger.info(f"Adding shield bonus of {item.properties['ac_bonus']} from properties")
                            shield_bonus += item.properties['ac_bonus']
                
                # Calculate expected AC
                expected_ac = base_ac + shield_bonus + dex_modifier
                logger.info(f"Expected AC calculation: {base_ac} (base) + {shield_bonus} (shield) + {dex_modifier} (DEX) = {expected_ac}")
                
                # Update AC if needed
                if character.armor_class != expected_ac:
                    logger.info(f"Updating AC for {character.name} from {character.armor_class} to {expected_ac}")
                    updated_count += 1
                    
                    if not check_only:
                        character.armor_class = expected_ac
                        db.add(character)
                else:
                    logger.info(f"AC is already correct for {character.name}: {character.armor_class}")
            
            # Commit changes if not in check-only mode
            if not check_only and updated_count > 0:
                db.commit()
                logger.info(f"Successfully updated AC for {updated_count} characters")
            else:
                if check_only:
                    logger.info(f"Found {updated_count} characters with incorrect AC calculations (check-only mode, no changes made)")
                else:
                    logger.info("No AC updates needed")
                
        except Exception as e:
            logger.error(f"Error updating character AC: {e}")
            db.rollback()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix character armor class calculations")
    parser.add_argument("--check-only", action="store_true", help="Check for AC issues without applying fixes")
    args = parser.parse_args()
    
    fix_character_ac_calculations(check_only=args.check_only)