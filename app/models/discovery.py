"""
Model for tracking room discoveries by characters in the BFRPG MUD.
This is used to implement the fog-of-war exploration system.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class RoomDiscovery(Base):
    """Model to track which rooms a character has discovered"""

    __tablename__ = "room_discoveries"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    room_id = Column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    is_visited = Column(Boolean, default=True)  # Character has physically been there
    discovery_date = Column(
        DateTime, server_default=func.now()
    )  # When first discovered

    # Ensure a character can't have duplicate discovery records for the same room
    __table_args__ = (
        UniqueConstraint(
            "character_id", "room_id", name="uix_character_room_discovery"
        ),
    )

    # Relationships
    character = relationship("Character")
    room = relationship("Room")

    @classmethod
    def discover_room(cls, db, character_id, room_id, visited=True):
        """
        Record that a character has discovered a room.

        Args:
            db: Database session
            character_id: ID of the character
            room_id: ID of the room
            visited: Whether the character physically visited the room
                   (False for rooms seen from a distance)

        Returns:
            RoomDiscovery: The room discovery record
        """
        # Check if discovery already exists
        discovery = (
            db.query(cls)
            .filter(cls.character_id == character_id, cls.room_id == room_id)
            .first()
        )

        if discovery:
            # Already discovered, update visited status if needed
            if visited and not discovery.is_visited:
                discovery.is_visited = True
                db.commit()
            return discovery

        # Create new discovery
        discovery = cls(character_id=character_id, room_id=room_id, is_visited=visited)
        db.add(discovery)
        db.commit()
        db.refresh(discovery)
        return discovery

    @classmethod
    def get_discovered_rooms(cls, db, character_id):
        """
        Get all rooms discovered by a character.

        Args:
            db: Database session
            character_id: ID of the character

        Returns:
            list: List of room IDs discovered by the character
        """
        discoveries = db.query(cls).filter(cls.character_id == character_id).all()
        return [d.room_id for d in discoveries]

    @classmethod
    def get_visited_rooms(cls, db, character_id):
        """
        Get all rooms visited by a character.

        Args:
            db: Database session
            character_id: ID of the character

        Returns:
            list: List of room IDs visited by the character
        """
        discoveries = (
            db.query(cls)
            .filter(cls.character_id == character_id, cls.is_visited == True)
            .all()
        )
        return [d.room_id for d in discoveries]
