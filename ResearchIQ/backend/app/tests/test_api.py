"""
Integration and API endpoint tests for ResearchIQ FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.session import Base, get_db

# Use in-memory SQLite for testing API endpoints
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ResearchIQ API"


def test_register_and_login_flow():
    # 1. Register
    reg_payload = {
        "email": "researcher@university.edu",
        "full_name": "Dr. Alan Turing",
        "password": "SecurePassword123!"
    }
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    user_data = reg_resp.json()
    assert user_data["email"] == "researcher@university.edu"

    # 2. Duplicate registration rejection
    dup_resp = client.post("/api/auth/register", json=reg_payload)
    assert dup_resp.status_code == 400

    # 3. Login
    login_data = {
        "username": "researcher@university.edu",
        "password": "SecurePassword123!"
    }
    login_resp = client.post("/api/auth/login", data=login_data)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 4. Access protected profile endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "researcher@university.edu"


def test_papers_list_empty():
    # Login as user
    login_data = {
        "username": "researcher@university.edu",
        "password": "SecurePassword123!"
    }
    login_resp = client.post("/api/auth/login", data=login_data)
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/papers", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
