from app.models.character import Character
from app.models.character_item import CharacterItem
from app.models.item import Item
from app.database import SessionLocal

db = SessionLocal()

print("=== Character Armor Class Calculation Check ===")

# Check character 20
char = db.query(Character).filter(Character.id == 20).first()
print(f"Character ID 20: {char.name}, AC: {char.armor_class}")
print(f"Race: {char.race}, Class: {char.character_class}")
print(f"Dexterity: {char.dexterity}")

# Get dexterity modifier
dex_score = char.dexterity
if dex_score == 3:
    dex_mod = -3
elif 4 <= dex_score <= 5:
    dex_mod = -2
elif 6 <= dex_score <= 8:
    dex_mod = -1
elif 9 <= dex_score <= 12:
    dex_mod = 0
elif 13 <= dex_score <= 15:
    dex_mod = 1
elif 16 <= dex_score <= 17:
    dex_mod = 2
elif dex_score == 18:
    dex_mod = 3
else:
    dex_mod = 0

print(f"Dexterity modifier: {dex_mod}")

# Check the character's equipped items
print("\nEquipped items from CharacterItem table:")
items = db.query(CharacterItem).filter(
    CharacterItem.character_id == 20, 
    CharacterItem.is_equipped == True
).all()

base_ac = 10
shield_bonus = 0

for ci in items:
    item = db.query(Item).filter(Item.id == ci.item_id).first()
    print(f" - {item.name} (ID: {item.id}) in slot {ci.equip_slot}")
    print(f"   Type: {item.item_type}")
    print(f"   AC bonus (column): {item.ac_bonus}")
    print(f"   Armor class (column): {item.armor_class}")
    print(f"   Properties: {item.properties}")
    
    # Calculate AC based on equipped items
    if item.item_type.value == "armor":
        # Check if it's in the body slot or just marked as equipped
        if ci.equip_slot == "body" or (ci.is_equipped and not ci.equip_slot):
            print(f"   This is armor and is equipped!")
            if item.armor_class is not None:
                base_ac = item.armor_class
                print(f"   Using armor AC from armor_class column: {base_ac}")
            elif item.ac_bonus is not None:
                base_ac = item.ac_bonus
                print(f"   Using armor AC from ac_bonus column: {base_ac}")
            elif item.properties and "armor_class" in item.properties:
                base_ac = item.properties["armor_class"]
                print(f"   Using armor AC from properties (armor_class): {base_ac}")
            elif item.properties and "ac_bonus" in item.properties:
                base_ac = item.properties["ac_bonus"]
                print(f"   Using armor AC from properties (ac_bonus): {base_ac}")
    
    if item.item_type.value == "shield" and (ci.equip_slot == "off_hand" or (ci.is_equipped and not ci.equip_slot)):
        print(f"   This is a shield and is equipped!")
        if item.ac_bonus is not None:
            shield_bonus = item.ac_bonus
            print(f"   Using shield bonus from ac_bonus column: {shield_bonus}")
        elif item.properties and "ac_bonus" in item.properties:
            shield_bonus = item.properties["ac_bonus"]
            print(f"   Using shield bonus from properties: {shield_bonus}")

# Compare JSON equipment with CharacterItem table
print("\nEquipment from JSON property:")
for slot, item_id in char.equipment.items():
    item = db.query(Item).filter(Item.id == item_id).first()
    print(f" - Slot {slot}: {item.name} (ID: {item.id})")

# Calculate expected AC
expected_ac = base_ac + shield_bonus + dex_mod
print(f"\nExpected AC calculation:")
print(f"Base AC: {base_ac}")
print(f"Shield bonus: {shield_bonus}")
print(f"Dexterity modifier: {dex_mod}")
print(f"Expected total AC: {expected_ac}")
print(f"Actual AC in database: {char.armor_class}")

if expected_ac == char.armor_class:
    print("\nAC calculation is CORRECT! ✓")
else:
    print("\nAC calculation is INCORRECT! ✗")

# Update character AC if needed
if expected_ac != char.armor_class:
    response = input("Would you like to update the character's AC to the expected value? (y/n): ")
    if response.lower() == 'y':
        char.armor_class = expected_ac
        db.add(char)
        db.commit()
        print(f"Updated character AC to {expected_ac}")
    else:
        print("No changes made.")

# Create a fix script for fixing this issue for all characters
print("\n=== Sample Fix Script ===")
print("""
def fix_character_ac_calculations():
    \"\"\"Fix armor class calculations for all characters based on equipped items\"\"\"
    with get_db_context() as db:
        characters = db.query(Character).all()
        for character in characters:
            # Get equipped items
            items = db.query(CharacterItem).filter(
                CharacterItem.character_id == character.id,
                CharacterItem.is_equipped == True
            ).all()
            
            # Start with base AC of 10
            base_ac = 10
            shield_bonus = 0
            
            # Calculate dexterity modifier
            dex_mod = get_ability_modifier(character.dexterity)
            
            # Process equipped items
            for ci in items:
                item = db.query(Item).filter(Item.id == ci.item_id).first()
                if not item:
                    continue
                    
                # Handle armor
                if item.item_type.value == "armor":
                    # Check if it's in the body slot or just marked as equipped
                    if ci.equip_slot == "body" or (ci.is_equipped and not ci.equip_slot):
                        if item.armor_class is not None:
                            base_ac = item.armor_class
                        elif item.ac_bonus is not None:
                            base_ac = item.ac_bonus
                        elif item.properties and "armor_class" in item.properties:
                            base_ac = item.properties["armor_class"]
                        elif item.properties and "ac_bonus" in item.properties:
                            base_ac = item.properties["ac_bonus"]
                
                # Handle shield
                if item.item_type.value == "shield" and (ci.equip_slot == "off_hand" or (ci.is_equipped and not ci.equip_slot)):
                    if item.ac_bonus is not None:
                        shield_bonus = item.ac_bonus
                    elif item.properties and "ac_bonus" in item.properties:
                        shield_bonus = item.properties["ac_bonus"]
            
            # Calculate new AC
            new_ac = base_ac + shield_bonus + dex_mod
            
            # Update if different
            if character.armor_class != new_ac:
                print(f"Updating {character.name} AC from {character.armor_class} to {new_ac}")
                character.armor_class = new_ac
                db.add(character)
        
        # Commit all changes
        db.commit()
        print("Armor class calculations fixed for all characters")
""")

db.close() 