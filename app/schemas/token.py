from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    """Schema for auth token response"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for token payload data"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True
        orm_mode = True  # For compatibility with older Pydantic 