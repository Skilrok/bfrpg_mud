import logging
import random
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.commands.base import (
    CommandCategory,
    CommandContext,
    CommandHandler,
    CommandRequirement,
    CommandResponse,
)
from app.commands.registry import command_registry
from app.models import Character, CharacterClass, CharacterLocation, CharacterRace
from app.routers.characters import (
    add_starting_equipment,
    calculate_racial_abilities,
    calculate_saving_throws,
    get_ability_modifier,
)
from app.schemas.character import CharacterCreate

logger = logging.getLogger(__name__)

# In-memory store for character creation state
# Key: user_id, Value: dict containing creation state data
creation_state_store: Dict[int, Dict[str, Any]] = {}


def get_valid_classes_for_race(race: CharacterRace) -> List[CharacterClass]:
    """Return a list of valid character classes for the given race."""
    race_to_classes = {
        CharacterRace.HUMAN: [
            CharacterClass.FIGHTER,
            CharacterClass.CLERIC,
            CharacterClass.MAGIC_USER,
            CharacterClass.THIEF,
        ],
        CharacterRace.DWARF: [
            CharacterClass.FIGHTER,
            CharacterClass.CLERIC,
            CharacterClass.THIEF,
        ],
        CharacterRace.ELF: [CharacterClass.FIGHTER_MAGIC_USER],
        CharacterRace.HALFLING: [CharacterClass.FIGHTER, CharacterClass.THIEF],
    }
    return race_to_classes.get(race, [])


class CreateCharacterCommand(CommandHandler):
    """Handler for the create character command"""

    name = "create"
    aliases = ["new"]
    help_text = "Create a new character. Usage: create character <n>"
    category = CommandCategory.BASIC

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Get DB session
        db = ctx.data.get("db")
        if not db:
            return CommandResponse(
                success=False,
                message="Database session not available.",
                errors=["No database session"],
            )

        user_id = ctx.user.id
        args = ctx.args  # ctx.args is already a list, no need to split

        # Initialize character creation state if needed
        if user_id not in creation_state_store:
            if not args or args[0].lower() != "character":
                return CommandResponse(
                    success=False,
                    message=("Invalid command format. Please use: create character"),
                )

            # Start a new character creation process
            creation_state_store[user_id] = {
                "creation_state": "race_selection",
                "races_msg": self._generate_races_message(),
            }

            # Store character name if provided after "create character"
            if len(args) > 1:
                character_name = args[1]
                creation_state_store[user_id]["name"] = character_name
                return CommandResponse(
                    success=True,
                    message=(
                        f"Starting character creation for '{character_name}'...\n\n"
                        "First, select your character's race:\n\n"
                        f"{creation_state_store[user_id]['races_msg']}\n\n"
                        "Type 'race <race_name>' to select a race."
                    ),
                )

            return CommandResponse(
                success=True,
                message=(
                    "Starting character creation...\n\n"
                    "First, select your character's race:\n\n"
                    f"{creation_state_store[user_id]['races_msg']}\n\n"
                    "Type 'race <race_name>' to select a race."
                ),
            )

        # If creation already in progress, check what we're doing
        state = creation_state_store[user_id]

        if args and args[0].lower() == "character":
            # Just show the current state
            return self._show_current_state(state)

        if state.get("name") and "confirm" not in args and not args:
            # If the character is ready to be confirmed, remind them
            return CommandResponse(
                success=True,
                message=(
                    "Your character is ready to be created!\n\n"
                    f"Name: {state['name']}\n"
                    f"Race: {state['race']}\n"
                    f"Class: {state['class']}\n"
                    f"Ability Scores: {self._format_ability_scores(state.get('ability_scores', {}))}\n\n"
                    "Type 'confirm' to create your character."
                ),
            )

        # Let them know to select race first
        if state.get("creation_state") == "race_selection":
            return CommandResponse(
                success=True,
                message=(
                    "Please select your character's race first.\n\n"
                    f"{state['races_msg']}\n\n"
                    "Type 'race <race_name>' to select a race."
                ),
            )

        # If they've reach confirmation, run the character confirmation command
        if args and args[0].lower() == "confirm":
            confirm_command = command_registry.get_command_handler("confirm")
            if confirm_command:
                return await confirm_command.execute(ctx)

        # Otherwise, show current state
        return self._show_current_state(state)

    def _generate_races_message(self):
        # Implementation of _generate_races_message method
        pass

    def _show_current_state(self, state):
        # Implementation of _show_current_state method
        pass

    def _format_ability_scores(self, scores):
        # Implementation of _format_ability_scores method
        pass


