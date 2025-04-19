"""
Setup Game Environment

This script performs the following setup tasks:
1. Creates an admin user (if one doesn't exist)
2. Creates the starter area
3. Reports on the setup status

Used for initial setup and testing
"""

import asyncio
import os
import sys
import logging
from getpass import getpass

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.exc import SQLAlchemyError
from app.database import get_db_context, init_db
from app.models.user import User
from app.models.room import Room, Area
from app.routers.auth import get_password_hash
from scripts.create_starter_area import create_starter_area

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user(username="admin", email="admin@example.com", password="admin"):
    """Create an admin user if one doesn't exist"""
    try:
        with get_db_context() as db:
            # Check if admin user already exists
            admin = db.query(User).filter(User.is_admin == True).first()
            if admin:
                logger.info(f"Admin user already exists: {admin.username}")
                return True
            
            # Use default password if not provided
            if not password:
                password = "admin"
                logger.info("Using default password: 'admin'")
            
            # Create admin user
            hashed_password = get_password_hash(password)
            admin_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                is_active=True,
                is_admin=True
            )
            
            db.add(admin_user)
            db.commit()
            
            logger.info(f"Created admin user: {username} with password: {password}")
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Database error creating admin user: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return False


async def setup_game():
    """Run all setup tasks"""
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Create admin user
        admin_created = await create_admin_user()
        if not admin_created:
            logger.warning("Failed to create admin user")
        
        # Create starter area
        await create_starter_area()
        
        logger.info("Game setup completed successfully!")
        
        # Report environment information
        logger.info("\nSetup Information:")
        logger.info("-" * 30)
        logger.info("Admin User: admin@example.com (username: admin)")
        with get_db_context() as db:
            user_count = db.query(User).count()
            
            # Import models here to avoid circular imports
            area_count = db.query(Area).count()
            room_count = db.query(Room).count()
            
        logger.info(f"User Count: {user_count}")
        logger.info(f"Area Count: {area_count}")
        logger.info(f"Room Count: {room_count}")
        logger.info("\nYou can now run the MUD server with: uvicorn app.main:app --reload")
        logger.info("Access the web interface at: http://localhost:8000")
        logger.info("-" * 30)
        
    except Exception as e:
        logger.error(f"Error during game setup: {str(e)}")


if __name__ == "__main__":
    # Run the setup
    asyncio.run(setup_game()) 