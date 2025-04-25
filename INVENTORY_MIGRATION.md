# Inventory Migration Guide

This guide details the migration from the JSON-based inventory system to a relational database model using the `CharacterItem` table.

## Migration Process

### 1. Pre-migration Steps

1. **Backup your database** before starting the migration process.
   ```bash
   # For SQLite
   cp your_database.db your_database.db.backup
   
   # For PostgreSQL
   pg_dump -U your_user -d your_database > database_backup.sql
   ```

2. **Update your codebase** with the new files and changes:
   - New `CharacterItem` model
   - Updated schemas
   - Updated API endpoints
   - Character model with compatibility properties

### 2. Database Migration

1. **Create the CharacterItem table** by running the Alembic migration:
   ```bash
   alembic upgrade a35b9c72e451
   ```

2. **Migrate the data** from JSON columns to the new table structure:
   ```bash
   python migrate_character_inventory.py
   ```

3. **Verify the migration** was successful:
   ```bash
   python migrate_character_inventory.py --verify
   ```

4. **Remove the redundant columns** by running the second Alembic migration:
   ```bash
   alembic upgrade b92c7e53a612
   ```

## Common Issues and Solutions

### Missing Items After Migration

If items appear to be missing after migration:

1. Check the migration logs for errors related to specific characters or items.
2. Run the verification script with debug logging enabled:
   ```bash
   LOGLEVEL=DEBUG python migrate_character_inventory.py --verify
   ```
3. Look for any JSON parsing issues or invalid data in the original inventory.

### Equipment Not Properly Equipped

If equipment items are not showing as equipped:

1. Verify the slot names are consistent between old and new data.
2. Check if any items were unequipped due to validation failures.
3. Run manual fixes using the SQL console if needed:
   ```sql
   UPDATE character_items 
   SET is_equipped = 1, equip_slot = 'main_hand' 
   WHERE character_id = ? AND item_id = ?;
   ```

### Database Constraints Violations

If you encounter unique constraint violations:

1. Verify there aren't duplicate entries for the same character and slot.
2. Check the unique constraint on equipment slots:
   ```sql
   SELECT character_id, equip_slot, COUNT(*) 
   FROM character_items 
   WHERE is_equipped = 1 AND equip_slot IS NOT NULL
   GROUP BY character_id, equip_slot
   HAVING COUNT(*) > 1;
   ```

## Accessing Character Inventory

### Using the ORM Relationship (Recommended)

```python
# Get a character's inventory items
character_items = db.query(models.CharacterItem).filter(
    models.CharacterItem.character_id == character_id
).all()

# Get equipped items
equipped_items = db.query(models.CharacterItem).filter(
    models.CharacterItem.character_id == character_id,
    models.CharacterItem.is_equipped == True
).all()

# Check if a character has a specific item
has_item = db.query(models.CharacterItem).filter(
    models.CharacterItem.character_id == character_id,
    models.CharacterItem.item_id == item_id
).first() is not None
```

### Using Backward-Compatible Properties

For code that hasn't been updated to use the new model directly:

```python
# Get inventory in legacy format
inventory = character.inventory  # Returns dict in old format

# Get equipment in legacy format
equipment = character.equipment  # Returns dict in old format

# Update inventory
character.inventory = new_inventory  # Updates CharacterItem entries
db.commit()
```

## Rollback Procedure

If you need to roll back the migration:

1. Restore from your database backup.
2. Alternatively, if you can't restore from backup, run the downgrade migrations:
   ```bash
   alembic downgrade a35b9c72e451  # To keep the items table but restore JSON columns
   ```

3. If you had run the data migration and need to roll back changes, there's no automated rollback. You'll need to restore from backup.

## Performance Considerations

- The new model provides better query performance but joins may be needed where simple JSON access was used before.
- Use eager loading for item details when querying character items:
  ```python
  from sqlalchemy.orm import joinedload
  
  # Fetch character items with item details in one query
  character_items = db.query(models.CharacterItem).options(
      joinedload(models.CharacterItem.item)
  ).filter(
      models.CharacterItem.character_id == character_id
  ).all()
  ```

- For large inventory operations, consider using bulk operations:
  ```python
  from sqlalchemy.dialects.postgresql import insert
  
  # Bulk insert example (PostgreSQL)
  items_to_add = [
      {"character_id": character_id, "item_id": item_id, "quantity": 1}
      for item_id in item_ids
  ]
  
  stmt = insert(models.CharacterItem).values(items_to_add)
  # Use on_conflict_do_update for upsert operations
  ``` 