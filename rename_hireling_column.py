#!/usr/bin/env python3
"""
Script to rename the 'master_id' column to 'character_id' in the hirelings table.
"""

import logging
import traceback
from sqlalchemy import text

from app.database import get_db_context
from app.models.hireling import Hireling

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


def rename_column(db):
    """Rename the master_id column to character_id in the hirelings table"""
    try:
        # Check if master_id exists and character_id doesn't
        master_exists = check_column_exists(db, "master_id")
        character_exists = check_column_exists(db, "character_id")
        
        if not master_exists:
            logger.error("Column 'master_id' doesn't exist in the hirelings table")
            return False
            
        if character_exists:
            logger.warning("Column 'character_id' already exists in the hirelings table")
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
            column_defs.append(f"{col_name} {col_type} {not_null} {default} {pk}".strip())
        
        # Create a new table with the updated schema
        create_table_query = text(f"""
        CREATE TABLE hirelings_new (
            {", ".join(column_defs)}
        )
        """)
        
        # Copy data from old table to new table, mapping master_id to character_id
        old_cols_str = ", ".join(old_columns)
        new_cols_str = ", ".join(new_columns)
        
        copy_data_query = text(f"""
        INSERT INTO hirelings_new ({new_cols_str})
        SELECT {old_cols_str} FROM hirelings
        """)
        
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


def update_foreign_keys():
    """Update foreign key constraints if needed"""
    # This would be needed in a system with proper foreign key constraints
    # For SQLite, the constraints may need to be recreated
    pass


def verify_data(db):
    """Verify data integrity after the migration"""
    try:
        # Count all hirelings
        count_query = text("SELECT COUNT(*) FROM hirelings")
        count = db.execute(count_query).scalar()
        logger.info(f"Total hirelings after migration: {count}")
        
        # Check for any character relationships
        related_query = text("SELECT COUNT(*) FROM hirelings WHERE character_id IS NOT NULL")
        related_count = db.execute(related_query).scalar()
        logger.info(f"Hirelings with character relationships: {related_count}")
        
        # Sample a few records
        sample_query = text("SELECT id, name, character_id FROM hirelings LIMIT 5")
        samples = db.execute(sample_query).fetchall()
        logger.info("Sample hireling records:")
        for sample in samples:
            logger.info(f"  ID: {sample[0]}, Name: {sample[1]}, Character ID: {sample[2]}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error verifying data: {str(e)}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    with get_db_context() as db:
        try:
            # Begin transaction
            db.begin()
            
            # Rename the column
            success = rename_column(db)
            
            if success:
                # Verify data integrity
                verify_data(db)
                
                # Commit the transaction
                logger.info("Committing changes...")
                db.commit()
                logger.info("Migration completed successfully")
            else:
                # Rollback on error
                logger.error("Migration failed, rolling back changes")
                db.rollback()
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            db.rollback()
            traceback.print_exc() 