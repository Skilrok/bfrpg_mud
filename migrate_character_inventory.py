#!/usr/bin/env python3
"""
Migration script to transfer character inventory data from JSON fields to CharacterItem table.
"""

import json
import logging
import traceback
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, ForeignKey, DateTime, text, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import text as sql_text

from app.database import get_db_context
from app.models import Character, Item, CharacterItem, CharacterRace, CharacterClass

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_enum_case_issues(db):
    """Fix case sensitivity issues in enum columns"""
    logger.info("Checking for case sensitivity issues in enum fields")
    
    try:
        # Use raw SQL to fetch characters without triggering ORM validation
        result = db.execute(sql_text("""
            SELECT id, race, character_class FROM characters
        """)).fetchall()
        
        # Process each character
        for row in result:
            char_id, race, char_class = row
            
            # Check if race needs fixing (lowercase race to match enum case)
            fixed_race = None
            if race and isinstance(race, str):
                for enum_value in CharacterRace:
                    if race.upper() == enum_value.value.upper():
                        fixed_race = enum_value.value
                        break
            
            # Check if class needs fixing
            fixed_class = None
            if char_class and isinstance(char_class, str):
                for enum_value in CharacterClass:
                    if char_class.upper() == enum_value.value.upper():
                        fixed_class = enum_value.value
                        break
            
            # Apply fixes if needed
            if fixed_race or fixed_class:
                update_fields = {}
                if fixed_race:
                    logger.info(f"Fixing character {char_id} race: '{race}' → '{fixed_race}'")
                    update_fields["race"] = fixed_race
                
                if fixed_class:
                    logger.info(f"Fixing character {char_id} class: '{char_class}' → '{fixed_class}'")
                    update_fields["character_class"] = fixed_class
                
                # Execute update without ORM validation
                if update_fields:
                    db.execute(
                        sql_text(f"""
                            UPDATE characters 
                            SET {', '.join([f"{k} = :{k}" for k in update_fields])} 
                            WHERE id = :id
                        """),
                        {**update_fields, "id": char_id}
                    )
                    
        # Commit changes
        db.commit()
        logger.info("Fixed enum case issues successfully")
        
    except Exception as e:
        logger.error(f"Error fixing enum case issues: {str(e)}")
        traceback.print_exc()
        db.rollback()
        return False
    
    return True

