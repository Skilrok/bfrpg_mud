import enum

from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import JSON_TYPE, Base


class NPCType(str, enum.Enum):
    """Types of NPCs in the game world"""

    VILLAGER = "villager"
    MERCHANT = "merchant"
    GUARD = "guard"
    NOBLE = "noble"
    MONSTER = "monster"
    QUEST_GIVER = "quest_giver"


class NPC(Base):
    """Model for non-player characters in the game world"""

    __tablename__ = "npcs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    npc_type = Column(Enum(NPCType), nullable=False, default=NPCType.VILLAGER)

    # NPC stats and properties
    level = Column(Integer, default=1)
    hit_points = Column(Integer, default=4)
    armor_class = Column(Integer, default=10)
    is_hostile = Column(Boolean, default=False)

    # Monster-specific fields
    monster_type = Column(String, nullable=True)  # goblin, orc, dragon, etc.
    challenge_rating = Column(Float, nullable=True)  # Difficulty rating
    treasure_table = Column(String, nullable=True)  # Reference to treasure table

    # Dialogue and interaction options
    dialogue = Column(JSON_TYPE, default=dict)
    inventory = Column(JSON_TYPE, default=list)
    properties = Column(JSON_TYPE, default=dict)  # For NPC-specific properties

    # Flexible fields for NPC-specific data
    dialogs = Column(JSON_TYPE, default=dict)  # For conversation responses

    @property
    def is_monster(self):
        """Helper to determine if this NPC is a monster"""
        return self.npc_type == NPCType.MONSTER

    @property
    def attacks(self):
        """Get the attack options for this NPC/monster"""
        return self.properties.get("attacks", [])

    @property
    def special_abilities(self):
        """Get special abilities for this NPC/monster"""
        return self.properties.get("special_abilities", [])

    @property
    def weaknesses(self):
        """Get weaknesses of this NPC/monster"""
        return self.properties.get("weaknesses", [])

    @property
    def resistances(self):
        """Get resistances of this NPC/monster"""
        return self.properties.get("resistances", [])
