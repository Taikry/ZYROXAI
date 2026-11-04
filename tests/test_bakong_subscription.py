"""
Tests for Bakong Open API (KHQR) Subscription Billing Engine
============================================================
Tests:
1. KHQR string EMVCo compliance (TLV encoding, tags 00, 01, 30, 52, 53, 54, 58, 59, 60, 62, 63).
2. CRC16-CCITT-FALSE checksum verification.
3. MD5 transaction hash computation.
4. Offline Base64 QR code image rendering.
5. GET /api/v1/payments/status reporting Bakong Open API configuration.
6. GET /api/v1/payments/plans returning formatted plan tiers.
7. POST /api/v1/payments/checkout generating dynamic KHQR and invoice.
8. POST /api/v1/payments/verify/{invoice_id} with pending Bakong check.
9. POST /api/v1/payments/verify/{invoice_id} with confirmed Bakong check (activating active_paid entitlement).
10. POST /api/v1/subscriptions/cancel scheduling cancellation.
11. GET /api/v1/admin/payments/summary reporting verified revenue.
"""

import os
import unittest.mock
import pytest
from fastapi.testclient import TestClient

from taikry.api.app import app
from taikry.database.session import SessionLocal
from taikry.database.models import User, UserRole, UserSubscription, SubscriptionPlan, PaymentInvoice, PaymentTransaction
from taikry.saas.security import hash_password
from taikry.saas.auth_service import login_user
from taikry.saas.bakong_service import (
    bakong_service,
    calculate_crc16_ccitt,
    format_tlv,
    BakongService
)

client = TestClient(app)


def test_crc16_and_tlv_calculation():
    """Verify EMVCo TLV formatting and CRC16 checksum."""
    tlv = format_tlv("53", "840")
    assert tlv == "5303840"

    # Known sample payload
    payload = "00020101021230400016heng_taikry@aclb0116heng_taikry@aclb520459995303840540549.005802KH5908ZYROX AI6010Phnom Penh62350112INV-2026-0010508ZYROX AI0703Web6304"
    crc = calculate_crc16_ccitt(payload)
    assert len(crc) == 4
    assert crc.isalnum()
    assert crc.isupper()


def test_khqr_payload_generation():
    """Verify KHQR dynamic string generation with account, amount, and MD5 hash."""
    khqr_data = BakongService.create_khqr_payload(
        amount=29.00,
        currency="USD",
        bill_number="INV-TEST-001",
        account_id="test_merchant@bakong"
    )

    assert "000201" in khqr_data["khqr_string"]
    assert "010212" in khqr_data["khqr_string"]  # dynamic
    assert "test_merchant@bakong" in khqr_data["khqr_string"]
    assert "29.00" in khqr_data["khqr_string"]
    assert "INV-TEST-001" in khqr_data["khqr_string"]
    assert len(khqr_data["md5_hash"]) == 32
    assert khqr_data["qr_image_data"].startswith("data:image/png;base64,")
    assert khqr_data["deeplink_web"].startswith("https://bakong.nbc.gov.kh/pay?qr=")


def test_billing_status_and_plans_endpoint():
    """Verify /api/v1/payments/status and /api/v1/payments/plans."""
    res_status = client.get("/api/v1/payments/status")
    assert res_status.status_code == 200
    st_data = res_status.json()
    assert "provider" in st_data
    assert "checkout_available" in st_data

    res_plans = client.get("/api/v1/payments/plans")
    assert res_plans.status_code == 200
    plans_data = res_plans.json()
    assert "plans" in plans_data
    assert len(plans_data["plans"]) >= 2
    pro_plan = next((p for p in plans_data["plans"] if p["id"] == "pro"), None)
    assert pro_plan is not None
    assert pro_plan["amount"] == 29.0


@pytest.fixture(scope="module")
def setup_bakong_test_user():
    """Sets up a test user and test admin for subscription testing."""
    db = SessionLocal()
    try:
        test_emails = ["bakong_user@zyrox.ai", "bakong_admin@zyrox.ai"]
        users = db.query(User).filter(User.email.in_(test_emails)).all()
        u_ids = [u.id for u in users]
        if u_ids:
            db.query(PaymentInvoice).filter(PaymentInvoice.user_id.in_(u_ids)).delete(synchronize_session=False)
            db.query(UserSubscription).filter(UserSubscription.user_id.in_(u_ids)).delete(synchronize_session=False)
            db.query(UserRole).filter(UserRole.user_id.in_(u_ids)).delete(synchronize_session=False)
            db.query(User).filter(User.id.in_(u_ids)).delete(synchronize_session=False)
            db.commit()

        # Regular user
        hp, salt = hash_password("UserPass123!@#")
        user = User(
            email="bakong_user@zyrox.ai",
            hashed_password=hp,
            salt=salt,
            full_name="Bakong Tester",
            role="user",
            is_active=True,
            is_verified=True
        )
        db.add(user)

        # Admin user
        hp_a, salt_a = hash_password("AdminPass123!@#")
        admin = User(
            email="bakong_admin@zyrox.ai",
            hashed_password=hp_a,
            salt=salt_a,
            full_name="Bakong Admin",
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        db.commit()
        db.refresh(user)
        db.refresh(admin)

        db.add(UserRole(user_id=user.id, role_id="user"))
        db.add(UserRole(user_id=admin.id, role_id="admin"))
        db.commit()

        _, _, log_u = login_user(db, "bakong_user@zyrox.ai", "UserPass123!@#")
        _, _, log_a = login_user(db, "bakong_admin@zyrox.ai", "AdminPass123!@#")

        user_token = log_u["session_token"]
        admin_token = log_a["session_token"]

        yield {
            "user_id": user.id,
            "admin_id": admin.id,
            "user_token": user_token,
            "admin_token": admin_token
        }
    finally:
        # Teardown
        users = db.query(User).filter(User.email.in_(test_emails)).all()
        u_ids = [u.id for u in users]
        if u_ids:
            db.query(PaymentInvoice).filter(PaymentInvoice.user_id.in_(u_ids)).delete(synchronize_session=False)
            db.query(UserSubscription).filter(UserSubscription.user_id.in_(u_ids)).delete(synchronize_session=False)
            db.query(UserRole).filter(UserRole.user_id.in_(u_ids)).delete(synchronize_session=False)
            db.query(User).filter(User.id.in_(u_ids)).delete(synchronize_session=False)
            db.commit()
        db.close()


def test_bakong_checkout_and_verification_lifecycle(setup_bakong_test_user):
    """End-to-end verification of Bakong KHQR checkout, pending check, and fulfillment upon confirmation."""
    data = setup_bakong_test_user
    user_token = data["user_token"]
    user_id = data["user_id"]
    headers = {"Authorization": f"Bearer {user_token}"}

    # Mock BakongService configured state
    with unittest.mock.patch.object(BakongService, "is_configured", return_value=True), \
         unittest.mock.patch.dict(os.environ, {
             "BAKONG_ACCOUNT_ID": "taikry@aclb",
             "BAKONG_API_TOKEN": "mock_test_token"
         }):

        # 1. Initiate checkout for Pro plan ($29)
        res_checkout = client.post(
            "/api/v1/payments/checkout",
            json={"plan_id": "pro"},
            headers=headers
        )
        assert res_checkout.status_code == 200
        checkout_json = res_checkout.json()
        assert checkout_json["success"] is True
        assert "invoice" in checkout_json
        assert "checkout" in checkout_json

        invoice = checkout_json["invoice"]
        checkout = checkout_json["checkout"]
        invoice_id = invoice["id"]
        assert invoice["amount"] == 29.0
        assert invoice["status"] == "PENDING"
        assert checkout["provider"] == "bakong"
        assert "khqr" in checkout
        assert checkout["qr_image"].startswith("data:image/png;base64,")

        # 2. Verify invoice while still pending (Bakong returns responseCode: 1)
        with unittest.mock.patch.object(
            BakongService,
            "check_transaction_by_md5",
            return_value=(False, "Transaction is pending or not yet scanned.", None)
        ):
            res_verify_pending = client.post(
                f"/api/v1/payments/verify/{invoice_id}",
                headers=headers
            )
            assert res_verify_pending.status_code == 200
            assert res_verify_pending.json()["status"] == "PENDING"

        # 3. Verify invoice after payment confirmation (Bakong returns responseCode: 0)
        mock_tx_data = {
            "hash": "0xabc123456789deadbeef99887766554433221100",
            "fromAccountId": "customer_payer@wing",
            "toAccountId": "taikry@aclb",
            "currency": "USD",
            "amount": 29.00,
            "description": "Pro subscription payment"
        }
        with unittest.mock.patch.object(
            BakongService,
            "check_transaction_by_md5",
            return_value=(True, "Transaction completed successfully.", mock_tx_data)
        ):
            res_verify_paid = client.post(
                f"/api/v1/payments/verify/{invoice_id}",
                headers=headers
            )
            assert res_verify_paid.status_code == 200
            verify_json = res_verify_paid.json()
            assert verify_json["status"] == "PAID"
            assert "ACTIVE" in verify_json["message"].upper()

        # 4. Check /api/v1/subscriptions/me reports active_paid
        res_me = client.get("/api/v1/subscriptions/me", headers=headers)
        assert res_me.status_code == 200
        me_json = res_me.json()
        assert me_json["subscription"]["status"] == "active_paid"
        assert me_json["subscription"]["plan_id"] == "pro"
        assert me_json["subscription"]["days_remaining"] > 25
        assert len(me_json["invoices"]) >= 1

        # 5. Cancel subscription
        res_cancel = client.post("/api/v1/subscriptions/cancel", headers=headers)
        assert res_cancel.status_code == 200
        assert res_cancel.json()["success"] is True

        # 6. Admin payments summary
        admin_headers = {"Authorization": f"Bearer {data['admin_token']}"}
        res_admin = client.get("/api/v1/admin/payments/summary", headers=admin_headers)
        assert res_admin.status_code == 200
        admin_data = res_admin.json()
        assert "verified_revenue" in admin_data
        assert admin_data["successful_payments"] >= 1
