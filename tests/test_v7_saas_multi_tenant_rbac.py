"""
Tests for ZYROX AI V7 — Multi-Tenant SaaS, RBAC & Strict User Data Isolation
=============================================================================
Tests:
1. User registration, default 'user' role assignment, and 14-day trial activation.
2. Login returning session token, user roles, and granular permissions.
3. Strict User Data Isolation: User B cannot access User A's private V6 setup (403 Forbidden).
4. Role Hierarchy: Standard user cannot access Admin endpoints (403), Admin cannot access Super Admin (403).
5. Super Admin Secret Protection: is_secret=True values are strictly masked as '[redacted]'.
6. Feature Flag management and canary rollout toggling.
7. AI Research Chat structured evidence sections (verified data, indicators, news, AI interpretation, unavailable data).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from taikry.api.app import app
from taikry.database.session import SessionLocal, engine
from taikry.database.models import User, UserRole, SystemSetting, FeatureFlag
from taikry.v6.db_models import V6BestSetupModel
from taikry.saas.security import hash_password, generate_session_token, get_user_roles, get_user_permissions
from taikry.saas.auth_service import sign_up_user, login_user
from taikry.ai.llm_client import chat_with_real_ai

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_test_users():
    """Sets up super_admin, admin, user_a, and user_b test accounts."""
    db = SessionLocal()
    try:
        # Clean any preexisting test users and their roles
        test_emails = [
            "v7_superadmin@zyrox.ai",
            "v7_admin@zyrox.ai",
            "v7_usera@zyrox.ai",
            "v7_userb@zyrox.ai"
        ]
        old_users = db.query(User).filter(User.email.in_(test_emails)).all()
        for u in old_users:
            db.query(UserRole).filter(UserRole.user_id == u.id).delete()
        db.query(User).filter(User.email.in_(test_emails)).delete(synchronize_session=False)
        db.commit()

        # 1. Create Super Admin
        hp, salt = hash_password("SuperAdminPass123!@#")
        super_admin = User(
            email="v7_superadmin@zyrox.ai",
            hashed_password=hp,
            salt=salt,
            full_name="Super Administrator",
            role="super_admin",
            is_active=True,
            is_verified=True
        )
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        db.add(UserRole(user_id=super_admin.id, role_id="super_admin"))

        # 2. Create Admin
        hp, salt = hash_password("PlatformAdmin123!@#")
        admin = User(
            email="v7_admin@zyrox.ai",
            hashed_password=hp,
            salt=salt,
            full_name="Operations Admin",
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        db.add(UserRole(user_id=admin.id, role_id="admin"))

        # 3. Create User A
        hp, salt = hash_password("TraderPass123!@#")
        user_a = User(
            email="v7_usera@zyrox.ai",
            hashed_password=hp,
            salt=salt,
            full_name="Trader Alice",
            role="user",
            is_active=True,
            is_verified=True
        )
        db.add(user_a)
        db.commit()
        db.refresh(user_a)
        db.add(UserRole(user_id=user_a.id, role_id="user"))

        # 4. Create User B
        hp, salt = hash_password("TraderPass123!@#")
        user_b = User(
            email="v7_userb@zyrox.ai",
            hashed_password=hp,
            salt=salt,
            full_name="Trader Bob",
            role="user",
            is_active=True,
            is_verified=True
        )
        db.add(user_b)
        db.commit()
        db.refresh(user_b)
        db.add(UserRole(user_id=user_b.id, role_id="user"))
        db.commit()

        # Generate login tokens
        _, _, log_sa = login_user(db, "v7_superadmin@zyrox.ai", "SuperAdminPass123!@#")
        _, _, log_ad = login_user(db, "v7_admin@zyrox.ai", "PlatformAdmin123!@#")
        _, _, log_ua = login_user(db, "v7_usera@zyrox.ai", "TraderPass123!@#")
        _, _, log_ub = login_user(db, "v7_userb@zyrox.ai", "TraderPass123!@#")

        tokens = {
            "super_admin": log_sa["session_token"],
            "admin": log_ad["session_token"],
            "user_a": log_ua["session_token"],
            "user_b": log_ub["session_token"],
            "user_a_id": user_a.id,
            "user_b_id": user_b.id,
            "admin_id": admin.id,
            "super_admin_id": super_admin.id
        }
    finally:
        db.close()

    yield tokens

    # Teardown
    db = SessionLocal()
    try:
        old_users = db.query(User).filter(User.email.in_(test_emails)).all()
        for u in old_users:
            db.query(UserRole).filter(UserRole.user_id == u.id).delete()
        db.query(User).filter(User.email.in_(test_emails)).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()


def test_user_signup_and_default_role():
    """Verify signup assigns role='user' and creates UserRole mapping."""
    db = SessionLocal()
    try:
        email = "test_signup_v7@example.com"
        old_u = db.query(User).filter(User.email == email).first()
        if old_u:
            db.query(UserRole).filter(UserRole.user_id == old_u.id).delete()
            db.query(User).filter(User.id == old_u.id).delete()
            db.commit()

        ok, msg, data = sign_up_user(db, email, "StrongTraderPass999!", full_name="New Trader")
        assert ok is True
        assert "activated" in msg.lower()
        user_id = data["user_id"]

        user = db.query(User).filter(User.id == user_id).first()
        assert user is not None
        assert user.role == "user"

        roles = get_user_roles(db, user_id)
        assert "user" in roles

        perms = get_user_permissions(db, user_id)
        assert "analysis.use" in perms
        assert "subscriptions.read" in perms
        # Should not have admin permissions
        assert "admins.manage" not in perms
        assert "system.settings.manage" not in perms
    finally:
        old_u = db.query(User).filter(User.email == "test_signup_v7@example.com").first()
        if old_u:
            db.query(UserRole).filter(UserRole.user_id == old_u.id).delete()
            db.query(User).filter(User.id == old_u.id).delete()
            db.commit()
        db.close()


def test_login_returns_roles_and_permissions(setup_test_users):
    """Verify login payload includes user roles and permissions array."""
    db = SessionLocal()
    try:
        ok, msg, data = login_user(db, "v7_usera@zyrox.ai", "TraderPass123!@#")
        assert ok is True
        user_info = data["user"]
        assert "roles" in user_info
        assert "user" in user_info["roles"]
        assert "permissions" in user_info
        assert isinstance(user_info["permissions"], list)
    finally:
        db.close()


def test_strict_user_data_isolation_v6_setups(setup_test_users):
    """User B must be rejected (403 Forbidden) when accessing User A's private setup."""
    tokens = setup_test_users
    db = SessionLocal()
    setup_id = "test_setup_iso_001"
    try:
        # Create a private setup owned by User A
        db.query(V6BestSetupModel).filter(V6BestSetupModel.setup_id == setup_id).delete()
        db.commit()

        setup_row = V6BestSetupModel(
            setup_id=setup_id,
            user_id=tokens["user_a_id"],
            symbol="XAUUSD",
            timeframe="M15",
            direction="BUY",
            regime="TREND_BULLISH_STRONG",
            quality_score=85,
            quality_classification="HIGH_QUALITY",
            entry_type="LIMIT",
            entry_price=2750.50,
            stop_loss=2740.00,
            tp1=2765.00,
            trade_plan_json={"direction": "BUY", "entry_price": 2750.50, "stop_loss": 2740.00, "tp1": 2765.00},
            quality_score_json={"total_score": 85, "classification": "HIGH_QUALITY"}
        )
        db.add(setup_row)
        db.commit()

        # 1. Unauthenticated request -> 401 Unauthorized
        res_anon = client.get(f"/api/v6/setups/{setup_id}")
        assert res_anon.status_code == 401

        # 2. User B (different tenant) -> 403 Forbidden
        headers_b = {"Authorization": f"Bearer {tokens['user_b']}"}
        res_b = client.get(f"/api/v6/setups/{setup_id}", headers=headers_b)
        assert res_b.status_code == 403
        assert "Access forbidden" in res_b.json().get("detail", "")

        # 3. User A (owner) -> 200 OK
        headers_a = {"Authorization": f"Bearer {tokens['user_a']}"}
        res_a = client.get(f"/api/v6/setups/{setup_id}", headers=headers_a)
        assert res_a.status_code == 200
        assert res_a.json()["setup_id"] == setup_id

        # 4. Admin (operational supervisor) -> 200 OK
        headers_admin = {"Authorization": f"Bearer {tokens['admin']}"}
        res_admin = client.get(f"/api/v6/setups/{setup_id}", headers=headers_admin)
        assert res_admin.status_code == 200
    finally:
        db.query(V6BestSetupModel).filter(V6BestSetupModel.setup_id == setup_id).delete()
        db.commit()
        db.close()


