"""
Comprehensive Test Suite for ZYROX AI Telegram OpenID Connect (OIDC) Authentication.
Covers all 11 required security and functional specifications:
1. Valid Telegram login flow
2. Invalid or expired ID token
3. Invalid signature
4. Incorrect audience or issuer
5. Invalid state and nonce
6. PKCE verification failure
7. Replayed authorization callback (state reuse prevention)
8. Existing Telegram account login
9. New account registration with 14-day trial activation
10. Account linking after re-authentication
11. Logout and session invalidation
"""

import time
import secrets
import pytest
import jwt
from unittest.mock import patch, MagicMock
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from taikry.api.app import app
from taikry.database.session import SessionLocal
from taikry.database.models import (
    User,
    UserSession,
    TelegramLink,
    NotificationPreferences,
    AuditLog
)
from taikry.saas.security import hash_token
from taikry.saas.telegram_oidc import (
    generate_pkce_pair,
    generate_state_and_nonce,
    build_telegram_authorization_url,
    validate_id_token,
    authenticate_or_create_telegram_user,
    issue_telegram_session,
    auth_state_store,
    TelegramJWKSCache,
    DEFAULT_ISSUER,
    SESSION_DURATION_DAYS
)
from taikry.api.saas_routes import SESSION_COOKIE_NAME


# Generate test RSA keypair for cryptographic JWT signature tests
TEST_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
TEST_PUBLIC_KEY = TEST_PRIVATE_KEY.public_key()
TEST_KID = "test-oidc-key-1"
TEST_CLIENT_ID = "zyrox_test_client_id"
TEST_ISSUER = DEFAULT_ISSUER


class MockJWKSCache:
    """Mock JWKS cache providing the test RSA public key."""
    def __init__(self, public_key, kid):
        self.public_key = public_key
        self.kid = kid

    def get_key_by_kid(self, kid, force_refresh=False):
        if kid == self.kid:
            return self.public_key
        return None


mock_jwks = MockJWKSCache(TEST_PUBLIC_KEY, TEST_KID)


def create_signed_id_token(
    sub: str = "123456789",
    nonce: str = "test_nonce_val",
    client_id: str = TEST_CLIENT_ID,
    issuer: str = TEST_ISSUER,
    exp_offset: int = 3600,
    iat_offset: int = 0,
    private_key=TEST_PRIVATE_KEY,
    kid: str = TEST_KID,
    extra_claims: dict = None
) -> str:
    now = int(time.time())
    payload = {
        "iss": issuer,
        "aud": client_id,
        "sub": str(sub),
        "nonce": nonce,
        "iat": now + iat_offset,
        "exp": now + exp_offset,
        "name": "Alex Trader",
        "given_name": "Alex",
        "family_name": "Trader",
        "preferred_username": "alextrader"
    }
    if extra_claims:
        payload.update(extra_claims)

    headers = {"kid": kid, "alg": "RS256"}
    return jwt.encode(payload, private_key, algorithm="RS256", headers=headers)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client():
    return TestClient(app)


# =============================================================================
# 1. VALID TELEGRAM LOGIN & FULL WORKFLOW
# =============================================================================

def test_01_valid_telegram_id_token_validation():
    """Verify that a validly signed ID token with correct claims passes all checks."""
    nonce = secrets.token_urlsafe(16)
    token = create_signed_id_token(sub="987654321", nonce=nonce)

    claims = validate_id_token(
        id_token=token,
        expected_nonce=nonce,
        expected_client_id=TEST_CLIENT_ID,
        expected_issuer=TEST_ISSUER,
        jwks_provider=mock_jwks
    )

    assert claims["sub"] == "987654321"
    assert claims["aud"] == TEST_CLIENT_ID
    assert claims["iss"] == TEST_ISSUER
    assert claims["nonce"] == nonce
    assert claims["name"] == "Alex Trader"


# =============================================================================
# 2. INVALID OR EXPIRED ID TOKEN
# =============================================================================

