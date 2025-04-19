import enum
import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import typing

from app.database import Base
from app.models.base import JSON_TYPE

class CharacterRace(str, enum.Enum):
    HUMAN = "human"
    DWARF = "dwarf"
    ELF = "elf"
    HALFLING = "halfling"

class CharacterClass(str, enum.Enum):
    FIGHTER = "fighter"
    CLERIC = "cleric"
    MAGIC_USER = "magic-user"
    THIEF = "thief"
    FIGHTER_MAGIC_USER = "fighter/magic-user"
    MAGIC_USER_THIEF = "magic-user/thief"

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    race = Column(Enum(CharacterRace), nullable=False)
    character_class = Column(Enum(CharacterClass), nullable=False)
    
    # Ability scores
    strength = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    wisdom = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    constitution = Column(Integer, nullable=False)
    charisma = Column(Integer, nullable=False)
    
    # Combat stats
    hit_points = Column(Integer, nullable=False)
    armor_class = Column(Integer, default=10)
    
    # Equipment and inventory (stored as JSON)
    equipment = Column(JSON_TYPE, default=dict)
    inventory = Column(JSON_TYPE, default=dict)
    gold = Column(Integer, default=0)
    
    # Known languages (comma-separated string)
    languages = Column(String, default="Common")
    
    # Saving throws
    save_death_ray_poison = Column(Integer)
    save_magic_wands = Column(Integer)
    save_paralysis_petrify = Column(Integer)
    save_dragon_breath = Column(Integer)
    save_spells = Column(Integer)
    
    # Special abilities based on race
    special_abilities = Column(JSON_TYPE, default=list)
    
    # For magic users and clerics
    spells_known = Column(JSON_TYPE, default=list)
    
    # For thieves
    thief_abilities = Column(JSON_TYPE, default=dict)
    
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="characters")
    hirelings = relationship("Hireling", back_populates="master")
    command_history = relationship(
        "CommandHistory", 
        back_populates="character", 
        cascade="all, delete",
        passive_deletes=True
    ) 