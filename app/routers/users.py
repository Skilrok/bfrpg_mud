from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Dict, Any, Optional
import logging

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_password_hash, get_current_user, get_current_active_user

router = APIRouter(tags=["users"])

logger = logging.getLogger(__name__)

@router.get("/", response_model=List[schemas.User])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a list of all users with pagination.
    Only available to authenticated users.
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.get("/me", response_model=schemas.UserDetail)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get detailed information about the currently authenticated user.
    """
    return current_user

@router.get("/{user_id}", response_model=schemas.UserDetail)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific user by ID.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/me", response_model=schemas.UserDetail)
async def update_current_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update the currently authenticated user's information.
    """
    # Check if the username is being changed and if it's already taken
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(models.User).filter(models.User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )
    
    # Check if the email is being changed and if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(models.User).filter(models.User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
    
    # Update user fields
    if user_update.username:
        current_user.username = user_update.username
    if user_update.email:
        current_user.email = user_update.email
    
    # Update password if provided
    if user_update.password:
        current_user.hashed_password = hash_password(user_update.password)
    
    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during user update: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user"
        )

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with the system.
    """
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

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a user by ID.
    Only admin users can delete other users.
    Users can delete their own accounts.
    """
    # Check if the current user is trying to delete someone else's account
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete other user accounts"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        db.delete(user)
        db.commit()
        return None
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )

@router.patch("/{user_id}/activate", response_model=schemas.UserDetail)
async def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Activate a user account.
    Only admin users can activate other user accounts.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to activate user accounts"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{user_id}/deactivate", response_model=schemas.UserDetail)
async def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Deactivate a user account.
    Only admin users can deactivate other user accounts.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to deactivate user accounts"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user

@router.patch("/{user_id}/make-admin", response_model=schemas.UserDetail)
async def make_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Grant admin privileges to a user.
    Only existing admin users can grant admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to grant admin privileges"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_admin = True
    db.commit()
    db.refresh(user)
    return user
