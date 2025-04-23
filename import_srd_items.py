#!/usr/bin/env python3
"""
Script to import items from the SRD equipment markdown file into the database.
This script parses the Basic Fantasy RPG SRD equipment lists and creates item records.
"""

import os
import re
import sys
from typing import Dict, List, Optional, Union

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db_context
from app.models import Item, ItemType

# Define regex patterns for extracting data
MISC_EQUIPMENT_PATTERN = r"\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
WEAPON_PATTERN = r"\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
ARMOR_PATTERN = r"\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"


def parse_price(price_str: str) -> int:
    """
    Parse price string into copper pieces (lowest denomination)
    Example: "10 gp" -> 1000 (copper pieces)
    """
    price_str = price_str.strip().lower()
    
    if price_str == "n/a" or not price_str:
        return 0
    
    # Extract number and denomination
    match = re.match(r"(\d+)\s*([a-z]+)", price_str)
    if not match:
        return 0
    
    amount, unit = match.groups()
    amount = int(amount)
    
    # Convert to copper pieces
    if "pp" in unit:
        return amount * 1000  # 1 pp = 5 gp = 5 * 200 cp
    elif "gp" in unit:
        return amount * 100  # 1 gp = 100 cp
    elif "ep" in unit:
        return amount * 50  # 1 ep = 5 sp = 5 * 10 cp
    elif "sp" in unit:
        return amount * 10  # 1 sp = 10 cp
    elif "cp" in unit:
        return amount
    
    return 0


def parse_weight(weight_str: str) -> float:
    """
    Parse weight string into a float value
    Handles special cases like "*" (light) and "**" (negligible)
    """
    weight_str = weight_str.strip()
    
    if weight_str == "*":
        return 0.1  # Light item (10 = 1 pound)
    elif weight_str == "**":
        return 0.01  # Negligible weight
    
    # Try to convert to float
    try:
        # Handle fractions like "½"
        if "½" in weight_str:
            weight_str = weight_str.replace("½", ".5")
        return float(weight_str)
    except ValueError:
        return 0.0


def parse_misc_equipment(content: str) -> List[Dict]:
    """Parse miscellaneous equipment from the markdown content"""
    items = []
    in_misc_section = False
    
    for line in content.split("\n"):
        # Check if we're in the misc equipment table
        if "| Item | Price | Weight |" in line:
            in_misc_section = True
            continue
        
        if in_misc_section and "| ---" in line:
            continue
        
        # Exit if we reach the next section
        if in_misc_section and "## Weapons" in line:
            break
        
        # Parse item rows
        if in_misc_section and "|" in line:
            match = re.search(MISC_EQUIPMENT_PATTERN, line)
            if match:
                name, price_str, weight_str = match.groups()
                
                # Skip header rows or separator rows
                if "---" in name or "Item" in name:
                    continue
                
                items.append({
                    "name": name.strip(),
                    "description": f"Basic Fantasy RPG equipment: {name.strip()}",
                    "item_type": ItemType.MISCELLANEOUS,
                    "weight": parse_weight(weight_str),
                    "value": parse_price(price_str),
                    "is_equippable": False,
                    "properties": {
                        "source": "BFRPG SRD",
                        "category": "miscellaneous"
                    }
                })
    
    return items


