from typing import List, Dict, Any, Optional, Tuple
import logging
import random
from sqlalchemy.orm import Session

from app.commands.base import CommandHandler, CommandContext, CommandResponse, CommandCategory, CommandRequirement
from app.commands.registry import command_registry
from app.models import Character, CharacterRace, CharacterClass, CharacterLocation
from app.schemas.character import CharacterCreate
from app.routers.characters import calculate_saving_throws, calculate_racial_abilities, add_starting_equipment

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
            CharacterClass.THIEF
        ],
        CharacterRace.DWARF: [
            CharacterClass.FIGHTER, 
            CharacterClass.CLERIC, 
            CharacterClass.THIEF
        ],
        CharacterRace.ELF: [
            CharacterClass.FIGHTER_MAGIC_USER
        ],
        CharacterRace.HALFLING: [
            CharacterClass.FIGHTER, 
            CharacterClass.THIEF
        ]
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
                errors=["No database session"]
            )
            
        # Need at least 2 args: "character" and a name
        if len(ctx.args) < 2 or ctx.args[0].lower() != "character":
            return CommandResponse(
                success=False,
                message="Usage: create character <n>",
                errors=["Invalid syntax"]
            )
            
        # Extract character name from args (may contain spaces)
        char_name = " ".join(ctx.args[1:])
        
        # Check if user already has a character with this name
        existing_char = db.query(Character).filter(
            Character.user_id == ctx.user.id,
            Character.name.ilike(char_name)
        ).first()
        
        if existing_char:
            return CommandResponse(
                success=False,
                message=f"You already have a character named '{char_name}'.",
                errors=["Duplicate character name"]
            )
            
        # Initialize character creation state
        creation_state_store[ctx.user.id] = {
            "creation_state": "race_selection",
            "name": char_name
        }
            
        # Guide user through character creation
        return CommandResponse(
            success=True,
            message=(
                f"Creating a new character named '{char_name}'.\n\n"
                f"Choose a race for your character by using the command:\n"
                f"'race <race>'\n\n"
                f"Available races: human, dwarf, elf, halfling"
            ),
            data={
                "creation_state": "race_selection",
                "name": char_name
            }
        )

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
                errors=["No race specified"]
            )
            
        # Check if we have a creation state
        if ctx.user.id not in creation_state_store or creation_state_store[ctx.user.id].get("creation_state") != "race_selection":
            return CommandResponse(
                success=False,
                message="You need to start character creation first with 'create character <name>'",
                errors=["No active character creation"]
            )
            
        race_input = ctx.args[0].lower()
        
        # Map race input to CharacterRace enum
        race_map = {
            "human": CharacterRace.HUMAN,
            "dwarf": CharacterRace.DWARF,
            "elf": CharacterRace.ELF,
            "halfling": CharacterRace.HALFLING
        }
        
        if race_input not in race_map:
            return CommandResponse(
                success=False,
                message=f"'{race_input}' is not a valid race. Available races: human, dwarf, elf, halfling",
                errors=["Invalid race"]
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
            data={
                "creation_state": "class_selection",
                "race": selected_race.value
            }
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
                errors=["No class specified"]
            )
            
        # Check if we have a creation state for class selection
        if ctx.user.id not in creation_state_store or creation_state_store[ctx.user.id].get("creation_state") != "class_selection":
            return CommandResponse(
                success=False,
                message="You need to select a race first using the 'race' command",
                errors=["Race not selected"]
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
                errors=["Invalid class for race"]
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
                "name": creation_state_store[ctx.user.id].get("name")
            }
        )