def test_role_hierarchy_and_permissions(setup_test_users):
    """
    Standard user cannot access Admin endpoints (403).
    Admin cannot access Super Admin endpoints (403).
    Super Admin has full access.
    """
    tokens = setup_test_users

    # 1. User A tries to access admin analytics -> 403
    res_user_to_admin = client.get("/api/v1/admin/analytics", headers={"Authorization": f"Bearer {tokens['user_a']}"})
    assert res_user_to_admin.status_code == 403

    # 2. Admin accesses admin analytics -> 200
    res_admin_to_admin = client.get("/api/v1/admin/analytics", headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res_admin_to_admin.status_code == 200

    # 3. Admin tries to access Super Admin governance -> 403
    res_admin_to_super = client.get("/api/v1/super-admin/admins", headers={"Authorization": f"Bearer {tokens['admin']}"})
    assert res_admin_to_super.status_code == 403
    assert "Super Administrator privileges required" in res_admin_to_super.json().get("detail", "")

    # 4. Super Admin accesses Super Admin governance -> 200
    res_super_to_super = client.get("/api/v1/super-admin/admins", headers={"Authorization": f"Bearer {tokens['super_admin']}"})
    assert res_super_to_super.status_code == 200
    assert "admins" in res_super_to_super.json()


def test_super_admin_secret_masking(setup_test_users):
    """Verify that is_secret=True values are NEVER leaked in GET responses."""
    tokens = setup_test_users
    headers_super = {"Authorization": f"Bearer {tokens['super_admin']}"}

    # Upsert a secret setting
    res_upsert = client.post("/api/v1/super-admin/system-settings", headers=headers_super, json={
        "key": "TEST_EXCHANGE_SECRET_KEY",
        "value": "super_secret_api_key_xyz_9876",
        "is_secret": True,
        "description": "Sensitive exchange API key"
    })
    assert res_upsert.status_code == 200

    # Retrieve all settings
    res_get = client.get("/api/v1/super-admin/system-settings", headers=headers_super)
    assert res_get.status_code == 200
    settings = res_get.json().get("settings", [])
    target = next((s for s in settings if s["key"] == "TEST_EXCHANGE_SECRET_KEY"), None)
    assert target is not None
    assert target["is_secret"] is True
    # MUST BE MASKED
    assert target["value"] == "[redacted]"
    assert "super_secret_api_key_xyz_9876" not in target["value"]


def test_feature_flags_toggle(setup_test_users):
    """Verify Super Admin can toggle feature flags."""
    tokens = setup_test_users
    headers_super = {"Authorization": f"Bearer {tokens['super_admin']}"}

    res = client.post("/api/v1/super-admin/feature-flags/v6_technical_intelligence", headers=headers_super, json={
        "enabled": True,
        "rollout_percentage": 100,
        "allowed_roles": ["super_admin", "admin", "premium_user", "user"]
    })
    assert res.status_code == 200
    assert res.json()["flag"]["enabled"] is True
    assert res.json()["flag"]["rollout_percentage"] == 100


def test_ai_research_chat_evidence_sections():
    """Verify AI Research Chat returns structured evidence sections."""
    res = chat_with_real_ai("Analyze XAUUSD current technical regime and liquidity zones", symbol="XAUUSD", timeframe="15m")
    assert "status" in res
    assert "evidence_sections" in res

    ev = res["evidence_sections"]
    assert "verified_market_data" in ev
    assert "calculated_indicators" in ev
    assert "verified_news" in ev
    assert "ai_interpretation" in ev
    assert "unavailable_data" in ev

    # Verify market data transparency
    m_data = ev["verified_market_data"]
    assert m_data["symbol"] == "XAUUSD"
    assert "price" in m_data
    assert "freshness" in m_data
