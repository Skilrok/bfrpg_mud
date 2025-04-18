from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.Item)
async def create_item(
    item: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Create a new item"""
    db_item = models.Item(
        name=item.name,
        description=item.description,
        item_type=item.item_type,
        value=item.value,
        weight=item.weight,
        properties=item.properties
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
    current_user: schemas.User = Depends(get_current_user)
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
    current_user: schemas.User = Depends(get_current_user)
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
    current_user: schemas.User = Depends(get_current_user)
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
    current_user: schemas.User = Depends(get_current_user)
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
    current_user: schemas.User = Depends(get_current_user)
):
    """Add an item to a character's inventory"""
    # Get the character
    db_character = db.query(models.Character).filter(
        models.Character.id == character_id, 
        models.Character.user_id == current_user.id
    ).first()
    
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Check if the item exists
    db_item = db.query(models.Item).filter(models.Item.id == add_item.item_id).first()
    
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get current inventory or initialize empty dict if None
    inventory = db_character.inventory or {}
    
    # Convert to dict if it's not already (handling potential JSONified data)
    if not isinstance(inventory, dict):
        inventory = dict(inventory)
    
    # Add or update item in inventory
    item_id_str = str(add_item.item_id)
    if item_id_str in inventory:
        inventory[item_id_str]["quantity"] += add_item.quantity
    else:
        inventory[item_id_str] = {
            "item_id": add_item.item_id,
            "quantity": add_item.quantity,
            "equipped": False,
            "slot": None
        }
    
    # Explicitly update the character's inventory
    db_character.inventory = inventory
    
    # Manual flushing to ensure it's in the transaction
    db.flush()
    db.commit()
    
    # Refresh from database to get the updated data
    db.refresh(db_character)
    
    # Sanity check - raise an error if the item wasn't added
    if item_id_str not in db_character.inventory:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to add item {add_item.item_id} to inventory - database didn't update"
        )
    
    return db_character


