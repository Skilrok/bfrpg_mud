# REMOVED: import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.Item)
async def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Create a new item"""
    db_item = models.Item(
        name=item.name,
        description=item.description,
        item_type=item.item_type,
        value=item.value,
        weight=item.weight,
        properties=item.properties,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[schemas.Item])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    item_type: Optional[schemas.ItemType] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """List all items with optional filtering by type"""
    query = db.query(models.Item)

    if item_type:
        query = query.filter(models.Item.item_type == item_type)

    return query.offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=schemas.Item)
async def get_item(
    item_id: int = Path(..., title="The ID of the item to get"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get a specific item by ID"""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return db_item


@router.put("/{item_id}", response_model=schemas.Item)
async def update_item(
    item: schemas.ItemCreate,
    item_id: int = Path(..., title="The ID of the item to update"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Update an existing item"""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update item attributes
    db_item.name = item.name
    db_item.description = item.description
    db_item.item_type = item.item_type
    db_item.value = item.value
    db_item.weight = item.weight
    db_item.properties = item.properties

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int = Path(..., title="The ID of the item to delete"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Delete an item"""
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_item)
    db.commit()
    return None


# Inventory endpoints
@router.post("/inventory/{character_id}/add", response_model=schemas.Character)
async def add_item_to_inventory(
    add_item: schemas.AddInventoryItem,
    character_id: int = Path(..., title="The ID of the character"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Add an item to a character's inventory"""
    # Get the character
    db_character = (
        db.query(models.Character)
        .filter(
            models.Character.id == character_id,
            models.Character.user_id == current_user.id,
        )
        .first()
    )

    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    # Check if the item exists
    db_item = db.query(models.Item).filter(models.Item.id == add_item.item_id).first()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if character already has this item
    existing_item = (
        db.query(models.CharacterItem)
        .filter(
            models.CharacterItem.character_id == character_id,
            models.CharacterItem.item_id == add_item.item_id,
            models.CharacterItem.is_equipped
            == False,  # Only match non-equipped items for stacking
        )
        .first()
    )

    if existing_item:
        # Update quantity of existing item
        existing_item.quantity += add_item.quantity
        db.add(existing_item)
    else:
        # Create new character item
        new_item = models.CharacterItem(
            character_id=character_id,
            item_id=add_item.item_id,
            quantity=add_item.quantity,
            is_equipped=False,
        )
        db.add(new_item)

    # Commit changes
    db.commit()
    db.refresh(db_character)

    # Verify the item was added
    added_item = (
        db.query(models.CharacterItem)
        .filter(
            models.CharacterItem.character_id == character_id,
            models.CharacterItem.item_id == add_item.item_id,
        )
        .first()
    )

    if not added_item:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add item {add_item.item_id} to inventory - database didn't update",
        )

    return db_character


@router.post("/inventory/{character_id}/remove", response_model=schemas.Character)
async def remove_item_from_inventory(
    remove_item: schemas.AddInventoryItem,
    character_id: int = Path(..., title="The ID of the character"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Remove an item from a character's inventory"""
    # Get the character
    db_character = (
        db.query(models.Character)
        .filter(
            models.Character.id == character_id,
            models.Character.user_id == current_user.id,
        )
        .first()
    )

    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    # Find the character item
    db_char_item = (
        db.query(models.CharacterItem)
        .filter(
            models.CharacterItem.character_id == character_id,
            models.CharacterItem.item_id == remove_item.item_id,
        )
        .first()
    )

    if db_char_item is None:
        raise HTTPException(status_code=404, detail="Item not found in inventory")

    # Update quantity or remove item
    if db_char_item.quantity > remove_item.quantity:
        # Reduce quantity
        db_char_item.quantity -= remove_item.quantity
        db.add(db_char_item)
    else:
        # Remove item completely
        db.delete(db_char_item)

    # Commit changes
    db.commit()
    db.refresh(db_character)
    return db_character


@router.post("/inventory/{character_id}/equip", response_model=schemas.Character)
async def equip_item(
    equip_request: schemas.EquipItem,
    character_id: int = Path(..., title="The ID of the character"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Equip an item from inventory to a specific slot"""
    # Get the character
    db_character = (
        db.query(models.Character)
        .filter(
            models.Character.id == character_id,
            models.Character.user_id == current_user.id,
        )
        .first()
    )

    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    # Find the character item
    db_char_item = (
        db.query(models.CharacterItem)
        .filter(
            models.CharacterItem.character_id == character_id,
            models.CharacterItem.item_id == equip_request.item_id,
        )
        .first()
    )

    if db_char_item is None:
        raise HTTPException(status_code=404, detail="Item not found in inventory")

    # Get the item type to validate slot
    db_item = (
        db.query(models.Item).filter(models.Item.id == equip_request.item_id).first()
    )
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found in database")

    # Validate slot is appropriate for item type (basic validation)
    valid_slots = {
        models.ItemType.WEAPON: ["main_hand", "off_hand"],
        models.ItemType.ARMOR: ["body"],
        models.ItemType.SHIELD: ["off_hand"],
        models.ItemType.RING: ["ring_1", "ring_2"],
        models.ItemType.AMMUNITION: ["ammo"],
        models.ItemType.CLOTHING: ["body", "head", "hands", "feet"],
    }

    if (
        db_item.item_type in valid_slots
        and equip_request.slot not in valid_slots[db_item.item_type]
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid slot '{equip_request.slot}' for item type '{db_item.item_type}'",
        )

    # Check if something is already equipped in that slot
    current_equipped = (
        db.query(models.CharacterItem)
        .filter(
            models.CharacterItem.character_id == character_id,
            models.CharacterItem.is_equipped == True,
            models.CharacterItem.equip_slot == equip_request.slot,
        )
        .first()
    )

    # If something is already equipped in that slot, unequip it
    if current_equipped:
        current_equipped.is_equipped = False
        current_equipped.equip_slot = None
        db.add(current_equipped)

    # Update the item to equip it
    db_char_item.is_equipped = True
    db_char_item.equip_slot = equip_request.slot
    db.add(db_char_item)

    # Commit changes
    db.commit()
    db.refresh(db_character)

    # Verify equipment was updated
    verification = (
        db.query(models.CharacterItem)
        .filter(
            models.CharacterItem.character_id == character_id,
            models.CharacterItem.item_id == equip_request.item_id,
            models.CharacterItem.is_equipped == True,
            models.CharacterItem.equip_slot == equip_request.slot,
        )
        .first()
    )

    if not verification:
        raise HTTPException(
            status_code=500, detail="Failed to equip item - equipment data not updated"
        )

    return db_character


@router.post("/inventory/{character_id}/unequip", response_model=schemas.Character)
async def unequip_item(
    slot: str = Query(..., title="Equipment slot to unequip"),
    character_id: int = Path(..., title="The ID of the character"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Unequip an item from a specific slot"""
    # Get the character
    db_character = (
        db.query(models.Character)
        .filter(
            models.Character.id == character_id,
            models.Character.user_id == current_user.id,
        )
        .first()
    )

    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    # Find the equipped item in the specified slot
    db_char_item = (
        db.query(models.CharacterItem)
        .filter(
            models.CharacterItem.character_id == character_id,
            models.CharacterItem.is_equipped == True,
            models.CharacterItem.equip_slot == slot,
        )
        .first()
    )

    if db_char_item is None:
        raise HTTPException(status_code=404, detail=f"No item equipped in slot {slot}")

    # Unequip the item
    db_char_item.is_equipped = False
    db_char_item.equip_slot = None
    db.add(db_char_item)

    # Commit changes
    db.commit()
    db.refresh(db_character)

    # Verify unequip was successful
    verification = (
        db.query(models.CharacterItem)
        .filter(
            models.CharacterItem.character_id == character_id,
            models.CharacterItem.is_equipped == True,
            models.CharacterItem.equip_slot == slot,
        )
        .first()
    )

    if verification:
        raise HTTPException(
            status_code=500, detail="Failed to unequip item - item is still equipped"
        )

    return db_character


@router.get("/inventory/{character_id}", response_model=Dict[str, Any])
async def get_inventory(
    character_id: int = Path(..., title="The ID of the character"),
    include_details: bool = Query(False, title="Include detailed item information"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    """Get a character's inventory with optional detailed item information"""
    # Get the character
    db_character = (
        db.query(models.Character)
        .filter(
            models.Character.id == character_id,
            models.Character.user_id == current_user.id,
        )
        .first()
    )

    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")

    # Get character items
    char_items = (
        db.query(models.CharacterItem)
        .filter(models.CharacterItem.character_id == character_id)
        .all()
    )

    # Convert to legacy inventory format for compatibility
    inventory = {}

    # If detailed information is requested, fetch all item details
    if include_details:
        for char_item in char_items:
            item_id_str = str(char_item.item_id)
            db_item = (
                db.query(models.Item)
                .filter(models.Item.id == char_item.item_id)
                .first()
            )

            if db_item:
                item_details = {
                    "id": db_item.id,
                    "name": db_item.name,
                    "description": db_item.description,
                    "item_type": db_item.item_type,
                    "value": db_item.value,
                    "weight": db_item.weight,
                    "properties": db_item.properties,
                    "quantity": char_item.quantity,
                    "equipped": char_item.is_equipped,
                    "slot": char_item.equip_slot,
                }
                inventory[item_id_str] = item_details
    else:
        # Basic inventory without detailed item info
        for char_item in char_items:
            item_id_str = str(char_item.item_id)
            inventory[item_id_str] = {
                "item_id": char_item.item_id,
                "quantity": char_item.quantity,
                "equipped": char_item.is_equipped,
                "slot": char_item.equip_slot,
            }

    return inventory
