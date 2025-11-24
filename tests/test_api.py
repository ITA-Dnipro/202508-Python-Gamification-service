import sys
import os
from pathlib import Path
import pytest
import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import Base
from app import models

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
Base.metadata.create_all(bind=TEST_ENGINE)
TEST_SESSION_MAKER = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

import app.database as db_module
db_module.engine = TEST_ENGINE
db_module.SessionLocal = TEST_SESSION_MAKER

from app.main import app
from app.routers.gamification import get_db


@pytest.fixture(scope="function")
def test_db():
    """Create a test database session with test data."""
    db = TEST_SESSION_MAKER()
    
    existing = db.query(models.ExpAction).filter(
        models.ExpAction.name == "test_action",
        models.ExpAction.role == "startup"
    ).first()
    
    if not existing:
        action = models.ExpAction(
            name="test_action",
            role="startup",
            exp_value=50,
            repeatable=False,
            description="Test action"
        )
        db.add(action)
        db.commit()
    
    yield db
    
    db.query(models.ExpTransaction).delete()
    db.query(models.UserExperience).delete()
    db.commit()
    db.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with database override."""
    def override_get_db():
        db = TEST_SESSION_MAKER()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    
    app.dependency_overrides.clear()


def create_test_token(user_id, role):
    return jwt.encode({"user_id": user_id, "role": role}, "test_secret", algorithm="HS256")


def test_successful_exp_award(client, test_db):
    """Test successful EXP award to a startup user."""
    token = create_test_token(1, "startup")
    response = client.post(
        "/api/gamification/startup/1/award-exp",
        json={
            "action_name": "test_action",
            "reference_id": 101
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["role"] == "startup"
    assert data["total_exp"] == 50


def test_duplicate_prevention(client, test_db):
    """Test that duplicate EXP awards are prevented."""
    token = create_test_token(2, "startup")
    response1 = client.post(
        "/api/gamification/startup/2/award-exp",
        json={
            "action_name": "test_action",
            "reference_id": 102
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 200
    
    response2 = client.post(
        "/api/gamification/startup/2/award-exp",
        json={
            "action_name": "test_action",
            "reference_id": 102
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code in [400, 500]


def test_fetch_user_exp_total(client, test_db):
    """Test fetching user's total EXP."""
    token = create_test_token(3, "startup")
    client.post(
        "/api/gamification/startup/3/award-exp",
        json={
            "action_name": "test_action",
            "reference_id": 103
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.get("/api/gamification/startup/3/experience")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 3
    assert data["role"] == "startup"
    assert data["total_exp"] == 50
