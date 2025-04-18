import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app import models
from app.routers.auth import get_current_user

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_basic.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Create a test user and override authentication
async def get_test_current_user():
    return {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
    }


app.dependency_overrides[get_current_user] = get_test_current_user

# Test client
client = TestClient(app)


def test_get_hirelings():
    response = client.get("/api/hirelings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to BFRPG MUD API"}
