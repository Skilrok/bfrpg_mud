from sqlalchemy import create_engine, text
import logging

from app.database import get_db
from app.models.character import CharacterClass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_character_class_enum():
    """
    Fix character class enum values in the database - converts lowercase values to uppercase.
    Using direct SQL to avoid SQLAlchemy enum validation issues.
    """
    db = next(get_db())
    
    try:
        # Get all character IDs and classes directly using SQL
        result = db.execute(text("""
            SELECT id, name, character_class FROM characters
        """))
        characters = result.fetchall()
        logger.info(f"Found {len(characters)} characters in the database")
        
        # Map of lowercase class values to their uppercase enum values
        class_map = {
            "fighter": "FIGHTER",
            "cleric": "CLERIC",
            "magic-user": "MAGIC_USER",
            "thief": "THIEF",
            "fighter/magic-user": "FIGHTER_MAGIC_USER",
            "magic-user/thief": "MAGIC_USER_THIEF"
        }
        
        # Check and fix class values
        fixed_count = 0
        for character in characters:
            char_id, char_name, current_class = character
            
            # If the class is already uppercase, skip
            if current_class in [cls.name for cls in CharacterClass]:
                logger.info(f"Character '{char_name}' (ID: {char_id}) already has correct class format: '{current_class}'")
                continue
            
            # If the class is in the map, update to uppercase
            if current_class in class_map:
                uppercase_class = class_map[current_class]
                logger.info(f"Fixing character '{char_name}' (ID: {char_id}): "
                           f"Changing class from '{current_class}' to '{uppercase_class}'")
                
                # Update the class via SQL
                db.execute(text("""
                    UPDATE characters 
                    SET character_class = :new_class 
                    WHERE id = :char_id
                """), {"new_class": uppercase_class, "char_id": char_id})
                fixed_count += 1
            else:
                logger.warning(f"Character '{char_name}' (ID: {char_id}) has class value '{current_class}' "
                              f"that doesn't match any expected value")
        
        # Commit changes
        if fixed_count > 0:
            db.commit()
            logger.info(f"Successfully fixed {fixed_count} character class values")
        else:
            logger.info("No character class values needed fixing")
            
        # Verify changes
        verify_result = db.execute(text("""
            SELECT id, name, character_class FROM characters
        """))
        characters = verify_result.fetchall()
        
        invalid_count = 0
        for character in characters:
            char_id, char_name, current_class = character
            if current_class not in [cls.name for cls in CharacterClass]:
                invalid_count += 1
                logger.error(f"Character '{char_name}' (ID: {char_id}) still has invalid class: '{current_class}'")
                
        if invalid_count == 0:
            logger.info("All character classes are now valid enum values")
        else:
            logger.error(f"Found {invalid_count} characters with still invalid class values after fix attempt")
            
    except Exception as e:
        logger.error(f"Error fixing character classes: {str(e)}")
        logger.error(f"Traceback:", exc_info=True)
        db.rollback()

if __name__ == "__main__":
    fix_character_class_enum() 