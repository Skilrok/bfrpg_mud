#!/usr/bin/env python
"""
Script to create an admin user in the database
"""

from app.database import SessionLocal
from app.models import User
from app.auth.password import get_password_hash

def create_admin_user():
    """Create an admin user account"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == 'admin').first()
        if existing_user:
            print("Admin user already exists")
            return
            
        # Create a new admin user
        user = User(
            username='admin',
            email='admin@example.com',
            hashed_password=get_password_hash('password123'),
            is_active=True,
            is_admin=True
        )
        db.add(user)
        db.commit()
        print("Admin user created successfully")
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 