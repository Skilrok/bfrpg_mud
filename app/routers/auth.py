from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
import traceback
import logging
from .. import models, schemas
from ..database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Security configuration
SECRET_KEY = "your-secret-key-keep-it-secret"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = (
        db.query(models.User)
        .filter(models.User.username == token_data.username)
        .first()
    )
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        logger.info(f"Attempting to register user: {user.username}")
        
        # Check if username already exists
        db_user = db.query(models.User).filter(models.User.username == user.username).first()
        if db_user:
            logger.warning(f"Username already registered: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if db_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        logger.info(f"Password hashed successfully")
        
        db_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        
        logger.info(f"Adding user to database")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User committed to database with ID: {db_user.id}")
        
        # Convert SQLAlchemy model to dictionary and create Pydantic model
        user_data = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "is_active": db_user.is_active
        }
        logger.info(f"Created user data dictionary: {user_data}")
        
        # Create and return the User schema
        pydantic_user = schemas.User(**user_data)
        logger.info(f"Created pydantic user: {pydantic_user}")
        return pydantic_user
        
    except Exception as e:
        logger.error(f"Error in user registration: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration error: {str(e)}"
        )


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: models.User = Depends(get_current_user)):
    """Endpoint for user logout (requires authentication)"""
    # For JWT, logout is handled client-side by removing the token
    # We simply acknowledge the request here
    return {"message": "Successfully logged out"}


@router.get("/debug-register")
async def debug_register(db: Session = Depends(get_db)):
    """Debug endpoint to test user registration"""
    try:
        # Create test user
        hashed_password = get_password_hash("testpassword")
        test_username = f"debug_user_{datetime.utcnow().timestamp()}"
        test_email = f"{test_username}@example.com"
        
        db_user = models.User(
            username=test_username,
            email=test_email,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Test dictionary conversion
        user_data = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "is_active": db_user.is_active
        }
        
        # Test pydantic model creation
        pydantic_user = schemas.User(**user_data)
        
        return {
            "success": True,
            "user_data": user_data,
            "pydantic_user": pydantic_user.dict()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e))
        }


@router.post("/register-simple")
async def register_user_simple(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """A simplified version of the register endpoint for debugging"""
    try:
        # Return only simple data to ensure our response works
        return {
            "id": 1,
            "username": user.username,
            "email": user.email,
            "is_active": True
        }
    except Exception as e:
        logger.error(f"Error in simple registration: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": str(e)}
