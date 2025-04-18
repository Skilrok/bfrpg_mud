from pydantic import BaseModel, EmailStr
from typing import List, Optional


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

    class Config:
        from_attributes = True