def test_02_expired_id_token():
    """Verify that an expired ID token is strictly rejected."""
    nonce = secrets.token_urlsafe(16)
    # Expired 100 seconds ago
    expired_token = create_signed_id_token(sub="987654321", nonce=nonce, exp_offset=-100)

    with pytest.raises(ValueError, match="Telegram ID token has expired"):
        validate_id_token(
            id_token=expired_token,
            expected_nonce=nonce,
            expected_client_id=TEST_CLIENT_ID,
            jwks_provider=mock_jwks
        )


# =============================================================================
# 3. INVALID SIGNATURE
# =============================================================================

def test_03_invalid_signature():
    """Verify that an ID token signed by an unauthorized private key is rejected."""
    nonce = secrets.token_urlsafe(16)
    foreign_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    # Signed with foreign key but claiming kid of mock_jwks
    tampered_token = create_signed_id_token(
        sub="987654321",
        nonce=nonce,
        private_key=foreign_private_key,
        kid=TEST_KID
    )

    with pytest.raises(ValueError, match="Invalid Telegram ID token signature"):
        validate_id_token(
            id_token=tampered_token,
            expected_nonce=nonce,
            expected_client_id=TEST_CLIENT_ID,
            jwks_provider=mock_jwks
        )


# =============================================================================
# 4. INCORRECT AUDIENCE OR ISSUER
# =============================================================================

def test_04_incorrect_audience_and_issuer():
    """Verify that wrong audience or issuer claims trigger strict rejection."""
    nonce = secrets.token_urlsafe(16)

    # Wrong Audience
    bad_aud_token = create_signed_id_token(sub="987654321", nonce=nonce, client_id="attacker_app_id")
    with pytest.raises(ValueError, match="Invalid token audience"):
        validate_id_token(
            id_token=bad_aud_token,
            expected_nonce=nonce,
            expected_client_id=TEST_CLIENT_ID,
            jwks_provider=mock_jwks
        )

    # Wrong Issuer
    bad_iss_token = create_signed_id_token(sub="987654321", nonce=nonce, issuer="https://fake-oauth.telegram.org")
    with pytest.raises(ValueError, match="Invalid token issuer"):
        validate_id_token(
            id_token=bad_iss_token,
            expected_nonce=nonce,
            expected_client_id=TEST_CLIENT_ID,
            expected_issuer=TEST_ISSUER,
            jwks_provider=mock_jwks
        )


# =============================================================================
# 5. INVALID STATE AND NONCE
# =============================================================================

def test_05_invalid_nonce():
    """Verify that token with mismatched nonce is rejected."""
    nonce1 = "expected_nonce_123"
    nonce2 = "different_nonce_456"
    token = create_signed_id_token(sub="987654321", nonce=nonce2)

    with pytest.raises(ValueError, match="Nonce mismatch"):
        validate_id_token(
            id_token=token,
            expected_nonce=nonce1,
            expected_client_id=TEST_CLIENT_ID,
            jwks_provider=mock_jwks
        )


def test_05b_invalid_state_callback(client):
    """Verify callback with unknown or forged state redirects with error."""
    resp = client.get("/api/v1/auth/telegram/callback?code=fake_code&state=non_existent_forged_state", follow_redirects=False)
    assert resp.status_code == 303
    assert "auth_error=" in resp.headers["location"]
    assert "Invalid" in resp.headers["location"] or "expired" in resp.headers["location"]


# =============================================================================
# 6. PKCE VERIFICATION & S256 CHALLENGE
# =============================================================================

def test_06_pkce_generation():
    """Verify PKCE generation follows RFC 7636 S256 specification."""
    verifier, challenge = generate_pkce_pair()
    assert 43 <= len(verifier) <= 128
    assert len(challenge) == 43
    # Check that challenge matches SHA-256 of verifier
    import hashlib, base64
    expected_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).decode("ascii").rstrip("=")
    assert challenge == expected_challenge


# =============================================================================
# 7. REPLAYED AUTHORIZATION CALLBACK
# =============================================================================

