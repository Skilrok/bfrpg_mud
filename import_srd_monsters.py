#!/usr/bin/env python3
"""
Script to import monsters from the SRD monsters markdown file into the database.
This script parses the Basic Fantasy RPG SRD monster descriptions and creates NPC records.
"""

# REMOVED: import json
import os
import re
import sys
from typing import Dict, List, Optional, Tuple, Union

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db_context
from app.models.npc import NPC, NPCType

# Define regex patterns for extracting data
MONSTER_HEADER_PATTERN = r"## (.+?) \[Anchor\]"
MONSTER_STAT_PATTERN = r"\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
MONSTER_DESC_PATTERN = r"XP: \| \d+ \|\s*\n\n([\s\S]+?)(?=##|\Z)"


def extract_monster_sections(content: str) -> List[Tuple[str, str, str]]:
    """
    Extract monster sections from the markdown content.
    Returns a list of tuples (name, stats_section, description).
    """
    monsters = []
    current_position = 0

    # Find all monster headers
    for match in re.finditer(MONSTER_HEADER_PATTERN, content):
        monster_name = match.group(1).strip()
        header_end_pos = match.end()

        # Find the next header or end of file
        next_header_match = re.search(MONSTER_HEADER_PATTERN, content[header_end_pos:])
        if next_header_match:
            next_header_pos = header_end_pos + next_header_match.start()
            monster_section = content[header_end_pos:next_header_pos]
        else:
            monster_section = content[header_end_pos:]

        # Split the section into stats table and description
        stats_end = re.search(r"XP: \| \d+ \|", monster_section)
        if stats_end:
            stats_end_pos = stats_end.end()
            stats_section = monster_section[:stats_end_pos]
            description = monster_section[stats_end_pos:].strip()
            monsters.append((monster_name, stats_section, description))

    return monsters


def parse_monster_stats(stats_section: str) -> Dict:
    """Parse monster stats from the stats section"""
    stats = {}

    for line in stats_section.split("\n"):
        match = re.search(MONSTER_STAT_PATTERN, line)
        if match:
            key, value = [g.strip() for g in match.groups()]

            if key == "Armor Class:":
                # Handle AC with parentheses like "15 (13)"
                ac_match = re.search(r"(\d+)(?:\s*\((\d+)\))?", value)
                if ac_match:
                    stats["armor_class"] = int(ac_match.group(1))

            elif key == "Hit Dice:":
                # Extract hit dice and hit points
                hd_match = re.search(r"(\d+(?:\+\d+|\-\d+)?|\d+/\d+)\*?(?:\*?)", value)
                if hd_match:
                    hit_dice = hd_match.group(1)
                    # Calculate approximate hit points based on hit dice
                    if "/" in hit_dice:  # Handle fractions like 1/2
                        stats["hit_points"] = 4  # Default for fractional HD
                        stats["level"] = 1
                    else:
                        # Parse X+Y format
                        hd_parts = re.match(r"(\d+)(?:\+(\d+)|\-(\d+))?", hit_dice)
                        if hd_parts:
                            base_hd = int(hd_parts.group(1))
                            bonus = (
                                int(hd_parts.group(2) or 0) if hd_parts.group(2) else 0
                            )
                            penalty = (
                                int(hd_parts.group(3) or 0) if hd_parts.group(3) else 0
                            )
                            stats["hit_points"] = (base_hd * 4) + bonus - penalty
                            stats["level"] = base_hd

            elif key == "No. of Attacks:":
                # Store in properties as attacks
                stats["attacks"] = value

            elif key == "Damage:":
                # Store in properties as damage
                stats["damage"] = value

            elif key == "Movement:":
                # Store in properties
                stats["movement"] = value

            elif key == "Morale:":
                # Parse morale value
                morale_match = re.search(r"(\d+)", value)
                if morale_match:
                    stats["morale"] = int(morale_match.group(1))
                    # If morale is high (9+), creature is hostile
                    stats["is_hostile"] = int(morale_match.group(1)) >= 9

            elif key == "Treasure Type:":
                # Store in properties
                stats["treasure_table"] = value

            elif key == "XP:":
                # Extract XP value for challenge rating approximation
                xp_match = re.search(r"(\d+(?:,\d+)?)", value)
                if xp_match:
                    xp = int(xp_match.group(1).replace(",", ""))
                    # Approximate challenge rating based on XP
                    if xp < 50:
                        stats["challenge_rating"] = 0.25
                    elif xp < 100:
                        stats["challenge_rating"] = 0.5
                    elif xp < 200:
                        stats["challenge_rating"] = 1
                    elif xp < 500:
                        stats["challenge_rating"] = 2
                    elif xp < 1000:
                        stats["challenge_rating"] = 3
                    elif xp < 2000:
                        stats["challenge_rating"] = 4
                    else:
                        stats["challenge_rating"] = 5

    return stats


