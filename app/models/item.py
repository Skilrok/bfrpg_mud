import enum

from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import JSON_TYPE, Base


class ItemType(str, enum.Enum):
    """Item types for classification and UI display"""

    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    POTION = "potion"
    SCROLL = "scroll"
    WAND = "wand"
    RING = "ring"
    AMULET = "amulet"
    TOOL = "tool"
    CONTAINER = "container"
    CLOTHING = "clothing"
    FOOD = "food"
    MISCELLANEOUS = "miscellaneous"


class Item(Base):
    """Item model for game objects that can be picked up, used, equipped, etc."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(Enum(ItemType), nullable=False, default=ItemType.MISCELLANEOUS)

    # Item properties that affect gameplay
    weight = Column(Integer, default=1)  # In coins/pounds
    value = Column(Integer, default=0)  # Value in copper coins

    # Properties specific to equipment
    is_equippable = Column(Boolean, default=False)
    equip_slot = Column(String, nullable=True)  # E.g., "main_hand", "body", "head"

    # Properties specific to weapon/armor types
    damage = Column(String, nullable=True)  # E.g. "1d6"
    armor_class = Column(Integer, nullable=True)
    properties = Column(JSON_TYPE, default=dict)
