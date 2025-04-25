#!/usr/bin/env python3
"""
Script to fix case sensitivity issues with enum values in the database.
"""

import logging
import traceback
from sqlalchemy import text
from app.database import get_db_context
from app.models.character import CharacterClass, CharacterRace

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_enum_values():
    """Inspect enum values in both the enum definitions and database"""
    logger.info("Inspecting enum values")
    
    # Print enum values from class definitions
    logger.info("Enum values from class definitions:")
    logger.info(f"CharacterRace: {[e.value for e in CharacterRace]}")
    logger.info(f"CharacterClass: {[e.value for e in CharacterClass]}")
    
    # Check values in database
    with get_db_context() as db:
        try:
            # Get distinct race values
            races = db.execute(text("SELECT DISTINCT race FROM characters")).fetchall()
            race_values = [r[0] for r in races]
            logger.info(f"Race values in database: {race_values}")
            
            # Get distinct class values
            classes = db.execute(text("SELECT DISTINCT character_class FROM characters")).fetchall()
            class_values = [c[0] for c in classes]
            logger.info(f"Class values in database: {class_values}")
            
            # Check for mismatches
            race_mismatches = []
            for db_race in race_values:
                if db_race not in [e.value for e in CharacterRace]:
                    race_mismatches.append(db_race)
            
            class_mismatches = []
            for db_class in class_values:
                if db_class not in [e.value for e in CharacterClass]:
                    class_mismatches.append(db_class)
            
            if race_mismatches:
                logger.warning(f"Race value mismatches: {race_mismatches}")
            else:
                logger.info("No race value mismatches")
                
            if class_mismatches:
                logger.warning(f"Class value mismatches: {class_mismatches}")
            else:
                logger.info("No class value mismatches")
                
            # Get records with potentially problematic values
            for race in race_mismatches:
                chars = db.execute(text(
                    "SELECT id, name FROM characters WHERE race = :race"
                ), {"race": race}).fetchall()
                for char_id, char_name in chars:
                    logger.warning(f"Character {char_name} (ID: {char_id}) has invalid race: '{race}'")
            
            for cls in class_mismatches:
                chars = db.execute(text(
                    "SELECT id, name FROM characters WHERE character_class = :class"
                ), {"class": cls}).fetchall()
                for char_id, char_name in chars:
                    logger.warning(f"Character {char_name} (ID: {char_id}) has invalid class: '{cls}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Error inspecting enum values: {str(e)}")
            traceback.print_exc()
            return False

def fix_enum_case_issues():
    """Fix case sensitivity issues in enum columns"""
    logger.info("Checking for case sensitivity issues in enum fields")
    
    with get_db_context() as db:
        try:
            # Use raw SQL to fetch characters without triggering ORM validation
            result = db.execute(text("""
                SELECT id, name, race, character_class FROM characters
            """)).fetchall()
            
            logger.info(f"Found {len(result)} characters in the database")
            
            fixes_applied = 0
            race_fixes = 0
            class_fixes = 0
            
            # Process each character
            for row in result:
                char_id, char_name, race, char_class = row
                logger.info(f"Checking character: {char_name} (ID: {char_id})")
                logger.info(f"  Race: '{race}', Class: '{char_class}'")
                
                # Check if race needs fixing
                fixed_race = None
                if race and isinstance(race, str):
                    for enum_value in CharacterRace:
                        if race.upper() == enum_value.value.upper() and race != enum_value.value:
                            fixed_race = enum_value.value
                            logger.info(f"  Fixing race: '{race}' → '{fixed_race}'")
                            break
                
                # Check if class needs fixing
                fixed_class = None
                if char_class and isinstance(char_class, str):
                    for enum_value in CharacterClass:
                        if char_class.upper() == enum_value.value.upper() and char_class != enum_value.value:
                            fixed_class = enum_value.value
                            logger.info(f"  Fixing class: '{char_class}' → '{fixed_class}'")
                            break
                
                # Apply fixes if needed
                if fixed_race or fixed_class:
                    update_fields = {}
                    if fixed_race:
                        update_fields["race"] = fixed_race
                        race_fixes += 1
                    
                    if fixed_class:
                        update_fields["character_class"] = fixed_class
                        class_fixes += 1
                    
                    # Execute update without ORM validation
                    if update_fields:
                        db.execute(
                            text(f"""
                                UPDATE characters 
                                SET {', '.join([f"{k} = :{k}" for k in update_fields])} 
                                WHERE id = :id
                            """),
                            {**update_fields, "id": char_id}
                        )
                        fixes_applied += 1
                        logger.info(f"  Applied fixes for character {char_name}")
            
            # Commit changes
            db.commit()
            logger.info(f"Fixed enum case issues for {fixes_applied} characters")
            logger.info(f"  Race fixes: {race_fixes}, Class fixes: {class_fixes}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error fixing enum case issues: {str(e)}")
            traceback.print_exc()
            db.rollback()
            return False

def force_fix_enum_values():
    """Force fix enum values in database by direct update"""
    logger.info("Force fixing enum values in database")
    
    with get_db_context() as db:
        try:
            # Get actual enum values
            race_values = {e.name: e.value for e in CharacterRace}
            class_values = {e.name: e.value for e in CharacterClass}
            
            logger.info(f"Valid race values: {race_values}")
            logger.info(f"Valid class values: {class_values}")
            
            # Map from lowercase value to correct value
            race_map = {v.lower(): v for v in race_values.values()}
            class_map = {v.lower(): v for v in class_values.values()}
            
            # Fix race values
            for lowercase, correct in race_map.items():
                if lowercase != correct:
                    result = db.execute(
                        text("UPDATE characters SET race = :correct WHERE LOWER(race) = :lowercase"),
                        {"correct": correct, "lowercase": lowercase}
                    )
                    if result.rowcount > 0:
                        logger.info(f"Fixed {result.rowcount} characters with race '{lowercase}' → '{correct}'")
            
            # Fix class values
            for lowercase, correct in class_map.items():
                if lowercase != correct:
                    result = db.execute(
                        text("UPDATE characters SET character_class = :correct WHERE LOWER(character_class) = :lowercase"),
                        {"correct": correct, "lowercase": lowercase}
                    )
                    if result.rowcount > 0:
                        logger.info(f"Fixed {result.rowcount} characters with class '{lowercase}' → '{correct}'")
            
            # Commit changes
            db.commit()
            logger.info("Forced fixes applied to enum values")
            
            # Verify the fixes worked
            return inspect_enum_values()
            
        except Exception as e:
            logger.error(f"Error force fixing enum values: {str(e)}")
            traceback.print_exc()
            db.rollback()
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix enum case sensitivity issues")
    parser.add_argument("--inspect", action="store_true", help="Only inspect enum values without fixing")
    parser.add_argument("--force", action="store_true", help="Force fix all enum values using direct SQL UPDATE")
    args = parser.parse_args()
    
    if args.inspect:
        inspect_enum_values()
    elif args.force:
        force_fix_enum_values()
    else:
        fix_enum_case_issues()
        inspect_enum_values() 