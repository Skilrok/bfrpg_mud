import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.database import Base

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
        passive_deletes=True
    ) 