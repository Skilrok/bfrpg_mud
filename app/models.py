from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
    DateTime,
)
from sqlalchemy.orm import relationship
from datetime import datetime
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


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
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
