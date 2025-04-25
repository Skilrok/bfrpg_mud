import logging
from app.database import get_db_context
from app.models.item import Item

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_shield_ac_bonus():
    """
    Check if the shield item (ID 80) has a value in the ac_bonus column
    and validate whether it matches the value in the properties dictionary.
    """
    try:
        with get_db_context() as db:
            # Get the shield item with ID 80
            shield = db.query(Item).filter(Item.id == 80).first()
            
            if not shield:
                logger.error("Shield with ID 80 not found in the database")
                return
            
            logger.info(f"Found shield: {shield.name} (ID: {shield.id})")
            logger.info(f"Item type: {shield.item_type}")
            
            # Check the ac_bonus column
            logger.info(f"ac_bonus column value: {shield.ac_bonus}")
            
            # Check the properties dictionary
            if shield.properties and 'ac_bonus' in shield.properties:
                logger.info(f"properties['ac_bonus'] value: {shield.properties['ac_bonus']}")
            else:
                logger.info("No ac_bonus found in properties dictionary")
            
            # Check example usage in code
            logger.info("\nAC bonus usage examples:")
            logger.info("1. Current code typically reads from properties['ac_bonus']")
            logger.info("2. New column value (shield.ac_bonus) is not used in most places")
            logger.info("3. To fully utilize the new column, code would need to be updated")
            
            # Recommendation
            logger.info("\nRecommendation:")
            if shield.ac_bonus is not None:
                logger.info("✅ The ac_bonus column is populated")
                
                # Check consistency
                if shield.properties and 'ac_bonus' in shield.properties:
                    if shield.ac_bonus == shield.properties['ac_bonus']:
                        logger.info("✅ The ac_bonus column value matches the properties value")
                    else:
                        logger.error("❌ The ac_bonus column value does NOT match the properties value")
                        logger.info(f"   Column: {shield.ac_bonus}, Properties: {shield.properties['ac_bonus']}")
            else:
                logger.error("❌ The ac_bonus column is NOT populated")
                logger.info("   Code using this column will not work as expected")
                
    except Exception as e:
        logger.error(f"Error checking shield ac_bonus: {e}")

if __name__ == "__main__":
    check_shield_ac_bonus() 