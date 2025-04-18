"""
Seed script to populate the database with basic items.
Run this script to initialize the database with common items.
"""
import os
import sys
from sqlalchemy.orm import Session

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Item, ItemType


def seed_items():
    """
    Seed the database with basic items for the game.
    """
    db = SessionLocal()
    
    try:
        # Check if we already have items
        existing_count = db.query(Item).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} items. Skipping seed.")
            return
        
        # Weapons
        weapons = [
            {
                "name": "Dagger",
                "description": "A small, easily concealable blade.",
                "item_type": ItemType.WEAPON,
                "value": 3,
                "weight": 1.0,
                "properties": {
                    "damage": "1d4",
                    "damage_type": "piercing",
                    "range": "melee",
                    "hands": 1
                }
            },
            {
                "name": "Shortsword",
                "description": "A lightweight blade favored by rogues and quick fighters.",
                "item_type": ItemType.WEAPON,
                "value": 10,
                "weight": 2.0,
                "properties": {
                    "damage": "1d6",
                    "damage_type": "piercing",
                    "range": "melee",
                    "hands": 1
                }
            },
            {
                "name": "Longsword",
                "description": "The standard weapon of knights and warriors.",
                "item_type": ItemType.WEAPON,
                "value": 15,
                "weight": 3.0,
                "properties": {
                    "damage": "1d8",
                    "damage_type": "slashing",
                    "range": "melee",
                    "hands": 1
                }
            },
            {
                "name": "Battleaxe",
                "description": "A heavy axe designed for combat.",
                "item_type": ItemType.WEAPON,
                "value": 10,
                "weight": 4.0,
                "properties": {
                    "damage": "1d8",
                    "damage_type": "slashing",
                    "range": "melee",
                    "hands": 1
                }
            },
            {
                "name": "Warhammer",
                "description": "A heavy hammer with a metal head.",
                "item_type": ItemType.WEAPON,
                "value": 12,
                "weight": 5.0,
                "properties": {
                    "damage": "1d8",
                    "damage_type": "bludgeoning",
                    "range": "melee",
                    "hands": 1
                }
            },
            {
                "name": "Shortbow",
                "description": "A small bow that can be used while mounted.",
                "item_type": ItemType.WEAPON,
                "value": 25,
                "weight": 2.0,
                "properties": {
                    "damage": "1d6",
                    "damage_type": "piercing",
                    "range": "80/320",
                    "hands": 2
                }
            },
            {
                "name": "Longbow",
                "description": "A tall bow that provides excellent range and power.",
                "item_type": ItemType.WEAPON,
                "value": 50,
                "weight": 3.0,
                "properties": {
                    "damage": "1d8",
                    "damage_type": "piercing",
                    "range": "150/600",
                    "hands": 2
                }
            },
            {
                "name": "Staff",
                "description": "A wooden staff, often used by magic-users and clerics.",
                "item_type": ItemType.WEAPON,
                "value": 5,
                "weight": 4.0,
                "properties": {
                    "damage": "1d6",
                    "damage_type": "bludgeoning",
                    "range": "melee",
                    "hands": 2
                }
            }
        ]
        
        # Armor
        armor = [
            {
                "name": "Leather Armor",
                "description": "Light armor made of treated animal hide.",
                "item_type": ItemType.ARMOR,
                "value": 10,
                "weight": 10.0,
                "properties": {
                    "base_ac": 12,
                    "dex_bonus": True,
                    "max_dex_bonus": None,
                    "type": "light"
                }
            },
            {
                "name": "Chain Mail",
                "description": "Medium armor made of interlocking metal rings.",
                "item_type": ItemType.ARMOR,
                "value": 75,
                "weight": 40.0,
                "properties": {
                    "base_ac": 14,
                    "dex_bonus": True,
                    "max_dex_bonus": 2,
                    "type": "medium"
                }
            },
            {
                "name": "Plate Mail",
                "description": "Heavy armor made of shaped metal plates.",
                "item_type": ItemType.ARMOR,
                "value": 400,
                "weight": 65.0,
                "properties": {
                    "base_ac": 16,
                    "dex_bonus": False,
                    "max_dex_bonus": 0,
                    "type": "heavy"
                }
            }
        ]
        
        # Shields
        shields = [
            {
                "name": "Wooden Shield",
                "description": "A simple wooden shield bound with iron.",
                "item_type": ItemType.SHIELD,
                "value": 10,
                "weight": 5.0,
                "properties": {
                    "ac_bonus": 1
                }
            },
            {
                "name": "Metal Shield",
                "description": "A sturdy shield made entirely of metal.",
                "item_type": ItemType.SHIELD,
                "value": 50,
                "weight": 8.0,
                "properties": {
                    "ac_bonus": 2
                }
            }
        ]
        
        # Potions
        potions = [
            {
                "name": "Healing Potion",
                "description": "A magical red liquid that heals wounds when consumed.",
                "item_type": ItemType.POTION,
                "value": 50,
                "weight": 0.5,
                "properties": {
                    "effect": "healing",
                    "healing": "1d8+2"
                }
            },
            {
                "name": "Potion of Strength",
                "description": "A thick, dark liquid that temporarily enhances strength.",
                "item_type": ItemType.POTION,
                "value": 100,
                "weight": 0.5,
                "properties": {
                    "effect": "buff",
                    "stat": "strength",
                    "bonus": 2,
                    "duration": "1d4 hours"
                }
            }
        ]
        
        # Tools
        tools = [
            {
                "name": "Thieves' Tools",
                "description": "A set of tools for picking locks and disarming traps.",
                "item_type": ItemType.TOOL,
                "value": 25,
                "weight": 1.0,
                "properties": {
                    "skill": "lock_picking",
                    "bonus": 2
                }
            },
            {
                "name": "Rope (50 ft)",
                "description": "A sturdy hemp rope, useful for climbing and binding.",
                "item_type": ItemType.TOOL,
                "value": 1,
                "weight": 10.0,
                "properties": {}
            },
            {
                "name": "Torch",
                "description": "A wooden stick with cloth wrapped around one end, soaked in pitch.",
                "item_type": ItemType.TOOL,
                "value": 0.1,
                "weight": 1.0,
                "properties": {
                    "light_radius": 30,
                    "duration": "1 hour"
                }
            }
        ]
        
        # Food
        food = [
            {
                "name": "Rations (1 day)",
                "description": "Preserved food for one day of travel.",
                "item_type": ItemType.FOOD,
                "value": 0.5,
                "weight": 2.0,
                "properties": {
                    "nutrition": 1,
                    "perishable": False
                }
            },
            {
                "name": "Bread",
                "description": "A fresh loaf of bread.",
                "item_type": ItemType.FOOD,
                "value": 0.2,
                "weight": 0.5,
                "properties": {
                    "nutrition": 0.5,
                    "perishable": True
                }
            }
        ]
        
        # Ammunition
        ammunition = [
            {
                "name": "Arrows (20)",
                "description": "A quiver of 20 arrows.",
                "item_type": ItemType.AMMUNITION,
                "value": 1,
                "weight": 1.0,
                "properties": {
                    "weapon": "bow",
                    "quantity": 20
                }
            },
            {
                "name": "Sling Stones (20)",
                "description": "A pouch of 20 sling stones.",
                "item_type": ItemType.AMMUNITION,
                "value": 0.1,
                "weight": 1.5,
                "properties": {
                    "weapon": "sling",
                    "quantity": 20
                }
            }
        ]
        
        # Containers
        containers = [
            {
                "name": "Backpack",
                "description": "A sturdy leather backpack for carrying equipment.",
                "item_type": ItemType.CONTAINER,
                "value": 2,
                "weight": 5.0,
                "properties": {
                    "capacity": 30,  # In pounds
                    "slots": 8
                }
            },
            {
                "name": "Pouch",
                "description": "A small leather pouch for carrying coins and small items.",
                "item_type": ItemType.CONTAINER,
                "value": 0.5,
                "weight": 0.5,
                "properties": {
                    "capacity": 5,  # In pounds
                    "slots": 2
                }
            }
        ]
        
        # Clothing
        clothing = [
            {
                "name": "Cloak",
                "description": "A warm woolen cloak.",
                "item_type": ItemType.CLOTHING,
                "value": 1,
                "weight": 3.0,
                "properties": {
                    "warmth": 2,
                    "slot": "shoulders"
                }
            },
            {
                "name": "Boots",
                "description": "Sturdy leather boots.",
                "item_type": ItemType.CLOTHING,
                "value": 1,
                "weight": 2.0,
                "properties": {
                    "protection": 1,
                    "slot": "feet"
                }
            }
        ]
        
        # Combine all items
        all_items = weapons + armor + shields + potions + tools + food + ammunition + containers + clothing
        
        # Add items to database
        for item_data in all_items:
            item = Item(**item_data)
            db.add(item)
        
        db.commit()
        print(f"Added {len(all_items)} items to the database.")
    
    except Exception as e:
        db.rollback()
        print(f"Error seeding items: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_items()
    print("Item seeding complete.") 