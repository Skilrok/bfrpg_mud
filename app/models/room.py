import enum
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import relationship

from app.models.base import JSON_TYPE, Base

# REMOVED: from sqlalchemy.ext.hybrid import hybrid_property
# REMOVED: from datetime import datetime


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
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

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
    """Represents a geographical area or dungeon in the game world."""

    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    level_range = Column(String, nullable=True)
    is_dungeon = Column(Boolean, nullable=False, default=True)
    is_hidden = Column(Boolean, nullable=False, default=False)
    properties = Column(JSON_TYPE, nullable=True)
    created_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    # New fields for hierarchical relationships
    parent_id = Column(Integer, ForeignKey("areas.id"), nullable=True)
    parent = relationship("Area", remote_side=[id], backref="children")

    # New fields for area categorization and relationships
    area_type = Column(
        String, nullable=True, default="region"
    )  # e.g., continent, region, dungeon, etc.
    related_areas = Column(
        JSON_TYPE, nullable=True, default=[]
    )  # Array of related area IDs
    tags = Column(JSON_TYPE, nullable=True, default=[])  # Flexible categorization
    area_metadata = Column(
        JSON_TYPE, nullable=True, default={}
    )  # Additional area information

    # Relationship with rooms
    rooms = relationship("Room", back_populates="area", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Area(id={self.id}, name='{self.name}', type='{self.area_type}')>"

    def add_related_area(self, area_id: int) -> None:
        """Add a related area ID to the related_areas list."""
        if not self.related_areas:
            self.related_areas = []
        if area_id not in self.related_areas:
            self.related_areas.append(area_id)

    def remove_related_area(self, area_id: int) -> None:
        """Remove a related area ID from the related_areas list."""
        if self.related_areas and area_id in self.related_areas:
            self.related_areas.remove(area_id)

    def add_tag(self, tag: str) -> None:
        """Add a tag to the area."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the area."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)

    def update_metadata(self, key: str, value: Any) -> None:
        """Update a metadata field."""
        if not self.area_metadata:
            self.area_metadata = {}
        self.area_metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata field value."""
        return self.area_metadata.get(key, default) if self.area_metadata else default


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
