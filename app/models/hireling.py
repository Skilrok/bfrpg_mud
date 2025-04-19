import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.models.base import JSON_TYPE, Base


class HirelingType(str, enum.Enum):
    """Types of hirelings a character can recruit"""

    PORTER = "porter"
    MERCENARY = "mercenary"
    SAGE = "sage"
    HEALER = "healer"
    GUIDE = "guide"
    SPECIALIST = "specialist"


class LoyaltyLevel(str, enum.Enum):
    """Loyalty levels for hired NPCs"""

    DISLOYAL = "disloyal"
    RELUCTANT = "reluctant"
    NEUTRAL = "neutral"
    LOYAL = "loyal"
    FANATIC = "fanatic"


class Hireling(Base):
    """Model for characters that can be hired by players"""

    __tablename__ = "hirelings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    character_class = Column(String)  # e.g., "fighter", "cleric", "magic-user"
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    loyalty = Column(Enum(LoyaltyLevel), default=LoyaltyLevel.NEUTRAL)
    wage = Column(Integer, default=10)  # gold pieces per day
    is_available = Column(Boolean, default=True)
    last_payment_date = Column(DateTime, nullable=True)
    days_unpaid = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"))
    master_id = Column(Integer, ForeignKey("characters.id"), nullable=True)
    hireling_type = Column(Enum(HirelingType), nullable=False)
    skills = Column(JSON_TYPE, default=list)  # List of skills the hireling has
    payment_due = Column(Integer, default=0)  # Payment due in gold coins
    payment_rate = Column(Integer, default=1)  # Gold per day
    payment_last_date = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    owner = relationship("User", back_populates="hirelings")
    master = relationship("Character", back_populates="hirelings")

    def update_loyalty(self, change: float):
        """Update loyalty score with bounds checking"""
        self.loyalty = max(0, min(100, self.loyalty + change))

    def update_payment_status(self):
        """Update days_unpaid based on last payment date"""
        if not self.last_payment_date:
            return

        days_since_payment = (datetime.datetime.utcnow() - self.last_payment_date).days
        self.days_unpaid = days_since_payment
