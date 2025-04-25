#!/usr/bin/env python3
"""
Simple script to check the character-hireling relationship
"""

import logging

from sqlalchemy import inspect, text

from app.database import get_db_context
from app.models import Character, Hireling

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_database_schema():
    """Check the database schema for the hirelings table"""
    logger.info("Checking database schema...")

    with get_db_context() as db:
        # Get the hireling table schema
        insp = inspect(db.get_bind())
        columns = insp.get_columns("hirelings")

        column_names = [col["name"] for col in columns]
        logger.info(f"Columns in hirelings table: {column_names}")

        # Check if character_id exists and master_id doesn't
        has_character_id = "character_id" in column_names
        has_master_id = "master_id" in column_names

        logger.info(f"Has character_id column: {has_character_id}")
        logger.info(f"Has master_id column: {has_master_id}")

        return has_character_id and not has_master_id


def check_character_hireling_relationship():
    """Check the relationship between characters and hirelings"""
    logger.info("Checking character-hireling relationship...")

    with get_db_context() as db:
        # Get all characters
        characters = db.query(Character).all()
        logger.info(f"Found {len(characters)} characters")

        # Get all hirelings
        hirelings = db.query(Hireling).all()
        logger.info(f"Found {len(hirelings)} hirelings")

        # Check characters with hirelings
        for character in characters:
            # Get hirelings for this character
            char_hirelings = (
                db.query(Hireling).filter(Hireling.character_id == character.id).all()
            )

            logger.info(
                f"Character {character.name} (ID: {character.id}) has {len(char_hirelings)} hirelings"
            )

            # List each hireling
            for hireling in char_hirelings:
                logger.info(f"  - Hireling: {hireling.name} (ID: {hireling.id})")

        # Check all hirelings and their associated characters
        for hireling in hirelings:
            if hireling.character_id:
                character = (
                    db.query(Character)
                    .filter(Character.id == hireling.character_id)
                    .first()
                )
                character_name = character.name if character else "Unknown"
                logger.info(
                    f"Hireling {hireling.name} (ID: {hireling.id}) belongs to character {character_name} (ID: {hireling.character_id})"
                )
            else:
                logger.info(
                    f"Hireling {hireling.name} (ID: {hireling.id}) is not assigned to any character"
                )


def try_direct_sql_query():
    """Try a direct SQL query to check the relationship"""
    logger.info("Running direct SQL query...")

    with get_db_context() as db:
        query = text(
            """
        SELECT c.id, c.name, h.id, h.name
        FROM characters c
        LEFT JOIN hirelings h ON c.id = h.character_id
        LIMIT 5
        """
        )

        result = db.execute(query).fetchall()

        logger.info("Character-Hireling Relationships:")
        for row in result:
            hireling_name = row[3] if row[3] else "None"
            logger.info(
                f"Character: {row[0]} ({row[1]}) -> Hireling: {row[2]} ({hireling_name})"
            )


if __name__ == "__main__":
    # Check database schema
    schema_ok = check_database_schema()

    if schema_ok:
        logger.info(
            "Database schema is correct (character_id exists, master_id doesn't)"
        )
    else:
        logger.warning("Database schema has issues!")

    # Check the relationship
    check_character_hireling_relationship()

    # Try direct SQL
    try_direct_sql_query()
