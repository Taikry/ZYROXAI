"""
ZYROX AI V6 — Phase 1 P0 Security Test Suite
Tests:
- A: Dashboard Authentication Gate (unauthenticated redirected, authenticated passed)
- B: AI Chat Authentication (401 on missing credentials, 403 on invalid/suspended, 200 on authenticated)
- C: MT5 Bridge Authentication (fail closed when token missing, constant-time compare, valid pass)
- D: Telegram OIDC (no secret leaks in public endpoints, NEEDS_CONFIGURATION status)
- E: Admin/User RBAC (admin endpoints reject non-admin / anonymous users with 401/403)
"""
import time
import pytest
from fastapi.testclient import TestClient

from taikry.api.app import app
from taikry.database.session import SessionLocal
from taikry.database.models import User, UserSession, UserRole
from taikry.saas.auth_service import sign_up_user, login_user
from taikry.data.mt5_receiver import MT5BridgeReceiver


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def setup_security_users():
    db = SessionLocal()
    from taikry.database.models import TrialGrantRecord, UserSubscription
    # Clean up test accounts and trial grant history
    test_emails = ["v6_sec_user@zyrox.ai", "v6_sec_admin@zyrox.ai"]
    for email in test_emails:
        db.query(TrialGrantRecord).filter(TrialGrantRecord.email == email).delete()
        u = db.query(User).filter(User.email == email).first()
        if u:
            db.query(UserSubscription).filter(UserSubscription.user_id == u.id).delete()
            db.query(UserSession).filter(UserSession.user_id == u.id).delete()
            db.query(UserRole).filter(UserRole.user_id == u.id).delete()
            db.delete(u)
    db.commit()

    # Create standard user
    ok_u, _, _ = sign_up_user(db, "v6_sec_user@zyrox.ai", "Password123!", "V6 Sec User")
    assert ok_u
    ok_login_u, _, data_u = login_user(db, "v6_sec_user@zyrox.ai", "Password123!")
    assert ok_login_u
    user_token = data_u["session_token"]
    user_id = data_u["user"]["id"]

    # Create admin user
    ok_a, _, _ = sign_up_user(db, "v6_sec_admin@zyrox.ai", "Password123!", "V6 Sec Admin")
    assert ok_a
    admin = db.query(User).filter(User.email == "v6_sec_admin@zyrox.ai").first()
    admin.role = "admin"
    admin_ur = UserRole(user_id=admin.id, role_id="admin")
    db.add(admin_ur)
    db.commit()
    ok_login_a, _, data_a = login_user(db, "v6_sec_admin@zyrox.ai", "Password123!")
    assert ok_login_a
    admin_token = data_a["session_token"]
    admin_id = data_a["user"]["id"]

    db.close()

    return {
        "user_token": user_token,
        "user_id": user_id,
        "admin_token": admin_token,
        "admin_id": admin_id
    }


# =============================================================================
# 1. PHASE 1.A: DASHBOARD AUTHENTICATION GATE
# =============================================================================

def test_dashboard_unauthenticated_redirect(client):
    """Anonymous visitors to /dashboard/ must be redirected to signin."""
    res = client.get("/dashboard/", follow_redirects=False)
    assert res.status_code == 303
    assert "/?auth=signin" in res.headers["location"]


def test_dashboard_direct_index_redirect(client):
    """Anonymous visitors to /dashboard/index.html must be redirected."""
    res = client.get("/dashboard/index.html", follow_redirects=False)
    assert res.status_code == 303
    assert "/?auth=signin" in res.headers["location"]


def test_dashboard_authenticated_success(client, setup_security_users):
    """Authenticated user with session cookie can access /dashboard/."""
    user_token = setup_security_users["user_token"]
    res = client.get(
        "/dashboard/",
        cookies={"zyrox_session": user_token},
        follow_redirects=False
    )
    assert res.status_code == 200
    assert "text/html" in res.headers.get("content-type", "")


def test_admin_page_unauthenticated_redirect(client):
    """Unauthenticated visitor to /admin must be redirected to signin."""
    res = client.get("/admin", follow_redirects=False)
    assert res.status_code == 303
    assert "/?auth=signin" in res.headers["location"]


def test_billing_page_unauthenticated_redirect(client):
    """Unauthenticated visitor to /billing must be redirected to signin."""
    res = client.get("/billing", follow_redirects=False)
    assert res.status_code == 303
    assert "/?auth=signin" in res.headers["location"]


