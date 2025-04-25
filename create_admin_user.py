import os
import sys

from passlib.context import CryptContext

# REMOVED: from sqlalchemy import insert

# Add the current directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User

# Set up password hashing - same as in app/routers/auth.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def main():
    """Create an admin user in the database"""
    print("Creating admin user...")

    # Connect to database
    db = SessionLocal()

    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.username == "admin").first()

        if admin:
            print(f"Admin user already exists with ID: {admin.id}")
            return

        # Hash the password
        hashed_password = get_password_hash("password123")

        # Create new admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
        )

        # Add to database
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"Admin user created successfully with ID: {admin.id}")

    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    main()
