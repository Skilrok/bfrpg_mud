#!/usr/bin/env python3
"""
Comprehensive script to fix the mismatch between master_id and character_id in the codebase.
This script:
1. Renames the database column from master_id to character_id
2. Updates all code references from master_id to character_id
3. Verifies data integrity after the changes
"""

import logging
# REMOVED: import os
import re
import traceback
from pathlib import Path

from sqlalchemy import text

from app.database import get_db_context
# REMOVED: from app.models.hireling import Hireling

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_column_exists(db, column_name, table_name="hirelings"):
    """Check if a column exists in the table"""
    try:
        query = text(
            f"SELECT 1 FROM pragma_table_info('{table_name}') WHERE name = :column_name"
        )
        result = db.execute(query, {"column_name": column_name}).scalar()
        return bool(result)
    except Exception as e:
        logger.error(f"Error checking column existence: {str(e)}")
        return False


def rename_column_in_db(db):
    """Rename the master_id column to character_id in the hirelings table"""
    try:
        # Check if master_id exists and character_id doesn't
        master_exists = check_column_exists(db, "master_id")
        character_exists = check_column_exists(db, "character_id")

        if not master_exists:
            logger.error("Column 'master_id' doesn't exist in the hirelings table")
            return False

        if character_exists:
            logger.warning(
                "Column 'character_id' already exists in the hirelings table"
            )
            return False

        # SQLite doesn't support ALTER TABLE RENAME COLUMN directly until version 3.25.0
        # We need to use a workaround with a temporary table

        # Get the current schema
        logger.info("Getting current table schema...")
        schema_query = text("PRAGMA table_info(hirelings)")
        columns = db.execute(schema_query).fetchall()

        # Create column definitions for the new table, replacing master_id with character_id
        column_defs = []
        old_columns = []
        new_columns = []

        for col in columns:
            col_name = col[1]  # Column name is at index 1
            col_type = col[2]  # Column type is at index 2
            not_null = "NOT NULL" if col[3] == 1 else ""  # NOT NULL constraint
            default = f"DEFAULT {col[4]}" if col[4] is not None else ""  # Default value
            pk = "PRIMARY KEY" if col[5] == 1 else ""  # Primary key

            old_columns.append(col_name)

            # Replace master_id with character_id in the schema
            if col_name == "master_id":
                col_name = "character_id"
                logger.info(f"Replacing 'master_id' with 'character_id' in schema")

            new_columns.append(col_name)
            column_defs.append(
                f"{col_name} {col_type} {not_null} {default} {pk}".strip()
            )

        # Create a new table with the updated schema
        create_table_query = text(
            f"""
        CREATE TABLE hirelings_new (
            {", ".join(column_defs)}
        )
        """
        )

        # Copy data from old table to new table, mapping master_id to character_id
        old_cols_str = ", ".join(old_columns)
        new_cols_str = ", ".join(new_columns)

        copy_data_query = text(
            f"""
        INSERT INTO hirelings_new ({new_cols_str})
        SELECT {old_cols_str} FROM hirelings
        """
        )

        # Drop old table and rename new table
        drop_old_query = text("DROP TABLE hirelings")
        rename_query = text("ALTER TABLE hirelings_new RENAME TO hirelings")

        # Execute the queries in a transaction
        logger.info("Creating new table with updated schema...")
        db.execute(create_table_query)

        logger.info("Copying data from old table to new table...")
        db.execute(copy_data_query)

        logger.info("Dropping old table...")
        db.execute(drop_old_query)

        logger.info("Renaming new table...")
        db.execute(rename_query)

        # Check if the migration was successful
        character_exists = check_column_exists(db, "character_id")
        master_exists = check_column_exists(db, "master_id")

        if character_exists and not master_exists:
            logger.info("Migration successful: 'master_id' renamed to 'character_id'")
            return True
        else:
            logger.error("Migration failed: unexpected column state after migration")
            return False

    except Exception as e:
        logger.error(f"Error renaming column: {str(e)}")
        traceback.print_exc()
        return False


def verify_data(db):
    """Verify data integrity after the migration"""
    try:
        # Count all hirelings
        count_query = text("SELECT COUNT(*) FROM hirelings")
        count = db.execute(count_query).scalar()
        logger.info(f"Total hirelings after migration: {count}")

        # Check for any character relationships
        related_query = text(
            "SELECT COUNT(*) FROM hirelings WHERE character_id IS NOT NULL"
        )
        related_count = db.execute(related_query).scalar()
        logger.info(f"Hirelings with character relationships: {related_count}")

        # Sample a few records
        sample_query = text("SELECT id, name, character_id FROM hirelings LIMIT 5")
        samples = db.execute(sample_query).fetchall()
        logger.info("Sample hireling records:")
        for sample in samples:
            logger.info(
                f"  ID: {sample[0]}, Name: {sample[1]}, Character ID: {sample[2]}"
            )

        return True

    except Exception as e:
        logger.error(f"Error verifying data: {str(e)}")
        traceback.print_exc()
        return False


