#!/usr/bin/env python3
"""
Generate treasure based on Basic Fantasy RPG SRD treasure tables.
This script can be used to generate treasure for monsters based on their treasure table codes.
"""

import json
import os
import random
import sys
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db_context
from app.models.item import Item, ItemType
from app.models.npc import NPC

# Treasure table definitions based on SRD
# Format: {chance_of_appearing: [dice_count, dice_type, multiplier]}

# Lair Treasures
LAIR_TREASURE_TABLES = {
    "A": {
        "copper": {"chance": 50, "dice": [5, 6, 100]},
        "silver": {"chance": 60, "dice": [5, 6, 100]},
        "electrum": {"chance": 40, "dice": [5, 4, 100]},
        "gold": {"chance": 70, "dice": [10, 6, 100]},
        "platinum": {"chance": 50, "dice": [1, 10, 100]},
        "gems": {"chance": 50, "dice": [6, 6, 1]},
        "jewelry": {"chance": 50, "dice": [6, 6, 1]},
        "magic_items": {"chance": 30, "items": 3},
    },
    "B": {
        "copper": {"chance": 75, "dice": [5, 10, 100]},
        "silver": {"chance": 50, "dice": [5, 6, 100]},
        "electrum": {"chance": 50, "dice": [5, 4, 100]},
        "gold": {"chance": 50, "dice": [3, 6, 100]},
        "platinum": {"chance": 0, "dice": [0, 0, 0]},
        "gems": {"chance": 25, "dice": [1, 6, 1]},
        "jewelry": {"chance": 25, "dice": [1, 6, 1]},
        "magic_items": {"chance": 10, "items": "1 weapon or armor"},
    },
    "C": {
        "copper": {"chance": 60, "dice": [6, 6, 100]},
        "silver": {"chance": 60, "dice": [5, 4, 100]},
        "electrum": {"chance": 30, "dice": [2, 6, 100]},
        "gold": {"chance": 0, "dice": [0, 0, 0]},
        "platinum": {"chance": 0, "dice": [0, 0, 0]},
        "gems": {"chance": 25, "dice": [1, 4, 1]},
        "jewelry": {"chance": 25, "dice": [1, 4, 1]},
        "magic_items": {"chance": 15, "items": "1d2"},
    },
    "D": {
        "copper": {"chance": 30, "dice": [4, 6, 100]},
        "silver": {"chance": 45, "dice": [6, 6, 100]},
        "electrum": {"chance": 0, "dice": [0, 0, 0]},
        "gold": {"chance": 90, "dice": [5, 8, 100]},
        "platinum": {"chance": 0, "dice": [0, 0, 0]},
        "gems": {"chance": 30, "dice": [1, 8, 1]},
        "jewelry": {"chance": 30, "dice": [1, 8, 1]},
        "magic_items": {"chance": 20, "items": "1d2 + 1 potion"},
    },
    "E": {
        "copper": {"chance": 5, "dice": [1, 10, 1000]},  # 1d10 × 1,000 cp
        "silver": {"chance": 30, "dice": [1, 12, 1000]},  # 1d12 × 1,000 sp
        "gold": {"chance": 25, "dice": [1, 6, 1000]},  # 1d6 × 1,000 gp
        "platinum": {"chance": 0, "dice": [0, 0, 0]},  # No platinum
        "gems": {"chance": 10, "dice": [1, 10, 1]},  # 1d10 gems
        "jewelry": {"chance": 5, "dice": [1, 6, 1]},  # 1d6 jewelry items
        "magic_items": {"chance": 5, "items": "Any 3 except weapons"},
    },
    "F": {
        "copper": {"chance": 10, "dice": [2, 10, 1000]},  # 2d10 × 1,000 cp
        "silver": {"chance": 20, "dice": [2, 8, 1000]},  # 2d8 × 1,000 sp
        "gold": {"chance": 45, "dice": [1, 12, 1000]},  # 1d12 × 1,000 gp
        "platinum": {"chance": 0, "dice": [0, 0, 0]},  # No platinum
        "gems": {"chance": 20, "dice": [2, 12, 1]},  # 2d12 gems
        "jewelry": {"chance": 10, "dice": [1, 12, 1]},  # 1d12 jewelry items
        "magic_items": {"chance": 10, "items": "Any 3 + 1 potion"},
    },
    "G": {
        "copper": {"chance": 0, "dice": [0, 0, 0]},  # No copper
        "silver": {"chance": 25, "dice": [3, 8, 1000]},  # 3d8 × 1,000 sp
        "gold": {"chance": 50, "dice": [1, 10, 10000]},  # 1d10 × 10,000 gp
        "platinum": {"chance": 25, "dice": [1, 8, 1000]},  # 1d8 × 1,000 pp
        "gems": {"chance": 30, "dice": [3, 6, 1]},  # 3d6 gems
        "jewelry": {"chance": 25, "dice": [1, 10, 1]},  # 1d10 jewelry items
        "magic_items": {"chance": 35, "items": "Any 4 + 1 scroll"},
    },
    "H": {
        "copper": {"chance": 5, "dice": [5, 8, 1000]},  # 5d8 × 1,000 cp
        "silver": {"chance": 50, "dice": [1, 100, 1000]},  # 1d100 × 1,000 sp
        "gold": {"chance": 50, "dice": [10, 4, 1000]},  # 10d4 × 1,000 gp
        "platinum": {"chance": 25, "dice": [1, 20, 1000]},  # 1d20 × 1,000 pp
        "gems": {"chance": 50, "dice": [5, 10, 1]},  # 5d10 gems
        "jewelry": {"chance": 50, "dice": [1, 100, 1]},  # 1d100 jewelry items
        "magic_items": {"chance": 15, "items": "Any 4 + 1 potion + 1 scroll"},
    },
    "I": {
        "platinum": {"chance": 30, "dice": [3, 10, 1000]},  # 3d10 × 1,000 pp
        "gems": {"chance": 50, "dice": [2, 6, 1]},  # 2d6 gems
        "jewelry": {"chance": 50, "dice": [2, 6, 1]},  # 2d6 jewelry items
        "magic_items": {"chance": 15, "items": "Any 1"},
    },
    "J": {
        "copper": {"chance": 25, "dice": [1, 4, 1000]},  # 1d4 × 1,000 cp
        "silver": {"chance": 10, "dice": [1, 3, 1000]},  # 1d3 × 1,000 sp
        "magic_items": {"chance": 10, "items": "1d4 potions"},
    },
    "K": {
        "silver": {"chance": 30, "dice": [1, 6, 1000]},  # 1d6 × 1,000 sp
        "gold": {"chance": 10, "dice": [1, 2, 1000]},  # 1d2 × 1,000 gp
        "magic_items": {"chance": 5, "items": "1d4 scrolls"},
    },
    "L": {
        "gems": {"chance": 50, "dice": [1, 4, 1]},  # 1d4 gems
        "magic_items": {"chance": 5, "items": "1 weapon or armor"},
    },
    "M": {
        "gold": {"chance": 40, "dice": [2, 4, 1000]},  # 2d4 × 1,000 gp
        "platinum": {"chance": 50, "dice": [5, 6, 100]},  # 5d6 × 100 pp
        "gems": {"chance": 55, "dice": [5, 4, 1]},  # 5d4 gems
        "jewelry": {"chance": 45, "dice": [2, 6, 1]},  # 2d6 jewelry items
        "magic_items": {"chance": 40, "items": "Any 3 + 1 scroll"},
    },
    "N": {
        "gold": {"chance": 40, "dice": [2, 4, 1000]},  # 2d4 × 1,000 gp
        "platinum": {"chance": 50, "dice": [5, 6, 100]},  # 5d6 × 100 pp
        "gems": {"chance": 55, "dice": [5, 4, 1]},  # 5d4 gems
        "jewelry": {"chance": 45, "dice": [2, 6, 1]},  # 2d6 jewelry items
        "magic_items": {"chance": 40, "items": "Any 3 + 1 potion"},
    },
    "O": {
        "copper": {"chance": 25, "dice": [3, 8, 1000]},  # 3d8 × 1,000 cp
        "silver": {"chance": 20, "dice": [1, 10, 1000]},  # 1d10 × 1,000 sp
        "gold": {"chance": 20, "dice": [1, 4, 1000]},  # 1d4 × 1,000 gp
        "platinum": {"chance": 0, "dice": [0, 0, 0]},  # No platinum
        "gems": {"chance": 0, "dice": [0, 0, 0]},  # No gems
        "jewelry": {"chance": 0, "dice": [0, 0, 0]},  # No jewelry
        "magic_items": {"chance": 0, "items": "None"},  # No magic items
    },
    "P": {
        "copper": {"chance": 100, "dice": [3, 8, 1000]},  # 3d8 × 1,000 cp
        "silver": {"chance": 0, "dice": [0, 0, 0]},  # No silver
        "gold": {"chance": 0, "dice": [0, 0, 0]},  # No gold
        "platinum": {"chance": 0, "dice": [0, 0, 0]},  # No platinum
        "gems": {"chance": 0, "dice": [0, 0, 0]},  # No gems
        "jewelry": {"chance": 0, "dice": [0, 0, 0]},  # No jewelry
        "magic_items": {"chance": 0, "items": "None"},  # No magic items
    },
    "Q": {
        "copper": {"chance": 0, "dice": [0, 0, 0]},  # No copper
        "silver": {"chance": 100, "dice": [3, 8, 1000]},  # 3d8 × 1,000 sp
        "gold": {"chance": 0, "dice": [0, 0, 0]},  # No gold
        "platinum": {"chance": 0, "dice": [0, 0, 0]},  # No platinum
        "gems": {"chance": 0, "dice": [0, 0, 0]},  # No gems
        "jewelry": {"chance": 0, "dice": [0, 0, 0]},  # No jewelry
        "magic_items": {"chance": 0, "items": "None"},  # No magic items
    },
    "R": {
        "copper": {"chance": 0, "dice": [0, 0, 0]},  # No copper
        "silver": {"chance": 0, "dice": [0, 0, 0]},  # No silver
        "gold": {"chance": 100, "dice": [2, 10, 1000]},  # 2d10 × 1,000 gp
        "platinum": {"chance": 0, "dice": [0, 0, 0]},  # No platinum
        "gems": {"chance": 0, "dice": [0, 0, 0]},  # No gems
        "jewelry": {"chance": 0, "dice": [0, 0, 0]},  # No jewelry
        "magic_items": {"chance": 0, "items": "None"},  # No magic items
    },
    "S": {
        "copper": {"chance": 0, "dice": [0, 0, 0]},  # No copper
        "silver": {"chance": 0, "dice": [0, 0, 0]},  # No silver
        "gold": {"chance": 0, "dice": [0, 0, 0]},  # No gold
        "platinum": {"chance": 100, "dice": [1, 8, 1000]},  # 1d8 × 1,000 pp
        "gems": {"chance": 0, "dice": [0, 0, 0]},  # No gems
        "jewelry": {"chance": 0, "dice": [0, 0, 0]},  # No jewelry
        "magic_items": {"chance": 0, "items": "None"},  # No magic items
    },
    "T": {
        "gems": {"chance": 100, "dice": [10, 8, 1]},  # 10d8 gems
        "jewelry": {"chance": 0, "dice": [0, 0, 0]},  # No jewelry
        "magic_items": {"chance": 0, "items": "None"},  # No magic items
    },
    "U": {
        "gems": {"chance": 0, "dice": [0, 0, 0]},  # No gems
        "jewelry": {"chance": 100, "dice": [5, 6, 1]},  # 5d6 jewelry items
        "magic_items": {"chance": 0, "items": "None"},  # No magic items
    },
    "V": {"magic_items": {"chance": 100, "items": "Any 2"}},  # Any 2 magic items
}

