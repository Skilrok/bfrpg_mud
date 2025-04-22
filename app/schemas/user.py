from typing import Optional, List
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

class UserBase(BaseModel):
    """Base user schema with common attributes"""
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
        orm_mode = True  # This is needed for compatibility with older Pydantic

class UserCreate(UserBase):
    """Schema for user creation including password fields"""
    password: str
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

class UserLogin(BaseModel):
    """Schema for user login credentials"""
    username: str
    password: str
    
    class Config:
        from_attributes = True
        orm_mode = True  # This is needed for compatibility with older Pydantic

class User(UserBase):
    """Schema for user responses without sensitive information"""
    id: int
    is_active: bool

    class Config:
        from_attributes = True
        orm_mode = True  # This is needed for compatibility with older Pydantic

class UserInDB(User):
    """Schema for database user representation - for internal use only"""
    hashed_password: str
    
    class Config:
        from_attributes = True
        orm_mode = True  # This is needed for compatibility with older Pydantic

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    password_confirm: Optional[str] = None
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if v is not None and 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v
    
    class Config:
        from_attributes = True
        orm_mode = True  # This is needed for compatibility with older Pydantic

class PasswordResetRequest(BaseModel):
    """Schema for requesting a password reset"""
    email: EmailStr
    
    class Config:
        from_attributes = True
        orm_mode = True  # This is needed for compatibility with older Pydantic

class PasswordReset(BaseModel):
    """Schema for password reset requests"""
    token: str
    new_password: str
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('passwords do not match')
        return v
    
    class Config:
        from_attributes = True
        orm_mode = True  # This is needed for compatibility with older Pydantic

class UserDetail(User):
    """Schema for detailed user information including admin status and timestamps"""
    is_admin: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        orm_mode = True  # This is needed for compatibility with older Pydantic 