from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Base
from app.database import DATABASE_URL
from app.routers.auth import get_password_hash

# Create an engine that connects to the database
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a test user
username = "testuser"
email = "test@example.com"
password = "password123"

# Hash the password
hashed_password = get_password_hash(password)

# Create a session
db = SessionLocal()

try:
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    
    if existing_user:
        print(f"User {username} already exists")
    else:
        # Create a new user
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"User {username} created with ID {user.id}")
        
    # Print login credentials
    print("\nLogin credentials:")
    print(f"Username: {username}")
    print(f"Password: {password}")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
    
finally:
    db.close() 