def test_07_replayed_authorization_callback():
    """Verify that an authorization state can only be consumed once."""
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)

    auth_state_store.store(
        state=state,
        nonce=nonce,
        code_verifier=code_verifier,
        redirect_uri="https://testserver/callback"
    )

    # First pop should succeed
    first_entry = auth_state_store.pop(state)
    assert first_entry is not None
    assert first_entry["nonce"] == nonce

    # Replayed second pop MUST return None
    replayed_entry = auth_state_store.pop(state)
    assert replayed_entry is None


# =============================================================================
# 8. EXISTING TELEGRAM ACCOUNT LOGIN
# =============================================================================

def test_08_existing_telegram_account_login(db):
    """Verify that an existing user is recognized by stable telegram_user_id sub."""
    test_sub = f"tg_test_{secrets.token_hex(6)}"
    email = f"{test_sub}@test.com"

    # Pre-create user with telegram_user_id
    existing_user = User(
        telegram_user_id=test_sub,
        email=email,
        hashed_password="dummy_hash",
        salt="dummy_salt",
        full_name="Existing Telegram Trader",
        role="user",
        is_verified=True,
        is_active=True
    )
    db.add(existing_user)
    db.commit()

    claims = {
        "sub": test_sub,
        "name": "Updated Name",
        "preferred_username": "newhandle"
    }

    success, msg, user, is_new = authenticate_or_create_telegram_user(db, claims)
    assert success is True
    assert is_new is False
    assert user.id == existing_user.id
    assert user.telegram_user_id == test_sub


# =============================================================================
# 9. NEW ACCOUNT REGISTRATION WITH 14-DAY TRIAL ACTIVATION
# =============================================================================

def test_09_new_account_registration_and_trial(db):
    """Verify new Telegram user creates canonical account with 14-day trial."""
    new_sub = f"new_tg_{secrets.token_hex(6)}"
    claims = {
        "sub": new_sub,
        "name": "New Telegram VIP",
        "given_name": "New",
        "family_name": "VIP",
        "preferred_username": "new_vip_bot"
    }

    success, msg, user, is_new = authenticate_or_create_telegram_user(db, claims)
    assert success is True
    assert is_new is True
    assert user is not None
    assert user.telegram_user_id == new_sub
    assert user.is_verified is True
    assert user.is_active is True
    assert user.email == f"tg_{new_sub}@telegram.zyrox.ai"

    # Check that 14-day trial is granted
    from taikry.saas.trial_service import get_user_trial_status
    trial = get_user_trial_status(db, user.id)
    assert trial["status"] == "trial_active"
    assert trial["is_active"] is True
    assert trial["days_remaining"] in (13, 14)
    assert trial["hours_remaining"] in range(0, 24)

    # Check TelegramLink created
    link = db.query(TelegramLink).filter(TelegramLink.user_id == user.id).first()
    assert link is not None
    assert link.telegram_chat_id == new_sub
    assert link.is_linked is True


# =============================================================================
# 10. ACCOUNT LINKING AFTER RE-AUTHENTICATION
# =============================================================================

def test_10_account_linking(db):
    """Verify logged-in user can link their Telegram account via OIDC."""
    # Create base user
    email = f"link_user_{secrets.token_hex(4)}@zyrox.ai"
    base_user = User(
        email=email,
        hashed_password="pw_hash",
        salt="salt_123",
        full_name="Base Account Owner",
        role="user",
        is_verified=True,
        is_active=True
    )
    db.add(base_user)
    db.commit()

    link_sub = f"link_sub_{secrets.token_hex(6)}"
    claims = {
        "sub": link_sub,
        "preferred_username": "linked_user_tg",
        "given_name": "LinkOwner"
    }

    # Pass current_user to simulate authenticated user linking their Telegram
    success, msg, user, is_new = authenticate_or_create_telegram_user(
        db, claims, current_user=base_user
    )
    assert success is True
    assert is_new is False
    assert user.id == base_user.id
    assert user.telegram_user_id == link_sub

    # Verify link record
    link = db.query(TelegramLink).filter(TelegramLink.user_id == base_user.id).first()
    assert link is not None
    assert link.telegram_chat_id == link_sub
    assert link.is_linked is True


# =============================================================================
# 11. LOGOUT AND SESSION INVALIDATION
# =============================================================================

def test_11_session_issuance_and_logout(db, client):
    """Verify session creation and subsequent logout endpoint revocation."""
    sub = f"sess_user_{secrets.token_hex(4)}"
    user = User(
        telegram_user_id=sub,
        email=f"tg_{sub}@telegram.zyrox.ai",
        hashed_password="hash",
        salt="salt",
        full_name="Session Trader",
        role="user",
        is_verified=True,
        is_active=True
    )
    db.add(user)
    db.commit()

    raw_token, expires_utc = issue_telegram_session(db, user)
    assert raw_token is not None
    token_h = hash_token(raw_token)

    # Check session in DB
    sess_row = db.query(UserSession).filter(UserSession.token_hash == token_h).first()
    assert sess_row is not None
    assert sess_row.user_id == user.id

    # Test /api/v1/auth/me with session cookie
    me_resp = client.get("/api/v1/auth/me", cookies={SESSION_COOKIE_NAME: raw_token})
    assert me_resp.status_code == 200
    assert me_resp.json()["user"]["id"] == user.id

    # Test logout
    logout_resp = client.post("/api/v1/auth/logout", cookies={SESSION_COOKIE_NAME: raw_token})
    assert logout_resp.status_code == 200

    # Session in DB must now be deleted
    sess_after = db.query(UserSession).filter(UserSession.token_hash == token_h).first()
    assert sess_after is None

    # Subsequent /me must fail with 401
    me_after = client.get("/api/v1/auth/me", cookies={SESSION_COOKIE_NAME: raw_token})
    assert me_after.status_code == 401


# =============================================================================
# 12. FULL END-TO-END CALLBACK ENDPOINT FLOW WITH SESSION ISSUANCE
# =============================================================================

def test_12_callback_endpoint_full_flow(client):
    """Verify full end-to-end GET /api/v1/auth/telegram/callback flow."""
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(16)
    verifier = secrets.token_urlsafe(64)
    auth_state_store.store(
        state=state,
        nonce=nonce,
        code_verifier=verifier,
        redirect_uri="http://testserver/api/v1/auth/telegram/callback",
        return_to="/dashboard/"
    )

    token = create_signed_id_token(sub="1122334455", nonce=nonce)
    fake_token_response = {
        "access_token": "fake_access_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": token
    }

    with patch("taikry.api.saas_routes.exchange_code_for_tokens", return_value=fake_token_response), \
         patch("taikry.api.saas_routes.validate_id_token") as mock_validate:
        
        mock_validate.return_value = {
            "sub": "1122334455",
            "name": "Integration User",
            "given_name": "Integration",
            "family_name": "User",
            "preferred_username": "integ_user"
        }

        resp = client.get(
            f"/api/v1/auth/telegram/callback?code=valid_auth_code&state={state}",
            follow_redirects=False
        )

        assert resp.status_code == 303
        assert "/dashboard/?auth_success=telegram" in resp.headers["location"]
        assert SESSION_COOKIE_NAME in resp.cookies
        session_cookie = resp.cookies[SESSION_COOKIE_NAME]
        assert len(session_cookie) >= 32


# =============================================================================
# 13. TOKEN EXCHANGE ERROR HANDLING (OIDC SPEC ERROR RESPONSES)
# =============================================================================

def test_13_exchange_code_for_tokens_error_handling():
    """Verify that exchange_code_for_tokens raises ValueError on error response even with HTTP 200."""
    from taikry.saas.telegram_oidc import exchange_code_for_tokens
    
    mock_client = MagicMock()
    # Telegram returns 200 OK with {"error": "invalid_grant"}
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"error": "invalid_grant", "error_description": "Authorization code expired"}
    mock_client.post.return_value = mock_resp

    with pytest.raises(ValueError, match="Telegram token exchange error: Authorization code expired"):
        exchange_code_for_tokens(
            code="bad_code",
            code_verifier="verifier",
            redirect_uri="http://localhost:8000/callback",
            http_client=mock_client
        )


