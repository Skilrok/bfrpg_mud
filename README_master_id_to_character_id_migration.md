# Master ID to Character ID Migration

## Summary

This migration fixes the inconsistency between the code and database related to the hireling-character relationship. Previously, the code referred to the relationship as `character_id` but the database column was named `master_id`, causing confusion and potential bugs.

## Changes Made

1. **Database Schema Update**: Renamed the `master_id` column in the `hirelings` table to `character_id` to match the model.

2. **Code References Update**: Updated all code references from `master_id` to `character_id` in:
   - Schemas (`app/schemas/hireling.py`, `app/schemas.py`)
   - Routers (`app/routers/hirelings.py`)
   - Tests (`tests/factories.py`, `tests/test_hirelings.py`)
   - Migrations (`migrations/versions/...`)

3. **Documentation**: Created this README to document the changes.

## Migration Scripts

Two scripts were created to facilitate this migration:

1. `rename_hireling_column.py`: A simple script to rename the database column.
2. `fix_hireling_master_character_relationship.py`: A comprehensive script that:
   - Renames the database column
   - Updates all code references
   - Verifies data integrity

## Verification

The changes were verified using the `check_character_hireling_relationship.py` script, which confirms:
- The database schema now has `character_id` and not `master_id`
- Character-hireling relationships can be queried correctly
- All code operates on the correct column name

## Why This Fix Was Needed

The mismatch between code and database column names caused confusion and potential bugs:
- The model (`app/models/hireling.py`) defined the column as `character_id`
- The database had the column as `master_id`
- Some parts of the code used `master_id` while others used `character_id`

This migration ensures consistency across the entire codebase.

## Implementation Notes

The migration used a SQLite-compatible approach:
1. Create a new table with the updated schema
2. Copy data from the old table to the new one
3. Drop the old table
4. Rename the new table to the original name

This approach ensures data integrity during the migration process.

## Related Issues

This migration resolves issues related to the hireling-character relationship naming inconsistency, which could have led to hard-to-debug errors in character management functionality.
