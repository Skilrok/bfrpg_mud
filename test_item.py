from app import models
from app.database import get_db_context

# Use the context manager properly
with get_db_context() as db:
    # Get all armor items
    armors = db.query(models.Item).filter(models.Item.item_type == 'armor').all()
    
    print(f"Found {len(armors)} armor items")
    
    # Print details of each armor
    for armor in armors:
        print(f"\nArmor: {armor.name}")
        print(f"  - item_type: {armor.item_type}")
        print(f"  - armor_class: {armor.armor_class}")
        print(f"  - properties: {armor.properties}")
        
        # Check if the armor has the correct AC properties
        if armor.properties:
            if "ac_bonus" in armor.properties:
                print(f"  - ac_bonus: {armor.properties['ac_bonus']}")
            elif "armor_class" in armor.properties:
                print(f"  - armor_class from properties: {armor.properties['armor_class']}")
            else:
                print("  - No AC value in properties!")
    
    # Get all shields
    shields = db.query(models.Item).filter(models.Item.item_type == 'shield').all()
    
    print(f"\nFound {len(shields)} shield items")
    
    # Print details of each shield
    for shield in shields:
        print(f"\nShield: {shield.name}")
        print(f"  - item_type: {shield.item_type}")
        print(f"  - armor_class: {shield.armor_class}")
        print(f"  - properties: {shield.properties}")
        
        # Check if the shield has the correct AC properties
        if shield.properties:
            if "ac_bonus" in shield.properties:
                print(f"  - ac_bonus: {shield.properties['ac_bonus']}")
            else:
                print("  - No ac_bonus in properties!") 