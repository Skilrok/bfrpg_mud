import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import Base


class CommandHistory(Base):
    """Model to track command history for users and characters"""

    __tablename__ = "command_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    character_id = Column(
        Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=True
    )
    command = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="command_history")
    character = relationship("Character", back_populates="command_history")