def parse_weapons(content: str) -> List[Dict]:
    """Parse weapons from the markdown content"""
    weapons = []
    in_weapons_section = False
    current_category = None
    
    for line in content.split("\n"):
        # Check if we're in the weapons table
        if "| Weapon | Price | Size | Weight | Dmg. |" in line:
            in_weapons_section = True
            continue
        
        if in_weapons_section and "| ---" in line:
            continue
        
        # Exit if we reach the next section
        if in_weapons_section and "## Weapon Size" in line:
            break
        
        # Parse weapon rows
        if in_weapons_section and "|" in line:
            # Check if this is a category header
            if "**" in line and "|" in line:
                category_match = re.search(r"\|\s*\*\*([^*]+)\*\*\s*\|", line)
                if category_match:
                    current_category = category_match.group(1).strip()
                continue
            
            match = re.search(WEAPON_PATTERN, line)
            if match:
                name, price_str, size_str, weight_str, damage = [g.strip() for g in match.groups()]
                
                # Skip header rows or separator rows
                if "---" in name or "Weapon" in name:
                    continue
                
                # Handle special cases for ammunition
                is_ammunition = False
                if any(x in name.lower() for x in ["arrow", "quarrel", "bullet", "stone"]) and not any(x in name.lower() for x in ["bow", "crossbow", "sling"]):
                    item_type = ItemType.AMMUNITION
                    is_ammunition = True
                else:
                    item_type = ItemType.WEAPON
                
                # Skip empty rows
                if not name or name == "Thrown (one handed)" or name == "Melee (one handed)" or name == "Melee (two handed)":
                    continue
                
                weapons.append({
                    "name": name,
                    "description": f"Basic Fantasy RPG weapon: {name}",
                    "item_type": item_type,
                    "weight": parse_weight(weight_str),
                    "value": parse_price(price_str),
                    "is_equippable": True,
                    "equip_slot": "main_hand" if item_type == ItemType.WEAPON else None,
                    "damage": damage if damage else None,
                    "properties": {
                        "source": "BFRPG SRD",
                        "category": current_category or "weapon",
                        "size": size_str if size_str else None,
                        "is_ammunition": is_ammunition,
                        "weapon_size": size_str if size_str else None
                    }
                })
    
    return weapons


def parse_armor(content: str) -> List[Dict]:
    """Parse armor and shields from the markdown content"""
    armor_items = []
    in_armor_section = False
    
    for line in content.split("\n"):
        # Check if we're in the armor table
        if "| Armor Type | Price | Weight | AC |" in line:
            in_armor_section = True
            continue
        
        if in_armor_section and "| ---" in line:
            continue
        
        # Exit if we reach the next section
        if in_armor_section and "## Beasts of Burden" in line:
            break
        
        # Parse armor rows
        if in_armor_section and "|" in line:
            match = re.search(ARMOR_PATTERN, line)
            if match:
                name, price_str, weight_str, ac_str = [g.strip() for g in match.groups()]
                
                # Skip header rows or separator rows
                if "---" in name or "Armor Type" in name:
                    continue
                
                # Determine item type
                if name.lower() == "shield":
                    item_type = ItemType.SHIELD
                    equip_slot = "off_hand"
                    properties = {"ac_bonus": 1, "source": "BFRPG SRD"}
                elif name.lower() == "no armor":
                    continue  # Skip "no armor" row
                else:
                    item_type = ItemType.ARMOR
                    equip_slot = "body"
                    properties = {"armor_class": int(ac_str), "source": "BFRPG SRD"}
                
                armor_items.append({
                    "name": name,
                    "description": f"Basic Fantasy RPG armor: {name}",
                    "item_type": item_type,
                    "weight": parse_weight(weight_str),
                    "value": parse_price(price_str),
                    "is_equippable": True,
                    "equip_slot": equip_slot,
                    "armor_class": int(ac_str) if ac_str.isdigit() else None,
                    "properties": properties
                })
    
    return armor_items


def read_srd_equipment_file() -> str:
    """Read the SRD equipment markdown file"""
    try:
        with open("docs/bfsrd/srd_equipment.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: SRD equipment file not found at docs/bfsrd/srd_equipment.md")
        sys.exit(1)


def import_items(db: Session, items: List[Dict]) -> None:
    """Import items into the database"""
    for item_dict in items:
        # Check if item already exists
        existing = db.query(Item).filter(Item.name == item_dict["name"]).first()
        if existing:
            print(f"Item '{item_dict['name']}' already exists, skipping.")
            continue
        
        # Create new item
        item = Item(**item_dict)
        db.add(item)
        print(f"Added item: {item.name}")
    
    db.commit()


def main():
    """Main entry point for the script"""
    print("Importing items from SRD equipment file...")
    
    # Read SRD equipment file
    content = read_srd_equipment_file()
    
    # Parse items
    misc_items = parse_misc_equipment(content)
    weapons = parse_weapons(content)
    armor = parse_armor(content)
    
    # Combine all items
    all_items = misc_items + weapons + armor
    
    # Import into database
    with get_db_context() as db:
        # Check how many items we already have
        existing_count = db.query(Item).count()
        print(f"Database currently has {existing_count} items.")
        
        # Import items
        import_items(db, all_items)
        
        # Report results
        new_count = db.query(Item).count()
        print(f"Successfully imported {new_count - existing_count} new items.")
        print(f"Total items in database: {new_count}")


if __name__ == "__main__":
    main() 