def migrate_character_inventory():
    """Migrate character inventory and equipment data from JSON to character_items table"""
    logger.info("Starting character inventory migration")
    
    # Get database session
    with get_db_context() as db:
        try:
            # Check if existing character items - if so, clear them to avoid duplicates
            existing_items = db.query(CharacterItem).count()
            if existing_items > 0:
                logger.warning(f"Found {existing_items} existing character items - clearing before migration")
                db.execute(sql_text("DELETE FROM character_items"))
                db.commit()
                logger.info("Cleared existing character items")
            
            # Check if the character_items table exists
            try:
                # Try to query the table
                db.query(CharacterItem).first()
                logger.info("CharacterItem table exists")
            except Exception as e:
                logger.error(f"CharacterItem table does not exist or cannot be queried: {str(e)}")
                logger.error("Please run the Alembic migration first: alembic upgrade a35b9c72e451")
                return False
            
            # Fix any enum case issues before proceeding
            logger.info("Fixing enum case issues before migration")
            if not fix_enum_case_issues(db):
                logger.error("Failed to fix enum case issues - aborting migration")
                return False
            
            # Get all characters using raw SQL to avoid ORM validation
            logger.info("Fetching characters from database")
            characters_raw = db.execute(sql_text("""
                SELECT id, name, inventory, equipment FROM characters
            """)).fetchall()
            
            logger.info(f"Found {len(characters_raw)} characters to migrate")
            
            total_characters = len(characters_raw)
            migrated_characters = 0
            total_items = 0
            
            # Process each character
            for char_row in characters_raw:
                char_id, char_name, inventory_json, equipment_json = char_row
                
                try:
                    # Parse JSON fields
                    try:
                        inventory = json.loads(inventory_json) if inventory_json and not isinstance(inventory_json, dict) else inventory_json or {}
                        equipment = json.loads(equipment_json) if equipment_json and not isinstance(equipment_json, dict) else equipment_json or {}
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON data for character {char_name} (ID: {char_id}) - skipping")
                        logger.warning(f"Inventory JSON: {inventory_json}")
                        logger.warning(f"Equipment JSON: {equipment_json}")
                        continue
                    
                    logger.info(f"Migrating inventory for character: {char_name} (ID: {char_id})")
                    logger.info(f"Equipment data: {equipment}")
                    
                    # Create a set to track which items we've processed
                    processed_items = set()
                    
                    # First, process inventory items
                    if isinstance(inventory, dict):
                        for item_id_str, item_data in inventory.items():
                            try:
                                item_id = int(item_id_str)
                                
                                # Check if item exists
                                item = db.query(Item).filter(Item.id == item_id).first()
                                if not item:
                                    logger.warning(f"Item ID {item_id} not found in database - skipping")
                                    continue
                                
                                # Check if the item is in equipment to determine if it's equipped
                                is_equipped = False
                                equip_slot = None
                                
                                # Check item_data first
                                if isinstance(item_data, dict):
                                    is_equipped = item_data.get("equipped", False)
                                    equip_slot = item_data.get("slot")
                                
                                # Check equipment dict as well to ensure we catch all equipped items
                                if isinstance(equipment, dict):
                                    for slot, eq_item_id in equipment.items():
                                        if eq_item_id == item_id:
                                            is_equipped = True
                                            equip_slot = slot
                                            break
                                
                                # Create new CharacterItem record
                                char_item = CharacterItem(
                                    character_id=char_id,
                                    item_id=item_id,
                                    quantity=item_data.get("quantity", 1) if isinstance(item_data, dict) else 1,
                                    is_equipped=is_equipped,
                                    equip_slot=equip_slot
                                )
                                
                                db.add(char_item)
                                processed_items.add(item_id)
                                total_items += 1
                                
                                logger.info(f"Added item {item_id} to character {char_name} (equipped: {is_equipped}, slot: {equip_slot})")
                                
                            except Exception as e:
                                logger.error(f"Error processing inventory item {item_id_str}: {str(e)}")
                                traceback.print_exc()
                    
                    # Now process equipment items that weren't in inventory
                    if isinstance(equipment, dict):
                        for slot, item_id in equipment.items():
                            try:
                                logger.info(f"Processing equipment item in slot {slot}: {item_id}")
                                
                                # Skip if we already processed this item
                                if item_id in processed_items:
                                    logger.info(f"Item {item_id} already processed from inventory")
                                    continue
                                
                                # Check if item exists
                                item = db.query(Item).filter(Item.id == item_id).first()
                                if not item:
                                    logger.warning(f"Equipment item ID {item_id} not found in database - skipping")
                                    continue
                                
                                # Create new CharacterItem record
                                char_item = CharacterItem(
                                    character_id=char_id,
                                    item_id=item_id,
                                    quantity=1,
                                    is_equipped=True,
                                    equip_slot=slot
                                )
                                
                                db.add(char_item)
                                total_items += 1
                                logger.info(f"Added equipment item {item_id} in slot {slot} to character {char_name}")
                                
                            except Exception as e:
                                logger.error(f"Error processing equipment item {item_id} in slot {slot}: {str(e)}")
                                traceback.print_exc()
                    
                    # Commit after each character
                    db.commit()
                    migrated_characters += 1
                    logger.info(f"Successfully migrated character {char_name}")
                    
                    # Verify the character immediately after migration
                    verify_character_migration(db, char_id, char_name, inventory, equipment)
                    
                except Exception as e:
                    logger.error(f"Error processing character {char_name} (ID: {char_id}): {str(e)}")
                    traceback.print_exc()
                    db.rollback()
                
            logger.info(f"Migration complete. Migrated {migrated_characters}/{total_characters} characters with {total_items} total items.")
            return True
            
        except Exception as e:
            logger.error(f"Error during migration: {str(e)}")
            traceback.print_exc()
            db.rollback()
            return False

