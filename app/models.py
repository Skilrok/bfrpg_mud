from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    Enum,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    characters = relationship("Character", back_populates="owner")
    hirelings = relationship("Hireling", back_populates="owner")


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
    equipment = Column(JSON, default=dict)
    inventory = Column(JSON, default=dict)
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
    special_abilities = Column(JSON, default=list)
    
    # For magic users and clerics
    spells_known = Column(JSON, default=list)
    
    # For thieves
    thief_abilities = Column(JSON, default=dict)
    
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="characters")
    hirelings = relationship("Hireling", back_populates="master")


class Hireling(Base):
    __tablename__ = "hirelings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    character_class = Column(String)  # e.g., "fighter", "cleric", "magic-user"
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    loyalty = Column(Float, default=50.0)  # 0-100 scale
    wage = Column(Integer, default=10)  # gold pieces per day
    is_available = Column(Boolean, default=True)
    last_payment_date = Column(DateTime, nullable=True)
    days_unpaid = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))
    master_id = Column(Integer, ForeignKey("characters.id"), nullable=True)

    owner = relationship("User", back_populates="hirelings")
    master = relationship("Character", back_populates="hirelings")

    def update_loyalty(self, change: float):
        """Update hireling loyalty with bounds checking"""
        self.loyalty = max(0.0, min(100.0, self.loyalty + change))

    def update_payment_status(self):
        """Update payment status and adjust loyalty accordingly"""
        if self.last_payment_date:
            days_since_payment = (datetime.utcnow() - self.last_payment_date).days
            if days_since_payment > 0:
                self.days_unpaid = days_since_payment
                # Loyalty decreases by 5 points per unpaid day
                self.update_loyalty(-5.0 * days_since_payment)
