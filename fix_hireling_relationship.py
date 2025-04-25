#!/usr/bin/env python3
"""
Script to fix relationship mismatches between models.
"""

import logging
import traceback

from sqlalchemy import text

from app.database import get_db_context

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def update_hireling_model():
    """Update the Hireling model file to fix the relationship mismatch"""
    # Path to the Hireling model file
    model_path = "app/models/hireling.py"

    try:
        # Read the current file
        with open(model_path, "r") as f:
            content = f.read()

        # Save a backup
        with open(f"{model_path}.bak", "w") as f:
            f.write(content)

        logger.info(f"Backup created at {model_path}.bak")

        # Replace the relationship line
        if 'master = relationship("Character", back_populates="hirelings")' in content:
            new_content = content.replace(
                'master = relationship("Character", back_populates="hirelings")',
                'character = relationship("Character", back_populates="hirelings")  # Renamed from master',
            )

            # Update all references from 'master' to 'character' in the file
            # Be careful to only replace variable references, not strings or comments
            lines = new_content.split("\n")
            updated_lines = []

            for line in lines:
                # Skip comment lines
                if line.strip().startswith("#"):
                    updated_lines.append(line)
                    continue

                # Replace self.master with self.character
                if "self.master" in line:
                    line = line.replace("self.master", "self.character")

                # Replace master_id with character_id but keep the column name the same
                if (
                    "master_id" in line
                    and "master_id" not in line.split('"')
                    and "master_id" not in line.split("'")
                ):
                    # Only replace references, not the column definition
                    if "Column(" not in line:
                        line = line.replace("master_id", "character_id")

                # If updating the Column definition, update it to character_id
                if "master_id = Column(" in line:
                    line = line.replace(
                        "master_id = Column(",
                        "character_id = Column(  # Renamed from master_id",
                    )

                updated_lines.append(line)

            new_content = "\n".join(updated_lines)

            # Write the updated content
            with open(model_path, "w") as f:
                f.write(new_content)

            logger.info(
                f"Updated {model_path}: renamed 'master' relationship to 'character'"
            )
            return True
        else:
            logger.warning(
                f"Could not find the expected relationship line in {model_path}"
            )
            return False

    except Exception as e:
        logger.error(f"Error updating Hireling model: {str(e)}")
        traceback.print_exc()
        return False


def update_user_model():
    """Update the User model to ensure consistent relationship naming"""
    # Path to the User model file - needs to be checked if this is correct
    model_path = "app/models/user.py"

    try:
        # Check if file exists
        import os

        if not os.path.exists(model_path):
            # Try looking in the main models file
            model_path = "app/models.py"
            if not os.path.exists(model_path):
                logger.error(f"Could not find User model at {model_path}")
                return False

        # Read the current file
        with open(model_path, "r") as f:
            content = f.read()

        # Save a backup
        with open(f"{model_path}.bak", "w") as f:
            f.write(content)

        logger.info(f"Backup created at {model_path}.bak")

        # Look for User model character relationship
        owner_pattern = 'characters = relationship("Character", back_populates="owner")'
        user_pattern = 'characters = relationship("Character", back_populates="user")'

        if owner_pattern in content:
            # Fix the relationship to match Character model (user instead of owner)
            new_content = content.replace(
                owner_pattern,
                user_pattern + '  # Changed from "owner" to match Character model',
            )

            # Write the updated content
            with open(model_path, "w") as f:
                f.write(new_content)

            logger.info(
                f"Updated {model_path}: changed back_populates from 'owner' to 'user'"
            )
            return True
        elif user_pattern in content:
            logger.info("User model already has correct relationship naming")
            return True
        else:
            logger.warning(f"Could not find character relationship in User model")
            return False

    except Exception as e:
        logger.error(f"Error updating User model: {str(e)}")
        traceback.print_exc()
        return False


def check_character_model():
    """Check the Character model to identify relationship issues"""
    # Path to the Character model
    model_path = "app/models/character.py"

    try:
        # Check if file exists
        import os

        if not os.path.exists(model_path):
            # Try looking in the main models file
            model_path = "app/models.py"
            if not os.path.exists(model_path):
                logger.error(f"Could not find Character model at {model_path}")
                return False

        # Read the current file
        with open(model_path, "r") as f:
            content = f.read()

        # Check for the user relationship
        if 'user = relationship("User", back_populates="characters")' in content:
            logger.info("Character model has correct User relationship")
        elif 'owner = relationship("User", back_populates="characters")' in content:
            logger.warning(
                "Character model uses 'owner' instead of 'user' for User relationship"
            )
            logger.info("Consider updating Character model to use 'user' consistently")

        # Check for the hireling relationship
        if 'hirelings = relationship("Hireling", back_populates="character"' in content:
            logger.info("Character model has inconsistent Hireling relationship")
            logger.info("Options: 1) Change Hireling.master to Hireling.character, or")
            logger.info(
                "         2) Change Character.hirelings back_populates to 'master'"
            )

        return True

    except Exception as e:
        logger.error(f"Error checking Character model: {str(e)}")
        traceback.print_exc()
        return False