# Individual Treasures
INDIVIDUAL_TREASURE_TABLES = {
    "P": {
        "copper": {"chance": 100, "dice": [3, 8, 1]},
        "silver": {"chance": 0, "dice": [0, 0, 0]},
        "electrum": {"chance": 0, "dice": [0, 0, 0]},
        "gold": {"chance": 0, "dice": [0, 0, 0]},
        "platinum": {"chance": 0, "dice": [0, 0, 0]},
    },
    "Q": {
        "copper": {"chance": 0, "dice": [0, 0, 0]},
        "silver": {"chance": 100, "dice": [3, 6, 1]},
        "electrum": {"chance": 0, "dice": [0, 0, 0]},
        "gold": {"chance": 0, "dice": [0, 0, 0]},
        "platinum": {"chance": 0, "dice": [0, 0, 0]},
    },
    "R": {
        "copper": {"chance": 0, "dice": [0, 0, 0]},
        "silver": {"chance": 0, "dice": [0, 0, 0]},
        "electrum": {"chance": 100, "dice": [2, 6, 1]},
        "gold": {"chance": 0, "dice": [0, 0, 0]},
        "platinum": {"chance": 0, "dice": [0, 0, 0]},
    },
    "S": {
        "copper": {"chance": 0, "dice": [0, 0, 0]},
        "silver": {"chance": 0, "dice": [0, 0, 0]},
        "electrum": {"chance": 0, "dice": [0, 0, 0]},
        "gold": {"chance": 100, "dice": [2, 4, 1]},
        "platinum": {"chance": 0, "dice": [0, 0, 0]},
    },
    "T": {
        "copper": {"chance": 0, "dice": [0, 0, 0]},
        "silver": {"chance": 0, "dice": [0, 0, 0]},
        "electrum": {"chance": 0, "dice": [0, 0, 0]},
        "gold": {"chance": 0, "dice": [0, 0, 0]},
        "platinum": {"chance": 100, "dice": [1, 6, 1]},
    },
}