def verify_character_migration(db, char_id, char_name, old_inventory, old_equipment):
    """Verify migration for a single character immediately after migration"""
    logger.info(f"Verifying migration for character {char_name} (ID: {char_id})")
    
    # Get new character items
    char_items = db.query(CharacterItem).filter(
        CharacterItem.character_id == char_id
    ).all()
    
    # Reconstruct inventory and equipment from character_items
    new_inventory = {}
    new_equipment = {}
    
    for char_item in char_items:
        # Add to new inventory
        new_inventory[str(char_item.item_id)] = {
            "item_id": char_item.item_id,
            "quantity": char_item.quantity,
            "equipped": char_item.is_equipped,
            "slot": char_item.equip_slot
        }
        
        # Add to new equipment if equipped
        if char_item.is_equipped and char_item.equip_slot:
            new_equipment[char_item.equip_slot] = char_item.item_id
    
    # Compare equipment
    equipment_issues = []
    if isinstance(old_equipment, dict):
        for slot, item_id in old_equipment.items():
            if slot not in new_equipment:
                equipment_issues.append(f"Slot {slot} missing for item {item_id}")
            elif new_equipment[slot] != item_id:
                equipment_issues.append(f"Item mismatch in slot {slot}: expected {item_id}, got {new_equipment[slot]}")
    
    if equipment_issues:
        logger.error(f"Equipment migration issues for {char_name}:")
        for issue in equipment_issues:
            logger.error(f"  - {issue}")
        logger.error(f"Old equipment: {old_equipment}")
        logger.error(f"New equipment: {new_equipment}")
        
        # Try to fix equipment issues
        logger.info(f"Attempting to fix equipment issues for {char_name}")
        
        # Get the item details for logging purposes
        item_names = {}
        for slot, item_id in old_equipment.items():
            item = db.query(Item).filter(Item.id == item_id).first()
            if item:
                item_names[slot] = f"{item.name} (ID: {item_id})"
            else:
                item_names[slot] = f"Unknown (ID: {item_id})"
                
        logger.info(f"Equipment details: {item_names}")
        
        for slot, item_id in old_equipment.items():
            if slot not in new_equipment or new_equipment[slot] != item_id:
                try:
                    # Check if item exists
                    item = db.query(Item).filter(Item.id == item_id).first()
                    if not item:
                        logger.warning(f"Cannot fix: Item {item_id} not found in database")
                        continue
                    
                    logger.info(f"Fixing equipment: {item.name} (ID: {item_id}) in slot {slot}")
                    
                    # Check if we already have this item in inventory but not equipped correctly
                    existing_item = db.query(CharacterItem).filter(
                        CharacterItem.character_id == char_id,
                        CharacterItem.item_id == item_id
                    ).first()
                    
                    if existing_item:
                        logger.info(f"Updating existing item {item_id} to be equipped in slot {slot}")
                        existing_item.is_equipped = True
                        existing_item.equip_slot = slot
                        db.add(existing_item)
                    else:
                        # Create new item
                        logger.info(f"Creating new equipped item {item_id} in slot {slot}")
                        char_item = CharacterItem(
                            character_id=char_id,
                            item_id=item_id,
                            quantity=1,
                            is_equipped=True,
                            equip_slot=slot
                        )
                        db.add(char_item)
                    
                    db.commit()
                    logger.info(f"Fixed equipment issue for slot {slot}")
                    
                except Exception as e:
                    logger.error(f"Error fixing equipment issue: {str(e)}")
                    traceback.print_exc()
                    db.rollback()
        
        # Double-check that the fixes worked
        char_items = db.query(CharacterItem).filter(
            CharacterItem.character_id == char_id
        ).all()
        
        new_equipment = {}
        for char_item in char_items:
            if char_item.is_equipped and char_item.equip_slot:
                new_equipment[char_item.equip_slot] = char_item.item_id
        
        all_fixed = True
        for slot, item_id in old_equipment.items():
            if slot not in new_equipment or new_equipment[slot] != item_id:
                all_fixed = False
                logger.error(f"Still missing/wrong after fix: {slot} - {item_id}")
        
        if all_fixed:
            logger.info(f"All equipment issues fixed for {char_name}")
        else:
            logger.error(f"Failed to fix all equipment issues for {char_name}")
            logger.error(f"Original equipment: {old_equipment}")
            logger.error(f"Current equipment: {new_equipment}")
            
            # Last resort: force direct update of equipment through SQL
            try:
                logger.info("Attempting direct SQL fix for equipment issues")
                for slot, item_id in old_equipment.items():
                    if slot not in new_equipment or new_equipment[slot] != item_id:
                        # Delete any existing entries for this slot
                        db.execute(sql_text("""
                            DELETE FROM character_items 
                            WHERE character_id = :char_id 
                            AND is_equipped = 1 
                            AND equip_slot = :slot
                        """), {"char_id": char_id, "slot": slot})
                        
                        # Insert new entry with correct values
                        db.execute(sql_text("""
                            INSERT INTO character_items (character_id, item_id, quantity, is_equipped, equip_slot)
                            VALUES (:char_id, :item_id, 1, 1, :slot)
                        """), {"char_id": char_id, "item_id": item_id, "slot": slot})
                        
                db.commit()
                logger.info("Direct SQL fix applied")
                
                # Final verification
                char_items = db.query(CharacterItem).filter(
                    CharacterItem.character_id == char_id,
                    CharacterItem.is_equipped == True
                ).all()
                
                fixed_equipment = {}
                for char_item in char_items:
                    if char_item.equip_slot:
                        fixed_equipment[char_item.equip_slot] = char_item.item_id
                
                logger.info(f"Final equipment state: {fixed_equipment}")
                
            except Exception as e:
                logger.error(f"Direct SQL fix failed: {str(e)}")
                traceback.print_exc()
                db.rollback()
    else:
        logger.info(f"Equipment migration successful for {char_name}")
        
    # Compare inventory sizes (just a sanity check)
    if isinstance(old_inventory, dict) and len(old_inventory) > len(new_inventory):
        logger.warning(f"Inventory size mismatch - old: {len(old_inventory)}, new: {len(new_inventory)}")
        
        # List missing items
        missing_items = []
        for item_id_str in old_inventory:
            if item_id_str not in new_inventory:
                item_id = int(item_id_str)
                item = db.query(Item).filter(Item.id == item_id).first()
                if item:
                    missing_items.append(f"{item.name} (ID: {item_id})")
                else:
                    missing_items.append(f"Unknown (ID: {item_id})")
        
        if missing_items:
            logger.warning(f"Missing inventory items: {', '.join(missing_items)}")
    
    return True