def create_monster_dict(name: str, stats: Dict, description: str) -> Dict:
    """Create a monster dictionary from parsed data"""
    # Determine monster type based on name or description
    monster_type = name.split(",")[0].split("(")[0].strip()

    # Check if the monster is a special type
    if "dragon" in name.lower():
        monster_type = "dragon"
    elif "giant" in name.lower() and "beetle" not in name.lower():
        monster_type = "giant"
    elif "undead" in description.lower() or any(
        x in name.lower() for x in ["ghost", "ghoul", "skeleton", "zombie", "vampire"]
    ):
        monster_type = "undead"

    # Create properties dictionary for additional data
    properties = {
        "source": "BFRPG SRD",
        "special_abilities": [],
        "weaknesses": [],
        "resistances": [],
    }

    # Add attacks
    if "attacks" in stats:
        properties["attacks"] = [
            {"name": attack.strip(), "damage": stats.get("damage", "")}
            for attack in stats.get("attacks", "").split("/")
        ]

    # Add movement
    if "movement" in stats:
        properties["movement"] = stats["movement"]

    # Check for special abilities, weaknesses, or resistances in description
    if "*" in name:
        properties["special_abilities"].append("Requires special weapons to hit")

    # Parse description for special abilities and weaknesses
    if "immune" in description.lower() or "immunity" in description.lower():
        for line in description.lower().split("."):
            if "immune" in line:
                properties["resistances"].append(line.strip())

    if "vulnerable" in description.lower() or "weakness" in description.lower():
        for line in description.lower().split("."):
            if "vulnerable" in line or "weakness" in line:
                properties["weaknesses"].append(line.strip())

    # Create the monster dictionary
    monster_dict = {
        "name": name,
        "description": (
            description[:500] if len(description) > 500 else description
        ),  # Truncate if too long
        "npc_type": NPCType.MONSTER,
        "monster_type": monster_type,
        "level": stats.get("level", 1),
        "hit_points": stats.get("hit_points", 4),
        "armor_class": stats.get("armor_class", 10),
        "is_hostile": stats.get("is_hostile", True),
        "challenge_rating": stats.get("challenge_rating", 0.5),
        "treasure_table": stats.get("treasure_table", "None"),
        "properties": properties,
        "dialogue": {},  # Monsters typically don't have dialogue
        "inventory": [],  # We'll leave inventory empty for now
    }

    return monster_dict


def read_srd_monsters_file() -> str:
    """Read the SRD monsters markdown file"""
    try:
        with open("docs/bfsrd/srd_monstersAll.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("Error: SRD monsters file not found at docs/bfsrd/srd_monstersAll.md")
        sys.exit(1)


def import_monsters(db: Session, monsters: List[Dict]) -> None:
    """Import monsters into the database"""
    for monster_dict in monsters:
        # Check if monster already exists
        existing = (
            db.query(NPC)
            .filter(NPC.name == monster_dict["name"], NPC.npc_type == NPCType.MONSTER)
            .first()
        )
        if existing:
            print(f"Monster '{monster_dict['name']}' already exists, skipping.")
            continue

        # Create new monster NPC
        monster = NPC(**monster_dict)
        db.add(monster)
        print(f"Added monster: {monster.name}")

    db.commit()


def main():
    """Main entry point for the script"""
    print("Importing monsters from SRD monsters file...")

    # Read SRD monsters file
    content = read_srd_monsters_file()

    # Extract monster sections
    monster_sections = extract_monster_sections(content)

    # Parse monsters
    monsters = []
    for name, stats_section, description in monster_sections:
        # Skip table of contents and section headers
        if not stats_section or "---" not in stats_section:
            continue

        # Parse stats and create monster dictionary
        stats = parse_monster_stats(stats_section)
        monster_dict = create_monster_dict(name, stats, description)
        monsters.append(monster_dict)

    # Import into database
    with get_db_context() as db:
        # Check how many NPCs we already have
        existing_count = db.query(NPC).filter(NPC.npc_type == NPCType.MONSTER).count()
        print(f"Database currently has {existing_count} monsters.")

        # Import monsters
        import_monsters(db, monsters)

        # Report results
        new_count = db.query(NPC).filter(NPC.npc_type == NPCType.MONSTER).count()
        print(f"Successfully imported {new_count - existing_count} new monsters.")
        print(f"Total monsters in database: {new_count}")


if __name__ == "__main__":
    main()
