import logging
import random
import sys

# REMOVED: from sqlalchemy.orm import Session

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug")

# Add parent directory to path to import app modules
sys.path.append(".")

from app.commands.character_commands import (
    calculate_racial_abilities,
    calculate_saving_throws,
)
from app.database import SessionLocal, engine

# Import necessary modules
from app.models import Character, CharacterClass, CharacterRace
from app.schemas.character import CharacterCreate


def test_character_creation():
    """Test character creation to identify potential issues"""
    # Create a database session
    db = SessionLocal()

    try:
        # Create a test character with randomly rolled stats
        character_data = {
            "name": "TestCharacter",
            "description": "A test character",
            "race": CharacterRace.HUMAN,
            "character_class": CharacterClass.FIGHTER,
            "strength": 16,
            "intelligence": 10,
            "wisdom": 12,
            "dexterity": 14,
            "constitution": 15,
            "charisma": 8,
        }

        # Print the character data
        logger.info(f"Creating character with data: {character_data}")

        # Create a CharacterCreate model
        character_model = CharacterCreate(**character_data)
        logger.info("Character model created successfully")

        # Calculate ability score modifiers
        ability_modifiers = {}
        for ability in [
            "strength",
            "intelligence",
            "wisdom",
            "dexterity",
            "constitution",
            "charisma",
        ]:
            score = getattr(character_model, ability)
            if score == 3:
                ability_modifiers[ability] = -3
            elif 4 <= score <= 5:
                ability_modifiers[ability] = -2
            elif 6 <= score <= 8:
                ability_modifiers[ability] = -1
            elif 9 <= score <= 12:
                ability_modifiers[ability] = 0
            elif 13 <= score <= 15:
                ability_modifiers[ability] = 1
            elif 16 <= score <= 17:
                ability_modifiers[ability] = 2
            elif score == 18:
                ability_modifiers[ability] = 3

        logger.info(f"Ability modifiers calculated: {ability_modifiers}")

        # Calculate hit points
        hp_dice = {
            CharacterClass.FIGHTER: 8,
            CharacterClass.CLERIC: 6,
            CharacterClass.MAGIC_USER: 4,
            CharacterClass.THIEF: 4,
            CharacterClass.FIGHTER_MAGIC_USER: 6,
            CharacterClass.MAGIC_USER_THIEF: 4,
        }

        # Get hit die for the class
        hit_die = hp_dice[character_model.character_class]

        # Halflings and Elves never roll larger than d6 for hit points
        if (
            character_model.race in [CharacterRace.HALFLING, CharacterRace.ELF]
            and hit_die > 6
        ):
            hit_die = 6

        # Roll hit points and add CON modifier
        hit_points = random.randint(1, hit_die) + ability_modifiers["constitution"]

        # Minimum of 1 hit point
        if hit_points < 1:
            hit_points = 1

        logger.info(f"Hit points calculated: {hit_points}")

        # Calculate starting gold (3d6 * 10)
        starting_gold = sum(random.randint(1, 6) for _ in range(3)) * 10
        logger.info(f"Starting gold calculated: {starting_gold}")

        # Calculate saving throws
        saves = calculate_saving_throws(
            character_model.character_class, 1, character_model.race
        )
        logger.info(f"Saving throws calculated: {saves}")

        # Calculate racial abilities
        special_abilities = calculate_racial_abilities(character_model.race)
        logger.info(f"Racial abilities calculated: {special_abilities}")

        # For magic users, generate starting spells
        spells_known = []
        if character_model.character_class in [
            CharacterClass.MAGIC_USER,
            CharacterClass.FIGHTER_MAGIC_USER,
            CharacterClass.MAGIC_USER_THIEF,
        ]:
            # All magic users start with read magic
            spells_known.append("read magic")

            # And one additional random spell
            first_level_spells = [
                "charm person",
                "detect magic",
                "floating disc",
                "hold portal",
                "light",
                "magic missile",
                "protection from evil",
                "read languages",
                "shield",
                "sleep",
                "ventriloquism",
            ]
            spells_known.append(random.choice(first_level_spells))

        logger.info(f"Spells known: {spells_known}")

        # Calculate thief abilities for thieves
        thief_abilities = {}
        if character_model.character_class in [
            CharacterClass.THIEF,
            CharacterClass.MAGIC_USER_THIEF,
        ]:
            thief_abilities = {
                "open_locks": 25,
                "remove_traps": 20,
                "pick_pockets": 30,
                "move_silently": 25,
                "climb_walls": 80,
                "hide": 10,
                "listen": 30,
            }

        logger.info(f"Thief abilities: {thief_abilities}")

        # Set up default equipment and inventory
        equipment = {}
        inventory = {}

        # Calculate languages
        languages = ["Common"]
        if character_model.race != CharacterRace.HUMAN:
            # Add racial language
            if character_model.race == CharacterRace.DWARF:
                languages.append("Dwarvish")
            elif character_model.race == CharacterRace.ELF:
                languages.append("Elvish")
            elif character_model.race == CharacterRace.HALFLING:
                languages.append("Halfling")

        logger.info(f"Languages: {languages}")

        # Create the character DB model
        logger.info(
            f"Creating character: {character_model.name} (Race: {character_model.race}, Class: {character_model.character_class})"
        )

        try:
            # Create a Character object for the database
            db_character = Character(
                name=character_model.name,
                description=character_model.description,
                race=character_model.race,
                character_class=character_model.character_class,
                strength=character_model.strength,
                intelligence=character_model.intelligence,
                wisdom=character_model.wisdom,
                dexterity=character_model.dexterity,
                constitution=character_model.constitution,
                charisma=character_model.charisma,
                hit_points=hit_points,
                armor_class=10 + ability_modifiers["dexterity"],
                gold=starting_gold,
                equipment=equipment,
                inventory=inventory,
                languages=",".join(languages),
                save_death_ray_poison=saves["death_ray_poison"],
                save_magic_wands=saves["magic_wands"],
                save_paralysis_petrify=saves["paralysis_petrify"],
                save_dragon_breath=saves["dragon_breath"],
                save_spells=saves["spells"],
                special_abilities=special_abilities,
                spells_known=spells_known,
                thief_abilities=thief_abilities,
                user_id=1,  # Use a test user ID
            )

            logger.info("Character object created successfully")

            # Add to database
            db.add(db_character)
            db.commit()
            db.refresh(db_character)

            logger.info(f"Character created successfully with ID: {db_character.id}")
            return True, db_character

        except Exception as e:
            logger.exception(f"Error creating character database entry: {e}")
            db.rollback()
            return False, str(e)

    except Exception as e:
        logger.exception(f"Error in character creation process: {e}")
        return False, str(e)
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Starting character creation debug script")
    success, result = test_character_creation()

    if success:
        logger.info(
            f"Test successful! Character created: {result.name} (ID: {result.id})"
        )
    else:
        logger.error(f"Test failed! Error: {result}")
