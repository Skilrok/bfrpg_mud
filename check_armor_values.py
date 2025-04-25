from app import models
from app.database import get_db_context

print("Checking armor values in the database...")

with get_db_context() as db:
    # Get Chain Mail armor
    chain_mail = db.query(models.Item).filter(models.Item.name == "Chain Mail").first()

    if chain_mail:
        print(f"\nChain Mail:")
        print(f"  - item_type: {chain_mail.item_type}")
        print(f"  - armor_class: {chain_mail.armor_class}")
        print(f"  - properties: {chain_mail.properties}")

        if chain_mail.properties:
            if "armor_class" in chain_mail.properties:
                print(
                    f"  - armor_class from properties: {chain_mail.properties['armor_class']}"
                )
            elif "base_ac" in chain_mail.properties:
                print(
                    f"  - base_ac from properties: {chain_mail.properties['base_ac']}"
                )
    else:
        print("Chain Mail not found in database")

    # Get Shield
    shield = db.query(models.Item).filter(models.Item.name == "Shield").first()

    if shield:
        print(f"\nShield:")
        print(f"  - item_type: {shield.item_type}")
        print(f"  - armor_class: {shield.armor_class}")
        print(f"  - properties: {shield.properties}")

        if shield.properties:
            if "ac_bonus" in shield.properties:
                print(f"  - ac_bonus from properties: {shield.properties['ac_bonus']}")
    else:
        print("Shield not found in database")

    # Also check all armor items to understand the AC values
    print("\nAll armor items:")
    armor_items = db.query(models.Item).filter(models.Item.item_type == "armor").all()
    for armor in armor_items:
        print(
            f"  - {armor.name}: AC={armor.armor_class}, properties={armor.properties}"
        )

    print("\nAll shield items:")
    shield_items = db.query(models.Item).filter(models.Item.item_type == "shield").all()
    for shield in shield_items:
        print(
            f"  - {shield.name}: AC={shield.armor_class}, properties={shield.properties}"
        )
