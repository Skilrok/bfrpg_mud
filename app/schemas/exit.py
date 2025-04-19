"""
Exit Schema

This module defines the Pydantic schemas for exit data validation and serialization.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from app.schemas.room import RoomBrief


class ExitBase(BaseModel):
    """Base schema for exit data"""
    direction: str
    name: Optional[str] = None
    description: Optional[str] = None
    is_hidden: bool = False
    is_locked: bool = False
    key_id: Optional[int] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class ExitCreate(ExitBase):
    """Schema for exit creation"""
    source_room_id: int
    destination_room_id: int


class ExitUpdate(BaseModel):
    """Schema for exit update (all fields optional)"""
    direction: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_hidden: Optional[bool] = None
    is_locked: Optional[bool] = None
    key_id: Optional[int] = None
    destination_room_id: Optional[int] = None
    properties: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class Exit(ExitBase):
    """Schema for exit responses"""
    id: int
    source_room_id: int
    destination_room_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExitDetail(Exit):
    """Detailed exit information including source and destination rooms"""
    source_room: Optional[RoomBrief] = None
    destination_room: Optional[RoomBrief] = None

    class Config:
        from_attributes = True 