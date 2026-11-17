"""
Tests for ZYROX AI V6.1 Authentication Flows:
- Google OAuth 2.0 PKCE / Authorization Code Flow
- Phone SMS OTP Verification Engine
"""
import pytest
import datetime
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from taikry.api.app import app
from taikry.database.session import SessionLocal
from taikry.database.models import User, PhoneOTPChallenge, UserSession
from taikry.saas.google_oauth import (
    is_google_auth_configured,
    get_google_auth_status,
    build_google_authorization_url,
    google_state_cache,
    generate_pkce_pair,
    authenticate_or_register_google_user
)
from taikry.saas.phone_otp import (
    normalize_e164_phone,
    generate_secure_otp,
    is_phone_auth_configured,
    get_phone_auth_status,
    request_phone_otp,
    verify_phone_otp_challenge
)


@pytest.fixture
def client():
    return TestClient(app)


def test_google_auth_status_unconfigured(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)

    status = get_google_auth_status()
    assert status["configured"] is False
    assert status["status"] == "NEEDS_CONFIGURATION"
    assert "GOOGLE_CLIENT_ID" in status["required_env_vars"]

    ok, msg = build_google_authorization_url()
    assert ok is False
    assert "not configured" in msg


def test_google_pkce_and_state_cache():
    verifier, challenge = generate_pkce_pair()
    assert len(verifier) >= 43
    assert len(challenge) >= 43

    google_state_cache.store("test_state_123", "test_nonce_456", verifier, "/dashboard/")
    popped = google_state_cache.pop("test_state_123")
    assert popped is not None
    assert popped["nonce"] == "test_nonce_456"
    assert popped["code_verifier"] == verifier

    # Replay protection: popping again returns None
    assert google_state_cache.pop("test_state_123") is None


def test_google_user_registration_and_linking():
    db = SessionLocal()
    try:
        sub = "google_user_unique_9988"
        email = "test_google_trader@example.com"
        claims = {
            "sub": sub,
            "email": email,
            "name": "Google Test Trader",
            "email_verified": True
        }

        # Clean existing test user if present
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            db.query(UserSession).filter(UserSession.user_id == existing.id).delete()
            db.delete(existing)
            db.commit()

        success, user, token, is_new, err = authenticate_or_register_google_user(
            db=db,
            claims=claims,
            client_ip="127.0.0.1",
            user_agent="Pytest-Agent"
        )

        assert success is True
        assert user is not None
        assert user.email == email
        assert user.google_user_id == sub
        assert is_new is True
        assert token is not None

        # Re-login with same Google sub (should not be new user)
        s2, u2, t2, is_new2, err2 = authenticate_or_register_google_user(
            db=db,
            claims=claims,
            client_ip="127.0.0.1"
        )
        assert s2 is True
        assert u2.id == user.id
        assert is_new2 is False
    finally:
        db.close()


def test_phone_e164_normalization():
    assert normalize_e164_phone("+85512345678") == "+85512345678"
    assert normalize_e164_phone("012345678") == "+85512345678"  # Local Cambodia normalization
    assert normalize_e164_phone("+1 (555) 234-5678") == "+15552345678"
    assert normalize_e164_phone("invalid_phone") is None
    assert normalize_e164_phone("") is None


def test_phone_otp_generation():
    code, salt, digest = generate_secure_otp()
    assert len(code) == 6
    assert code.isdigit()
    assert len(salt) == 32
    assert len(digest) == 64


def test_phone_auth_status_unconfigured(monkeypatch):
    monkeypatch.delenv("TWILIO_ACCOUNT_SID", raising=False)
    monkeypatch.delenv("TWILIO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TWILIO_PHONE_NUMBER", raising=False)

    status = get_phone_auth_status()
    assert status["configured"] is False
    assert status["status"] == "NEEDS_CONFIGURATION"
    assert "TWILIO_ACCOUNT_SID" in status["required_env_vars"]


def test_phone_otp_challenge_flow_and_verification(monkeypatch):
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACmockaccount00000000000000000000")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "mocktoken000000000000000000000000")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+15005550006")

    # Mock actual twilio SMS delivery to succeed without network call
    from taikry.saas import phone_otp
    monkeypatch.setattr(phone_otp, "send_twilio_sms", lambda to, msg: (True, "Mock SMS sent"))

    db = SessionLocal()
    phone = "+85599887766"
    try:
        # 1. Clean previous challenges
        db.query(PhoneOTPChallenge).filter(PhoneOTPChallenge.phone_number == phone).delete()
        db.commit()

        # 2. Request OTP
        ok, msg, meta = request_phone_otp(db, phone, client_ip="127.0.0.1")
        assert ok is True
        assert "sent" in msg.lower()

        # Retrieve stored challenge to inspect
        ch = db.query(PhoneOTPChallenge).filter(
            PhoneOTPChallenge.phone_number == phone,
            PhoneOTPChallenge.is_used.is_(False)
        ).first()
        assert ch is not None
        assert ch.attempts == 0
        assert ch.max_attempts == 5
        assert len(ch.otp_hash) == 64

        # 3. Test wrong code fails and increments attempts
        v_bad, _, _, _, bad_msg = verify_phone_otp_challenge(db, phone, "000000")
        assert v_bad is False
        assert "remaining" in bad_msg

        db.refresh(ch)
        assert ch.attempts == 1

        # 4. Verify with correct code by reconstructing valid digest match
        # To test without brute forcing, we use the known code if we generate a controlled one
        ch.salt = "testsalt"
        import hashlib
        ch.otp_hash = hashlib.sha256(("testsalt" + "654321").encode("utf-8")).hexdigest()
        db.commit()

        v_ok, user, token, is_new, _ = verify_phone_otp_challenge(db, phone, "654321")
        assert v_ok is True
        assert user is not None
        assert user.phone_number == phone
        assert token is not None

        # 5. Challenge is single-use; verifying again fails
        v_replay, _, _, _, _ = verify_phone_otp_challenge(db, phone, "654321")
        assert v_replay is False
    finally:
        db.close()