class RaceCommand(CommandHandler):
    """Handler for selecting a character's race during creation"""

    name = "race"
    help_text = "Select a race for your new character. Usage: race <race_name>"
    category = CommandCategory.BASIC

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check if a race was specified
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="Please specify a race. Available races: human, dwarf, elf, halfling",
                errors=["No race specified"],
            )

        # Check if we have a creation state
        if (
            ctx.user.id not in creation_state_store
            or creation_state_store[ctx.user.id].get("creation_state")
            != "race_selection"
        ):
            return CommandResponse(
                success=False,
                message="You need to start character creation first with 'create character'",
                errors=["No active character creation"],
            )

        race_input = ctx.args[0].lower()

        # Map race input to CharacterRace enum
        race_map = {
            "human": CharacterRace.HUMAN,
            "dwarf": CharacterRace.DWARF,
            "elf": CharacterRace.ELF,
            "halfling": CharacterRace.HALFLING,
        }

        if race_input not in race_map:
            return CommandResponse(
                success=False,
                message=f"'{race_input}' is not a valid race. Available races: human, dwarf, elf, halfling",
                errors=["Invalid race"],
            )

        selected_race = race_map[race_input]

        # Update state
        creation_state_store[ctx.user.id]["creation_state"] = "class_selection"
        creation_state_store[ctx.user.id]["race"] = selected_race.value

        # Return response with class selection prompt
        classes_msg = (
            "human: fighter, cleric, magic-user, thief\n"
            "dwarf: fighter, cleric, thief\n"
            "elf: fighter/magic-user\n"
            "halfling: fighter, thief"
        )

        return CommandResponse(
            success=True,
            message=(
                f"Race selected: {selected_race.value}\n\n"
                f"Now choose a class for your character by using the command:\n"
                f"'class <class>'\n\n"
                f"Available classes based on your race:\n{classes_msg}"
            ),
            data={"creation_state": "class_selection", "race": selected_race.value},
        )


class ClassCommand(CommandHandler):
    """Handler for selecting a character's class during creation"""

    name = "class"
    help_text = "Select a class for your new character. Usage: class <class_name>"
    category = CommandCategory.BASIC

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check if a class was specified
        if not ctx.args:
            return CommandResponse(
                success=False,
                message="Please specify a class",
                errors=["No class specified"],
            )

        # Check if we have a creation state for class selection
        if (
            ctx.user.id not in creation_state_store
            or creation_state_store[ctx.user.id].get("creation_state")
            != "class_selection"
        ):
            return CommandResponse(
                success=False,
                message="You need to select a race first using the 'race' command",
                errors=["Race not selected"],
            )

        class_input = ctx.args[0].lower()
        race_value = creation_state_store[ctx.user.id].get("race")
        race = CharacterRace(race_value)

        # Validate class based on race
        valid_classes = get_valid_classes_for_race(race)
        selected_class = None

        for valid_class in valid_classes:
            if valid_class.value.lower() == class_input:
                selected_class = valid_class
                break

        if not selected_class:
            valid_class_names = [c.value.lower() for c in valid_classes]
            return CommandResponse(
                success=False,
                message=f"'{class_input}' is not a valid class for {race.value}. Valid classes: {', '.join(valid_class_names)}",
                errors=["Invalid class for race"],
            )

        # Store the selected class in state
        creation_state_store[ctx.user.id]["class"] = selected_class.value
        creation_state_store[ctx.user.id]["creation_state"] = "stats_selection"

        return CommandResponse(
            success=True,
            message=(
                f"Class selected: {selected_class.value}\n\n"
                f"Now you need to determine your character's ability scores.\n"
                f"Use 'roll stats' to randomly generate ability scores, or\n"
                f"'standard stats' to use recommended values for your class."
            ),
            data={
                "creation_state": "stats_selection",
                "race": race.value,
                "class": selected_class.value,
                "name": creation_state_store[ctx.user.id].get("name"),
            },
        )


