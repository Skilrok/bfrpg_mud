import os
import sys
from typing import List, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Item, ItemType


def check_items():
    """Check items in the database"""
    db = SessionLocal()

    try:
        # Check for axe items
        axe_items = db.query(Item).filter(Item.name.ilike("%axe%")).all()
        print(f"Found {len(axe_items)} axe items:")
        for item in axe_items:
            print(f"ID: {item.id}, Name: {item.name}, Type: {item.item_type.value}")
            print(f"  Properties: {item.properties}")

        # Also list other weapon types for reference
        print("\nAll weapons in database:")
        weapons = db.query(Item).filter(Item.item_type == ItemType.WEAPON).all()
        for weapon in weapons:
            print(f"ID: {weapon.id}, Name: {weapon.name}")

    except Exception as e:
        print(f"Error checking items: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_items()