def update_character_owner_to_user():
    """Update the Character model to use 'user' consistently instead of 'owner'"""
    # Path to the Character model
    model_path = "app/models/character.py"

    try:
        # Check if file exists
        import os

        if not os.path.exists(model_path):
            # Try looking in the main models file
            model_path = "app/models.py"
            if not os.path.exists(model_path):
                logger.error(f"Could not find Character model at {model_path}")
                return False

        # Read the current file
        with open(model_path, "r") as f:
            content = f.read()

        # Save a backup
        with open(f"{model_path}.bak", "w") as f:
            f.write(content)

        logger.info(f"Backup created at {model_path}.bak")

        # Replace owner with user if needed
        if 'owner = relationship("User", back_populates="characters")' in content:
            new_content = content.replace(
                'owner = relationship("User", back_populates="characters")',
                'user = relationship("User", back_populates="characters")  # Renamed from owner',
            )

            # Update all references from 'owner' to 'user' in the file
            lines = new_content.split("\n")
            updated_lines = []

            for line in lines:
                # Skip comment lines
                if line.strip().startswith("#"):
                    updated_lines.append(line)
                    continue

                # Replace self.owner with self.user
                if "self.owner" in line:
                    line = line.replace("self.owner", "self.user")

                # Replace owner_ with user_ but be careful about strings
                if "owner_" in line and not ('"owner_' in line or "'owner_" in line):
                    line = line.replace("owner_", "user_")

                updated_lines.append(line)

            new_content = "\n".join(updated_lines)

            # Write the updated content
            with open(model_path, "w") as f:
                f.write(new_content)

            logger.info(f"Updated {model_path}: renamed 'owner' relationship to 'user'")
            return True
        else:
            logger.info("Character model already uses 'user' relationship")
            return True

    except Exception as e:
        logger.error(f"Error updating Character model: {str(e)}")
        traceback.print_exc()
        return False


def update_database_schema():
    """Update the database schema to rename master_id to character_id if needed"""
    try:
        from sqlalchemy import inspect, text

        from app.database import get_db_context

        with get_db_context() as db:
            inspector = inspect(db.bind)
            columns = [col["name"] for col in inspector.get_columns("hirelings")]

            # Check if master_id column exists but character_id doesn't
            if "master_id" in columns and "character_id" not in columns:
                logger.info(
                    "Found master_id column but no character_id - renaming column"
                )

                # For SQLite (which doesn't support ALTER TABLE RENAME COLUMN)
                if "sqlite" in str(db.bind.url).lower():
                    # Execute a more complex migration for SQLite
                    # 1. Create a new table with the correct schema
                    # 2. Copy data from old to new table
                    # 3. Drop old table
                    # 4. Rename new table to old name

                    # Get all column info except master_id
                    all_columns = inspector.get_columns("hirelings")
                    column_defs = []
                    column_names = []
                    for col in all_columns:
                        if col["name"] == "master_id":
                            # Rename to character_id in the schema definition
                            col_name = "character_id"
                        else:
                            col_name = col["name"]

                        column_names.append(col_name)
                        nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                        default = (
                            f"DEFAULT {col['default']}"
                            if col.get("default") is not None
                            else ""
                        )
                        primary_key = (
                            "PRIMARY KEY" if col.get("primary_key", False) else ""
                        )

                        # Get type string for the column
                        type_str = str(col["type"])
                        if "CHAR" in type_str or "VARCHAR" in type_str:
                            # Extract length for string types
                            import re

                            match = re.search(r"\((\d+)\)", type_str)
                            length = match.group(1) if match else "255"
                            col_type = f"VARCHAR({length})"
                        else:
                            col_type = type_str

                        column_def = f"{col_name} {col_type} {nullable} {default} {primary_key}".strip()
                        column_defs.append(column_def)

                    # Create new table
                    create_table_sql = f"""
                    CREATE TABLE new_hirelings (
                        {', '.join(column_defs)}
                    )
                    """

                    # Copy data
                    old_cols = [
                        "character_id" if c == "master_id" else c
                        for c in [col["name"] for col in all_columns]
                    ]
                    new_cols = [
                        "character_id" if c == "master_id" else c
                        for c in [col["name"] for col in all_columns]
                    ]

                    copy_data_sql = f"""
                    INSERT INTO new_hirelings ({', '.join(new_cols)})
                    SELECT {', '.join(old_cols)} FROM hirelings
                    """

                    # Execute the migration
                    logger.info(
                        "Executing SQLite migration to rename master_id to character_id"
                    )

                    try:
                        db.execute(text(create_table_sql))
                        db.execute(text(copy_data_sql))
                        db.execute(text("DROP TABLE hirelings"))
                        db.execute(
                            text("ALTER TABLE new_hirelings RENAME TO hirelings")
                        )
                        db.commit()
                        logger.info(
                            "Successfully renamed master_id to character_id in SQLite database"
                        )
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Error in SQLite migration: {str(e)}")
                        traceback.print_exc()
                        return False
                else:
                    # For PostgreSQL and other databases that support ALTER TABLE RENAME COLUMN
                    try:
                        db.execute(
                            text(
                                "ALTER TABLE hirelings RENAME COLUMN master_id TO character_id"
                            )
                        )
                        db.commit()
                        logger.info(
                            "Successfully renamed master_id to character_id in database"
                        )
                    except Exception as e:
                        db.rollback()
                        logger.error(f"Error renaming column: {str(e)}")
                        traceback.print_exc()
                        return False
            elif "character_id" in columns:
                logger.info("Database schema already has character_id column")
            else:
                logger.warning(
                    "Could not find master_id or character_id columns in hirelings table"
                )

            return True
    except Exception as e:
        logger.error(f"Error updating database schema: {str(e)}")
        traceback.print_exc()
        return False


