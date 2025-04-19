import os
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .constants import CharacterClass, CharacterRace, ItemType
from .database import Base, JSONEncodedDict

# Determine if using SQLite (for JSON handling)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bfrpg.db")
JSON_TYPE = JSONEncodedDict if DATABASE_URL.startswith("sqlite") else JSON


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    reset_token = Column(String, nullable=True)
    reset_token_expiry = Column(DateTime, nullable=True)

    characters = relationship("Character", back_populates="owner")
    hirelings = relationship("Hireling", back_populates="owner")
    command_history = relationship(
        "CommandHistory",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )


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
        passive_deletes=True,
    )


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

    def update_loyalty(self, change: float) -> None:
        """Update hireling loyalty with bounds checking"""
        self.loyalty = max(0.0, min(100.0, self.loyalty + change))

    def update_payment_status(self) -> None:
        """Update payment status and adjust loyalty accordingly"""
        if self.last_payment_date:
            days_since_payment = (datetime.utcnow() - self.last_payment_date).days
            if days_since_payment > 0:
                self.days_unpaid = days_since_payment
                # Loyalty decreases by 5 points per unpaid day
                self.update_loyalty(-5.0 * days_since_payment)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    item_type = Column(Enum(ItemType), nullable=False)
    value = Column(Integer, default=0)  # Value in gold pieces
    weight = Column(Float, default=0.0)  # Weight in pounds
    properties = Column(
        JSON_TYPE, default=dict
    )  # Flexible field for item-specific properties


class CommandHistory(Base):
    """Stores command history for users"""

    __tablename__ = "command_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    character_id = Column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=True
    )
    command = Column(String(255), nullable=False)
    response = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="command_history")
    character = relationship("Character", back_populates="command_history")
