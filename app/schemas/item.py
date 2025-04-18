from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models import ItemType

class ItemBase(BaseModel):
    """Base item schema with common attributes"""
    name: str
    description: Optional[str] = None
    item_type: ItemType
    value: int = 0  # Value in gold pieces
    weight: float = 0.0  # Weight in pounds
    properties: Dict[str, Any] = Field(default_factory=dict)  # Flexible field for item-specific properties
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class ItemCreate(ItemBase):
    """Schema for item creation"""
    pass

class Item(ItemBase):
    """Schema for item responses"""
    id: int
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class ItemUpdate(BaseModel):
    """Schema for item updates"""
    name: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[ItemType] = None
    value: Optional[int] = None
    weight: Optional[float] = None
    properties: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class InventoryItem(BaseModel):
    """Schema for items in a character's inventory"""
    item_id: int
    quantity: int = 1
    equipped: bool = False
    slot: Optional[str] = None  # Equipment slot if equipped
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class AddInventoryItem(BaseModel):
    """Schema for adding an item to a character's inventory"""
    item_id: int
    quantity: int = 1
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class EquipItem(BaseModel):
    """Schema for equipping an item"""
    item_id: int
    slot: str
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic 