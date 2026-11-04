"""
Test suite for Zero-Trust Session Token Refresh endpoint (POST /api/v1/auth/refresh).
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from taikry.api.app import app

client = TestClient(app)


def test_auth_refresh_flow():
    """Verify session token rotation and refresh lifecycle."""
    test_email = f"refresh_user_{uuid.uuid4().hex[:8]}@example.com"
    test_password = "RefreshSecurePass123!"

    # 1. Sign up
    signup_res = client.post("/api/v1/auth/signup", json={
        "email": test_email,
        "password": test_password,
        "full_name": "Refresh Tester"
    })
    assert signup_res.status_code == 200, signup_res.text

    # 2. Login to get initial session token
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": test_password
    })
    assert login_res.status_code == 200, login_res.text
    initial_data = login_res.json()["data"]
    initial_token = initial_data["session_token"]
    assert initial_token

    # 3. Call refresh endpoint with initial Bearer token
    refresh_res = client.post("/api/v1/auth/refresh", headers={
        "Authorization": f"Bearer {initial_token}"
    })
    assert refresh_res.status_code == 200, refresh_res.text
    refresh_json = refresh_res.json()
    assert refresh_json["success"] is True
    new_token = refresh_json["data"]["session_token"]
    assert new_token != initial_token, "Token must be rotated"

    # 4. Old token should now be invalidated
    old_token_res = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {initial_token}"
    })
    assert old_token_res.status_code == 401, "Old token must be rejected"

    # 5. New token should be valid
    new_token_res = client.get("/api/v1/auth/me", headers={
        "Authorization": f"Bearer {new_token}"
    })
    assert new_token_res.status_code == 200
    assert new_token_res.json()["user"]["email"] == test_email


def test_auth_refresh_unauthorized_rejection():
    """Verify refresh fails on invalid or missing tokens."""
    unauthed_client = TestClient(app)
    res_no_token = unauthed_client.post("/api/v1/auth/refresh")
    assert res_no_token.status_code == 401

    res_fake_token = unauthed_client.post("/api/v1/auth/refresh", headers={
        "Authorization": "Bearer fake_token_that_does_not_exist_in_db_12345"
    })
    assert res_fake_token.status_code == 401
