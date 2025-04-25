import logging
from app.database import get_db
from app.models.item import Item

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_item_ac_bonus():
    """Update item ID 80 to add ac_bonus property"""
    db = next(get_db())
    
    try:
        # Get item 80
        item = db.query(Item).filter(Item.id == 80).first()
        
        if not item:
            logger.error("Item ID 80 not found in database")
            return False
            
        logger.info(f"Found item: {item.name} (ID: {item.id})")
        logger.info(f"Current properties: {item.properties}")
        
        # Initialize properties if None
        if item.properties is None:
            item.properties = {}
            
        # Add ac_bonus if it doesn't exist
        if 'ac_bonus' not in item.properties:
            # Set ac_bonus to 1 by default, adjust as needed
            item.properties['ac_bonus'] = 1
            db.commit()
            logger.info(f"Added ac_bonus=1 to item {item.name}")
        else:
            logger.info(f"Item already has ac_bonus = {item.properties['ac_bonus']}")
            
        # Verify the update
        item = db.query(Item).filter(Item.id == 80).first()
        logger.info(f"Updated properties: {item.properties}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        db.rollback()
        return False

if __name__ == "__main__":
    update_item_ac_bonus() 