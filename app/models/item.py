import enum
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import JSON_TYPE

class ItemType(str, enum.Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    POTION = "potion"
    SCROLL = "scroll"
    WAND = "wand"
    RING = "ring"
    AMMUNITION = "ammunition"
    TOOL = "tool"
    CONTAINER = "container"
    CLOTHING = "clothing"
    FOOD = "food"
    MISCELLANEOUS = "miscellaneous"

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(Enum(ItemType), nullable=False)
    value = Column(Integer, default=0)  # Value in gold pieces
    weight = Column(Float, default=0.0)  # Weight in pounds
    properties = Column(JSON_TYPE, default=dict)  # Flexible field for item-specific properties 