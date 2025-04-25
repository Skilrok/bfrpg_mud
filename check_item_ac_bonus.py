import logging

from app.database import get_db
from app.models.item import Item

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_item_ac_bonus():
    """
    Check if item with ID 80 has ac_bonus property in its properties JSON field.
    """
    try:
        # Get database session
        db = next(get_db())

        # Query item with ID 80
        item = db.query(Item).filter(Item.id == 80).first()

        if not item:
            logger.error(f"Item with ID 80 not found in the database")
            return

        logger.info(f"Item ID 80: {item.name}, Type: {item.item_type}")
        logger.info(f"Properties: {item.properties}")

        # Check if ac_bonus property exists
        if item.properties and "ac_bonus" in item.properties:
            logger.info(
                f"ac_bonus property exists with value: {item.properties['ac_bonus']}"
            )
        else:
            logger.info("ac_bonus property does not exist in the item properties")

    except Exception as e:
        logger.error(f"Error checking item ac_bonus: {str(e)}")


if __name__ == "__main__":
    check_item_ac_bonus()
