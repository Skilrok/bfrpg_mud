from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_password_hash

router = APIRouter(tags=["users"])


@router.get("/")
async def get_users():
    return {"message": "Get users endpoint"}


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user_by_username = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_user_by_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user data dict and exclude password_confirm
    user_data = user.dict(exclude={"password_confirm"})
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data["password"])
    
    # Remove plain password and add hashed_password
    del user_data["password"]
    user_data["hashed_password"] = hashed_password
    user_data["is_active"] = True
    
    # Create and save user
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Return user model that matches the Pydantic schema
    return schemas.User(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active
    )
