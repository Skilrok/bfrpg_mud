import logging
import os
import sys
from sqlalchemy import Column, Integer, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# Add the current directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, get_db
from app.models.item import Item

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_ac_bonus_column():
    """
    Add ac_bonus column to items table if it doesn't exist and 
    migrate ac_bonus values from properties
    """
    inspector = inspect(engine)
    columns = [column['name'] for column in inspector.get_columns('items')]
    
    # Check if column already exists
    if 'ac_bonus' in columns:
        logger.info("ac_bonus column already exists in items table")
        return False
    
    try:
        # Add the column
        with engine.begin() as conn:
            logger.info("Adding ac_bonus column to items table")
            conn.execute(text("ALTER TABLE items ADD COLUMN ac_bonus INTEGER"))
        
        # Migrate data from properties
        with Session(engine) as session:
            # Get all items that might have ac_bonus in properties
            items = session.query(Item).all()
            count = 0
            
            for item in items:
                # Extract ac_bonus from properties if it exists
                if item.properties and 'ac_bonus' in item.properties:
                    try:
                        ac_bonus_value = int(item.properties['ac_bonus'])
                        item.ac_bonus = ac_bonus_value
                        logger.info(f"Set ac_bonus={ac_bonus_value} for item id={item.id}, name='{item.name}'")
                        count += 1
                    except (ValueError, TypeError) as e:
                        logger.error(f"Error converting ac_bonus for item {item.id}: {e}")
            
            if count > 0:
                logger.info(f"Migrated ac_bonus for {count} items")
                session.commit()
            else:
                logger.info("No items found with ac_bonus in properties")
        
        return True
    
    except Exception as e:
        logger.error(f"Error adding ac_bonus column: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful"""
    # Check a specific item (shield with ID 80)
    with Session(engine) as session:
        shield = session.query(Item).filter(Item.id == 80).first()
        
        if not shield:
            logger.warning("Shield with ID 80 not found for verification")
            return
        
        logger.info(f"Verification - Item ID 80: {shield.name}")
        logger.info(f"  - ac_bonus column value: {shield.ac_bonus}")
        logger.info(f"  - properties value: {shield.properties.get('ac_bonus') if shield.properties else None}")

def run_migration():
    """Run the migration and verify results"""
    logger.info("Starting ac_bonus column migration")
    
    success = add_ac_bonus_column()
    
    if success:
        logger.info("Migration completed successfully")
        verify_migration()
    else:
        logger.info("Migration skipped or failed")
    
    logger.info("Migration process completed")

if __name__ == "__main__":
    run_migration() 