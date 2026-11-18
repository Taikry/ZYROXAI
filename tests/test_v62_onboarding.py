"""
V6.2 / V6.2.1 Onboarding & Interactive Tutorial Test Suite
Tests:
- First-time login onboarding status (completed=False, step=1, dismissed=False)
- Progressive tutorial step advancement (step 1 -> 14)
- Persistent completion flag and dismissal
- Tutorial reset to step 1
- Dashboard preferences read and write
- Multi-user isolation (one user's tutorial state does not leak to another)
"""
import pytest
import datetime
from starlette.testclient import TestClient
from taikry.api.app import app
from taikry.database.session import SessionLocal
from taikry.database.models import User, UserSession
from taikry.saas.security import hash_password, hash_token

SESSION_COOKIE_NAME = "zyrox_session"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_onboarding_users():
    db = SessionLocal()
    salt, hpass = hash_password("ValidPassword123!")

    # User A: Brand new first-time user
    user_a = db.query(User).filter(User.email == "onboarding_new_user@zyrox.ai").first()
    if not user_a:
        user_a = User(
            email="onboarding_new_user@zyrox.ai",
            full_name="New Trader",
            hashed_password=hpass,
            salt=salt,
            role="USER",
            is_verified=True,
            is_active=True,
            onboarding_completed=False,
            onboarding_step=1,
            onboarding_dismissed=False,
            tutorial_version="v6.2.1"
        )
        db.add(user_a)
        db.commit()
        db.refresh(user_a)
    else:
        user_a.onboarding_completed = False
        user_a.onboarding_step = 1
        user_a.onboarding_dismissed = False
        db.commit()

    # Session for User A
    tok_a = "onboarding_tok_a_12345678901234567890"
    thash_a = hash_token(tok_a)
    s_a = db.query(UserSession).filter(UserSession.token_hash == thash_a).first()
    if not s_a:
        s_a = UserSession(
            user_id=user_a.id,
            token_hash=thash_a,
            ip_address="127.0.0.1",
            user_agent="Playwright Test",
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
        )
        db.add(s_a)
        db.commit()

    # User B: Returning user
    user_b = db.query(User).filter(User.email == "onboarding_user_b@zyrox.ai").first()
    if not user_b:
        user_b = User(
            email="onboarding_user_b@zyrox.ai",
            full_name="Experienced Trader",
            hashed_password=hpass,
            salt=salt,
            role="USER",
            is_verified=True,
            is_active=True,
            onboarding_completed=True,
            onboarding_step=14,
            onboarding_dismissed=False,
            tutorial_version="v6.2.1"
        )
        db.add(user_b)
        db.commit()
        db.refresh(user_b)

    tok_b = "onboarding_tok_b_12345678901234567890"
    thash_b = hash_token(tok_b)
    s_b = db.query(UserSession).filter(UserSession.token_hash == thash_b).first()
    if not s_b:
        s_b = UserSession(
            user_id=user_b.id,
            token_hash=thash_b,
            ip_address="127.0.0.1",
            user_agent="Playwright Test",
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
        )
        db.add(s_b)
        db.commit()

    db.close()
    return (user_a, tok_a), (user_b, tok_b)


def test_onboarding_unauthenticated_fails(client):
    res = client.get("/api/v1/user/onboarding")
    assert res.status_code == 401


def test_onboarding_first_time_user_read(client, test_onboarding_users):
    (user_a, tok_a), _ = test_onboarding_users
    client.cookies.set(SESSION_COOKIE_NAME, tok_a)

    res = client.get("/api/v1/user/onboarding")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["onboarding_completed"] is False
    assert data["onboarding_step"] == 1
    assert data["onboarding_dismissed"] is False
    assert data["tutorial_version"] == "v6.2.1"


def test_onboarding_step_progression(client, test_onboarding_users):
    (user_a, tok_a), _ = test_onboarding_users
    client.cookies.set(SESSION_COOKIE_NAME, tok_a)

    # Advance to step 5
    res = client.post("/api/v1/user/onboarding", json={"step": 5})
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["onboarding_step"] == 5
    assert data["onboarding_completed"] is False

    # Check persistence
    res = client.get("/api/v1/user/onboarding")
    assert res.json()["onboarding_step"] == 5


def test_onboarding_completion(client, test_onboarding_users):
    (user_a, tok_a), _ = test_onboarding_users
    client.cookies.set(SESSION_COOKIE_NAME, tok_a)

    # Complete tutorial
    res = client.post("/api/v1/user/onboarding", json={"step": 14, "completed": True})
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["onboarding_completed"] is True
    assert data["onboarding_step"] == 14

    # Check via /api/v1/auth/me
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 200
    me_data = res.json()
    assert me_data["onboarding"]["completed"] is True
    assert me_data["onboarding"]["step"] == 14


def test_onboarding_reset(client, test_onboarding_users):
    (user_a, tok_a), _ = test_onboarding_users
    client.cookies.set(SESSION_COOKIE_NAME, tok_a)

    # Reset
    res = client.post("/api/v1/user/onboarding/reset")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["onboarding_completed"] is False
    assert data["onboarding_step"] == 1
    assert data["onboarding_dismissed"] is False


def test_user_preferences_read_write(client, test_onboarding_users):
    (user_a, tok_a), _ = test_onboarding_users
    client.cookies.set(SESSION_COOKIE_NAME, tok_a)

    # Write preferences
    res = client.post("/api/v1/user/preferences", json={
        "preferences": {"chart_theme": "dark", "sound_alerts": False},
        "language": "kh"
    })
    assert res.status_code == 200

    # Read back
    res = client.get("/api/v1/user/preferences")
    assert res.status_code == 200
    data = res.json()
    assert data["preferences"]["chart_theme"] == "dark"
    assert data["preferences"]["sound_alerts"] is False
    assert data["language"] == "kh"


def test_onboarding_multi_user_isolation(client, test_onboarding_users):
    (user_a, tok_a), (user_b, tok_b) = test_onboarding_users

    # Verify User B is completed while User A is reset
    client.cookies.set(SESSION_COOKIE_NAME, tok_b)
    res_b = client.get("/api/v1/user/onboarding")
    assert res_b.json()["onboarding_completed"] is True
    assert res_b.json()["onboarding_step"] == 14

    client.cookies.set(SESSION_COOKIE_NAME, tok_a)
    res_a = client.get("/api/v1/user/onboarding")
    assert res_a.json()["onboarding_completed"] is False
    assert res_a.json()["onboarding_step"] == 1