# =============================================================================
# 2. PHASE 1.B: AI CHAT AUTHENTICATION
# =============================================================================

def test_ai_chat_unauthenticated_rejected(client):
    """POST /api/v1/ai/chat without credentials must return HTTP 401."""
    res = client.post(
        "/api/v1/ai/chat",
        json={"query": "Hello AI", "symbol": "XAUUSD"}
    )
    assert res.status_code == 401
    assert "Authentication required" in res.json().get("detail", "")


def test_ai_chat_invalid_token_rejected(client):
    """POST /api/v1/ai/chat with bogus token must return HTTP 401."""
    res = client.post(
        "/api/v1/ai/chat",
        json={"query": "Hello AI", "symbol": "XAUUSD"},
        headers={"Authorization": "Bearer invalid_bogus_token_1234567890"}
    )
    assert res.status_code == 401


def test_ai_chat_authenticated_success(client, setup_security_users):
    """POST /api/v1/ai/chat with valid token must succeed."""
    user_token = setup_security_users["user_token"]
    res = client.post(
        "/api/v1/ai/chat",
        json={"query": "HELLO", "symbol": "XAUUSD", "timeframe": "15m"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "response" in data or "smart_analysis" in data or "card" in data or "query" in data


def test_ai_chat_empty_query_rejected(client, setup_security_users):
    """POST /api/v1/ai/chat with empty query must return HTTP 400."""
    user_token = setup_security_users["user_token"]
    res = client.post(
        "/api/v1/ai/chat",
        json={"query": "   ", "symbol": "XAUUSD"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 400


# =============================================================================
# 3. PHASE 1.C: MT5 BRIDGE AUTHENTICATION
# =============================================================================

def test_mt5_bridge_fails_closed_when_token_unset(monkeypatch):
    """MT5 receiver must fail closed if MT5_BRIDGE_TOKEN is None or empty."""
    from taikry.data import mt5_receiver as mod_mt5
    receiver = MT5BridgeReceiver()

    monkeypatch.setattr(mod_mt5, "MT5_BRIDGE_ENABLED", True)
    monkeypatch.setattr(mod_mt5, "MT5_BRIDGE_TOKEN", "")

    # Even with a provided token, it must fail closed if server token is unset
    now_ts = str(time.time())
    result = receiver.verify_auth_token("some_token", timestamp_header=now_ts)
    assert result is False


def test_mt5_bridge_rejects_invalid_token(monkeypatch):
    """MT5 receiver must reject invalid bridge tokens using constant-time check."""
    from taikry.data import mt5_receiver as mod_mt5
    receiver = MT5BridgeReceiver()

    monkeypatch.setattr(mod_mt5, "MT5_BRIDGE_ENABLED", True)
    monkeypatch.setattr(mod_mt5, "MT5_BRIDGE_TOKEN", "real_secret_token_123")

    now_ts = str(time.time())
    assert receiver.verify_auth_token("wrong_token", timestamp_header=now_ts) is False
    assert receiver.verify_auth_token("real_secret_token_123", timestamp_header=now_ts) is True


# =============================================================================
# 4. PHASE 1.D: TELEGRAM OIDC SECURITY
# =============================================================================

def test_telegram_oidc_status_does_not_leak_secrets(client):
    """GET /api/v1/auth/telegram/status must NEVER expose client secrets."""
    res = client.get("/api/v1/auth/telegram/status")
    assert res.status_code == 200
    data = res.json()
    assert "client_secret" not in data
    assert "status" in data
    assert data["status"] in ("READY", "NEEDS_CONFIGURATION")


# =============================================================================
# 5. PHASE 1.E: RBAC ENFORCEMENT
# =============================================================================

def test_admin_api_rejects_anonymous_user(client):
    """Admin APIs must reject unauthenticated requests with HTTP 401."""
    res = client.get("/api/v1/admin/analytics")
    assert res.status_code == 401


def test_admin_api_rejects_regular_user(client, setup_security_users):
    """Admin APIs must reject regular non-admin users with HTTP 403."""
    user_token = setup_security_users["user_token"]
    res = client.get(
        "/api/v1/admin/analytics",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert res.status_code == 403


def test_admin_api_accepts_admin_user(client, setup_security_users):
    """Admin APIs must allow verified admin users with HTTP 200."""
    admin_token = setup_security_users["admin_token"]
    res = client.get(
        "/api/v1/admin/analytics",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
