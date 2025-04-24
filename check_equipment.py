import json
import sqlite3

# Connect to the database
conn = sqlite3.connect("dev.db")
cursor = conn.cursor()

# Query the character
cursor.execute(
    'SELECT id, name, inventory, equipment FROM characters WHERE name = "EquipmentTest"'
)
result = cursor.fetchone()

if result:
    char_id, name, inventory_json, equipment_json = result

    print(f"Character: {name}")

    # Parse JSON data
    inventory = json.loads(inventory_json) if inventory_json else {}
    equipment = json.loads(equipment_json) if equipment_json else {}

    print("\nOriginal Inventory:")
    print(json.dumps(inventory, indent=2))

    print("\nOriginal Equipment:")
    print(json.dumps(equipment, indent=2))

    # Look up items in inventory
    print("\nOriginal Inventory Items:")
    for item_id, item_data in inventory.items():
        cursor.execute("SELECT name, item_type FROM items WHERE id = ?", (item_id,))
        item_result = cursor.fetchone()
        if item_result:
            item_name, item_type = item_result
            print(f"  - {item_name} (ID: {item_id}, Type: {item_type})")
            print(
                f"    Status: {'Equipped' if item_data.get('equipped') else 'Not equipped'}, Slot: {item_data.get('slot')}"
            )

    # Add shield to inventory
    shield_id = "80"
    print("\nAdding Shield (ID: 80) to inventory...")

    # Create new inventory entry for shield
    inventory[shield_id] = {
        "item_id": 80,
        "quantity": 1,
        "equipped": False,
        "slot": None,
    }

    # Update character inventory in database
    inventory_json = json.dumps(inventory)
    cursor.execute(
        "UPDATE characters SET inventory = ? WHERE id = ?", (inventory_json, char_id)
    )
    conn.commit()

    print("Shield added to inventory.")

    # Query the updated character data
    cursor.execute(
        "SELECT inventory, equipment FROM characters WHERE id = ?", (char_id,)
    )
    updated_result = cursor.fetchone()
    updated_inventory_json, updated_equipment_json = updated_result

    # Parse updated JSON data
    updated_inventory = json.loads(updated_inventory_json)
    updated_equipment = json.loads(updated_equipment_json)

    print("\nUpdated Inventory:")
    print(json.dumps(updated_inventory, indent=2))

    print("\nUpdated Inventory Items:")
    for item_id, item_data in updated_inventory.items():
        cursor.execute("SELECT name, item_type FROM items WHERE id = ?", (item_id,))
        item_result = cursor.fetchone()
        if item_result:
            item_name, item_type = item_result
            print(f"  - {item_name} (ID: {item_id}, Type: {item_type})")
            print(
                f"    Status: {'Equipped' if item_data.get('equipped') else 'Not equipped'}, Slot: {item_data.get('slot')}"
            )
else:
    print("Character 'EquipmentTest' not found in database.")

# Search for shield items
print("\nSearching for shield items:")
cursor.execute(
    "SELECT id, name, item_type FROM items WHERE name LIKE '%Shield%' OR item_type = 'SHIELD'"
)
shields = cursor.fetchall()

if shields:
    for shield in shields:
        shield_id, shield_name, shield_type = shield
        print(f"  - {shield_name} (ID: {shield_id}, Type: {shield_type})")
else:
    print("No shield items found in database.")

# Close the connection
conn.close()
