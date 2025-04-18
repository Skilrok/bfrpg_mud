import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.routers.auth import get_current_user
from tests.test_auth import get_test_user


@pytest.fixture(autouse=True)
def override_auth_dependency():
    """Override the authentication dependency for all tests"""
    app.dependency_overrides[get_current_user] = get_test_user
    yield
    app.dependency_overrides.clear()
