import json
import logging
import random
import traceback
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user
from ..services.character_service import set_character_starting_location

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.Character])
async def get_characters(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get all characters belonging to the current user"""
    try:
        characters = (
            db.query(models.Character)
            .filter(models.Character.user_id == current_user.id)
            .all()
        )
        # Convert SQLAlchemy models to Pydantic models
        return [schemas.Character.from_orm(character) for character in characters]
    except Exception as e:
        print(f"Error in get_characters: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving characters: {str(e)}",
        )


@router.post("/", response_model=schemas.Character)
async def create_character(
    character: schemas.CharacterCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Create a new character following BFRPG rules"""
    try:
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
            score = getattr(character, ability)
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

        # Calculate starting hit points based on class and CON modifier
        hp_dice = {
            schemas.CharacterClass.FIGHTER: 8,
            schemas.CharacterClass.CLERIC: 6,
            schemas.CharacterClass.MAGIC_USER: 4,
            schemas.CharacterClass.THIEF: 4,
            schemas.CharacterClass.FIGHTER_MAGIC_USER: 6,  # Elves roll d6 for HP
            schemas.CharacterClass.MAGIC_USER_THIEF: 4,
        }

        # Get the appropriate hit die for the class
        hit_die = hp_dice[character.character_class]

        # Halflings and Elves never roll larger than d6 for hit points
        if (
            character.race
            in [schemas.CharacterRace.HALFLING, schemas.CharacterRace.ELF]
            and hit_die > 6
        ):
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

        # Calculate saving throws based on class and level
        saves = calculate_saving_throws(character.character_class, 1, character.race)

        # Calculate special abilities based on race
        special_abilities = calculate_racial_abilities(character.race)

        # For magic users, generate a starting spell
        spells_known = []
        if character.character_class in [
            schemas.CharacterClass.MAGIC_USER,
            schemas.CharacterClass.FIGHTER_MAGIC_USER,
            schemas.CharacterClass.MAGIC_USER_THIEF,
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

        # Calculate thief abilities for thieves
        thief_abilities = {}
        if character.character_class in [
            schemas.CharacterClass.THIEF,
            schemas.CharacterClass.MAGIC_USER_THIEF,
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

        # Calculate starting languages
        languages = ["Common"]
        if character.race != schemas.CharacterRace.HUMAN:
            # Add racial language
            if character.race == schemas.CharacterRace.DWARF:
                languages.append("Dwarvish")
            elif character.race == schemas.CharacterRace.ELF:
                languages.append("Elvish")
            elif character.race == schemas.CharacterRace.HALFLING:
                languages.append("Halfling")

        # Add bonus languages based on INT
        if ability_modifiers["intelligence"] > 0:
            bonus_languages_count = ability_modifiers["intelligence"]
            available_languages = [
                "Dwarvish",
                "Elvish",
                "Halfling",
                "Goblin",
                "Hobgoblin",
                "Gnoll",
                "Orc",
            ]
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
        try:
            print(
                f"Creating character with race={character.race}, class={character.character_class}"
            )

            db_character = models.Character(
                name=character.name,
                description=character.description,
                race=character.race,
                character_class=character.character_class,
                strength=character.strength,
                intelligence=character.intelligence,
                wisdom=character.wisdom,
                dexterity=character.dexterity,
                constitution=character.constitution,
                charisma=character.charisma,
                hit_points=hit_points,
                armor_class=10
                + ability_modifiers["dexterity"],  # Base AC + DEX modifier
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
                user_id=current_user.id,
            )

            db.add(db_character)
            db.commit()
            db.refresh(db_character)

            # Add starting equipment
            add_starting_equipment(db, db_character)
            # Auto-equip starting items
            equip_starting_items(db_character)
            db.commit()

            # Set the character's starting location
            location_success = set_character_starting_location(db, db_character.id)
            if not location_success:
                logger.warning(
                    f"Failed to set starting location for character {db_character.id}"
                )

            # Refresh again to get the updated inventory and location
            db.refresh(db_character)

            # Convert SQLAlchemy model to Pydantic model
            return schemas.Character.from_orm(db_character)
        except Exception as e:
            print(f"Error during character creation DB operations: {e}")
            traceback.print_exc()
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
    except Exception as e:
        print(f"Error in create_character: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating character: {str(e)}",
        )


@router.get("/{character_id}", response_model=schemas.Character)
async def get_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get a specific character by ID"""
    try:
        # Get the character
        character = (
            db.query(models.Character)
            .filter(
                models.Character.id == character_id,
                models.Character.user_id == current_user.id,
            )
            .first()
        )

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {character_id} not found",
            )

        # Try to ensure character has a location, but don't fail if it doesn't work
        try:
            location_success = ensure_character_location(db, character_id)
            if location_success:
                logger.info(
                    f"Successfully set character {character_id} to starting location"
                )
            else:
                logger.warning(
                    f"Could not set character {character_id} location, but continuing anyway"
                )
        except Exception as e:
            # Log the error but continue
            logger.error(f"Error ensuring character location: {str(e)}")
            # Don't re-raise, we'll return the character data anyway

        return schemas.Character.from_orm(character)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_character: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving character: {str(e)}",
        )


@router.patch("/{character_id}/state", response_model=schemas.Character)
async def update_character_state(
    character_id: int,
    state_update: schemas.CharacterStateUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Update a character's state (hit points, experience, gold, etc.)"""
    try:
        # Find the character
        character = (
            db.query(models.Character)
            .filter(
                models.Character.id == character_id,
                models.Character.user_id == current_user.id,
            )
            .first()
        )

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
            )

        # Update character state with non-None values from the request
        update_data = state_update.dict(exclude_unset=True, exclude_none=True)

        # Handle the update
        for key, value in update_data.items():
            if hasattr(character, key):
                setattr(character, key, value)

        # Check for level up based on experience
        if (
            "experience" in update_data
            and character.experience >= character.level * 2000
        ):
            # Character leveled up
            character.level = character.experience // 2000 + 1

            # Increase hit points based on class
            hit_die = get_hit_die_for_class(character.character_class, character.race)

            # Roll for additional hit points and add CON modifier
            # For simplicity, we're using random.randint here, but you might want a more
            # controlled approach in a real game
            con_modifier = get_ability_modifier(character.constitution)
            hp_roll = random.randint(1, hit_die) + con_modifier
            if hp_roll < 1:
                hp_roll = 1  # Minimum 1 HP per level

            character.hit_points += hp_roll

        # Save changes
        db.commit()
        db.refresh(character)

        # Convert SQLAlchemy model to Pydantic model
        return schemas.Character.from_orm(character)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating character state: {e}")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating character state: {str(e)}",
        )


@router.get("/{character_id}/inventory", response_model=List[Dict[str, Any]])
async def get_character_inventory(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get a character's inventory in a format suitable for the UI"""
    try:
        # Get the character
        character = (
            db.query(models.Character)
            .filter(
                models.Character.id == character_id,
                models.Character.user_id == current_user.id,
            )
            .first()
        )

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {character_id} not found",
            )

        # Get character items
        char_items = (
            db.query(models.CharacterItem)
            .filter(models.CharacterItem.character_id == character_id)
            .all()
        )

        # Convert inventory from internal format to UI format
        inventory_list = []

        # Process each inventory item
        for char_item in char_items:
            try:
                # Get item details from database
                db_item = (
                    db.query(models.Item).filter(models.Item.id == char_item.item_id).first()
                )

                if db_item:
                    # Add item to list with full details
                    inventory_list.append(
                        {
                            "id": db_item.id,
                            "name": db_item.name,
                            "description": db_item.description,
                            "item_type": db_item.item_type,
                            "quantity": char_item.quantity,
                            "equipped": char_item.is_equipped,
                            "slot": char_item.equip_slot,
                            "value": db_item.value,
                            "weight": db_item.weight,
                            "properties": db_item.properties or {},
                        }
                    )
                else:
                    # Item exists in inventory but not in database - add minimal info
                    inventory_list.append(
                        {
                            "id": char_item.item_id,
                            "name": f"Unknown Item ({char_item.item_id})",
                            "description": "Item details not found",
                            "quantity": char_item.quantity,
                            "equipped": char_item.is_equipped,
                            "slot": char_item.equip_slot,
                        }
                    )
            except Exception as item_error:
                logger.warning(
                    f"Error processing inventory item {char_item.item_id}: {str(item_error)}"
                )
                # Continue processing other items

        return inventory_list

    except Exception as e:
        logger.error(f"Error getting character inventory: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve inventory",
        )


@router.get("/{character_id}/journal", response_model=Dict[str, Any])
async def get_character_journal(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get a character's journal entries"""
    try:
        # Get the character
        character = (
            db.query(models.Character)
            .filter(
                models.Character.id == character_id,
                models.Character.user_id == current_user.id,
            )
            .first()
        )

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {character_id} not found",
            )

        # For now, we'll return a sample journal structure
        # In the future, this should be stored in the database

        # Get journal entries from database or create empty list
        # In this implementation, we're creating a mock response
        # since the actual journal feature is not implemented yet

        return {
            "entries": [
                {
                    "date": "2025-04-21 20:45:12",
                    "text": "Started my adventure in the village.",
                },
                {
                    "date": "2025-04-21 20:46:30",
                    "text": "Found my way to the town square.",
                },
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving character journal: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving character journal: {str(e)}",
        )


@router.get("/{character_id}/hirelings", response_model=List[Dict[str, Any]])
async def get_character_hirelings(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get a character's hired companions/hirelings"""
    try:
        # Get the character
        character = (
            db.query(models.Character)
            .filter(
                models.Character.id == character_id,
                models.Character.user_id == current_user.id,
            )
            .first()
        )

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {character_id} not found",
            )

        # Get hirelings from database
        hirelings = (
            db.query(models.Hireling)
            .filter(models.Hireling.master_id == character_id)
            .all()
        )

        # Convert to response format
        hireling_list = []
        for h in hirelings:
            hireling_list.append(
                {
                    "id": h.id,
                    "name": h.name,
                    "character_class": h.character_class,
                    "level": h.level,
                    "hit_points": h.hit_points,
                    "max_hit_points": h.max_hit_points,
                    "description": h.description,
                    "abilities": h.abilities,
                }
            )

        return hireling_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving character hirelings: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving character hirelings: {str(e)}",
        )


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    character_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Delete a character"""
    try:
        # Find the character
        character = (
            db.query(models.Character)
            .filter(
                models.Character.id == character_id,
                models.Character.user_id == current_user.id,
            )
            .first()
        )

        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Character not found"
            )

        # Check for associated resources (like hirelings) that may need cleanup
        hirelings = (
            db.query(models.Hireling)
            .filter(models.Hireling.master_id == character.id)
            .all()
        )

        # Update hirelings to no longer be associated with this character
        for hireling in hirelings:
            hireling.master_id = None
            # Mark them as available again
            hireling.is_available = True

        # Delete the character
        db.delete(character)
        db.commit()

        return None

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting character: {e}")
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting character: {str(e)}",
        )


# Helper functions
def calculate_saving_throws(
    char_class: schemas.CharacterClass, level: int, race: schemas.CharacterRace
) -> Dict[str, int]:
    """Calculate saving throw values based on class and level"""
    base_saves = {
        # Format: death_ray_poison, magic_wands, paralysis_petrify, dragon_breath, spells
        schemas.CharacterClass.FIGHTER: {1: (12, 13, 14, 15, 17)},
        schemas.CharacterClass.CLERIC: {1: (11, 12, 14, 16, 15)},
        schemas.CharacterClass.MAGIC_USER: {1: (13, 14, 13, 16, 15)},
        schemas.CharacterClass.THIEF: {1: (13, 14, 13, 16, 15)},
        schemas.CharacterClass.FIGHTER_MAGIC_USER: {
            1: (12, 13, 13, 15, 15)
        },  # Use best of fighter/magic-user
        schemas.CharacterClass.MAGIC_USER_THIEF: {
            1: (13, 14, 13, 16, 15)
        },  # Use best of magic-user/thief
    }

    # Get base saving throws for class and level
    saves = base_saves[char_class][level]

    # Apply racial modifiers
    race_mods = {
        # Format: death_ray_poison, magic_wands, paralysis_petrify, dragon_breath, spells
        schemas.CharacterRace.DWARF: (4, 4, 4, 3, 4),
        schemas.CharacterRace.ELF: (0, 2, 1, 0, 2),
        schemas.CharacterRace.HALFLING: (4, 4, 4, 3, 4),
        schemas.CharacterRace.HUMAN: (0, 0, 0, 0, 0),
    }

    mods = race_mods[race]

    # Apply the modifiers (lower is better for saving throws)
    adjusted_saves = {
        "death_ray_poison": max(1, saves[0] - mods[0]),
        "magic_wands": max(1, saves[1] - mods[1]),
        "paralysis_petrify": max(1, saves[2] - mods[2]),
        "dragon_breath": max(1, saves[3] - mods[3]),
        "spells": max(1, saves[4] - mods[4]),
    }

    return adjusted_saves


def calculate_racial_abilities(race: schemas.CharacterRace) -> List[str]:
    """Calculate special abilities based on race"""
    abilities = []

    if race == schemas.CharacterRace.DWARF:
        abilities.extend(
            [
                "Darkvision (60')",
                "Detect slanting passages, traps, shifting walls and new construction on 1-2 on 1d6",
            ]
        )
    elif race == schemas.CharacterRace.ELF:
        abilities.extend(
            [
                "Darkvision (60')",
                "Detect secret doors (1-2 on 1d6, 1 on 1d6 with cursory look)",
                "Immune to ghoul paralysis",
                "Less likely to be surprised (-1 on surprise roll)",
            ]
        )
    elif race == schemas.CharacterRace.HALFLING:
        abilities.extend(
            [
                "+1 bonus to attack with ranged weapons",
                "+2 AC bonus against creatures larger than man-sized",
                "+1 to Initiative rolls",
                "Hide effectively outdoors (10% detection chance) and indoors (30% detection chance)",
            ]
        )

    return abilities


def add_starting_equipment(db: Session, character: models.Character):
    """Add starting equipment to a character based on their class"""
    try:
        # Common equipment for all classes
        # Note: Using existing item names that match the database
        common_items = [
            # No exact container matches, using weapons for now
            {
                "name": "Hand Axe",
                "type": models.ItemType.WEAPON,
                "quantity": 1,
            },  # Substitute for backpack
            # No rations in DB
            {
                "name": "Club/Cudgel/Walking Staff",
                "type": models.ItemType.WEAPON,
                "quantity": 1,
            },  # Substitute for torch
            # No exact pouch match
        ]

        # Class-specific equipment
        class_items = {
            models.CharacterClass.FIGHTER: [
                {"name": "Longsword/Scimitar", "type": models.ItemType.WEAPON},
                {"name": "Chain Mail", "type": models.ItemType.ARMOR},
                {"name": "Shield", "type": models.ItemType.SHIELD},
            ],
            models.CharacterClass.CLERIC: [
                {"name": "Warhammer", "type": models.ItemType.WEAPON},
                {"name": "Chain Mail", "type": models.ItemType.ARMOR},
                {"name": "Shield", "type": models.ItemType.SHIELD},
            ],
            models.CharacterClass.MAGIC_USER: [
                {"name": "Dagger", "type": models.ItemType.WEAPON},
                {
                    "name": "Quarterstaff",
                    "type": models.ItemType.WEAPON,
                },  # Using Quarterstaff instead of Staff
                {"name": "Leather Armor", "type": models.ItemType.ARMOR},
            ],
            models.CharacterClass.THIEF: [
                {"name": "Shortsword", "type": models.ItemType.WEAPON},
                {"name": "Leather Armor", "type": models.ItemType.ARMOR},
                {
                    "name": "Dagger",
                    "type": models.ItemType.WEAPON,
                },  # Substitute for Thieves' Tools
            ],
            models.CharacterClass.FIGHTER_MAGIC_USER: [  # Elf fighter/magic-user
                {"name": "Longsword/Scimitar", "type": models.ItemType.WEAPON},
                {"name": "Leather Armor", "type": models.ItemType.ARMOR},
                {"name": "Shortbow", "type": models.ItemType.WEAPON},
                # No exact arrow match
            ],
            models.CharacterClass.MAGIC_USER_THIEF: [  # Elf magic-user/thief
                {"name": "Dagger", "type": models.ItemType.WEAPON},
                {
                    "name": "Shortsword",
                    "type": models.ItemType.WEAPON,
                },  # Substitute for Thieves' Tools
                {"name": "Leather Armor", "type": models.ItemType.ARMOR},
            ],
        }

        # Get items for this character's class
        items_to_add = common_items + class_items.get(character.character_class, [])

        # Initialize inventory if needed
        if not character.inventory:
            character.inventory = {}

        # Add each item to the character's inventory
        for item_data in items_to_add:
            # Find the item in the database
            item = (
                db.query(models.Item)
                .filter(
                    models.Item.name == item_data["name"],
                    models.Item.item_type == item_data["type"],
                )
                .first()
            )

            if item:
                quantity = item_data.get("quantity", 1)
                item_id_str = str(item.id)

                # Add to inventory or increment quantity
                if item_id_str in character.inventory:
                    character.inventory[item_id_str]["quantity"] += quantity
                else:
                    character.inventory[item_id_str] = {
                        "item_id": item.id,
                        "quantity": quantity,
                        "equipped": False,
                        "slot": None,
                    }

        # Auto-equip basic armor and weapon
        equip_starting_items(character)

        # Save changes
        db.commit()

    except Exception as e:
        print(f"Error adding starting equipment: {e}")
        traceback.print_exc()
        raise


def equip_starting_items(character: models.Character):
    """Automatically equip basic armor and weapon from inventory"""
    try:
        # Initialize equipment if needed
        if not character.equipment:
            character.equipment = {}

        # Track what slots we've already equipped
        equipped_slots = set()

        # First, get items from inventory with their actual DB data
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            items_to_equip = []
            for item_id_str, item_data in character.inventory.items():
                # Skip already equipped items
                if item_data.get("equipped", False):
                    continue

                # Get the actual item from database to know its type
                item_id = int(item_id_str)
                db_item = (
                    db.query(models.Item).filter(models.Item.id == item_id).first()
                )

                if db_item:
                    # Add to the list of items to check with the actual item data
                    items_to_equip.append((item_id_str, item_data, db_item))

            # Process armor first, then shield, then weapon
            item_priorities = ["armor", "shield", "weapon"]

            for item_type in item_priorities:
                # Skip if we've already equipped this slot type
                slot_map = {
                    "weapon": "main_hand",
                    "armor": "body",
                    "shield": "off_hand",
                }
                slot = slot_map.get(item_type)

                if slot in equipped_slots:
                    continue

                # Find an item of this type in the inventory
                for item_id_str, item_data, db_item in items_to_equip:
                    # Now we can correctly check the item type
                    if db_item.item_type.value == item_type:
                        # Equip this item
                        character.equipment[slot] = int(item_id_str)
                        item_data["equipped"] = True
                        item_data["slot"] = slot
                        equipped_slots.add(slot)
                        # Update the character's inventory with this equipped item
                        character.inventory[item_id_str] = item_data
                        break

            # Calculate new armor class based on equipped items
            base_ac = 10
            dex_mod = get_ability_modifier(character.dexterity)

            # Add AC from equipped armor and shield
            for slot, item_id in character.equipment.items():
                item_id_str = str(item_id)
                if item_id_str in character.inventory:
                    item_data = character.inventory[item_id_str]
                    db_item = (
                        db.query(models.Item).filter(models.Item.id == item_id).first()
                    )
                    if (
                        db_item
                        and db_item.properties
                        and "ac_bonus" in db_item.properties
                    ):
                        ac_bonus = db_item.properties["ac_bonus"]
                        if slot == "body" and db_item.item_type.value == "armor":
                            # Armor replaces base AC
                            base_ac = ac_bonus
                        elif slot == "off_hand" and db_item.item_type.value == "shield":
                            # Shield adds to AC
                            base_ac += (
                                ac_bonus  # In ascending AC system, higher is better
                            )

            # Apply dexterity modifier
            character.armor_class = (
                base_ac + dex_mod
            )  # Higher is better in ascending AC system

            logger.info(
                f"Equipped slots: {equipped_slots} for character {character.id}"
            )
            logger.info(f"Character equipment: {character.equipment}")
            logger.info(f"Updated armor class to {character.armor_class}")
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error equipping starting items: {e}")
        traceback.print_exc()


# Helper function for state management
def get_hit_die_for_class(
    character_class: models.CharacterClass, race: models.CharacterRace
) -> int:
    """Get the hit die size for a character class"""
    hit_dice = {
        models.CharacterClass.FIGHTER: 8,
        models.CharacterClass.CLERIC: 6,
        models.CharacterClass.MAGIC_USER: 4,
        models.CharacterClass.THIEF: 4,
        models.CharacterClass.FIGHTER_MAGIC_USER: 6,  # Elves roll d6 for HP
        models.CharacterClass.MAGIC_USER_THIEF: 4,
    }

    hit_die = hit_dice[character_class]

    # Halflings and Elves never roll larger than d6 for hit points
    if (
        race in [models.CharacterRace.HALFLING, models.CharacterRace.ELF]
        and hit_die > 6
    ):
        hit_die = 6

    return hit_die


def get_ability_modifier(score: int) -> int:
    """Calculate ability score modifier based on BFRPG rules"""
    if score == 3:
        return -3
    elif 4 <= score <= 5:
        return -2
    elif 6 <= score <= 8:
        return -1
    elif 9 <= score <= 12:
        return 0
    elif 13 <= score <= 15:
        return 1
    elif 16 <= score <= 17:
        return 2
    elif score == 18:
        return 3
    else:
        return 0


def ensure_character_location(db: Session, character_id: int) -> bool:
    """Ensure that a character has a location in the starting room (room_id=1)"""
    try:
        # First ensure room 1 exists using the character service
        from ..services.character_service import set_character_starting_location

        # Use the service function which handles all the details including room creation
        success = set_character_starting_location(db, character_id)

        if success:
            logger.info(
                f"Successfully set character {character_id} to starting location"
            )
            return True
        else:
            logger.error(f"Failed to set character {character_id} to starting location")
            return False
    except Exception as e:
        logger.error(f"Error ensuring character location: {str(e)}")
        traceback.print_exc()
        db.rollback()
        return False
