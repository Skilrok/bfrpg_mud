from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.models import RoomType

class RoomBase(BaseModel):
    """Base schema for room data"""
    name: str
    description: str
    room_type: RoomType
    x: int = 0
    y: int = 0
    z: int = 0
    is_dark: bool = False
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class RoomCreate(RoomBase):
    """Schema for room creation"""
    area_id: Optional[int] = None
    exits: Dict[str, int] = Field(default_factory=dict)
    properties: Dict[str, Any] = Field(default_factory=dict)

class Room(RoomBase):
    """Schema for room responses"""
    id: int
    area_id: Optional[int] = None
    exits: Dict[str, int] = Field(default_factory=dict)
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class RoomDetail(Room):
    """Detailed room information including items and NPCs"""
    items: List[Dict[str, Any]] = Field(default_factory=list)
    npcs: List[Dict[str, Any]] = Field(default_factory=list)
    characters: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class AreaBase(BaseModel):
    """Base schema for area data"""
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class AreaCreate(AreaBase):
    """Schema for area creation"""
    pass

class Area(AreaBase):
    """Schema for area responses"""
    id: int
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class AreaDetail(Area):
    """Detailed area information including list of rooms"""
    rooms: List[Room] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic 