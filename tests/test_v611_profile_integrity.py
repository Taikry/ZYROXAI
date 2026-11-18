"""
Tests for Phase G: User Profile & Device History Data Integrity.
Verifies:
- ZERO hardcoded placeholders in /api/v1/auth/me.
- Empty fields return None instead of fabricated fallbacks.
- Device history returns real active sessions only (empty list when no sessions).
- Only exact token hash match yields is_current=True.
- Real is_verified flag is honored.
"""
import datetime
import pytest
from fastapi.testclient import TestClient
from taikry.api.app import app
from taikry.database.session import SessionLocal, init_db
from taikry.database.models import User, UserSession
from taikry.saas.security import hash_password, hash_token

SESSION_COOKIE_NAME = "zyrox_session"


@pytest.fixture
def client():
    init_db()
    return TestClient(app)


def test_profile_zero_hardcoded_placeholders_for_empty_user(client):
    db = SessionLocal()
    email = "empty_profile_user_v611@zyrox.ai"
    try:
        # Delete if exists
        db.query(User).filter_by(email=email).delete()
        db.commit()

        salt, hpass = hash_password("EmptyPass123!")
        user = User(
            email=email,
            hashed_password=hpass,
            salt=salt,
            full_name=None,
            phone_number=None,
            country=None,
            telegram_user_id=None,
            is_verified=False,
            is_active=True,
            role="USER",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create session with token
        raw_token = "empty_user_test_token_99999999999999999999"
        thash = hash_token(raw_token)
        # Intentionally create NO UserSession records in DB to verify empty device list!

        client.cookies.set(SESSION_COOKIE_NAME, raw_token)
        # Mock get_current_user returning this user
        from taikry.api.saas_routes import get_current_user
        app.dependency_overrides[get_current_user] = lambda: user

        res = client.get("/api/v1/auth/me")
        assert res.status_code == 200
        data = res.json()

        u = data["user"]
        # CRITICAL VERIFICATIONS: ZERO HARDCODED FALLBACKS
        assert u["full_name"] is None, "full_name must be None when not set, not 'Heng Taikry'"
        assert u["mobile_phone"] is None, "mobile_phone must be None when not set, not '0968288832'"
        assert u["telegram"] is None, "telegram must be None when not set, not '@heng_taikry'"
        assert u["country"] is None, "country must be None when not set, not 'Cambodia'"
        assert u["is_verified"] is False, "is_verified must be real False, not forced True"

        # Devices list must be empty [] (no fabricated Safari Mac sessions)
        devices = data["devices"]
        assert isinstance(devices, list)
        assert len(devices) == 0, f"Expected 0 devices for user with no sessions, got {len(devices)}"

    finally:
        app.dependency_overrides.clear()
        db.query(User).filter_by(email=email).delete()
        db.commit()
        db.close()


def test_profile_current_device_exact_token_match(client):
    db = SessionLocal()
    email = "device_matching_user_v611@zyrox.ai"
    try:
        db.query(User).filter_by(email=email).delete()
        db.commit()

        salt, hpass = hash_password("ValidPass123!")
        user = User(
            email=email,
            hashed_password=hpass,
            salt=salt,
            full_name="Alice Trader",
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create two sessions in DB: session1 and session2
        raw_token_1 = "tok_session_1_valid_abcdef1234567890"
        raw_token_2 = "tok_session_2_valid_abcdef1234567890"

        s1 = UserSession(
            user_id=user.id,
            token_hash=hash_token(raw_token_1),
            ip_address="10.0.0.1",
            user_agent="Firefox on Linux",
            last_seen_at=datetime.datetime.now(datetime.timezone.utc),
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
        )
        s2 = UserSession(
            user_id=user.id,
            token_hash=hash_token(raw_token_2),
            ip_address="10.0.0.2",
            user_agent="Chrome on Windows",
            last_seen_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=2),
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1),
        )
        db.add_all([s1, s2])
        db.commit()

        from taikry.api.saas_routes import get_current_user
        app.dependency_overrides[get_current_user] = lambda: user

        # Request with session 1 cookie
        client.cookies.set(SESSION_COOKIE_NAME, raw_token_1)
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 200
        devs = res.json()["devices"]
        assert len(devs) == 2

        curr_dev = next(d for d in devs if d["is_current"])
        other_dev = next(d for d in devs if not d["is_current"])

        assert curr_dev["ip_address"] == "10.0.0.1"
        assert curr_dev["status"] == "This device"
        assert other_dev["ip_address"] == "10.0.0.2"
        assert other_dev["status"] == "Signed out"

    finally:
        app.dependency_overrides.clear()
        db.query(UserSession).filter_by(user_id=user.id).delete()
        db.query(User).filter_by(email=email).delete()
        db.commit()
        db.close()
