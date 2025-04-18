from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class HirelingBase(BaseModel):
    """Base hireling schema with common attributes"""
    name: str
    character_class: str
    level: int = 1
    experience: int = 0
    loyalty: float = 50.0
    wage: int = 10

    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class HirelingCreate(HirelingBase):
    """Schema for hireling creation"""
    pass

class Hireling(HirelingBase):
    """Schema for hireling responses"""
    id: int
    is_available: bool
    user_id: int
    master_id: Optional[int] = None
    days_unpaid: int = 0
    last_payment_date: Optional[datetime] = None

    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic

class HirelingUpdate(BaseModel):
    """Schema for hireling updates"""
    name: Optional[str] = None
    character_class: Optional[str] = None
    level: Optional[int] = None
    experience: Optional[int] = None
    loyalty: Optional[float] = None
    wage: Optional[int] = None
    is_available: Optional[bool] = None
    master_id: Optional[int] = None
    days_unpaid: Optional[int] = None
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic 