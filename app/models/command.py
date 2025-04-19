import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base

class CommandHistory(Base):
    """Stores command history for users"""
    __tablename__ = "command_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=True)
    command = Column(String(255), nullable=False)
    response = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="command_history")
    character = relationship("Character", back_populates="command_history") 