# Magic item tables
MAGIC_ITEM_TYPES = {
    "any": {
        "weapon": (1, 20),
        "armor": (21, 35),
        "potion": (36, 50),
        "scroll": (51, 65),
        "ring": (66, 80),
        "wand": (81, 90),
        "misc": (91, 100),
    },
    "weapon_armor": {"weapon": (1, 60), "armor": (61, 100)},
    "except_weapons": {
        "armor": (1, 20),
        "potion": (21, 35),
        "scroll": (36, 50),
        "ring": (51, 70),
        "wand": (71, 85),
        "misc": (86, 100),
    },
}

# Gem and jewelry tables
GEM_VALUES = [
    {
        "value": 10,
        "types": ["Quartz", "Citrine", "Rock Crystal", "Turquoise", "Hematite"],
    },
    {
        "value": 50,
        "types": ["Amber", "Amethyst", "Garnet", "Jade", "Jasper", "Pearl", "Spinel"],
    },
    {
        "value": 100,
        "types": ["Aquamarine", "Alexandrite", "Topaz", "Opal", "Coral", "Tourmaline"],
    },
    {
        "value": 500,
        "types": [
            "Ruby",
            "Emerald",
            "Sapphire",
            "Diamond",
            "Star Ruby",
            "Star Sapphire",
        ],
    },
]