class RollStatsCommand(CommandHandler):
    """Handler for rolling ability scores during character creation"""
    name = "roll"
    aliases = ["roll-stats"]
    help_text = "Roll ability scores for your new character. Usage: roll stats"
    category = CommandCategory.BASIC
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check if creation state is set correctly
        if not ctx.data.get("creation_state") or ctx.data.get("creation_state") != "stats_selection":
            return CommandResponse(
                success=False,
                message="You need to select a class first using the 'class' command.",
                errors=["Invalid creation state"]
            )
            
        # Check if command is "roll stats"
        if len(ctx.args) != 1 or ctx.args[0].lower() != "stats":
            return CommandResponse(
                success=False,
                message="Usage: roll stats",
                errors=["Invalid syntax"]
            )
            
        # Roll 3d6 for each ability score
        scores = {}
        ability_names = ["strength", "intelligence", "wisdom", "dexterity", "constitution", "charisma"]
        for ability in ability_names:
            scores[ability] = sum(random.randint(1, 6) for _ in range(3))
            
        # Check if the scores meet the class requirements
        valid_scores, error_msg = self._validate_scores(scores, CharacterClass(ctx.data.get("class")))
        
        if not valid_scores:
            return CommandResponse(
                success=False,
                message=(
                    f"Rolled scores do not meet requirements for {ctx.data.get('class')}.\n"
                    f"{error_msg}\n\n"
                    f"Please try again with 'roll stats' or use 'standard stats'."
                ),
                errors=["Insufficient ability scores"]
            )
        
        # Display the scores to the user
        scores_display = "\n".join([f"{ability.capitalize()}: {score}" for ability, score in scores.items()])
        
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
                "race": ctx.data.get("race"),
                "class": ctx.data.get("class"),
                "name": ctx.data.get("name"),
                "ability_scores": scores
            }
        )
        
    def _validate_scores(self, scores: Dict[str, int], char_class: CharacterClass) -> Tuple[bool, str]:
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
    help_text = "Use standard ability scores for your new character. Usage: standard stats"
    category = CommandCategory.BASIC
    
    async def execute(self, ctx: CommandContext) -> CommandResponse:
        # Check if creation state is set correctly
        if not ctx.data.get("creation_state") or ctx.data.get("creation_state") != "stats_selection":
            return CommandResponse(
                success=False,
                message="You need to select a class first using the 'class' command.",
                errors=["Invalid creation state"]
            )
            
        # Check if command is "standard stats"
        if len(ctx.args) != 1 or ctx.args[0].lower() != "stats":
            return CommandResponse(
                success=False,
                message="Usage: standard stats",
                errors=["Invalid syntax"]
            )
            
        # Generate standard scores based on class
        char_class = CharacterClass(ctx.data.get("class"))
        scores = self._get_standard_scores(char_class)
        
        # Display the scores to the user
        scores_display = "\n".join([f"{ability.capitalize()}: {score}" for ability, score in scores.items()])
        
        return CommandResponse(
            success=True,
            message=(
                f"Standard ability scores for {char_class.value}:\n\n"
                f"{scores_display}\n\n"
                f"To complete character creation, type 'confirm' to use these scores "
                f"or try 'roll stats' for random scores."
            ),
            data={
                "creation_state": "confirm",
                "race": ctx.data.get("race"),
                "class": ctx.data.get("class"),
                "name": ctx.data.get("name"),
                "ability_scores": scores
            }
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
            "charisma": 10
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
            return CommandResponse(
                success=False,
                message="Database session not available.",
                errors=["No database session"]
            )
            
        # Check if creation state is set correctly
        if not ctx.data.get("creation_state") or ctx.data.get("creation_state") != "confirm":
            return CommandResponse(
                success=False,
                message="Character creation is not ready to be confirmed.",
                errors=["Invalid creation state"]
            )
            
        # Get character data from context
        name = ctx.data.get("name")
        race = ctx.data.get("race")
        char_class = ctx.data.get("class")
        ability_scores = ctx.data.get("ability_scores")
        
        if not all([name, race, char_class, ability_scores]):
            return CommandResponse(
                success=False,
                message="Character information is incomplete. Please restart character creation.",
                errors=["Incomplete character data"]
            )
            
        try:
            # Create CharacterCreate model
            character_data = CharacterCreate(
                name=name,
                description=f"A brave {race} {char_class}",
                race=race,
                character_class=char_class,
                strength=ability_scores["strength"],
                intelligence=ability_scores["intelligence"],
                wisdom=ability_scores["wisdom"],
                dexterity=ability_scores["dexterity"],
                constitution=ability_scores["constitution"],
                charisma=ability_scores["charisma"]
            )
            
            # Calculate ability score modifiers
            ability_modifiers = {}
            for ability in ["strength", "intelligence", "wisdom", "dexterity", "constitution", "charisma"]:
                score = getattr(character_data, ability)
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
            
            # Calculate starting hit points
            hp_dice = {
                CharacterClass.FIGHTER: 8,
                CharacterClass.CLERIC: 6,
                CharacterClass.MAGIC_USER: 4,
                CharacterClass.THIEF: 4,
                CharacterClass.FIGHTER_MAGIC_USER: 6,
                CharacterClass.MAGIC_USER_THIEF: 4
            }
            
            # Get hit die for the class
            hit_die = hp_dice[CharacterClass(char_class)]
            
            # Halflings and Elves never roll larger than d6 for hit points
            if CharacterRace(race) in [CharacterRace.HALFLING, CharacterRace.ELF] and hit_die > 6:
                hit_die = 6
                
            # Roll hit points and add CON modifier
            hit_points = random.randint(1, hit_die) + ability_modifiers["constitution"]
            
            # Minimum of 1 hit point
            if hit_points < 1:
                hit_points = 1
            
            # Calculate starting gold (3d6 * 10)
            starting_gold = sum(random.randint(1, 6) for _ in range(3)) * 10
            
            # Set up default equipment and inventory
            equipment = {}
            inventory = {}
            
            # Calculate saving throws
            saves = calculate_saving_throws(CharacterClass(char_class), 1, CharacterRace(race))
            
            # Calculate racial abilities
            special_abilities = calculate_racial_abilities(CharacterRace(race))
            
            # For magic users, generate starting spells
            spells_known = []
            if CharacterClass(char_class) in [
                CharacterClass.MAGIC_USER, 
                CharacterClass.FIGHTER_MAGIC_USER, 
                CharacterClass.MAGIC_USER_THIEF
            ]:
                # All magic users start with read magic
                spells_known.append("read magic")
                
                # And one additional random spell
                first_level_spells = [
                    "charm person", "detect magic", "floating disc", 
                    "hold portal", "light", "magic missile", 
                    "protection from evil", "read languages", 
                    "shield", "sleep", "ventriloquism"
                ]
                spells_known.append(random.choice(first_level_spells))
            
            # Calculate thief abilities
            thief_abilities = {}
            if CharacterClass(char_class) in [CharacterClass.THIEF, CharacterClass.MAGIC_USER_THIEF]:
                thief_abilities = {
                    "open_locks": 25,
                    "remove_traps": 20,
                    "pick_pockets": 30,
                    "move_silently": 25,
                    "climb_walls": 80,
                    "hide": 10,
                    "listen": 30
                }
            
            # Calculate languages
            languages = ["Common"]
            if race != "human":
                # Add racial language
                if race == "dwarf":
                    languages.append("Dwarvish")
                elif race == "elf":
                    languages.append("Elvish")
                elif race == "halfling":
                    languages.append("Halfling")
            
            # Add bonus languages based on INT
            if ability_modifiers["intelligence"] > 0:
                bonus_languages_count = ability_modifiers["intelligence"]
                available_languages = ["Dwarvish", "Elvish", "Halfling", "Goblin", "Hobgoblin", "Gnoll", "Orc"]
                
                # Remove languages already known
                for lang in languages:
                    if lang in available_languages:
                        available_languages.remove(lang)
                
                # Add random bonus languages up to the INT modifier
                for _ in range(min(bonus_languages_count, len(available_languages))):
                    bonus_lang = random.choice(available_languages)
                    languages.append(bonus_lang)
                    available_languages.remove(bonus_lang)
            
            # Create the character DB model
            logger.info(f"Creating character: {name} (Race: {race}, Class: {char_class})")
            
            db_character = Character(
                name=name,
                description=character_data.description,
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
                user_id=ctx.user.id
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
            
            return CommandResponse(
                success=True,
                message=(
                    f"Character created successfully!\n\n"
                    f"Name: {db_character.name}\n"
                    f"Race: {db_character.race.value}\n"
                    f"Class: {db_character.character_class.value}\n"
                    f"Hit Points: {db_character.hit_points}\n"
                    f"Armor Class: {db_character.armor_class}\n"
                    f"Gold: {db_character.gold}\n\n"
                    f"Your adventure begins! Type 'look' to see your surroundings."
                ),
                data={"character_id": db_character.id}
            )
            
        except Exception as e:
            logger.exception(f"Error creating character: {e}")
            db.rollback()
            return CommandResponse(
                success=False,
                message=f"Error creating character: {str(e)}",
                errors=[str(e)]
            )
    
    def _place_in_starting_room(self, db: Session, character_id: int) -> bool:
        """Place character in the starting room"""
        try:
            # Check if location already exists
            existing_location = db.query(CharacterLocation).filter(
                CharacterLocation.character_id == character_id
            ).first()
            
            if existing_location:
                existing_location.room_id = 1
                db.commit()
            else:
                # Create new location entry
                location = CharacterLocation(
                    character_id=character_id,
                    room_id=1
                )
                db.add(location)
                db.commit()
                
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