class RollStatsCommand(CommandHandler):
    """Handler for rolling ability scores during character creation"""

    name = "roll"
    aliases = ["roll-stats"]
    help_text = "Roll ability scores for your new character. Usage: roll stats"
    category = CommandCategory.BASIC

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check both context data and the state store
        user_id = ctx.user.id
        creation_state = ctx.data.get("creation_state")
        stored_state = creation_state_store.get(user_id, {}).get("creation_state")

        # Log the states for debugging
        logger.info(
            f"RollStatsCommand: ctx state: {creation_state}, stored state: {stored_state}"
        )

        # Check if creation state is set correctly (either in context or in store)
        if not (
            (creation_state == "stats_selection" or stored_state == "stats_selection")
            or (creation_state == "confirm" or stored_state == "confirm")
        ):
            return CommandResponse(
                success=False,
                message="You need to select a class first using the 'class' command.",
                errors=["Invalid creation state"],
            )

        # Check if command is "roll stats"
        if len(ctx.args) != 1 or ctx.args[0].lower() != "stats":
            return CommandResponse(
                success=False, message="Usage: roll stats", errors=["Invalid syntax"]
            )

        try:
            # Roll 3d6 for each ability score
            scores = {}
            ability_names = [
                "strength",
                "intelligence",
                "wisdom",
                "dexterity",
                "constitution",
                "charisma",
            ]
            for ability in ability_names:
                scores[ability] = sum(random.randint(1, 6) for _ in range(3))

            # Get character class from context or stored state
            char_class = ctx.data.get("class") or creation_state_store.get(
                user_id, {}
            ).get("class")
            if not char_class:
                return CommandResponse(
                    success=False,
                    message="Character class information is missing. Please restart character creation.",
                    errors=["Missing class information"],
                )

            # Check if the scores meet the class requirements
            valid_scores, error_msg = self._validate_scores(
                scores, CharacterClass(char_class)
            )

            if not valid_scores:
                return CommandResponse(
                    success=False,
                    message=(
                        f"Rolled scores do not meet requirements for {char_class}.\n"
                        f"{error_msg}\n\n"
                        f"Please try again with 'roll stats' or use 'standard stats'."
                    ),
                    errors=["Insufficient ability scores"],
                )

            # Display the scores to the user
            scores_display = "\n".join(
                [
                    f"{ability.capitalize()}: {score}"
                    for ability, score in scores.items()
                ]
            )

            # Make sure the creation state is stored properly
            if user_id not in creation_state_store:
                creation_state_store[user_id] = {}

            # Get race and name from context or stored state
            race = ctx.data.get("race") or creation_state_store.get(user_id, {}).get(
                "race"
            )
            name = ctx.data.get("name") or creation_state_store.get(user_id, {}).get(
                "name"
            )

            creation_state_store[user_id].update(
                {
                    "creation_state": "confirm",
                    "race": race,
                    "class": char_class,
                    "name": name,
                    "ability_scores": scores,
                }
            )

            # Log the updated creation state for debugging
            logger.info(
                f"Updated creation state for user {user_id}: {creation_state_store[user_id]}"
            )

            return CommandResponse(
                success=True,
                message=(
                    f"Your ability scores have been rolled:\n\n"
                    f"{scores_display}\n\n"
                    f"To complete character creation, type 'confirm' to use these scores "
                    f"or 'roll stats' to try again."
                ),
                data={
                    "creation_state": "confirm",
                    "race": race,
                    "class": char_class,
                    "name": name,
                    "ability_scores": scores,
                },
            )
        except Exception as e:
            logger.exception(f"Error in RollStatsCommand: {str(e)}")
            return CommandResponse(
                success=False,
                message=f"An error occurred while rolling stats: {str(e)}",
                errors=[str(e)],
            )

    def _validate_scores(
        self, scores: Dict[str, int], char_class: CharacterClass
    ) -> Tuple[bool, str]:
        """Validate if ability scores meet class requirements"""
        # Check prime requisite requirements
        if char_class == CharacterClass.FIGHTER and scores["strength"] < 9:
            return False, "Fighters must have at least 9 Strength."

        if char_class == CharacterClass.MAGIC_USER and scores["intelligence"] < 9:
            return False, "Magic-Users must have at least 9 Intelligence."

        if char_class == CharacterClass.CLERIC and scores["wisdom"] < 9:
            return False, "Clerics must have at least 9 Wisdom."

        if char_class == CharacterClass.THIEF and scores["dexterity"] < 9:
            return False, "Thieves must have at least 9 Dexterity."

        if char_class == CharacterClass.FIGHTER_MAGIC_USER:
            if scores["strength"] < 9:
                return False, "Fighter/Magic-Users must have at least 9 Strength."
            if scores["intelligence"] < 9:
                return False, "Fighter/Magic-Users must have at least 9 Intelligence."

        if char_class == CharacterClass.MAGIC_USER_THIEF:
            if scores["intelligence"] < 9:
                return False, "Magic-User/Thieves must have at least 9 Intelligence."
            if scores["dexterity"] < 9:
                return False, "Magic-User/Thieves must have at least 9 Dexterity."

        return True, ""