JEWELRY_VALUE_DICE = {
    "low": {"dice": [1, 6, 100]},  # 1d6 × 100 gp
    "medium": {"dice": [2, 4, 100]},  # 2d4 × 100 gp
    "high": {"dice": [1, 4, 1000]},  # 1d4 × 1000 gp
}


# Helper functions for dice rolling
def roll_dice(num: int, sides: int, multiplier: int = 1) -> int:
    """Roll num dice with sides sides and multiply the result by multiplier."""
    result = sum(random.randint(1, sides) for _ in range(num))
    return result * multiplier


def roll_percentile() -> int:
    """Roll percentile dice (1-100)."""
    return roll_dice(1, 100)


def determine_magic_item_type(category: str = "any") -> str:
    """Determine the type of magic item to generate."""
    roll = roll_percentile()

    if category not in MAGIC_ITEM_TYPES:
        category = "any"

    ranges = MAGIC_ITEM_TYPES[category]
    for item_type, (min_val, max_val) in ranges.items():
        if min_val <= roll <= max_val:
            return item_type

    # Default to miscellaneous if no range matched
    return "misc"


def generate_gem() -> Dict:
    """Generate a random gem."""
    roll = roll_percentile()
    value_category = 0

    if roll <= 40:
        value_category = 0  # 10 gp gems
    elif roll <= 75:
        value_category = 1  # 50 gp gems
    elif roll <= 90:
        value_category = 2  # 100 gp gems
    else:
        value_category = 3  # 500 gp gems

    gem_info = GEM_VALUES[value_category]
    gem_type = random.choice(gem_info["types"])

    return {
        "name": f"{gem_type} Gem",
        "description": f"A {gem_type} gem worth {gem_info['value']} gold pieces.",
        "value": gem_info["value"],
        "type": "gem",
    }


def generate_jewelry() -> Dict:
    """Generate a random piece of jewelry."""
    jewelry_types = [
        "Ring",
        "Necklace",
        "Bracelet",
        "Brooch",
        "Crown",
        "Tiara",
        "Earrings",
        "Anklet",
        "Medallion",
        "Amulet",
    ]

    materials = [
        "Gold",
        "Silver",
        "Platinum",
        "Electrum",
        "Bronze",
        "Copper",
        "Ivory",
        "Pearl-studded",
    ]

    jewelry_type = random.choice(jewelry_types)
    material = random.choice(materials)

    # Determine value (low, medium, or high)
    roll = roll_percentile()
    value_category = "low"
    if roll <= 60:
        value_category = "low"
    elif roll <= 90:
        value_category = "medium"
    else:
        value_category = "high"

    dice_info = JEWELRY_VALUE_DICE[value_category]
    value = roll_dice(*dice_info["dice"])

    return {
        "name": f"{material} {jewelry_type}",
        "description": f"A {material.lower()} {jewelry_type.lower()} worth {value} gold pieces.",
        "value": value,
        "type": "jewelry",
    }


def create_magic_weapon() -> Dict:
    """Create a random magic weapon."""
    weapons = [
        "Sword",
        "Axe",
        "Mace",
        "Dagger",
        "Spear",
        "Bow",
        "Arrow",
        "Warhammer",
        "Flail",
        "Staff",
    ]

    # Determine weapon bonus
    roll = roll_percentile()
    bonus = 1  # default +1

    if roll <= 70:
        bonus = 1
    elif roll <= 90:
        bonus = 2
    else:
        bonus = 3

    weapon_type = random.choice(weapons)

    return {
        "name": f"+{bonus} {weapon_type}",
        "description": f"A magic {weapon_type.lower()} that grants a +{bonus} bonus to attack and damage rolls.",
        "item_type": "WEAPON",
        "value": 1000 * bonus,
        "is_equippable": True,
        "equip_slot": "HAND",
        "properties": {"magic_bonus": bonus, "is_magical": True},
    }


def create_magic_armor() -> Dict:
    """Create a random piece of magic armor."""
    armors = ["Leather Armor", "Chain Mail", "Plate Mail", "Shield"]

    # Determine armor bonus
    roll = roll_percentile()
    bonus = 1  # default +1

    if roll <= 60:
        bonus = 1
    elif roll <= 90:
        bonus = 2
    else:
        bonus = 3

    armor_type = random.choice(armors)

    item_type = "ARMOR"
    equip_slot = "BODY"

    if armor_type == "Shield":
        item_type = "SHIELD"
        equip_slot = "OFFHAND"

    return {
        "name": f"+{bonus} {armor_type}",
        "description": f"Magic {armor_type.lower()} that grants a +{bonus} bonus to Armor Class.",
        "item_type": item_type,
        "value": 1000 * bonus,
        "is_equippable": True,
        "equip_slot": equip_slot,
        "properties": {"magic_bonus": bonus, "is_magical": True},
    }