@router.post("/inventory/{character_id}/remove", response_model=schemas.Character)
async def remove_item_from_inventory(
    remove_item: schemas.AddInventoryItem,
    character_id: int = Path(..., title="The ID of the character"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Remove an item from a character's inventory"""
    # Get the character
    db_character = db.query(models.Character).filter(
        models.Character.id == character_id, 
        models.Character.user_id == current_user.id
    ).first()
    
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get current inventory
    inventory = db_character.inventory or {}
    
    # Check if the item is in the inventory
    item_id_str = str(remove_item.item_id)
    if item_id_str not in inventory:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    
    # Update quantity or remove item
    if inventory[item_id_str]["quantity"] > remove_item.quantity:
        inventory[item_id_str]["quantity"] -= remove_item.quantity
    else:
        # If item is equipped, remove it from equipment
        if inventory[item_id_str].get("equipped", False):
            equipment = db_character.equipment or {}
            for slot, equipped_item in list(equipment.items()):
                if str(equipped_item) == item_id_str:
                    equipment.pop(slot)
                    break
            db_character.equipment = equipment
            
        # Remove item from inventory
        inventory.pop(item_id_str)
    
    # Update character's inventory
    db_character.inventory = inventory
    
    db.commit()
    db.refresh(db_character)
    return db_character


@router.post("/inventory/{character_id}/equip", response_model=schemas.Character)
async def equip_item(
    equip_request: schemas.EquipItem,
    character_id: int = Path(..., title="The ID of the character"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Equip an item from inventory to a specific slot"""
    # Get the character
    db_character = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get inventory and equipment
    inventory = db_character.inventory or {}
    equipment = db_character.equipment or {}
    
    # Convert to dict if needed
    if not isinstance(inventory, dict):
        inventory = dict(inventory)
    if not isinstance(equipment, dict):
        equipment = dict(equipment)
    
    # Check if the item is in inventory
    item_id_str = str(equip_request.item_id)
    if item_id_str not in inventory:
        raise HTTPException(status_code=404, detail="Item not found in inventory")
    
    # Get the item type to validate slot
    db_item = db.query(models.Item).filter(models.Item.id == equip_request.item_id).first()
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
    
    if db_item.item_type in valid_slots and equip_request.slot not in valid_slots[db_item.item_type]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid slot '{equip_request.slot}' for item type '{db_item.item_type}'"
        )
    
    # If something is already equipped in that slot, unequip it
    if equip_request.slot in equipment:
        old_item_id = equipment[equip_request.slot]
        old_item_id_str = str(old_item_id)
        if old_item_id_str in inventory:
            inventory[old_item_id_str]["equipped"] = False
            inventory[old_item_id_str]["slot"] = None
    
    # Update equipment
    equipment[equip_request.slot] = equip_request.item_id
    
    # Update inventory item as equipped
    inventory[item_id_str]["equipped"] = True
    inventory[item_id_str]["slot"] = equip_request.slot
    
    # Explicitly update character
    db_character.equipment = equipment
    db_character.inventory = inventory
    
    # Save changes
    db.flush()
    db.commit()
    db.refresh(db_character)
    
    # Verify equipment was updated
    if equip_request.slot not in db_character.equipment or db_character.equipment[equip_request.slot] != equip_request.item_id:
        raise HTTPException(
            status_code=500,
            detail="Failed to equip item - equipment data not updated"
        )
    
    return db_character


@router.post("/inventory/{character_id}/unequip", response_model=schemas.Character)
async def unequip_item(
    slot: str = Query(..., title="Equipment slot to unequip"),
    character_id: int = Path(..., title="The ID of the character"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Unequip an item from a specific slot"""
    # Get the character
    db_character = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get inventory and equipment
    inventory = db_character.inventory or {}
    equipment = db_character.equipment or {}
    
    # Convert to dict if needed
    if not isinstance(inventory, dict):
        inventory = dict(inventory)
    if not isinstance(equipment, dict):
        equipment = dict(equipment)
    
    # Check if there's an item in that slot
    if slot not in equipment:
        raise HTTPException(status_code=404, detail=f"No item equipped in slot {slot}")
    
    # Get the item ID
    item_id = equipment[slot]
    item_id_str = str(item_id)
    
    # Remove from equipment - create a new dict instead of modifying
    new_equipment = dict(equipment)
    del new_equipment[slot]
    
    # Update inventory item as unequipped
    if item_id_str in inventory:
        inventory[item_id_str]["equipped"] = False
        inventory[item_id_str]["slot"] = None
    
    # Update character with the new dictionaries
    db_character.equipment = new_equipment
    db_character.inventory = inventory
    
    # Save changes
    db.flush()
    db.commit()
    db.refresh(db_character)
    
    # Verify equipment was updated - with more flexible check
    if db_character.equipment and slot in db_character.equipment:
        raise HTTPException(
            status_code=500,
            detail="Failed to unequip item - equipment data not updated"
        )
    
    return db_character


@router.get("/inventory/{character_id}", response_model=Dict[str, Any])
async def get_inventory(
    character_id: int = Path(..., title="The ID of the character"),
    include_details: bool = Query(False, title="Include detailed item information"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Get a character's inventory with optional detailed item information"""
    # Get the character
    db_character = db.query(models.Character).filter(
        models.Character.id == character_id,
        models.Character.user_id == current_user.id
    ).first()
    
    if db_character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get inventory and equipment
    inventory = db_character.inventory or {}
    
    # If detailed information is requested, fetch all item details
    if include_details:
        result = {}
        for item_id_str, item_data in inventory.items():
            item_id = int(item_id_str)
            db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
            
            if db_item:
                item_details = {
                    "id": db_item.id,
                    "name": db_item.name,
                    "description": db_item.description,
                    "item_type": db_item.item_type,
                    "value": db_item.value,
                    "weight": db_item.weight,
                    "properties": db_item.properties,
                    "quantity": item_data["quantity"],
                    "equipped": item_data.get("equipped", False),
                    "slot": item_data.get("slot", None)
                }
                result[item_id_str] = item_details
        
        return result
    
    # Otherwise just return the basic inventory
    return inventory