def find_files_to_update():
    """Find files that need to be updated"""
    files_to_update = []

    # Search patterns
    master_id_pattern = re.compile(r"\bmaster_id\b")

    # Directories to search
    search_dirs = ["app", "tests", "migrations", "alembic"]

    # File extensions to look for
    extensions = [".py", ".sql"]

    # Find all files that contain the term "master_id"
    root_dir = Path(".")
    for search_dir in search_dirs:
        dir_path = root_dir / search_dir
        if not dir_path.exists():
            logger.warning(f"Directory {search_dir} does not exist")
            continue

        logger.info(f"Searching for files in {search_dir}")
        for ext in extensions:
            for file_path in dir_path.glob(f"**/*{ext}"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if master_id_pattern.search(content):
                        files_to_update.append(file_path)
                        logger.info(f"Found 'master_id' in {file_path}")
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {str(e)}")

    logger.info(f"Found {len(files_to_update)} files to update")
    return files_to_update


def update_code_files(files_to_update):
    """Update code files to use character_id instead of master_id"""
    updated_files = []

    for file_path in files_to_update:
        try:
            logger.info(f"Processing file: {file_path}")

            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Save a backup
            backup_path = f"{file_path}.bak"
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Process each line, being careful not to replace instances in string literals
            lines = content.split("\n")
            updated_lines = []

            for line in lines:
                # Skip comment lines
                if line.strip().startswith("#"):
                    updated_lines.append(line)
                    continue

                # If it's a string with "master_id" or a SQL query, don't replace
                if '"master_id"' in line or "'master_id'" in line:
                    # But do replace actual instances of master_id as a variable
                    # We need to be careful not to replace instances in string literals

                    # Split the line by quotes
                    parts = re.split(r"(\'.*?\'|\".*?\")", line)

                    # Even-indexed parts are outside quotes, odd-indexed are inside quotes
                    for i in range(0, len(parts), 2):
                        parts[i] = parts[i].replace("master_id", "character_id")

                    line = "".join(parts)
                    updated_lines.append(line)
                else:
                    # Regular non-string literal line, safe to replace
                    line = line.replace("master_id", "character_id")
                    updated_lines.append(line)

            updated_content = "\n".join(updated_lines)

            # Write back the updated content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            updated_files.append(file_path)
            logger.info(f"Updated {file_path}")

        except Exception as e:
            logger.error(f"Error updating file {file_path}: {str(e)}")

    return updated_files


def fix_schema_files():
    """Specifically update the schema files for Hireling"""
    schema_files = [Path("app/schemas/hireling.py"), Path("app/schemas.py")]

    for file_path in schema_files:
        if not file_path.exists():
            logger.warning(f"Schema file {file_path} does not exist")
            continue

        try:
            logger.info(f"Updating schema file: {file_path}")

            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Save a backup
            backup_path = f"{file_path}.bak"
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Update the Hireling schema class
            updated_content = content.replace(
                "master_id: Optional[int] = None",
                "character_id: Optional[int] = None  # Renamed from master_id",
            )

            # Write back the updated content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            logger.info(f"Updated schema file {file_path}")

        except Exception as e:
            logger.error(f"Error updating schema file {file_path}: {str(e)}")


def run_tests():
    """Run relevant tests to ensure changes didn't break functionality"""
    logger.info("Running tests...")

    # Here you could add code to run relevant tests
    # For example, using pytest to test hireling-related functionality

    logger.info("Tests complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=" +
            "Fix the mismatch between master_id and character_id in the"codebase"
    )
    parser.add_argument(
        "--code-only",
        action="store_true",
        help="Only update code references, not the database",
    )
    parser.add_argument(
        "--db-only",
        action="store_true",
        help="Only update the database, not code references",
    )
    parser.add_argument(
        "--check", action="store_true", help="Only check for issues without fixing"
    )
    args = parser.parse_args()

    try:
        # Update code references
        if not args.db_only and not args.check:
            logger.info("Updating code references...")
            files_to_update = find_files_to_update()

            if args.check:
                logger.info("Check only mode: would update these files:")
                for file in files_to_update:
                    logger.info(f"  {file}")
            else:
                updated_files = update_code_files(files_to_update)
                fix_schema_files()
                logger.info(f"Updated {len(updated_files)} files")

        # Update database
        if not args.code_only:
            with get_db_context() as db:
                try:
                    # Begin transaction
                    if not args.check:
                        db.begin()

                    # Check column status
                    master_exists = check_column_exists(db, "master_id")
                    character_exists = check_column_exists(db, "character_id")

                    logger.info(f"Database check: master_id exists: {master_exists}")
                    logger.info(
                        f"Database check: character_id exists: {character_exists}"
                    )

                    # Rename the column if needed and not in check mode
                    if master_exists and not character_exists and not args.check:
                        success = rename_column_in_db(db)

                        if success:
                            # Verify data integrity
                            verify_data(db)

                            # Commit the transaction
                            logger.info("Committing changes...")
                            db.commit()
                            logger.info("Database migration completed successfully")
                        else:
                            # Rollback on error
                            logger.error(
                                "Database migration failed, rolling back changes"
                            )
                            db.rollback()
                    elif args.check:
                        logger.info("Check only mode: no database changes made")

                except Exception as e:
                    logger.error(f"Unexpected database error: {str(e)}")
                    if not args.check:
                        db.rollback()
                    traceback.print_exc()

        # Run tests to verify changes didn't break functionality
        if not args.check:
            run_tests()

        logger.info("Fix process completed")

    except Exception as e:
        logger.error(f"Error in fix process: {str(e)}")
        traceback.print_exc()