def create_magic_potion() -> Dict:
    """Create a random magic potion."""
    potion_types = [
        "Healing",
        "Extra Healing",
        "Fire Resistance",
        "Cold Resistance",
        "Invisibility",
        "Gaseous Form",
        "Speed",
        "Strength",
        "Growth",
        "Diminution",
        "Flying",
        "Animal Control",
        "Undead Control",
        "Plant Control",
        "Giant Control",
    ]

    potion_type = random.choice(potion_types)

    return {
        "name": f"Potion of {potion_type}",
        "description": f"A magical potion that grants {potion_type.lower()} when consumed.",
        "item_type": "POTION",
        "value": 300,
        "is_equippable": False,
        "properties": {
            "is_magical": True,
            "effect": potion_type.lower().replace(" ", "_"),
        },
    }


def create_magic_scroll() -> Dict:
    """Create a random magic scroll."""
    # 70% chance for a spell scroll, 30% for a protection scroll
    roll = roll_percentile()

    if roll <= 70:
        # Spell scroll
        spell_levels = {
            1: ["Magic Missile", "Sleep", "Shield", "Detect Magic", "Read Magic"],
            2: ["Web", "Invisibility", "Knock", "Mirror Image", "Detect Evil"],
            3: ["Fireball", "Lightning Bolt", "Fly", "Dispel Magic", "Hold Person"],
        }

        # Determine level of spells on scroll
        level_roll = roll_percentile()
        level = 1
        if level_roll <= 50:
            level = 1
        elif level_roll <= 80:
            level = 2
        else:
            level = 3

        num_spells = random.randint(1, 3)
        spells = random.sample(
            spell_levels[level], min(num_spells, len(spell_levels[level]))
        )

        return {
            "name": f"Scroll of {', '.join(spells)}",
            "description": f"A magical scroll inscribed with the following spell{'s' if len(spells) > 1 else ''}: {', '.join(spells)}.",
            "item_type": "SCROLL",
            "value": 100 * level * len(spells),
            "is_equippable": False,
            "properties": {"is_magical": True, "spells": spells, "level": level},
        }
    else:
        # Protection scroll
        protection_types = [
            "Protection from Elementals",
            "Protection from Lycanthropes",
            "Protection from Undead",
            "Protection from Magic",
        ]

        protection_type = random.choice(protection_types)

        return {
            "name": f"Scroll of {protection_type}",
            "description": f"A magical scroll that provides {protection_type.lower()} when read.",
            "item_type": "SCROLL",
            "value": 500,
            "is_equippable": False,
            "properties": {
                "is_magical": True,
                "effect": protection_type.lower().replace(" ", "_"),
            },
        }


def create_magic_ring() -> Dict:
    """Create a random magic ring."""
    ring_types = [
        "Protection +1",
        "Protection +2",
        "Fire Resistance",
        "Invisibility",
        "Regeneration",
        "Water Walking",
        "Wishes",
        "X-Ray Vision",
        "Animal Control",
    ]

    ring_type = random.choice(ring_types)
    value = 1000

    if "Protection +2" in ring_type:
        value = 2000
    elif "Wishes" in ring_type:
        value = 10000
    elif "Regeneration" in ring_type:
        value = 5000

    return {
        "name": f"Ring of {ring_type}",
        "description": f"A magical ring that grants {ring_type.lower()}.",
        "item_type": "RING",
        "value": value,
        "is_equippable": True,
        "equip_slot": "FINGER",
        "properties": {
            "is_magical": True,
            "effect": ring_type.lower().replace(" ", "_").replace("+", ""),
        },
    }


def create_magic_wand() -> Dict:
    """Create a random magic wand."""
    wand_types = [
        "Magic Detection",
        "Enemy Detection",
        "Illusion",
        "Fear",
        "Fireballs",
        "Lightning Bolts",
        "Cold",
        "Paralyzation",
        "Polymorph",
    ]

    wand_type = random.choice(wand_types)

    charges = random.randint(10, 20)

    return {
        "name": f"Wand of {wand_type}",
        "description": f"A magical wand that can cast {wand_type.lower()}. It has {charges} charges remaining.",
        "item_type": "WAND",
        "value": 1000,
        "is_equippable": True,
        "equip_slot": "HAND",
        "properties": {
            "is_magical": True,
            "effect": wand_type.lower().replace(" ", "_"),
            "charges": charges,
        },
    }


