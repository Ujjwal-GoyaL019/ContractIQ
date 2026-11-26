import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.dependencies import get_db, require_admin, require_analyst_or_admin
from app.db.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

# In-memory SQLite DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_password_hashing():
    raw = "SecureSecret!99"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_flow():
    payload_data = {"sub": "usr_123", "email": "test@contractiq.ai", "role": "admin"}
    token = create_access_token(payload_data)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "usr_123"
    assert decoded["email"] == "test@contractiq.ai"
    assert decoded["role"] == "admin"


def test_user_registration():
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "sarah@contractiq.ai",
            "password": "Password123!",
            "full_name": "Sarah Connor",
            "role": "admin",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "sarah@contractiq.ai"
    assert data["user"]["role"] == "admin"


def test_duplicate_registration_fails():
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@contractiq.ai",
            "password": "Password123!",
            "full_name": "Duplicate User",
            "role": "procurement_analyst",
        },
    )
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@contractiq.ai",
            "password": "AnotherPassword456!",
            "full_name": "Duplicate User 2",
            "role": "procurement_analyst",
        },
    )
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_user_login_success_and_failure():
    # Register user first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "analyst@contractiq.ai",
            "password": "ValidPassword123!",
            "full_name": "Marcus Analyst",
            "role": "procurement_analyst",
        },
    )

    # Correct login
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@contractiq.ai", "password": "ValidPassword123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    # Incorrect login
    bad_res = client.post(
        "/api/v1/auth/login",
        json={"email": "analyst@contractiq.ai", "password": "WrongPassword!"},
    )
    assert bad_res.status_code == 401


def test_auth_me_endpoint():
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "viewer@contractiq.ai",
            "password": "ViewerPassword123!",
            "full_name": "Alex Viewer",
            "role": "viewer",
        },
    )
    token = reg.json()["access_token"]

    # Call /me with valid token
    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "viewer@contractiq.ai"
    assert me_res.json()["role"] == "viewer"

    # Call /me with invalid token
    bad_me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.xyz"},
    )
    assert bad_me.status_code == 401


def test_rbac_restrictions():
    # Create an admin and a viewer user
    admin_user = User(
        id="adm_1",
        email="adm@contractiq.ai",
        hashed_password="hash",
        full_name="Admin",
        role="admin",
        is_active=True,
    )
    viewer_user = User(
        id="view_1",
        email="view@contractiq.ai",
        hashed_password="hash",
        full_name="Viewer",
        role="viewer",
        is_active=True,
    )

    assert require_admin(admin_user) == admin_user
    with pytest.raises(Exception):
        require_admin(viewer_user)

    assert require_analyst_or_admin(admin_user) == admin_user
    with pytest.raises(Exception):
        require_analyst_or_admin(viewer_user)
