import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    inspect,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import JSON_TYPE, Base
from app.database import engine


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

    # Exits to other rooms - legacy field, keeping for compatibility
    exits = Column(JSON_TYPE, default=dict)  # {"north": 1, "east": 2, etc.}

    # Room state and properties
    is_dark = Column(Boolean, default=False)  # Requires light source
    properties = Column(
        JSON_TYPE, default=dict
    )  # Flexible field for room-specific properties

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    area = relationship("Area", back_populates="rooms")
    items = relationship("RoomItem", back_populates="room")
    npcs = relationship("RoomNPC", back_populates="room")
    characters = relationship("CharacterLocation", back_populates="room")

    # Exit relationships
    outgoing_exits = relationship(
        "Exit",
        foreign_keys="Exit.source_room_id",
        back_populates="source_room",
        cascade="all, delete-orphan",
    )
    incoming_exits = relationship(
        "Exit",
        foreign_keys="Exit.destination_room_id",
        back_populates="destination_room",
        cascade="all, delete-orphan",
    )

    # Property to get coordinates as a dict from individual fields
    @property
    def coordinates(self):
        return {"x": self.x, "y": self.y, "z": self.z}


class Area(Base):
    """Area model for grouping related rooms"""

    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    level_range = Column(String, nullable=True)  # e.g. "1-5"
    
    # The following columns may not exist in older databases, make them safe
    @declared_attr
    def is_dungeon(cls):
        try:
            insp = inspect(engine)
            columns = [c['name'] for c in insp.get_columns('areas')]
            if 'is_dungeon' in columns:
                return Column(Boolean, default=True)
            else:
                return None
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error checking is_dungeon column: {e}")
            return Column(Boolean, default=True, nullable=True)
    
    @declared_attr
    def is_hidden(cls):
        try:
            insp = inspect(engine)
            columns = [c['name'] for c in insp.get_columns('areas')]
            if 'is_hidden' in columns:
                return Column(Boolean, default=False)
            else:
                return None
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error checking is_hidden column: {e}")
            return Column(Boolean, default=False, nullable=True)
    
    @declared_attr
    def properties(cls):
        try:
            insp = inspect(engine)
            columns = [c['name'] for c in insp.get_columns('areas')]
            if 'properties' in columns:
                return Column(JSON_TYPE, default=dict)
            else:
                return None
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Error checking properties column: {e}")
            return Column(JSON_TYPE, default=dict, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    rooms = relationship("Room", back_populates="area")


class RoomItem(Base):
    """Items present in a room"""

    __tablename__ = "room_items"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    item_id = Column(
        Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    quantity = Column(Integer, default=1)
    properties = Column(
        JSON_TYPE, default=dict
    )  # For special item placement properties

    # Relationships
    room = relationship("Room", back_populates="items")
    item = relationship("Item")


class RoomNPC(Base):
    """NPCs present in a room"""

    __tablename__ = "room_npcs"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    npc_id = Column(Integer, ForeignKey("npcs.id", ondelete="CASCADE"), nullable=False)
    properties = Column(JSON_TYPE, default=dict)  # For NPC state in this room

    # Relationships
    room = relationship("Room", back_populates="npcs")
    npc = relationship("NPC")


class CharacterLocation(Base):
    """Tracks where characters are located"""

    __tablename__ = "character_locations"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    room_id = Column(
        Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True
    )

    # For wilderness/overworld travel
    x = Column(Integer, nullable=True)
    y = Column(Integer, nullable=True)

    # Relationships
    character = relationship("Character")
    room = relationship("Room", back_populates="characters")
