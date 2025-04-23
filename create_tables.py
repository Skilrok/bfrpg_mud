#!/usr/bin/env python3
"""
Script to directly create the missing tables in the database.
This is useful when Alembic migrations are not working as expected.
"""

import os
import sys

from sqlalchemy import inspect, text

from app.database import engine
from app.models.combat import CombatEncounter, CombatParticipant
from app.models.discovery import RoomDiscovery
from app.models.journal import JournalEntry
from app.models.spell import CharacterSpell, Spell

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_missing_tables():
    """Create any missing tables from our models"""

    print("Checking for missing tables...")

    # Get existing tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # List of model tables we want to ensure exist
    model_tables = [
        "combat_encounters",
        "combat_participants",
        "journal_entries",
        "spells",
        "character_spells",
        "room_discoveries",
    ]

    # Check which tables are missing
    missing_tables = [table for table in model_tables if table not in existing_tables]

    if not missing_tables:
        print("All tables already exist!")
        return

    print(f"Missing tables: {', '.join(missing_tables)}")

    # Create the missing tables
    print("Creating missing tables...")

    # Create tables selectively
    try:
        # Check each model class and create its table if missing
        if "combat_encounters" in missing_tables:
            CombatEncounter.__table__.create(engine, checkfirst=True)
            print("  - Created table: combat_encounters")

        if "combat_participants" in missing_tables:
            CombatParticipant.__table__.create(engine, checkfirst=True)
            print("  - Created table: combat_participants")

        if "journal_entries" in missing_tables:
            JournalEntry.__table__.create(engine, checkfirst=True)
            print("  - Created table: journal_entries")

        if "spells" in missing_tables:
            Spell.__table__.create(engine, checkfirst=True)
            print("  - Created table: spells")

        if "character_spells" in missing_tables:
            CharacterSpell.__table__.create(engine, checkfirst=True)
            print("  - Created table: character_spells")

        if "room_discoveries" in missing_tables:
            RoomDiscovery.__table__.create(engine, checkfirst=True)
            print("  - Created table: room_discoveries")

        print("Successfully created all missing tables!")

    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        sys.exit(1)


def add_monster_fields_to_npcs(conn):
    """Add monster-related fields to the npcs table if they don't exist."""
    print("Checking NPC table for monster fields...")
    inspector = inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("npcs")]

    missing_columns = []
    if "monster_type" not in columns:
        missing_columns.append("monster_type")
    if "challenge_rating" not in columns:
        missing_columns.append("challenge_rating")
    if "treasure_table" not in columns:
        missing_columns.append("treasure_table")

    if missing_columns:
        print(f"Missing columns: {', '.join(missing_columns)}")
        print("Adding missing columns to npcs table...")
        try:
            if "monster_type" in missing_columns:
                conn.execute(text("ALTER TABLE npcs ADD COLUMN monster_type VARCHAR"))
            if "challenge_rating" in missing_columns:
                conn.execute(text("ALTER TABLE npcs ADD COLUMN challenge_rating FLOAT"))
            if "treasure_table" in missing_columns:
                conn.execute(text("ALTER TABLE npcs ADD COLUMN treasure_table VARCHAR"))
            print("Successfully added missing columns to npcs table.")
        except Exception as e:
            print(f"Error adding columns: {e}")
    else:
        print("All monster fields already exist in npcs table.")


def create_indexes():
    """Create any missing indexes for performance optimization"""

    print("Creating performance indexes...")

    try:
        # Check and create indexes on characters table
        if table_exists("characters"):
            create_index_if_not_exists("characters", "ix_characters_user_id", "user_id")
            create_index_if_not_exists("characters", "ix_characters_level", "level")

        # Room indexes
        if table_exists("rooms"):
            create_index_if_not_exists("rooms", "ix_rooms_room_type", "room_type")
            # Composite index for coords
            create_composite_index_if_not_exists(
                "rooms", "ix_rooms_coords", ["x", "y", "z"]
            )

        # Exit indexes
        if table_exists("exits"):
            create_index_if_not_exists(
                "exits", "ix_exits_source_room_id", "source_room_id"
            )
            create_index_if_not_exists(
                "exits", "ix_exits_destination_room_id", "destination_room_id"
            )

        # Room content indexes
        if table_exists("room_items"):
            create_index_if_not_exists("room_items", "ix_room_items_room_id", "room_id")

        if table_exists("room_npcs"):
            create_index_if_not_exists("room_npcs", "ix_room_npcs_room_id", "room_id")

        # Combat indexes
        if table_exists("combat_encounters"):
            create_index_if_not_exists(
                "combat_encounters", "ix_combat_encounters_room_id", "room_id"
            )

        if table_exists("combat_participants"):
            ix_name = "ix_combat_participants_character_id"
            create_index_if_not_exists("combat_participants", ix_name, "character_id")
            create_index_if_not_exists(
                "combat_participants", "ix_combat_participants_npc_id", "npc_id"
            )

        # Character location indexes
        if table_exists("character_locations"):
            ix_name = "ix_character_locations_character_id"
            create_index_if_not_exists("character_locations", ix_name, "character_id")
            create_index_if_not_exists(
                "character_locations", "ix_character_locations_room_id", "room_id"
            )

        # Spell index
        if table_exists("spells"):
            create_index_if_not_exists("spells", "ix_spells_name", "name")

        print("Successfully created all necessary indexes!")

    except Exception as e:
        print(f"Error creating indexes: {str(e)}")
        sys.exit(1)


def table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def index_exists(table_name, index_name):
    """Check if an index exists on a table"""
    inspector = inspect(engine)
    indices = [idx["name"] for idx in inspector.get_indexes(table_name)]
    return index_name in indices


def create_index_if_not_exists(table_name, index_name, column_name):
    """Create an index if it doesn't already exist"""
    if not index_exists(table_name, index_name):
        with engine.connect() as conn:
            sql = (
                f"CREATE INDEX IF NOT EXISTS {index_name} "
                f"ON {table_name} ({column_name})"
            )
            conn.execute(text(sql))
            print(
                f"  - Created index: {index_name} on "
                f"{table_name}.{column_name}"
            )


def create_composite_index_if_not_exists(table_name, index_name, column_names):
    """Create a composite index if it doesn't already exist"""
    if not index_exists(table_name, index_name):
        columns_str = ', '.join(column_names)
        with engine.connect() as conn:
            sql = (
                f"CREATE INDEX IF NOT EXISTS {index_name} "
                f"ON {table_name} ({columns_str})"
            )
            conn.execute(text(sql))
            print(
                f"  - Created composite index: {index_name} "
                f"on {table_name}.({columns_str})"
            )


def main():
    """Main entry point for the script"""

    # Create missing tables
    create_missing_tables()

    # Add monster fields to NPCs
    with engine.connect() as conn:
        add_monster_fields_to_npcs(conn)

    # Create performance indexes
    create_indexes()

    print("\nDatabase schema update complete!")


if __name__ == "__main__":
    main()
