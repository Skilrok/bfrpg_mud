import logging
from app.database import get_db
from app.models.item import Item

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_shield_item():
    """Check details of the shield with ID 80"""
    try:
        db = next(get_db())
        
        # Query the database for the shield item
        shield = db.query(Item).filter(Item.id == 80).first()
        
        if shield:
            logger.info(f"Found shield item (ID: {shield.id})")
            logger.info(f"  Name: {shield.name}")
            logger.info(f"  Description: {shield.description}")
            logger.info(f"  Type: {shield.item_type}")
            logger.info(f"  Value: {shield.value} gold")
            logger.info(f"  Weight: {shield.weight} lbs")
            
            # Log all properties in a structured way
            logger.info("  Properties:")
            if shield.properties:
                for key, value in shield.properties.items():
                    logger.info(f"    {key}: {value}")
            else:
                logger.info("    No properties defined")
        else:
            logger.error(f"Shield with ID 80 not found!")
    
    except Exception as e:
        logger.error(f"Error checking shield: {str(e)}")

if __name__ == "__main__":
    check_shield_item() 