def create_miscellaneous_magic() -> Dict:
    """Create a random miscellaneous magic item."""
    misc_items = [
        "Bag of Holding",
        "Boots of Speed",
        "Boots of Levitation",
        "Crystal Ball",
        "Cloak of Displacement",
        "Gauntlets of Ogre Power",
        "Helm of Telepathy",
        "Rope of Climbing",
        "Medallion of ESP",
        "Broom of Flying",
    ]

    item_type = random.choice(misc_items)

    equip_slot = "NONE"
    if "Boots" in item_type:
        equip_slot = "FEET"
    elif "Gauntlets" in item_type:
        equip_slot = "HANDS"
    elif "Cloak" in item_type:
        equip_slot = "BACK"
    elif "Helm" in item_type:
        equip_slot = "HEAD"
    elif "Medallion" in item_type:
        equip_slot = "NECK"

    return {
        "name": item_type,
        "description": f"A {item_type.lower()}, a rare magical item.",
        "item_type": "MISC",
        "value": 2000,
        "is_equippable": equip_slot != "NONE",
        "equip_slot": equip_slot,
        "properties": {
            "is_magical": True,
            "effect": item_type.lower().replace(" ", "_").replace("'", ""),
        },
    }


def create_magic_item(item_type: str) -> Dict:
    """Create a magic item of the specified type."""
    if item_type == "weapon":
        return create_magic_weapon()
    elif item_type == "armor":
        return create_magic_armor()
    elif item_type == "potion":
        return create_magic_potion()
    elif item_type == "scroll":
        return create_magic_scroll()
    elif item_type == "ring":
        return create_magic_ring()
    elif item_type == "wand":
        return create_magic_wand()
    elif item_type == "misc":
        return create_miscellaneous_magic()
    else:
        return create_miscellaneous_magic()  # Default fallback


def parse_magic_items_spec(spec: str) -> List[str]:
    """Parse a magic items specification string and return a list of item types to generate."""
    if not spec or spec.lower() == "none":
        return []

    items = []

    # Parse item count and type
    import re

    # Handle "Any X" format
    any_match = re.match(r"Any (\d+)( except weapons)?", spec)
    if any_match:
        count = int(any_match.group(1))
        category = "any" if not any_match.group(2) else "except_weapons"

        for _ in range(count):
            items.append(determine_magic_item_type(category))
        return items

    # Handle "X weapon/armor" format
    weapon_armor_match = re.match(r"(\d+) weapon or armor", spec)
    if weapon_armor_match:
        count = int(weapon_armor_match.group(1))

        for _ in range(count):
            items.append(determine_magic_item_type("weapon_armor"))
        return items

    # Parse more complex specifications
    parts = spec.split(" + ")
    for part in parts:
        # Handle "1d4 + 1 scroll" format
        dice_match = re.match(r"(\d+)d(\d+)( \+\s*\d+)? (.+)", part)
        if dice_match:
            num_dice = int(dice_match.group(1))
            sides = int(dice_match.group(2))
            bonus = 0
            if dice_match.group(3):
                bonus = int(dice_match.group(3).replace("+", "").strip())

            item_type = dice_match.group(4).strip().lower()

            # Handle "except weapons" qualifier
            category = "any"
            if "except weapons" in item_type:
                category = "except_weapons"
                item_type = item_type.replace("except weapons", "").strip()

            # Handle specific item types
            count = roll_dice(num_dice, sides) + bonus

            if item_type == "any":
                for _ in range(count):
                    items.append(determine_magic_item_type(category))
            elif item_type in [
                "weapon",
                "armor",
                "potion",
                "scroll",
                "ring",
                "wand",
                "misc",
            ]:
                items.extend([item_type] * count)
            else:
                # For combined types like "weapon or armor"
                if "weapon or armor" in item_type:
                    for _ in range(count):
                        items.append(determine_magic_item_type("weapon_armor"))
        else:
            # Handle simple counts "1 potion" format
            simple_match = re.match(r"(\d+) (.+)", part)
            if simple_match:
                count = int(simple_match.group(1))
                item_type = simple_match.group(2).strip().lower()

                if item_type in [
                    "weapon",
                    "armor",
                    "potion",
                    "scroll",
                    "ring",
                    "wand",
                    "misc",
                ]:
                    items.extend([item_type] * count)
                elif item_type == "any":
                    for _ in range(count):
                        items.append(determine_magic_item_type("any"))

    return items


def generate_magic_items(spec: str) -> List[Dict]:
    """Generate magic items based on the specification."""
    item_types = parse_magic_items_spec(spec)

    return [create_magic_item(item_type) for item_type in item_types]