def verify_migration():
    """Verify that the migration was successful by comparing old and new data"""
    logger.info("Verifying migration results")
    
    with get_db_context() as db:
        try:
            # Get all characters using raw SQL to avoid ORM validation
            characters_raw = db.execute(sql_text("""
                SELECT id, name, inventory, equipment FROM characters
            """)).fetchall()
            
            total_success = 0
            total_failure = 0
            failed_characters = []
            
            for char_row in characters_raw:
                char_id, char_name, inventory_json, equipment_json = char_row
                
                # Parse JSON fields
                try:
                    old_inventory = json.loads(inventory_json) if inventory_json and not isinstance(inventory_json, dict) else inventory_json or {}
                    old_equipment = json.loads(equipment_json) if equipment_json and not isinstance(equipment_json, dict) else equipment_json or {}
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON data for character {char_name} (ID: {char_id})")
                    logger.warning(f"Inventory JSON: {inventory_json}")
                    logger.warning(f"Equipment JSON: {equipment_json}")
                    continue
                
                # Get new character items
                char_items = db.query(CharacterItem).filter(
                    CharacterItem.character_id == char_id
                ).all()
                
                # Reconstruct inventory and equipment from character_items
                new_inventory = {}
                new_equipment = {}
                
                for char_item in char_items:
                    # Add to new inventory
                    new_inventory[str(char_item.item_id)] = {
                        "item_id": char_item.item_id,
                        "quantity": char_item.quantity,
                        "equipped": char_item.is_equipped,
                        "slot": char_item.equip_slot
                    }
                    
                    # Add to new equipment if equipped
                    if char_item.is_equipped and char_item.equip_slot:
                        new_equipment[char_item.equip_slot] = char_item.item_id
                
                # Compare old and new
                inventory_match = True
                equipment_match = True
                
                # Check if all old inventory items are in new inventory
                if isinstance(old_inventory, dict):
                    for item_id_str, item_data in old_inventory.items():
                        if item_id_str not in new_inventory:
                            inventory_match = False
                            logger.warning(f"Item {item_id_str} missing from new inventory for character {char_name}")
                        else:
                            # Check item details
                            new_item = new_inventory[item_id_str]
                            if new_item["quantity"] != item_data.get("quantity", 1) or \
                               new_item["equipped"] != item_data.get("equipped", False) or \
                               new_item["slot"] != item_data.get("slot"):
                                inventory_match = False
                                logger.warning(f"Item {item_id_str} details mismatch for character {char_name}")
                                logger.warning(f"  Old: {item_data}")
                                logger.warning(f"  New: {new_item}")
                
                # Check if all old equipment items are in new equipment
                if isinstance(old_equipment, dict):
                    for slot, item_id in old_equipment.items():
                        if slot not in new_equipment or new_equipment[slot] != item_id:
                            equipment_match = False
                            logger.warning(f"Equipment slot {slot} mismatch for character {char_name}")
                            
                            # Get item name for better logging
                            item = db.query(Item).filter(Item.id == item_id).first()
                            item_name = item.name if item else "Unknown"
                            
                            logger.warning(f"  Expected: {slot} -> {item_name} (ID: {item_id})")
                            if slot in new_equipment:
                                new_item = db.query(Item).filter(Item.id == new_equipment[slot]).first()
                                new_item_name = new_item.name if new_item else "Unknown"
                                logger.warning(f"  Actual: {slot} -> {new_item_name} (ID: {new_equipment[slot]})")
                            else:
                                logger.warning(f"  Actual: {slot} -> Not equipped")
                
                if inventory_match and equipment_match:
                    logger.info(f"Verification successful for character {char_name} (ID: {char_id})")
                    total_success += 1
                else:
                    logger.error(f"Verification failed for character {char_name} (ID: {char_id})")
                    failed_characters.append(char_name)
                    
                    # Log detailed differences
                    if not inventory_match:
                        logger.error(f"Old inventory: {old_inventory}")
                        logger.error(f"New inventory: {new_inventory}")
                    if not equipment_match:
                        logger.error(f"Old equipment: {old_equipment}")
                        logger.error(f"New equipment: {new_equipment}")
                        
                        # Try to auto-fix the equipment issues
                        verify_character_migration(db, char_id, char_name, old_inventory, old_equipment)
                        
                    total_failure += 1
            
            logger.info(f"Verification complete: {total_success} successful, {total_failure} failed")
            
            if total_failure > 0:
                logger.warning(f"Failed characters: {', '.join(failed_characters)}")
                
                # One last verification attempt after fixes
                if verify_again():
                    logger.info("All issues resolved after auto-fixes")
                    return True
                    
                logger.warning("There were verification failures that couldn't be auto-fixed.")
                return False
            return True
            
        except Exception as e:
            logger.error(f"Error during verification: {str(e)}")
            traceback.print_exc()
            return False
            
            
def verify_again():
    """Perform one final verification pass after fixes"""
    logger.info("Performing final verification pass")
    
    with get_db_context() as db:
        try:
            # Get all characters using raw SQL to avoid ORM validation
            characters_raw = db.execute(sql_text("""
                SELECT id, name, inventory, equipment FROM characters
            """)).fetchall()
            
            all_success = True
            
            for char_row in characters_raw:
                char_id, char_name, inventory_json, equipment_json = char_row
                
                # Parse JSON fields
                try:
                    old_equipment = json.loads(equipment_json) if equipment_json and not isinstance(equipment_json, dict) else equipment_json or {}
                except json.JSONDecodeError:
                    continue
                
                if not isinstance(old_equipment, dict):
                    continue
                    
                # We only care about equipment for the final check
                char_items = db.query(CharacterItem).filter(
                    CharacterItem.character_id == char_id,
                    CharacterItem.is_equipped == True
                ).all()
                
                new_equipment = {}
                for char_item in char_items:
                    if char_item.equip_slot:
                        new_equipment[char_item.equip_slot] = char_item.item_id
                
                # Check for missing equipment
                for slot, item_id in old_equipment.items():
                    if slot not in new_equipment or new_equipment[slot] != item_id:
                        all_success = False
                        logger.error(f"Still missing equipment for {char_name}: {slot} -> {item_id}")
            
            return all_success
            
        except Exception as e:
            logger.error(f"Error during final verification: {str(e)}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate character inventory data to the new table structure")
    parser.add_argument("--verify", action="store_true", help="Verify migration results without performing migration")
    args = parser.parse_args()
    
    if args.verify:
        verify_migration()
    else:
        if migrate_character_inventory():
            verify_migration() 