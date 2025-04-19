"""
Exit model for representing connections between rooms in the MUD
"""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, JSON_TYPE


class Exit(Base):
    """Exit model representing a connection between two rooms"""

    __tablename__ = "exits"

    id = Column(Integer, primary_key=True, index=True)
    
    # Direction in the source room (north, south, east, west, etc.)
    direction = Column(String, nullable=False)
    
    # Display name and description
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    # Room references
    source_room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    destination_room_id = Column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    
    # Exit properties
    is_hidden = Column(Boolean, default=False)  # Hidden exit, not visible in room description
    is_locked = Column(Boolean, default=False)  # Locked exit, requiring a key
    key_id = Column(Integer, ForeignKey("items.id", ondelete="SET NULL"), nullable=True)
    
    # Flexible properties field for exit-specific attributes
    properties = Column(JSON_TYPE, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    source_room = relationship("Room", foreign_keys=[source_room_id], back_populates="outgoing_exits")
    destination_room = relationship("Room", foreign_keys=[destination_room_id], back_populates="incoming_exits")
    key = relationship("Item", foreign_keys=[key_id]) 