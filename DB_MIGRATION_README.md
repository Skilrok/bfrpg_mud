# BFRPG MUD Database Migration Guide

This guide explains how to apply the extended database schema for the BFRPG MUD project. The changes include new tables for combat encounters, journal entries, spells, and room discoveries, as well as enhancements to existing tables.

## Overview of Changes

The database migration adds the following new tables:
- **Combat Encounters & Participants**: For tracking battles between characters and monsters
- **Journal Entries**: For character quest logs, notes, and achievements
- **Spells & Character Spells**: For magic system implementation
- **Room Discoveries**: For tracking which rooms characters have explored

It also enhances existing tables:
- **NPCs**: Added monster-specific fields (monster_type, challenge_rating, treasure_table)
- **Various Indexes**: Added performance optimization indexes to key tables

## Prerequisites

- Python 3.6+
- Access to the BFRPG MUD database
- Project dependencies installed (`pip install -r requirements.txt`)

## Step 1: Apply the Database Migration

Run the migration script to create the new tables and update existing ones:

```bash
python apply_db_migration.py
```

**Options:**
- `--revision <rev>`: Specify a specific migration revision (default: 'head')
- `--sql-only`: Only print the SQL without applying it (for review)

Example to see the SQL that would be executed:
```bash
python apply_db_migration.py --sql-only
```

## Step 2: Seed Initial Data (Optional)

Populate the new tables with sample data:

```bash
python seed_db_data.py
```

**Options:**
- `--spells`: Only seed spell data
- `--journal`: Only seed journal entries
- `--monsters`: Only seed monster NPCs
- `--discoveries`: Only seed room discoveries
- `--all`: Seed all data types (default if no option specified)

Example to seed only spells and monsters:
```bash
python seed_db_data.py --spells --monsters
```

## Step 3: Verify the Migration

You can verify the migration was successful by:

1. Checking if the new tables exist in your database
2. Confirming the seeded data appears correctly
3. Testing the new functionality in the application

## Rollback (If Needed)

If you need to roll back the migration:

```bash
python apply_db_migration.py --revision extended_db_schema-1
```

## Database Model Usage

### Combat System

```python
# Start a new combat encounter
encounter = CombatEncounter(
    room_id=current_room.id,
    name="Ambush!"
)
db.add(encounter)
db.commit()

# Add a player character to the encounter
player = CombatParticipant(
    encounter_id=encounter.id,
    character_id=player_character.id,
    initiative=12
)
db.add(player)

# Add a monster to the encounter
monster = CombatParticipant(
    encounter_id=encounter.id,
    npc_id=goblin.id,
    initiative=8
)
db.add(monster)
db.commit()
```

### Journal System

```python
# Add a quest to a character's journal
quest = JournalEntry(
    character_id=character.id,
    title="The Dragon's Hoard",
    content="Defeat the dragon and recover the stolen treasure.",
    entry_type=JournalEntryType.QUEST
)
db.add(quest)
db.commit()

# Mark a quest as completed
quest.complete()
db.commit()
```

### Spell System

```python
# Grant a spell to a character
character_spell = CharacterSpell(
    character_id=mage.id,
    spell_id=fireball.id
)
db.add(character_spell)
db.commit()

# Mark a spell as prepared
character_spell.prepare()
db.commit()

# Cast a spell
character_spell.cast()
db.commit()
```

### Room Discovery System

```python
# Record that a character discovered a room
RoomDiscovery.discover_room(db, character.id, new_room.id)

# Get all rooms a character has visited
visited_rooms = RoomDiscovery.get_visited_rooms(db, character.id)
```

## Troubleshooting

If you encounter issues:

1. **Migration Errors**:
   - Check that the database user has sufficient privileges
   - Verify that any referenced tables exist before migration

2. **Seeding Errors**:
   - Make sure the migration was applied successfully first
   - Check for data validation issues in the seed script

3. **Database Connection Issues**:
   - Verify your database connection settings in `.env`
   - Check that the database server is running

If problems persist, run the migration with:
```bash
alembic upgrade extended_db_schema --sql
```
To see the exact SQL statements being executed.

## Additional Information

For more details, refer to:
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- The model files in `app/models/`