def generate_treasure_from_code(treasure_code: str) -> Dict:
    """Generate treasure based on the given treasure code."""
    result = {
        "coins": {"cp": 0, "sp": 0, "gp": 0, "pp": 0},
        "gems": [],
        "jewelry": [],
        "magic_items": [],
    }

    # Check if code exists in either table
    if treasure_code in INDIVIDUAL_TREASURE_TABLES:
        treasure_table = INDIVIDUAL_TREASURE_TABLES[treasure_code]
    elif treasure_code in LAIR_TREASURE_TABLES:
        treasure_table = LAIR_TREASURE_TABLES[treasure_code]
    else:
        print(f"Warning: Unknown treasure code '{treasure_code}'")
        return result

    # Roll for coins
    for coin_type in ["copper", "silver", "electrum", "gold", "platinum"]:
        if coin_type not in treasure_table:
            continue

        coin_info = treasure_table[coin_type]
        chance = coin_info["chance"]

        if chance > 0 and roll_percentile() <= chance:
            num_dice, sides, multiplier = coin_info["dice"]
            amount = roll_dice(num_dice, sides, multiplier)

            if coin_type == "copper":
                result["coins"]["cp"] += amount
            elif coin_type == "silver":
                result["coins"]["sp"] += amount
            elif coin_type == "electrum":
                # Convert electrum to gold pieces (2 ep = 1 gp)
                result["coins"]["gp"] += amount // 2
                if amount % 2 == 1:
                    result["coins"]["sp"] += 5  # Add 5 sp for the remainder
            elif coin_type == "gold":
                result["coins"]["gp"] += amount
            elif coin_type == "platinum":
                result["coins"]["pp"] += amount

    # Roll for gems
    if "gems" in treasure_table:
        gem_info = treasure_table["gems"]
        chance = gem_info["chance"]

        if chance > 0 and roll_percentile() <= chance:
            num_dice, sides, multiplier = gem_info["dice"]
            num_gems = roll_dice(num_dice, sides, multiplier)

            for _ in range(num_gems):
                result["gems"].append(generate_gem())

    # Roll for jewelry
    if "jewelry" in treasure_table:
        jewelry_info = treasure_table["jewelry"]
        chance = jewelry_info["chance"]

        if chance > 0 and roll_percentile() <= chance:
            num_dice, sides, multiplier = jewelry_info["dice"]
            num_jewelry = roll_dice(num_dice, sides, multiplier)

            for _ in range(num_jewelry):
                result["jewelry"].append(generate_jewelry())

    # Roll for magic items
    if "magic_items" in treasure_table:
        magic_info = treasure_table["magic_items"]
        chance = magic_info["chance"]

        if chance > 0 and roll_percentile() <= chance:
            items_spec = magic_info["items"]
            result["magic_items"] = generate_magic_items(items_spec)

    return result


def generate_treasure_for_monster(monster_id: int, session) -> Dict:
    """Generate treasure for a specific monster based on its treasure code."""
    from app.models.npc import NPC

    # Query the monster from the database
    monster = session.query(NPC).filter(NPC.id == monster_id).first()

    if not monster:
        print(f"Monster with ID {monster_id} not found.")
        return None

    # Get the treasure code from the monster's properties
    if not monster.properties or "treasure_code" not in monster.properties:
        print(f"Monster with ID {monster_id} does not have a treasure code defined.")
        return None

    treasure_code = monster.properties["treasure_code"]

    # Generate treasure based on the treasure code
    return generate_treasure_from_code(treasure_code)


