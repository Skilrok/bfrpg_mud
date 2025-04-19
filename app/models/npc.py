from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import JSON_TYPE

class NPC(Base):
    """NPC model representing non-player characters in the game"""
    __tablename__ = "npcs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Basic stats
    level = Column(Integer, default=1)
    hp = Column(Integer, default=1)
    max_hp = Column(Integer, default=1)
    armor_class = Column(Integer, default=10)
    
    # Behavior flags
    hostile = Column(Boolean, default=False)
    
    # Flexible fields for NPC-specific data
    properties = Column(JSON_TYPE, default=dict)
    dialogs = Column(JSON_TYPE, default=dict)  # For conversation responses 