class StandardStatsCommand(CommandHandler):
    """Handler for using standard ability scores during character creation"""

    name = "standard"
    aliases = ["standard-stats"]
    help_text = (
        "Use standard ability scores for your new character. Usage: standard stats"
    )
    category = CommandCategory.BASIC

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check both context data and the state store
        user_id = ctx.user.id
        creation_state = ctx.data.get("creation_state")
        stored_state = creation_state_store.get(user_id, {}).get("creation_state")

        # Log the states for debugging
        logger.info(
            f"StandardStatsCommand: ctx state: {creation_state}, stored state: {stored_state}"
        )

        # Check if creation state is set correctly (either in context or in store)
        if not (
            (creation_state == "stats_selection" or stored_state == "stats_selection")
        ):
            return CommandResponse(
                success=False,
                message="You need to select a class first using the 'class' command.",
                errors=["Invalid creation state"],
            )

        # Check if command is "standard stats"
        if len(ctx.args) != 1 or ctx.args[0].lower() != "stats":
            return CommandResponse(
                success=False,
                message="Usage: standard stats",
                errors=["Invalid syntax"],
            )

        try:
            # Get character class from context or stored state
            char_class = ctx.data.get("class") or creation_state_store.get(
                user_id, {}
            ).get("class")
            if not char_class:
                return CommandResponse(
                    success=False,
                    message="Character class information is missing. Please restart character creation.",
                    errors=["Missing class information"],
                )

            # Generate standard scores based on class
            scores = self._get_standard_scores(CharacterClass(char_class))

            # Get race and name from context or stored state
            race = ctx.data.get("race") or creation_state_store.get(user_id, {}).get(
                "race"
            )
            name = ctx.data.get("name") or creation_state_store.get(user_id, {}).get(
                "name"
            )

            # Store the creation state
            if user_id not in creation_state_store:
                creation_state_store[user_id] = {}

            creation_state_store[user_id].update(
                {
                    "creation_state": "confirm",
                    "race": race,
                    "class": char_class,
                    "name": name,
                    "ability_scores": scores,
                }
            )

            # Log the updated creation state for debugging
            logger.info(
                f"Updated creation state for user {user_id}: {creation_state_store[user_id]}"
            )

            # Display the scores to the user
            scores_display = "\n".join(
                [
                    f"{ability.capitalize()}: {score}"
                    for ability, score in scores.items()
                ]
            )

            return CommandResponse(
                success=True,
                message=(
                    f"Standard ability scores for {char_class}:\n\n"
                    f"{scores_display}\n\n"
                    f"To complete character creation, type 'confirm' to use these scores "
                    f"or try 'roll stats' for random scores."
                ),
                data={
                    "creation_state": "confirm",
                    "race": race,
                    "class": char_class,
                    "name": name,
                    "ability_scores": scores,
                },
            )
        except Exception as e:
            logger.exception(f"Error in StandardStatsCommand: {str(e)}")
            return CommandResponse(
                success=False,
                message=f"An error occurred while generating standard stats: {str(e)}",
                errors=[str(e)],
            )

    def _get_standard_scores(self, char_class: CharacterClass) -> Dict[str, int]:
        """Get standard ability scores based on character class"""
        # Base scores that every class gets
        scores = {
            "strength": 10,
            "intelligence": 10,
            "wisdom": 10,
            "dexterity": 10,
            "constitution": 10,
            "charisma": 10,
        }

        # Adjust based on class prime requisites
        if char_class == CharacterClass.FIGHTER:
            scores["strength"] = 14
            scores["constitution"] = 12
        elif char_class == CharacterClass.MAGIC_USER:
            scores["intelligence"] = 14
            scores["wisdom"] = 12
        elif char_class == CharacterClass.CLERIC:
            scores["wisdom"] = 14
            scores["strength"] = 12
        elif char_class == CharacterClass.THIEF:
            scores["dexterity"] = 14
            scores["intelligence"] = 12
        elif char_class == CharacterClass.FIGHTER_MAGIC_USER:
            scores["strength"] = 13
            scores["intelligence"] = 13
            scores["constitution"] = 12
        elif char_class == CharacterClass.MAGIC_USER_THIEF:
            scores["intelligence"] = 13
            scores["dexterity"] = 13

        return scores


