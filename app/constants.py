"""
Common constants and enumerations for the BFRPG MUD application.

This module centralizes all constants and enumerations used throughout the application
to ensure consistency and maintainability.
"""

import enum
from typing import Dict, Set

# Game configuration constants
MAX_PARTY_SIZE: int = 5
"""Maximum number of characters in a party"""

DEFAULT_STARTING_ROOM: int = 1
"""Default room ID where new characters start their adventure"""

MAX_INVENTORY_ITEMS: int = 50
"""Maximum number of items a character can carry in their inventory"""

MAX_EQUIPPED_ITEMS: int = 12
"""Maximum number of items a character can have equipped at once"""

MAX_ROOM_CAPACITY: int = 20
"""Maximum number of entities (characters, NPCs, etc.) in a single room"""

MAX_HIRELING_COUNT: int = 3
"""Maximum number of hirelings a character can have at once"""

# Game mechanics constants
BASE_HIT_POINTS: int = 8
"""Base hit points for new characters before modifiers"""

BASE_MOVEMENT_RATE: int = 12
"""Base movement rate in units per turn"""

BASE_ARMOR_CLASS: int = 10
"""Base armor class without any armor or modifiers"""

XP_LEVEL_THRESHOLDS: Dict[int, int] = {
    1: 0,
    2: 2000,
    3: 4000,
    4: 8000,
    5: 16000,
    6: 32000,
    7: 64000,
    8: 120000,
    9: 240000,
}
"""Experience points required to reach each level"""


# Character races
class CharacterRace(str, enum.Enum):
    """
    Available character races in the BFRPG system.

    Each race has specific ability score requirements and class restrictions.
    """

    HUMAN = "human"
    DWARF = "dwarf"
    ELF = "elf"
    HALFLING = "halfling"


# Character classes
class CharacterClass(str, enum.Enum):
    """
    Available character classes in the BFRPG system.

    Each class has specific ability score requirements and race restrictions.
    Some classes are only available to certain races.
    """

    FIGHTER = "fighter"
    CLERIC = "cleric"
    MAGIC_USER = "magic-user"
    THIEF = "thief"
    FIGHTER_MAGIC_USER = "fighter/magic-user"
    MAGIC_USER_THIEF = "magic-user/thief"


# Item types
class ItemType(str, enum.Enum):
    """
    Types of items available in the game world.

    Used for categorizing items and determining their behavior in the game.
    """

    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    POTION = "potion"
    SCROLL = "scroll"
    WAND = "wand"
    RING = "ring"
    AMMUNITION = "ammunition"
    TOOL = "tool"
    CONTAINER = "container"
    CLOTHING = "clothing"
    FOOD = "food"
    MISCELLANEOUS = "miscellaneous"


# Equipment slots
class EquipmentSlot(str, enum.Enum):
    """
    Available equipment slots for characters.
    
    Each character can equip items in specific slots based on the item type.
    Some slots are mutually exclusive with others.
    """
    HEAD = "head"
    BODY = "body"
    MAIN_HAND = "main_hand"
    OFF_HAND = "off_hand"
    BOTH_HANDS = "both_hands"
    NECK = "neck"
    WAIST = "waist"
    FEET = "feet"
    HANDS = "hands"
    FINGER_LEFT = "finger_left"
    FINGER_RIGHT = "finger_right"
    BACK = "back"


# Valid class/race combinations
VALID_CLASS_RACE_COMBINATIONS: Dict[CharacterRace, Set[CharacterClass]] = {
    CharacterRace.HUMAN: {
        CharacterClass.FIGHTER,
        CharacterClass.CLERIC,
        CharacterClass.MAGIC_USER,
        CharacterClass.THIEF,
    },
    CharacterRace.DWARF: {
        CharacterClass.FIGHTER,
        CharacterClass.CLERIC,
        CharacterClass.THIEF,
    },
    CharacterRace.ELF: {
        CharacterClass.FIGHTER,
        CharacterClass.MAGIC_USER,
        CharacterClass.THIEF,
        CharacterClass.FIGHTER_MAGIC_USER,
        CharacterClass.MAGIC_USER_THIEF,
    },
    CharacterRace.HALFLING: {
        CharacterClass.FIGHTER,
        CharacterClass.THIEF,
    },
}
