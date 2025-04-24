import logging
import sys
from app.database import get_db_context
from app.models import Character, Item
from app.routers.items import unequip_item

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_unequip_armor(character_name):
    """Test the unequipping of armor for a character"""
    logger.info(f"Starting armor unequip test for {character_name}")
    
    # Get DB context
    with get_db_context() as db:
        try:
            # Query the character by name
            character = db.query(Character).filter(Character.name == character_name).first()
            
            if not character:
                logger.error(f"Character {character_name} not found in database")
                return False
            
            logger.info(f"Retrieved character: {character.name} (ID: {character.id})")
            
            # Check if character has equipped armor
            if not character.equipment:
                logger.error(f"Character {character_name} has no equipment")
                return False
            
            # Find armor in equipment - in this case, the slot is "body"
            body_slot = None
            for slot, item_id in character.equipment.items():
                if slot == "body":
                    body_slot = slot
                    break
            
            if not body_slot:
                logger.error(f"Character {character_name} has no armor equipped")
                return False
            
            logger.info(f"Found equipped armor in slot '{body_slot}'")
            
            # Get the armor item
            armor_id = character.equipment[body_slot]
            armor_item = db.query(Item).filter(Item.id == armor_id).first()
            
            # Calculate expected AC after unequipping
            shield_bonus = 0
            if "off_hand" in character.equipment:
                shield_id = character.equipment["off_hand"]
                shield_item = db.query(Item).filter(Item.id == shield_id).first()
                if shield_item and shield_item.properties and "ac_bonus" in shield_item.properties:
                    shield_bonus = shield_item.properties["ac_bonus"]
            
            # Calculate dexterity modifier
            dex_mod = (character.dexterity - 10) // 2
            expected_ac = 10 + dex_mod + shield_bonus
            
            logger.info(f"Unequipping armor. Expected AC will be: {expected_ac}")
            
            # Create mock user for FastAPI dependency
            class MockUser:
                id = character.user_id
            
            # Call the unequip_item function with the required parameters
            updated_character = unequip_item(
                slot=body_slot,
                character_id=character.id,
                db=db,
                current_user=MockUser()
            )
            
            # Verify AC after unequipping
            logger.info(f"After unequipping - AC: {updated_character.armor_class}, Expected: {expected_ac}")
            if updated_character.armor_class != expected_ac:
                logger.error(f"AC mismatch after unequipping: Got {updated_character.armor_class}, Expected {expected_ac}")
            else:
                logger.info("Armor class correctly updated after unequipping armor.")
            
            # Test completed
            logger.info(f"Armor unequip test completed for {character_name}")
            return True
        
        except Exception as e:
            logger.error(f"Error in unequip armor test: {str(e)}")
            return False

# Modify this to use asyncio.run for async functions
import asyncio

if __name__ == "__main__":
    asyncio.run(test_unequip_armor("Skilrok")) 