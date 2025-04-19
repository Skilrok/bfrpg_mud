from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.models import RoomType


class RoomBrief(BaseModel):
    """Brief room information for references"""
    id: int
    name: str
    area_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    """Base schema for room data"""
    name: str
    description: str
    room_type: Optional[RoomType] = RoomType.DUNGEON
    is_dark: bool = False
    coordinates: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class RoomCreate(RoomBase):
    """Schema for room creation"""
    area_id: Optional[int] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class RoomUpdate(BaseModel):
    """Schema for room update (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    room_type: Optional[RoomType] = None
    is_dark: Optional[bool] = None
    coordinates: Optional[Dict[str, Any]] = None
    area_id: Optional[int] = None
    properties: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class Room(RoomBase):
    """Schema for room responses"""
    id: int
    area_id: Optional[int] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoomDetail(Room):
    """Detailed room information including exits, items, and NPCs"""
    area: Optional["AreaBrief"] = None
    exits: List[Any] = Field(default_factory=list)
    items: List[Any] = Field(default_factory=list)
    npcs: List[Any] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class AreaBase(BaseModel):
    """Base schema for area data"""
    name: str
    description: Optional[str] = None
    level_range: Optional[str] = None
    is_dungeon: bool = True
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class AreaBrief(BaseModel):
    """Brief area information for references"""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class AreaCreate(AreaBase):
    """Schema for area creation"""
    pass


class AreaUpdate(BaseModel):
    """Schema for area update (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    level_range: Optional[str] = None
    is_dungeon: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class Area(AreaBase):
    """Schema for area responses"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AreaDetail(Area):
    """Detailed area information including count of rooms"""
    room_count: int = 0
    
    class Config:
        from_attributes = True 