from app.models.character import Character
from app.models.character_item import CharacterItem
from app.database import SessionLocal
import json

db = SessionLocal()

print("=== Character Inventory Migration Status Check ===")

# Check Characters with JSON inventory/equipment
chars = db.query(Character).all()
print(f"Total characters in database: {len(chars)}")

# Check the first three characters
for i, char in enumerate(chars[:3]):
    print(f"\nCharacter #{i+1}: {char.name} (ID: {char.id})")
    print(f"  Equipment (JSON): {json.dumps(char.equipment, indent=2)}")
    print(f"  Inventory (JSON): {json.dumps(char.inventory, indent=2)}")

# Check CharacterItem table
character_items = db.query(CharacterItem).all()
print(f"\nTotal items in CharacterItem table: {len(character_items)}")

# Show distribution of character items
char_item_counts = {}
for item in character_items:
    char_id = item.character_id
    if char_id not in char_item_counts:
        char_item_counts[char_id] = 0
    char_item_counts[char_id] += 1

print("\nItems per character:")
for char_id, count in char_item_counts.items():
    char = db.query(Character).filter(Character.id == char_id).first()
    char_name = char.name if char else "Unknown"
    print(f"  Character {char_name} (ID: {char_id}): {count} items")

# Check for characters with items but empty JSON
chars_with_items = db.query(Character).join(CharacterItem).distinct().all()
print(f"\nCharacters with entries in CharacterItem table: {len(chars_with_items)}")

# Check for empty JSON but items in CharacterItem
print("\nChecking for inconsistencies...")
for char in chars_with_items:
    items_count = db.query(CharacterItem).filter(CharacterItem.character_id == char.id).count()
    if (not char.inventory or len(char.inventory) == 0) and items_count > 0:
        print(f"  Character {char.name} has {items_count} items in CharacterItem but empty inventory JSON")
    if (not char.equipment or len(char.equipment) == 0) and items_count > 0:
        print(f"  Character {char.name} has {items_count} items in CharacterItem but empty equipment JSON")

db.close()
print("\nCheck completed.") 