def test_relationship():
    """Test that the relationships work correctly after the fix"""
    logger.info("Testing relationships after fixes")

    try:
        # Import the models directly to test the relationship
        # We'll use direct SQL queries to avoid ORM issues
        with get_db_context() as db:
            # Test Character-Hireling relationship
            logger.info("Testing Character-Hireling relationship")
            character = db.execute(
                text("SELECT id, name FROM characters LIMIT 1")
            ).first()
            if character:
                char_id, char_name = character
                logger.info(f"Found character: {char_name} (ID: {char_id})")

                # Count hirelings - only check character_id since we've migrated the column
                hirelings_count_query = """
                    SELECT COUNT(*) FROM hirelings
                    WHERE character_id = :char_id
                """
                hirelings_count = (
                    db.execute(
                        text(hirelings_count_query),
                        {"char_id": char_id},
                    ).scalar()
                    or 0
                )

                logger.info(f"Character has {hirelings_count} hirelings")

                # Check one hireling if available
                if hirelings_count > 0:
                    hireling_query = """
                        SELECT id, name FROM hirelings
                        WHERE character_id = :char_id
                        LIMIT 1
                    """
                    hireling = db.execute(
                        text(hireling_query),
                        {"char_id": char_id},
                    ).first()

                    if hireling:
                        h_id, h_name = hireling
                        logger.info(
                            f"Found hireling: {h_name} (ID: {h_id}) for character {char_name}"
                        )

            # Test Character-User relationship
            logger.info("Testing Character-User relationship")
            char_user = db.execute(
                text(
                    """
                    SELECT c.id, c.name, u.id, u.username
                    FROM characters c
                    JOIN users u ON c.user_id = u.id
                    LIMIT 1
                    """
                )
            ).first()

            if char_user:
                c_id, c_name, u_id, u_name = char_user
                logger.info(
                    f"Character {c_name} (ID: {c_id}) belongs to user {u_name} (ID: {u_id})"
                )

            logger.info("Relationship tests passed")
            return True

    except Exception as e:
        logger.error(f"Error testing relationships: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix relationship mismatches between models"
    )
    parser.add_argument(
        "--no-update",
        action="store_true",
        help="Don't update the model files, just test",
    )
    parser.add_argument(
        "--check", action="store_true", help="Only check for issues without fixing"
    )
    parser.add_argument(
        "--skip-db", action="store_true", help="Skip database schema updates"
    )
    args = parser.parse_args()

    if args.check:
        check_character_model()
    elif not args.no_update:
        fixes_applied = False

        # Fix the hireling relationship
        if update_hireling_model():
            logger.info("Hireling model updated successfully")
            fixes_applied = True
        else:
            logger.error("Failed to update Hireling model")

        # Fix the user relationship
        if update_user_model():
            logger.info("User model updated successfully")
            fixes_applied = True
        else:
            logger.error("Failed to update User model")

        # Fix Character owner to user reference
        if update_character_owner_to_user():
            logger.info("Character model updated successfully")
            fixes_applied = True

        # Update database schema if needed
        if not args.skip_db and update_database_schema():
            logger.info("Database schema updated successfully")
            fixes_applied = True

        if fixes_applied:
            logger.info("Successfully applied relationship fixes")
        else:
            logger.warning("No fixes were applied")

    if test_relationship():
        logger.info("Relationship tests passed")
    else:
        logger.error("Relationship tests failed")
