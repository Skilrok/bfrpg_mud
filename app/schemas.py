from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None


class CharacterCreate(CharacterBase):
    pass


class Character(CharacterBase):
    id: int
    level: int
    experience: int
    user_id: int

    class Config:
        from_attributes = True


class HirelingBase(BaseModel):
    name: str
    character_class: str
    level: int = 1
    experience: int = 0
    loyalty: float = 50.0
    wage: int = 10


class HirelingCreate(HirelingBase):
    pass


class Hireling(HirelingBase):
    id: int
    is_available: bool
    user_id: int
    master_id: Optional[int] = None
    days_unpaid: int = 0
    last_payment_date: Optional[datetime] = None

    class Config:
        from_attributes = True
        orm_mode = True  # Include this for backward compatibility with older versions
