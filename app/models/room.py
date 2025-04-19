import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from typing import Dict, Any, List

from app.database import Base
from app.models.base import JSON_TYPE

class RoomType(str, enum.Enum):
    """Room types for various terrain and location types"""
    TOWN = "town"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    CAVE = "cave"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    WATER = "water"
    BUILDING = "building"
    SPECIAL = "special"

class Room(Base):
    """Room/location model representing a place in the game world"""
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False, default=RoomType.DUNGEON)
    
    # Location coordinates (for mapping)
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    z = Column(Integer, default=0)  # Level/floor
    
    # Area grouping (optional - for organizing rooms)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)
    
    # Exits to other rooms
    exits = Column(JSON_TYPE, default=dict)  # {"north": 1, "east": 2, etc.}
    
    # Room state and properties
    is_dark = Column(Boolean, default=False)  # Requires light source
    properties = Column(JSON_TYPE, default=dict)  # Flexible field for room-specific properties
    
    # Relationships
    area = relationship("Area", back_populates="rooms")
    items = relationship("RoomItem", back_populates="room")
    npcs = relationship("RoomNPC", back_populates="room")
    characters = relationship("CharacterLocation", back_populates="room")

class Area(Base):
    """Area model for grouping related rooms"""
    __tablename__ = "areas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    rooms = relationship("Room", back_populates="area")

class RoomItem(Base):
    """Items present in a room"""
    __tablename__ = "room_items"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1)
    properties = Column(JSON_TYPE, default=dict)  # For special item placement properties
    
    # Relationships
    room = relationship("Room", back_populates="items")
    item = relationship("Item")

class RoomNPC(Base):
    """NPCs present in a room"""
    __tablename__ = "room_npcs"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    npc_id = Column(Integer, ForeignKey("npcs.id", ondelete="CASCADE"), nullable=False)
    properties = Column(JSON_TYPE, default=dict)  # For NPC state in this room
    
    # Relationships
    room = relationship("Room", back_populates="npcs")
    npc = relationship("NPC")

class CharacterLocation(Base):
    """Tracks where characters are located"""
    __tablename__ = "character_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    
    # For wilderness/overworld travel
    x = Column(Integer, nullable=True)
    y = Column(Integer, nullable=True)
    
    # Relationships
    character = relationship("Character")
    room = relationship("Room", back_populates="characters") 