class ConfirmCharacterCommand(CommandHandler):
    """Handler for confirming character creation"""

    name = "confirm"
    help_text = "Confirm and complete character creation."
    category = CommandCategory.BASIC

    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Get DB session
        db = ctx.data.get("db")

        if not db:
            # Try to get it from context directly
            db = ctx.db

        user_id = ctx.user.id

        # Check if the user is in character creation
        if user_id not in creation_state_store:
            return CommandResponse(
                success=False,
                message="You haven't started character creation. Use 'create character' first.",
                errors=["No active character creation"],
            )

        character_data = creation_state_store[user_id]

        # Make sure we have the necessary data
        if not all(
            key in character_data for key in ["name", "race", "class", "ability_scores"]
        ):
            return CommandResponse(
                success=False,
                message="Character creation is incomplete. Make sure you've set a name, race, class, and ability scores.",
                errors=["Incomplete character data"],
            )

        try:
            # Get the character data
            name = character_data["name"] or f"Character {random.randint(1000, 9999)}"
            race = character_data["race"]
            char_class = character_data["class"]
            ability_scores = character_data["ability_scores"]

            # Default description if not provided
            description = character_data.get("description", f"A {race} {char_class}")

            # Calculate ability modifiers
            ability_modifiers = {
                "strength": get_ability_modifier(ability_scores["strength"]),
                "intelligence": get_ability_modifier(ability_scores["intelligence"]),
                "wisdom": get_ability_modifier(ability_scores["wisdom"]),
                "dexterity": get_ability_modifier(ability_scores["dexterity"]),
                "constitution": get_ability_modifier(ability_scores["constitution"]),
                "charisma": get_ability_modifier(ability_scores["charisma"]),
            }

            # Calculate hit points based on class and con modifier
            hit_points = self._generate_hit_dice(
                CharacterClass(char_class), ability_modifiers["constitution"]
            )

            # Roll for starting gold (3d6 x 10)
            starting_gold = sum(random.randint(1, 6) for _ in range(3)) * 10

            # Initialize equipment and inventory
            equipment = {}
            inventory = {}

            # Calculate saving throws based on class and level
            saves = calculate_saving_throws(
                CharacterClass(char_class), 1, CharacterRace(race)
            )

            # Calculate special abilities based on race
            special_abilities = calculate_racial_abilities(CharacterRace(race))

            # Initialize spells_known for magic users
            spells_known = {}

            # Initialize thief abilities
            thief_abilities = {}

            # Determine starting languages
            languages = ["Common"]

            # Add race-specific languages
            race_languages = {
                CharacterRace.DWARF: ["Dwarvish"],
                CharacterRace.ELF: ["Elvish"],
                CharacterRace.HALFLING: ["Halfling"],
                CharacterRace.HUMAN: [],
            }
            races_with_languages = race_languages.get(CharacterRace(race), [])

            for lang in races_with_languages:
                if lang not in languages:
                    languages.append(lang)

            # Add bonus languages based on intelligence
            if ability_modifiers["intelligence"] > 0:
                # In Basic Fantasy, high INT gives bonus languages
                bonus_langs = min(ability_modifiers["intelligence"], 4)
                bonus_language_options = [
                    "Orcish",
                    "Goblin",
                    "Gnomish",
                    "Hobbit",
                    "Draconic",
                    "Fey",
                    "Sylvan",
                    "Undercommon",
                    "Giant",
                ]
                # Randomly select bonus languages
                for _ in range(bonus_langs):
                    if not bonus_language_options:
                        break
                    random_lang = random.choice(bonus_language_options)
                    if random_lang not in languages:
                        languages.append(random_lang)
                    bonus_language_options.remove(random_lang)

            # Use a try-except block specifically for DB operations
            try:
                db_character = Character(
                    name=name,
                    description=description,
                    race=CharacterRace(race),
                    character_class=CharacterClass(char_class),
                    strength=ability_scores["strength"],
                    intelligence=ability_scores["intelligence"],
                    wisdom=ability_scores["wisdom"],
                    dexterity=ability_scores["dexterity"],
                    constitution=ability_scores["constitution"],
                    charisma=ability_scores["charisma"],
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
                    user_id=ctx.user.id,
                )

                db.add(db_character)
                db.commit()
                db.refresh(db_character)

                # Add starting equipment
                add_starting_equipment(db, db_character)

                # Refresh to get updated inventory
                db.refresh(db_character)

                # Place character in the starting room (room_id=1)
                self._place_in_starting_room(db, db_character.id)

                # Clear the character creation state
                if user_id in creation_state_store:
                    del creation_state_store[user_id]

                return CommandResponse(
                    success=True,
                    message=(
                        f"Character '{name}' has been created!\n\n"
                        f"Race: {race}\n"
                        f"Class: {char_class}\n"
                        f"HP: {hit_points}\n"
                        f"AC: {10 + ability_modifiers['dexterity']}\n"
                        f"Gold: {starting_gold} gp\n\n"
                        f"Your character has been equipped with starting items based on class.\n\n"
                        "You can now use this character in-game with the 'use character' command."
                    ),
                )

            except Exception as e:
                logger.error(f"Database error creating character: {e}")
                return CommandResponse(
                    success=False,
                    message="There was an error creating your character. Please try again.",
                    errors=[str(e)],
                )

        except Exception as e:
            logger.error(f"Error in character creation: {e}")
            return CommandResponse(
                success=False,
                message="There was an error creating your character. Please try again.",
                errors=[str(e)],
            )

    def _generate_hit_dice(self, char_class: CharacterClass, con_modifier: int) -> int:
        """Generate hit points for a new character based on class and constitution modifier"""
        # Basic Fantasy RPG hit dice by class (at level 1)
        hit_dice = {
            CharacterClass.FIGHTER: 8,
            CharacterClass.CLERIC: 6,
            CharacterClass.MAGIC_USER: 4,
            CharacterClass.THIEF: 4,
            CharacterClass.FIGHTER_MAGIC_USER: 6,  # Elf (average between fighter and magic-user)
            CharacterClass.MAGIC_USER_THIEF: 4,  # Custom (assumed for multi-class)
        }

        # Get base hit dice for class (default to 4 if not found)
        base_hp = hit_dice.get(char_class, 4)

        # Add constitution modifier
        total_hp = base_hp + con_modifier

        # Minimum of 1 HP
        return max(1, total_hp)

    def _place_in_starting_room(self, db: Session, character_id: int) -> bool:
        """Place character in the starting room"""
        try:
            # Check if location already exists
            existing_location = (
                db.query(CharacterLocation)
                .filter(CharacterLocation.character_id == character_id)
                .first()
            )

            if existing_location:
                existing_location.room_id = 1
                db.commit()
                logger.info(f"Updated character {character_id} location to room 1")
            else:
                # Create new location entry
                location = CharacterLocation(character_id=character_id, room_id=1)
                db.add(location)
                db.commit()
                logger.info(
                    f"Created new location for character {character_id} in room 1"
                )

            # Double-check if the character location was set correctly
            check_location = (
                db.query(CharacterLocation)
                .filter(CharacterLocation.character_id == character_id)
                .first()
            )

            if not check_location or check_location.room_id != 1:
                logger.error(
                    f"Failed to verify character {character_id} location in room 1"
                )
                return False

            return True
        except Exception as e:
            logger.exception(f"Error placing character in starting room: {e}")
            db.rollback()
            return False


# Register all commands
command_registry.register(CreateCharacterCommand)
command_registry.register(RaceCommand)
command_registry.register(ClassCommand)
command_registry.register(RollStatsCommand)
command_registry.register(StandardStatsCommand)
command_registry.register(ConfirmCharacterCommand)
