import logging
import sys

from sqlalchemy import inspect

from app.database import get_db
from app.models.character import Character
from app.models.user import User

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger()


def fix_character_owner_relationship():
    """
    Diagnose and fix the issue with Character.owner relationship.
    """
    try:
        # Get database session
        db = next(get_db())

        # Inspect Character model
        character_inspector = inspect(Character)
        logger.info(
            f"Character model attributes: {[c.key for c in character_inspector.columns]}"
        )
        logger.info(
            f"Character model relationships: {list(character_inspector.relationships.keys())}"
        )

        # Inspect User model
        user_inspector = inspect(User)
        logger.info(
            f"User model relationships: {list(user_inspector.relationships.keys())}"
        )

        # Check foreign keys
        for column in character_inspector.columns:
            if column.foreign_keys:
                logger.info(
                    f"Foreign key in Character: {column.key} -> {next(iter(column.foreign_keys))}"
                )

        # Count characters
        character_count = db.query(Character).count()
        logger.info(f"Total characters in database: {character_count}")

        # Check if there are any characters with owners
        if character_count > 0:
            first_character = db.query(Character).first()
            logger.info(f"First character ID: {first_character.id}")

            # Check user relationship
            if hasattr(first_character, "user"):
                logger.info(
                    f"First character user ID: {first_character.user.id if first_character.user else None}"
                )
            else:
                logger.warning("Character has no 'user' attribute")

            # Check for owner attribute
            if hasattr(first_character, "owner"):
                logger.info(f"First character owner: {first_character.owner}")
            else:
                logger.warning("Character has no 'owner' attribute")

        logger.info("Issue diagnosis:")
        logger.info(
            "1. The error 'Mapper has no property owner' indicates code is trying to access Character.owner"
        )
        logger.info(
            "2. The Character model has a relationship with User called 'user', not 'owner'"
        )

        logger.info("\nPossible fixes:")
        logger.info(
            "1. Update all code references from Character.owner to Character.user"
        )
        logger.info(
            "2. Add an owner property to Character that points to the user relationship"
        )
        logger.info(
            "3. Update the relationship in Character from 'user' to 'owner' (requires database migration)"
        )

        logger.info("\nRecommended solution:")
        logger.info(
            "The safest approach is option 1: Update all code references from Character.owner to Character.user"
        )
        logger.info(
            "This avoids database changes and maintains consistency with the existing model"
        )

    except Exception as e:
        logger.error(f"Error diagnosing relationship: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())


if __name__ == "__main__":
    fix_character_owner_relationship()
