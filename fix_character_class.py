import logging
import sys
from app.database import get_db, engine
from app.models.base import Base
from app.models.character import Character
from sqlalchemy import text
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

def fix_character_class():
    """Fix case sensitivity issues in character class enum values"""
    logger.info("Starting character class enum value fix")
    
    with Session(engine) as session:
        # Check for characters with lowercase class values
        fighter_query = text("SELECT COUNT(*) FROM characters WHERE character_class = 'fighter'")
        cleric_query = text("SELECT COUNT(*) FROM characters WHERE character_class = 'cleric'")
        magic_user_query = text("SELECT COUNT(*) FROM characters WHERE character_class = 'magic-user'")
        thief_query = text("SELECT COUNT(*) FROM characters WHERE character_class = 'thief'")
        
        fighter_count = session.execute(fighter_query).scalar() or 0
        cleric_count = session.execute(cleric_query).scalar() or 0
        magic_user_count = session.execute(magic_user_query).scalar() or 0
        thief_count = session.execute(thief_query).scalar() or 0
        
        total_lowercase = fighter_count + cleric_count + magic_user_count + thief_count
        
        if total_lowercase == 0:
            logger.info("No characters found with lowercase class values. No updates needed.")
            return
        
        logger.info(f"Found {total_lowercase} characters with lowercase class values:")
        logger.info(f"- 'fighter': {fighter_count}")
        logger.info(f"- 'cleric': {cleric_count}")
        logger.info(f"- 'magic-user': {magic_user_count}")
        logger.info(f"- 'thief': {thief_count}")
        
        # Perform updates if requested
        if len(sys.argv) > 1 and sys.argv[1] == "--check-only":
            logger.info("Check-only mode. Not performing updates.")
            return
        
        # Update each class type to uppercase
        try:
            if fighter_count > 0:
                update_fighter = text("UPDATE characters SET character_class = 'FIGHTER' WHERE character_class = 'fighter'")
                session.execute(update_fighter)
                logger.info(f"Updated {fighter_count} fighter characters")
            
            if cleric_count > 0:
                update_cleric = text("UPDATE characters SET character_class = 'CLERIC' WHERE character_class = 'cleric'")
                session.execute(update_cleric)
                logger.info(f"Updated {cleric_count} cleric characters")
            
            if magic_user_count > 0:
                update_magic_user = text("UPDATE characters SET character_class = 'MAGIC-USER' WHERE character_class = 'magic-user'")
                session.execute(update_magic_user)
                logger.info(f"Updated {magic_user_count} magic-user characters")
            
            if thief_count > 0:
                update_thief = text("UPDATE characters SET character_class = 'THIEF' WHERE character_class = 'thief'")
                session.execute(update_thief)
                logger.info(f"Updated {thief_count} thief characters")
            
            session.commit()
            logger.info("Successfully updated all character class values to uppercase")
            
            # Verify the updates worked
            verify_query = text("SELECT COUNT(*) FROM characters WHERE character_class IN ('fighter', 'cleric', 'magic-user', 'thief')")
            remaining_lowercase = session.execute(verify_query).scalar() or 0
            
            if remaining_lowercase > 0:
                logger.error(f"Update incomplete. Still found {remaining_lowercase} characters with lowercase class values.")
            else:
                logger.info("Verification successful. All character class values are now uppercase.")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating character class values: {str(e)}")
            raise

if __name__ == "__main__":
    fix_character_class() 