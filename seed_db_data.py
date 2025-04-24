#!/usr/bin/env python3
"""
Script to seed initial data for the extended database schema.
This will populate the new tables with some example data.
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_context
from app.models import (
    NPC,
    Character,
    CharacterSpell,
    CombatEncounter,
    JournalEntry,
    JournalEntryType,
    NPCType,
    Room,
    RoomDiscovery,
    Spell,
    SpellSchool,
)


def seed_spells(db):
    """Seed the spells table with basic magic-user and cleric spells."""
    print("Seeding spells...")

    # Check if we already have spells
    existing_spells = db.query(Spell).count()
    if existing_spells > 0:
        print(f"Found {existing_spells} existing spells, skipping...")
        return

    # Basic magic-user spells
    magic_user_spells = [
        {
            "name": "Light",
            "description": "Creates a light source that lasts for 6 turns + 1 turn per level.",
            "level": 1,
            "school": SpellSchool.EVOCATION,
            "casting_time": "1 round",
            "range": "120'",
            "duration": "6 turns + 1/level",
            "components": "V, S",
            "spell_class": "magic-user",
            "properties": {
                "reversible": True,
                "reverse_name": "Darkness",
            },
        },
        {
            "name": "Magic Missile",
            "description": "Creates a dart of magical energy that hits its target for 1d6+1 damage. Additional missile at 3rd level and every 2 levels thereafter.",
            "level": 1,
            "school": SpellSchool.EVOCATION,
            "casting_time": "1 round",
            "range": "150'",
            "duration": "Instantaneous",
            "components": "V, S",
            "spell_class": "magic-user",
        },
        {
            "name": "Sleep",
            "description": "Puts 2d8 Hit Dice of creatures to sleep for 4d4 turns.",
            "level": 1,
            "school": SpellSchool.ENCHANTMENT,
            "casting_time": "1 round",
            "range": "240'",
            "duration": "4d4 turns",
            "components": "V, S, M",
            "spell_class": "magic-user",
            "properties": {
                "material_components": ["Fine sand", "Rose petals", "Cricket"],
            },
        },
    ]

    # Basic cleric spells
    cleric_spells = [
        {
            "name": "Cure Light Wounds",
            "description": "Cures 1d6+1 points of damage.",
            "level": 1,
            "school": SpellSchool.CLERICAL,
            "casting_time": "1 round",
            "range": "Touch",
            "duration": "Permanent",
            "components": "V, S",
            "spell_class": "cleric",
            "properties": {
                "reversible": True,
                "reverse_name": "Cause Light Wounds",
            },
        },
        {
            "name": "Detect Evil",
            "description": "Reveals evil creatures, objects, or areas.",
            "level": 1,
            "school": SpellSchool.CLERICAL,
            "casting_time": "1 round",
            "range": "60'",
            "duration": "6 turns",
            "components": "V, S",
            "spell_class": "cleric",
            "properties": {
                "reversible": True,
                "reverse_name": "Detect Good",
            },
        },
        {
            "name": "Protection from Evil",
            "description": "Creates a barrier around the target that protects against evil creatures.",
            "level": 1,
            "school": SpellSchool.CLERICAL,
            "casting_time": "1 round",
            "range": "Touch",
            "duration": "3 turns",
            "components": "V, S, M",
            "spell_class": "cleric",
            "properties": {
                "material_components": ["Holy water"],
                "reversible": True,
                "reverse_name": "Protection from Good",
            },
        },
    ]

    # Add magic-user spells
    for spell_data in magic_user_spells:
        spell = Spell(**spell_data)
        db.add(spell)

    # Add cleric spells
    for spell_data in cleric_spells:
        spell = Spell(**spell_data)
        db.add(spell)

    db.commit()
    print(f"Added {len(magic_user_spells) + len(cleric_spells)} spells")


def seed_journal_entries(db):
    """Seed journal entries for existing characters."""
    print("Seeding journal entries...")

    # Get existing characters
    characters = db.query(Character).all()
    if not characters:
        print("No characters found, skipping journal entries...")
        return

    # Add a welcome journal entry for each character
    entries_added = 0
    for character in characters:
        # Check if character already has entries
        existing_entries = (
            db.query(JournalEntry)
            .filter(JournalEntry.character_id == character.id)
            .count()
        )

        if existing_entries == 0:
            welcome_entry = JournalEntry(
                character_id=character.id,
                title="Welcome to the Adventure",
                content=(
                    f"Welcome, {character.name}! Your adventure begins now.\n\n"
                    "This journal will record your quests, discoveries, and notable events "
                    "throughout your journey in this world. Be sure to check back often for "
                    "updates and to track your progress."
                ),
                entry_type=JournalEntryType.SYSTEM,
            )
            db.add(welcome_entry)
            entries_added += 1

            # Add a sample quest
            quest_entry = JournalEntry(
                character_id=character.id,
                title="The Missing Merchant",
                content=(
                    "I've heard rumors in town about a merchant who went missing on the road "
                    "to the next village. The town guard is offering a reward for information "
                    "about his whereabouts or safe return. I should check with the captain of "
                    "the guard for more details."
                ),
                entry_type=JournalEntryType.QUEST,
                is_completed=False,
            )
            db.add(quest_entry)
            entries_added += 1

    db.commit()
    print(f"Added {entries_added} journal entries")


def seed_monster_npcs(db):
    """Seed monster NPCs for combat encounters."""
    print("Seeding monster NPCs...")

    # Check if we already have monster NPCs
    existing_monsters = db.query(NPC).filter(NPC.npc_type == NPCType.MONSTER).count()

    if existing_monsters > 0:
        print(f"Found {existing_monsters} existing monster NPCs, skipping...")
        return

    # Basic monster templates
    monsters = [
        {
            "name": "Goblin Warrior",
            "description": "A small, green-skinned humanoid with sharp teeth and yellow eyes.",
            "npc_type": NPCType.MONSTER,
            "level": 1,
            "hit_points": 5,
            "armor_class": 6,
            "is_hostile": True,
            "monster_type": "goblin",
            "challenge_rating": 0.25,
            "treasure_table": "individual_d",
            "properties": {
                "attacks": [
                    {"name": "Short Sword", "damage": "1d6", "hit_bonus": 1},
                    {
                        "name": "Shortbow",
                        "damage": "1d6",
                        "hit_bonus": 1,
                        "range": "60'",
                    },
                ],
                "move_rate": "30'",
                "morale": 7,
                "xp_value": 15,
            },
        },
        {
            "name": "Orc Brute",
            "description": "A muscular, pig-faced humanoid with tusks protruding from its lower jaw.",
            "npc_type": NPCType.MONSTER,
            "level": 2,
            "hit_points": 9,
            "armor_class": 6,
            "is_hostile": True,
            "monster_type": "orc",
            "challenge_rating": 0.5,
            "treasure_table": "individual_c",
            "properties": {
                "attacks": [
                    {"name": "Battleaxe", "damage": "1d8+1", "hit_bonus": 2},
                    {
                        "name": "Javelin",
                        "damage": "1d6+1",
                        "hit_bonus": 1,
                        "range": "30'",
                    },
                ],
                "move_rate": "30'",
                "morale": 8,
                "xp_value": 25,
                "special_abilities": ["Darkvision 60'"],
            },
        },
        {
            "name": "Skeleton Warrior",
            "description": "A animated skeleton clutching rusty weapons, its eye sockets glowing with malevolent energy.",
            "npc_type": NPCType.MONSTER,
            "level": 1,
            "hit_points": 6,
            "armor_class": 7,
            "is_hostile": True,
            "monster_type": "undead",
            "challenge_rating": 0.25,
            "treasure_table": "none",
            "properties": {
                "attacks": [
                    {"name": "Rusty Sword", "damage": "1d6", "hit_bonus": 0},
                    {"name": "Bone Claw", "damage": "1d4", "hit_bonus": 0},
                ],
                "move_rate": "20'",
                "morale": 12,
                "xp_value": 20,
                "special_abilities": ["Undead Immunities"],
                "resistances": ["Piercing", "Cold"],
                "weaknesses": ["Bludgeoning"],
            },
        },
    ]

    # Add monsters
    for monster_data in monsters:
        monster = NPC(**monster_data)
        db.add(monster)

    db.commit()
    print(f"Added {len(monsters)} monster NPCs")


def seed_room_discoveries(db):
    """Seed room discoveries for existing characters."""
    print("Seeding room discoveries...")

    # Get existing characters and rooms
    characters = db.query(Character).all()
    if not characters:
        print("No characters found, skipping room discoveries...")
        return

    rooms = db.query(Room).limit(10).all()
    if not rooms:
        print("No rooms found, skipping room discoveries...")
        return

    # Add starting room discoveries for each character
    discoveries_added = 0
    for character in characters:
        # Get current location if any
        character_location = (
            db.query(CharacterLocation)
            .filter(CharacterLocation.character_id == character.id)
            .first()
        )

        if character_location and character_location.room_id:
            # Discover current room
            discovery = RoomDiscovery(
                character_id=character.id,
                room_id=character_location.room_id,
                is_visited=True,
                discovery_date=datetime.utcnow(),
            )
            db.add(discovery)
            discoveries_added += 1

            # Discover a few nearby rooms (simulate previous exploration)
            for i, room in enumerate(rooms[:3]):
                if room.id != character_location.room_id:
                    discovery = RoomDiscovery(
                        character_id=character.id,
                        room_id=room.id,
                        is_visited=(i < 2),  # First 2 rooms visited, others just seen
                        discovery_date=datetime.utcnow(),
                    )
                    db.add(discovery)
                    discoveries_added += 1

    db.commit()
    print(f"Added {discoveries_added} room discoveries")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Seed initial data for the BFRPG MUD.")
    parser.add_argument("--spells", action="store_true", help="Seed spell data")
    parser.add_argument("--journal", action="store_true", help="Seed journal entries")
    parser.add_argument("--monsters", action="store_true", help="Seed monster NPCs")
    parser.add_argument(
        "--discoveries", action="store_true", help="Seed room discoveries"
    )
    parser.add_argument("--all", action="store_true", help="Seed all data types")

    args = parser.parse_args()

    # If no specific option is chosen, seed all
    if not any([args.spells, args.journal, args.monsters, args.discoveries, args.all]):
        args.all = True

    with get_db_context() as db:
        if args.spells or args.all:
            seed_spells(db)

        if args.journal or args.all:
            seed_journal_entries(db)

        if args.monsters or args.all:
            seed_monster_npcs(db)

        if args.discoveries or args.all:
            seed_room_discoveries(db)

    print("Database seeding complete!")


if __name__ == "__main__":
    main()
