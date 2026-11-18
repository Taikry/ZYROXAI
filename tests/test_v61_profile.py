"""
ZYROX AI V6.1 - User Profile & Device History Integration Tests
Verifies that the /api/v1/auth/me endpoint correctly returns enriched user profile data,
plan details, and device history matching the institutional design specification.
"""

import pytest
from fastapi.testclient import TestClient
from taikry.api.app import app
from taikry.database.session import SessionLocal
from taikry.database.models import User, UserSession
from taikry.saas.security import hash_token
from taikry.api.saas_routes import SESSION_COOKIE_NAME
import datetime


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_user_session():
    db = SessionLocal()
    email = "prof_test_user@zyrox.ai"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        from taikry.saas.security import hash_password
        salt, hpass = hash_password("ValidPassword123!")
        user = User(
            email=email,
            full_name="Heng Taikry",
            phone_number="0968288899",
            country="Cambodia",
            hashed_password=hpass,
            salt=salt,
            role="USER",
            is_verified=True,
            is_active=True,
            language="en",
            timezone="Asia/Phnom_Penh",
            created_at=datetime.datetime(2026, 7, 6, 12, 0, 0, tzinfo=datetime.timezone.utc)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.country = "Cambodia"
        user.phone_number = "0968288899"
        db.commit()

    # Create session
    raw_token = "prof_test_raw_token_xyz_12345678901234567890"
    thash = hash_token(raw_token)
    session = db.query(UserSession).filter(UserSession.token_hash == thash).first()
    if not session:
        session = UserSession(
            user_id=user.id,
            token_hash=thash,
            ip_address="175.100.52.54",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
            last_seen_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)
        )
        db.add(session)
        db.commit()

    db.close()
    return user, raw_token


def test_auth_me_unauthenticated(client):
    """Accessing /api/v1/auth/me without a session must return 401."""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_auth_me_returns_profile_spec(client, test_user_session):
    """Accessing /api/v1/auth/me with a valid session returns enriched profile and devices."""
    user, raw_token = test_user_session
    client.cookies.set(SESSION_COOKIE_NAME, raw_token)

    res = client.get("/api/v1/auth/me")
    assert res.status_code == 200
    data = res.json()

    assert "user" in data
    assert "plan" in data
    assert "devices" in data

    u = data["user"]
    assert u["full_name"] == "Heng Taikry"
    assert u["handle"] == "@hengtaikry"
    assert u["email"] == "prof_test_user@zyrox.ai"
    assert u["country"] == "Cambodia"
    assert u["country_flag"] == "🇰🇭"
    assert u["mobile_phone"] == "0968288899"
    assert u["member_since"] == "Jul 06, 2026"
    assert u["is_verified"] is True

    p = data["plan"]
    assert "name" in p
    assert "badge" in p
    assert "subtitle" in p
    assert "notice" in p

    devs = data["devices"]
    assert len(devs) >= 1
    current_dev = next((d for d in devs if d["is_current"]), None)
    assert current_dev is not None
    assert current_dev["status"] == "This device"
    assert "Safari · Mac" in current_dev["browser_os"]


def test_update_profile_phone_and_language(client, test_user_session):
    """PUT /api/v1/auth/profile updates full name, phone number, and language."""
    user, raw_token = test_user_session
    client.cookies.set(SESSION_COOKIE_NAME, raw_token)

    update_payload = {
        "full_name": "Heng Taikry",
        "phone_number": "0968288899",
        "language": "kh",
        "timezone": "Asia/Phnom_Penh"
    }
    res = client.put("/api/v1/auth/profile", json=update_payload)
    assert res.status_code == 200

    # Fetch updated profile
    res2 = client.get("/api/v1/auth/me")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["user"]["phone_number"] == "0968288899" or data2["user"]["mobile_phone"] == "0968288899"
    assert data2["user"]["language"] == "kh"
