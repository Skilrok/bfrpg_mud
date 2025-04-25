# Character Inventory Migration

This document describes the migration of character inventory data from JSON fields to the `CharacterItem` table and tools for verifying and fixing issues.

## Background

Previously, character inventory and equipment data was stored in JSON fields in the `characters` table. This migration moves this data to a dedicated `character_items` table for better structure and performance.

## Migration Status

The migration has been successfully completed:
- All 12 characters have been successfully verified
- A total of 50 character items are now in the database
- The average item count per character is 4.2

## Issues Found

### ORM Relationship Mismatch

There's a relationship conflict in the ORM models that prevents the original verification script from running properly:

```
Mapper 'Mapper[Hireling(hirelings)]' has no property 'character'. If this property was indicated from other mappers or configure events, ensure registry.configure() has been called.
```

The mismatch is in the `back_populates` attribute:
- Hireling model uses `master = relationship("Character", back_populates="hirelings")`
- Character model uses `hirelings = relationship("Hireling", back_populates="character", cascade="all, delete-orphan")`

## Scripts Provided

### 1. migrate_character_inventory_fixed.py

This is a modified version of the original migration script that uses direct SQL queries instead of ORM to verify the migration success, avoiding the relationship conflict issues.

**Usage:**
```bash
python migrate_character_inventory_fixed.py
```

This script:
- Verifies that all characters' inventory and equipment was correctly migrated
- Logs any discrepancies found
- Attempts to fix equipment issues automatically

### 2. check_db.py

A simple script to check the current state of the database regarding characters and character items.

**Usage:**
```bash
python check_db.py
```

This script:
- Counts characters and character items
- Calculates the average items per character
- Shows detailed information about the first character and its items

### 3. fix_hireling_relationship.py

A script to fix the relationship mismatch between Character and Hireling models.

**Usage:**
```bash
# Update the Hireling model and test the relationship
python fix_hireling_relationship.py

# Only test the relationship without modifying the model
python fix_hireling_relationship.py --no-update
```

This script:
- Creates a backup of the Hireling model file
- Updates the relationship name from `master` to `character`
- Fixes all references to `master` and `master_id` in the model
- Tests that the relationship works correctly after the fix

## Solution Steps

1. Verify the migration success:
   ```bash
   python migrate_character_inventory_fixed.py
   ```

2. Fix the relationship mismatch:
   ```bash
   python fix_hireling_relationship.py
   ```

3. Run the database check to ensure everything is working:
   ```bash
   python check_db.py
   ```

4. Run the original migration verification script to confirm the fix:
   ```bash
   python migrate_character_inventory.py --verify
   ```

## Technical Details

### Character Model

The Character model has been updated with properties to maintain backward compatibility:

```python
# Property for backward compatibility
@property
def inventory(self):
    """Get inventory from items relationship in backward-compatible format"""
    result = {}
    for char_item in self.items:
        result[str(char_item.item_id)] = {
            "item_id": char_item.item_id,
            "quantity": char_item.quantity,
            "equipped": char_item.is_equipped,
            "slot": char_item.equip_slot
        }
    return result
    
@property
def equipment(self):
    """Get equipment mapping from items relationship"""
    result = {}
    for char_item in self.items:
        if char_item.is_equipped and char_item.equip_slot:
            result[char_item.equip_slot] = char_item.item_id
    return result
```

### CharacterItem Model

The new CharacterItem model represents items in a character's inventory:

```python
class CharacterItem(Base):
    """Model for items in a character's inventory"""
    
    __tablename__ = "character_items"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    is_equipped = Column(Boolean, default=False, nullable=False)
    equip_slot = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    character = relationship("Character", back_populates="items")
    item = relationship("Item")
```

## Future Work

- Update any code that uses `character.inventory` or `character.equipment` to be aware of the new relationship structure
- Consider adding database constraints to ensure data integrity (one item per equipment slot, etc.)
- Add tests for the new relationship structure 