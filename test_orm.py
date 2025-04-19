"""
ORM Configuration Test Script

This script tests the ORM configuration for SQLAlchemy models and Pydantic schemas,
specifically focusing on the User model and the from_orm method that's causing issues.

Run with: python test_orm.py
"""

import logging
import os
import sys
from datetime import datetime

from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.models import User, Base
from app.schemas import User as UserSchema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_user_orm():
    """Test User model ORM configuration with Pydantic models"""
    
    # First ensure the database exists with tables
    logger.info("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    # Get a database session
    db = next(get_db())
    
    try:
        # 1. Create a test user
        logger.info("Creating test user...")
        test_username = f"test_orm_user_{datetime.utcnow().timestamp()}"
        test_email = f"{test_username}@example.com"
        test_user = User(
            username=test_username,
            email=test_email,
            hashed_password="test_hashed_password",
            is_active=True
        )
        
        # 2. Add to database
        logger.info("Adding user to database...")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        logger.info(f"User created with ID: {test_user.id}")
        
        # 3. Convert to dict and then to Pydantic model
        logger.info("Converting to dict...")
        user_dict = {
            "id": test_user.id,
            "username": test_user.username,
            "email": test_user.email,
            "is_active": test_user.is_active
        }
        logger.info(f"User dict: {user_dict}")
        
        # 4. Create Pydantic model from dict
        logger.info("Creating Pydantic model from dict...")
        pydantic_user = UserSchema(**user_dict)
        logger.info(f"Pydantic user: {pydantic_user}")
        
        # 5. Test from_orm method
        logger.info("Testing from_orm method...")
        try:
            orm_user = UserSchema.from_orm(test_user)
            logger.info(f"from_orm successful: {orm_user}")
        except Exception as e:
            logger.error(f"from_orm failed: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"UserSchema Config: {getattr(UserSchema, 'Config', None)}")
            logger.error(f"Config contents: {dir(getattr(UserSchema, 'Config', {}))}")
            
        # 6. Clean up
        logger.info("Cleaning up test user...")
        db.delete(test_user)
        db.commit()
        logger.info("Test user deleted")
        
        return True
    
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_user_orm()
    if success:
        logger.info("ORM test completed successfully")
        sys.exit(0)
    else:
        logger.error("ORM test failed")
        sys.exit(1) 