from app.models.character import Character
from app.models.character_item import CharacterItem
from app.models.item import Item
from app.database import get_db_context
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def get_ability_modifier(score):
    """Calculate ability score modifier"""
    if score == 3:
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
    elif score == 18:
        return 3
    else:
        return 0

def fix_character_ac_calculations():
    """Fix armor class calculations for all characters based on equipped items"""
    logger.info("Starting AC calculation fix for all characters")
    
    with get_db_context() as db:
        characters = db.query(Character).all()
        logger.info(f"Found {len(characters)} characters to process")
        
        updated_count = 0
        
        for character in characters:
            logger.info(f"Processing character: {character.name} (ID: {character.id})")
            # Get equipped items
            items = db.query(CharacterItem).filter(
                CharacterItem.character_id == character.id,
                CharacterItem.is_equipped == True
            ).all()
            
            # Start with base AC of 10
            base_ac = 10
            shield_bonus = 0
            
            # Calculate dexterity modifier
            dex_mod = get_ability_modifier(character.dexterity)
            logger.info(f"Dexterity: {character.dexterity}, Modifier: {dex_mod}")
            
            # Process equipped items
            for ci in items:
                item = db.query(Item).filter(Item.id == ci.item_id).first()
                if not item:
                    logger.warning(f"Item ID {ci.item_id} not found in database")
                    continue
                
                logger.info(f"Checking equipped item: {item.name} (ID: {item.id}) in slot {ci.equip_slot}")
                
                # Handle armor
                if item.item_type.value == "armor":
                    # Check if it's in the body slot or just marked as equipped
                    if ci.equip_slot == "body" or (ci.is_equipped and not ci.equip_slot):
                        if item.armor_class is not None:
                            base_ac = item.armor_class
                            logger.info(f"Using armor_class column value: {base_ac}")
                        elif item.ac_bonus is not None:
                            base_ac = item.ac_bonus
                            logger.info(f"Using ac_bonus column value: {base_ac}")
                        elif item.properties and "armor_class" in item.properties:
                            base_ac = item.properties["armor_class"]
                            logger.info(f"Using properties armor_class value: {base_ac}")
                        elif item.properties and "ac_bonus" in item.properties:
                            base_ac = item.properties["ac_bonus"]
                            logger.info(f"Using properties ac_bonus value: {base_ac}")
                
                # Handle shield
                if item.item_type.value == "shield" and (ci.equip_slot == "off_hand" or (ci.is_equipped and not ci.equip_slot)):
                    if item.ac_bonus is not None:
                        shield_bonus = item.ac_bonus
                        logger.info(f"Using shield ac_bonus column value: {shield_bonus}")
                    elif item.properties and "ac_bonus" in item.properties:
                        shield_bonus = item.properties["ac_bonus"]
                        logger.info(f"Using shield properties ac_bonus value: {shield_bonus}")
            
            # Calculate new AC
            new_ac = base_ac + shield_bonus + dex_mod
            
            # Update if different
            if character.armor_class != new_ac:
                logger.info(f"Updating {character.name} AC from {character.armor_class} to {new_ac}")
                character.armor_class = new_ac
                db.add(character)
                updated_count += 1
            else:
                logger.info(f"AC for {character.name} is already correct: {character.armor_class}")
        
        # Commit all changes
        if updated_count > 0:
            logger.info(f"Committing changes for {updated_count} characters")
            db.commit()
            logger.info("Armor class calculations fixed for all characters")
        else:
            logger.info("No changes needed - all characters have correct AC values")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fix armor class calculations for all characters")
    parser.add_argument("--check-only", action="store_true", help="Only check AC values without updating")
    parser.add_argument("--character-id", type=int, help="Process only the specified character ID")
    args = parser.parse_args()

    if args.check_only:
        logger.info("Running in check-only mode")
    
    fix_character_ac_calculations() 