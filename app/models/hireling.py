import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship

from app.database import Base

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
        """Update loyalty score with bounds checking"""
        self.loyalty = max(0, min(100, self.loyalty + change))
        
    def update_payment_status(self):
        """Update days_unpaid based on last payment date"""
        if not self.last_payment_date:
            return
            
        days_since_payment = (datetime.datetime.utcnow() - self.last_payment_date).days
        self.days_unpaid = days_since_payment 