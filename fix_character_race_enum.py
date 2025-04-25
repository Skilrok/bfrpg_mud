import logging

from sqlalchemy import create_engine, text

from app.database import get_db
from app.models.character import CharacterRace

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_character_race_enum():
    """
    Fix character race enum values in the database - converts lowercase values to uppercase.
    Using direct SQL to avoid SQLAlchemy enum validation issues.
    """
    db = next(get_db())

    try:
        # Get all character IDs and races directly using SQL
        result = db.execute(
            text(
                """
            SELECT id, name, race FROM characters
        """
            )
        )
        characters = result.fetchall()
        logger.info(f"Found {len(characters)} characters in the database")

        # Map of lowercase race values to their uppercase enum values
        race_map = {
            "human": "HUMAN",
            "dwarf": "DWARF",
            "elf": "ELF",
            "halfling": "HALFLING",
        }

        # Check and fix race values
        fixed_count = 0
        for character in characters:
            char_id, char_name, current_race = character

            # If the race is already uppercase, skip
            if current_race in [race.name for race in CharacterRace]:
                logger.info(
                    f"Character '{char_name}' (ID: {char_id}) already has correct race format: '{current_race}'"
                )
                continue

            # If the race is lowercase, update to uppercase
            if current_race in race_map:
                uppercase_race = race_map[current_race]
                logger.info(
                    f"Fixing character '{char_name}' (ID: {char_id}): "
                    f"Changing race from '{current_race}' to '{uppercase_race}'"
                )

                # Update the race via SQL
                db.execute(
                    text(
                        """
                    UPDATE characters
                    SET race = :new_race
                    WHERE id = :char_id
                """
                    ),
                    {"new_race": uppercase_race, "char_id": char_id},
                )
                fixed_count += 1
            else:
                logger.warning(
                    f"Character '{char_name}' (ID: {char_id}) has race value '{current_race}' "
                    f"that doesn't match any expected value"
                )

        # Commit changes
        if fixed_count > 0:
            db.commit()
            logger.info(f"Successfully fixed {fixed_count} character race values")
        else:
            logger.info("No character race values needed fixing")

        # Verify changes
        verify_result = db.execute(
            text(
                """
            SELECT id, name, race FROM characters
        """
            )
        )
        characters = verify_result.fetchall()

        invalid_count = 0
        for character in characters:
            char_id, char_name, current_race = character
            if current_race not in [race.name for race in CharacterRace]:
                invalid_count += 1
                logger.error(
                    f"Character '{char_name}' (ID: {char_id}) still has invalid race: '{current_race}'"
                )

        if invalid_count == 0:
            logger.info("All character races are now valid enum values")
        else:
            logger.error(
                f"Found {invalid_count} characters with still invalid race values after fix attempt"
            )

    except Exception as e:
        logger.error(f"Error fixing character races: {str(e)}")
        logger.error(f"Traceback:", exc_info=True)
        db.rollback()


if __name__ == "__main__":
    fix_character_race_enum()