def add_treasure_to_database(treasure: Dict, owner_id: int, session) -> None:
    """Add the generated treasure to the database."""
    import uuid

    from sqlalchemy import func

    from app.models.inventory import Inventory, InventoryItem
    from app.models.item import Item, ItemType

    # Get the inventory for the monster/NPC, or create one if it doesn't exist
    inventory = session.query(Inventory).filter(Inventory.owner_id == owner_id).first()

    if not inventory:
        inventory = Inventory(
            id=str(uuid.uuid4()),
            owner_id=owner_id,
            capacity=1000,  # Arbitrary large capacity
        )
        session.add(inventory)
        session.flush()

    # Add coins to the inventory
    if (
        treasure["coins"]["cp"] > 0
        or treasure["coins"]["sp"] > 0
        or treasure["coins"]["gp"] > 0
        or treasure["coins"]["pp"] > 0
    ):

        # Check if coins already exist in inventory
        coin_item = (
            session.query(Item)
            .filter(Item.name == "Coins", Item.item_type == ItemType.CURRENCY)
            .first()
        )

        if not coin_item:
            # Create a new coin item
            coin_item = Item(
                id=str(uuid.uuid4()),
                name="Coins",
                description="A collection of coins of various denominations.",
                item_type=ItemType.CURRENCY,
                weight=0,  # Coins are weightless for simplicity
                value=0,
                properties={"cp": 0, "sp": 0, "gp": 0, "pp": 0},
            )
            session.add(coin_item)
            session.flush()

        # Check if this item is already in the inventory
        inventory_item = (
            session.query(InventoryItem)
            .filter(
                InventoryItem.inventory_id == inventory.id,
                InventoryItem.item_id == coin_item.id,
            )
            .first()
        )

        if inventory_item:
            # Update the existing inventory item
            if "properties" not in coin_item.properties:
                coin_item.properties["properties"] = {}

            coin_item.properties["cp"] = (
                coin_item.properties.get("cp", 0) + treasure["coins"]["cp"]
            )
            coin_item.properties["sp"] = (
                coin_item.properties.get("sp", 0) + treasure["coins"]["sp"]
            )
            coin_item.properties["gp"] = (
                coin_item.properties.get("gp", 0) + treasure["coins"]["gp"]
            )
            coin_item.properties["pp"] = (
                coin_item.properties.get("pp", 0) + treasure["coins"]["pp"]
            )
        else:
            # Add coin item to inventory
            inventory_item = InventoryItem(
                id=str(uuid.uuid4()),
                inventory_id=inventory.id,
                item_id=coin_item.id,
                quantity=1,
                is_equipped=False,
            )
            session.add(inventory_item)

    # Add gems to the database and inventory
    for gem in treasure["gems"]:
        item = Item(
            id=str(uuid.uuid4()),
            name=gem["name"],
            description=gem["description"],
            item_type=ItemType.TREASURE,
            weight=0.1,  # Gems are light
            value=gem["value"],
            properties={"type": "gem"},
        )
        session.add(item)
        session.flush()

        inventory_item = InventoryItem(
            id=str(uuid.uuid4()),
            inventory_id=inventory.id,
            item_id=item.id,
            quantity=1,
            is_equipped=False,
        )
        session.add(inventory_item)

    # Add jewelry to the database and inventory
    for jewelry in treasure["jewelry"]:
        item = Item(
            id=str(uuid.uuid4()),
            name=jewelry["name"],
            description=jewelry["description"],
            item_type=ItemType.TREASURE,
            weight=0.2,  # Jewelry is light
            value=jewelry["value"],
            properties={"type": "jewelry"},
        )
        session.add(item)
        session.flush()

        inventory_item = InventoryItem(
            id=str(uuid.uuid4()),
            inventory_id=inventory.id,
            item_id=item.id,
            quantity=1,
            is_equipped=False,
        )
        session.add(inventory_item)

    # Add magic items to the database and inventory
    for magic_item in treasure["magic_items"]:
        item_type = ItemType[magic_item["item_type"]]

        item = Item(
            id=str(uuid.uuid4()),
            name=magic_item["name"],
            description=magic_item["description"],
            item_type=item_type,
            weight=1.0,  # Default weight
            value=magic_item["value"],
            is_equippable=magic_item["is_equippable"],
            equip_slot=(
                magic_item["equip_slot"] if magic_item["is_equippable"] else None
            ),
            properties=magic_item["properties"],
        )
        session.add(item)
        session.flush()

        inventory_item = InventoryItem(
            id=str(uuid.uuid4()),
            inventory_id=inventory.id,
            item_id=item.id,
            quantity=1,
            is_equipped=False,
        )
        session.add(inventory_item)

    session.commit()


def main():
    """Main function to test treasure generation."""
    import sys

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models.base import Base

    if len(sys.argv) < 2:
        print("Usage: python generate_treasure.py <treasure_code> [monster_id]")
        return

    treasure_code = sys.argv[1].upper()

    # Check if code exists in either table
    if (
        treasure_code not in INDIVIDUAL_TREASURE_TABLES
        and treasure_code not in LAIR_TREASURE_TABLES
    ):
        print(f"Invalid treasure code: {treasure_code}")
        print(f"Valid individual codes: {', '.join(INDIVIDUAL_TREASURE_TABLES.keys())}")
        print(f"Valid lair codes: {', '.join(LAIR_TREASURE_TABLES.keys())}")
        return

    # Generate and display treasure
    treasure = generate_treasure_from_code(treasure_code)

    print(f"Treasure generated for code {treasure_code}:")

    print("\nCoins:")
    for coin, amount in treasure["coins"].items():
        if amount > 0:
            print(f"  {coin}: {amount}")

    if treasure["gems"]:
        print("\nGems:")
        for gem in treasure["gems"]:
            print(f"  {gem['name']} - {gem['value']} gp")

    if treasure["jewelry"]:
        print("\nJewelry:")
        for jewelry in treasure["jewelry"]:
            print(f"  {jewelry['name']} - {jewelry['value']} gp")

    if treasure["magic_items"]:
        print("\nMagic Items:")
        for item in treasure["magic_items"]:
            print(f"  {item['name']} - {item['description']}")

    # If a monster ID is provided, add the treasure to the database
    if len(sys.argv) > 2:
        monster_id = int(sys.argv[2])

        # Set up the database connection
        from app.db.session import engine

        Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = Session()

        try:
            add_treasure_to_database(treasure, monster_id, session)
            print(f"\nTreasure added to the database for monster ID {monster_id}.")
        except Exception as e:
            print(f"Error adding treasure to database: {e}")
            session.rollback()
        finally:
            session.close()


if __name__ == "__main__":
    main()
