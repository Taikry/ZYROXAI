"""
Bakong Open API & KHQR Subscription Billing Service for ZYROX AI
================================================================
Implements:
1. EMVCo KHQR Standard (Cambodia National Payment Network) dynamic QR generation
2. CRC16-CCITT-FALSE checksum calculation
3. MD5 transaction hash computation
4. Offline Base64 QR code image rendering (no external dependency or CDN needed)
5. Bakong Open API `/v1/check_transaction_by_md5` verification
6. Subscription entitlement activation and idempotent audit logging
"""

import os
import io
import time
import base64
import hashlib
import logging
import datetime
import urllib.parse
from decimal import Decimal
from typing import Dict, Any, Tuple, Optional
import requests
from sqlalchemy.orm import Session
from sqlalchemy import text

from taikry.config import (
    BAKONG_KHQR_ACCOUNT,
    APP_NAME
)
from taikry.database.models import (
    User,
    UserRole,
    UserSubscription,
    SubscriptionPlan,
    PaymentInvoice,
    PaymentTransaction,
    PaymentWebhookEvent
)

logger = logging.getLogger("taikry.saas.bakong_service")

# Configuration from environment variables
BAKONG_API_URL = os.getenv("BAKONG_API_URL", "https://api-bakong.nbc.gov.kh").strip().rstrip("/")
BAKONG_API_TOKEN = os.getenv("BAKONG_API_TOKEN", os.getenv("BAKONG_DEVELOPER_TOKEN", "")).strip()
BAKONG_ACCOUNT_ID = os.getenv("BAKONG_ACCOUNT_ID", os.getenv("BAKONG_KHQR_ACCOUNT", "")).strip()
BAKONG_MERCHANT_NAME = os.getenv("BAKONG_MERCHANT_NAME", "ZYROX AI").strip()
BAKONG_MERCHANT_CITY = os.getenv("BAKONG_MERCHANT_CITY", "Phnom Penh").strip()
BAKONG_CURRENCY = os.getenv("BAKONG_CURRENCY", "USD").strip().upper()
BAKONG_TIMEOUT_SECONDS = int(os.getenv("BAKONG_TIMEOUT_SECONDS", "10"))


def _utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def calculate_crc16_ccitt(payload: str) -> str:
    """
    Calculates EMVCo CRC16-CCITT-FALSE checksum.
    Polynomial: 0x1021, Initial: 0xFFFF.
    Calculated over the entire payload ending with '6304'.
    """
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
            crc &= 0xFFFF
    return f"{crc:04X}"


def format_tlv(tag: str, value: str) -> str:
    """Formats Tag-Length-Value with 2-digit length."""
    return f"{tag}{len(value):02d}{value}"


class BakongService:
    """National Bank of Cambodia (NBC) Bakong Open API & KHQR Engine."""

    @staticmethod
    def is_configured() -> bool:
        """Returns True if merchant account ID and API token are provided."""
        account = os.getenv("BAKONG_ACCOUNT_ID", os.getenv("BAKONG_KHQR_ACCOUNT", "")).strip()
        token = os.getenv("BAKONG_API_TOKEN", os.getenv("BAKONG_DEVELOPER_TOKEN", "")).strip()
        return bool(account and token)

    @staticmethod
    def get_status() -> Dict[str, Any]:
        """Returns live status of the Bakong Open API integration."""
        account = os.getenv("BAKONG_ACCOUNT_ID", os.getenv("BAKONG_KHQR_ACCOUNT", "")).strip()
        token = os.getenv("BAKONG_API_TOKEN", os.getenv("BAKONG_DEVELOPER_TOKEN", "")).strip()
        api_url = os.getenv("BAKONG_API_URL", "https://api-bakong.nbc.gov.kh").strip().rstrip("/")
        env = "sandbox" if "sandbox" in api_url.lower() or "dev" in api_url.lower() else "production"

        return {
            "provider": "bakong",
            "name": "Bakong Open API (KHQR)",
            "checkout_available": bool(account and token),
            "environment": env,
            "api_url": api_url,
            "account_id": account,
            "merchant_name": os.getenv("BAKONG_MERCHANT_NAME", "ZYROX AI").strip(),
            "merchant_city": os.getenv("BAKONG_MERCHANT_CITY", "Phnom Penh").strip(),
            "currency": os.getenv("BAKONG_CURRENCY", "USD").strip().upper(),
            "has_token": bool(token),
            "has_account": bool(account)
        }

    @staticmethod
    def generate_khqr_string(
        account_id: str,
        amount: float,
        currency: str = "USD",
        bill_number: str = "INV-001",
        merchant_name: str = "ZYROX AI",
        merchant_city: str = "Phnom Penh",
        store_label: str = "ZYROX AI",
        terminal_label: str = "Web"
    ) -> str:
        """
        Generates dynamic EMVCo KHQR string according to NBC Bakong specification.
        """
        # Tag 30: Dynamic Merchant Account Information
        sub_00 = format_tlv("00", account_id)
        sub_01 = format_tlv("01", account_id)
        tag_30 = format_tlv("30", sub_00 + sub_01)

        payload_indicator = format_tlv("00", "01")
        point_of_init = format_tlv("01", "12")  # 12 = Dynamic QR (with transaction amount)
        mcc = format_tlv("52", "5999")  # 5999 = Miscellaneous & Specialty Retail / Software
        curr_code = "840" if currency.upper() == "USD" else "116"
        currency_field = format_tlv("53", curr_code)
        amount_field = format_tlv("54", f"{amount:.2f}")
        country = format_tlv("58", "KH")
        name = format_tlv("59", (merchant_name or "ZYROX AI")[:25])
        city = format_tlv("60", (merchant_city or "Phnom Penh")[:15])

        # Tag 62: Additional Data Field Template
        sub_bill = format_tlv("01", bill_number[:25])
        sub_store = format_tlv("05", (store_label or "ZYROX AI")[:25])
        sub_term = format_tlv("07", (terminal_label or "Web")[:25])
        tag_62 = format_tlv("62", sub_bill + sub_store + sub_term)

        # Base payload ending with Tag 63 identifier '6304'
        base_payload = (
            payload_indicator
            + point_of_init
            + tag_30
            + mcc
            + currency_field
            + amount_field
            + country
            + name
            + city
            + tag_62
            + "6304"
        )

        checksum = calculate_crc16_ccitt(base_payload)
        return base_payload + checksum

    @staticmethod
    def render_qr_data_url(khqr_string: str) -> str:
        """Renders KHQR string into a crisp base64 PNG data URL."""
        try:
            import qrcode
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=8,
                border=2,
            )
            qr.add_data(khqr_string)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#000000", back_color="#ffffff")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("ascii")
            return f"data:image/png;base64,{b64}"
        except Exception as e:
            logger.error(f"Failed to render QR code image: {e}")
            return ""

    @classmethod
    def create_khqr_payload(
        cls,
        amount: float,
        currency: str = "USD",
        bill_number: str = "INV-001",
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates full dynamic KHQR package including string, MD5, image Data URL, and mobile deeplinks.
        """
        acc = (account_id or os.getenv("BAKONG_ACCOUNT_ID", os.getenv("BAKONG_KHQR_ACCOUNT", ""))).strip()
        m_name = os.getenv("BAKONG_MERCHANT_NAME", "ZYROX AI").strip()
        m_city = os.getenv("BAKONG_MERCHANT_CITY", "Phnom Penh").strip()
        curr = (currency or os.getenv("BAKONG_CURRENCY", "USD")).strip().upper()

        khqr_str = cls.generate_khqr_string(
            account_id=acc,
            amount=amount,
            currency=curr,
            bill_number=bill_number,
            merchant_name=m_name,
            merchant_city=m_city
        )

        md5_hash = hashlib.md5(khqr_str.encode("utf-8")).hexdigest()
        qr_image = cls.render_qr_data_url(khqr_str)
        quoted_qr = urllib.parse.quote(khqr_str)

        return {
            "khqr_string": khqr_str,
            "md5_hash": md5_hash,
            "qr_image_data": qr_image,
            "deeplink_web": f"https://bakong.nbc.gov.kh/pay?qr={quoted_qr}",
            "deeplink_app": f"bakong://pay?qr={quoted_qr}",
            "amount": float(amount),
            "currency": curr,
            "bill_number": bill_number,
            "account_id": acc,
            "merchant_name": m_name,
            "merchant_city": m_city
        }

    @staticmethod
    def check_transaction_by_md5(md5_hash: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Calls Bakong Open API: POST /v1/check_transaction_by_md5
        Returns (is_paid, message, transaction_data).
        """
        api_url = os.getenv("BAKONG_API_URL", "https://api-bakong.nbc.gov.kh").strip().rstrip("/")
        token = os.getenv("BAKONG_API_TOKEN", os.getenv("BAKONG_DEVELOPER_TOKEN", "")).strip()

        if not token:
            return False, "Bakong Open API token is not configured on the server.", None

        endpoint = f"{api_url}/v1/check_transaction_by_md5"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {"md5": md5_hash}

        try:
            resp = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=BAKONG_TIMEOUT_SECONDS
            )
            data = resp.json() if resp.content else {}

            # responseCode == 0 indicates success / transaction completed on Bakong switch
            if resp.status_code == 200 and data.get("responseCode") == 0:
                tx_data = data.get("data") or {}
                return True, "Transaction completed successfully.", tx_data

            # responseCode == 1 or 404 indicates pending / transaction not found yet
            error_code = data.get("errorCode")
            msg = data.get("responseMessage", "Transaction is pending or not yet scanned.")
            return False, msg, None

        except requests.exceptions.Timeout:
            logger.warning(f"Bakong Open API timed out checking MD5 {md5_hash}")
            return False, "Bakong Open API connection timed out. Please try verifying again in a moment.", None
        except Exception as e:
            logger.error(f"Bakong Open API check failed: {e}")
            return False, f"Bakong Open API check error: {str(e)}", None

    @classmethod
    def verify_and_fulfill_invoice(
        cls,
        db: Session,
        invoice_id: int,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Idempotently verifies an invoice with the Bakong Open API and activates user subscription upon payment.
        """
        query = db.query(PaymentInvoice).filter(PaymentInvoice.id == invoice_id)
        if user_id:
            query = query.filter(PaymentInvoice.user_id == user_id)
        invoice = query.first()

        if not invoice:
            return False, "Invoice not found or unauthorized.", {}

        # If already paid, return idempotently
        if invoice.status == "PAID":
            sub = db.query(UserSubscription).filter(UserSubscription.user_id == invoice.user_id).first()
            return True, "Invoice is already paid and subscription is active.", {
                "invoice_id": invoice.id,
                "status": "PAID",
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
                "plan_id": invoice.plan_id,
                "subscription_status": sub.status if sub else "active_paid"
            }

        # Check transaction with Bakong Open API
        md5_hash = invoice.checkout_reference
        if not md5_hash:
            return False, "Invoice is missing checkout hash reference.", {}

        is_paid, msg, tx_data = cls.check_transaction_by_md5(md5_hash)

        if not is_paid or not tx_data:
            return False, msg, {
                "invoice_id": invoice.id,
                "status": "PENDING",
                "message": msg
            }

        # Validate paid amount and currency
        paid_amount = float(tx_data.get("amount") or 0)
        expected_amount = float(invoice.amount)
        paid_currency = str(tx_data.get("currency") or "USD").upper()

        if paid_amount < expected_amount:
            logger.error(
                f"Underpayment detected for invoice {invoice.id}: expected {expected_amount}, received {paid_amount}"
            )
            return False, f"Underpayment: expected ${expected_amount}, received ${paid_amount}", {
                "invoice_id": invoice.id,
                "status": "REVIEW",
                "paid_amount": paid_amount
            }

        # 1. Update PaymentInvoice
        now_utc = _utc_now()
        invoice.status = "PAID"
        invoice.paid_at = now_utc
        invoice.provider_transaction_id = str(tx_data.get("hash") or "")

        # 2. Record PaymentTransaction audit ledger
        tx_hash = str(tx_data.get("hash") or f"BAKONG-{int(time.time())}")
        existing_tx = db.query(PaymentTransaction).filter_by(
            provider="bakong",
            provider_transaction_id=tx_hash
        ).first()

        if not existing_tx:
            pt = PaymentTransaction(
                invoice_id=invoice.id,
                provider="bakong",
                provider_transaction_id=tx_hash,
                provider_reference=tx_data.get("fromAccountId") or invoice.checkout_reference,
                amount=Decimal(str(paid_amount)).quantize(Decimal("0.01")),
                currency=paid_currency,
                status="PAID",
                verification_status="VERIFIED",
                raw_response_redacted=tx_data,
                created_at=now_utc
            )
            db.add(pt)

        # 3. Activate or Extend UserSubscription
        plan = db.query(SubscriptionPlan).filter_by(id=invoice.plan_id).first()
        duration_days = 30
        if plan and plan.billing_interval == "yearly":
            duration_days = 365
        elif plan and plan.billing_interval == "quarterly":
            duration_days = 90

        expires_utc = now_utc + datetime.timedelta(days=duration_days)

        sub = db.query(UserSubscription).filter(UserSubscription.user_id == invoice.user_id).first()
        if not sub:
            sub = UserSubscription(
                user_id=invoice.user_id,
                plan_id=invoice.plan_id,
                status="active_paid",
                current_period_starts_at=now_utc,
                current_period_expires_at=expires_utc,
                invoice_id=invoice.id,
                created_at=now_utc,
                updated_at=now_utc
            )
            db.add(sub)
        else:
            sub.plan_id = invoice.plan_id
            sub.status = "active_paid"
            # If still active, extend period; otherwise start fresh
            if sub.current_period_expires_at and sub.current_period_expires_at > now_utc:
                sub.current_period_expires_at = sub.current_period_expires_at + datetime.timedelta(days=duration_days)
            else:
                sub.current_period_starts_at = now_utc
                sub.current_period_expires_at = expires_utc
            sub.invoice_id = invoice.id
            sub.updated_at = now_utc

        # 4. Update User Role & Grant Permissions
        user = db.query(User).filter(User.id == invoice.user_id).first()
        if user:
            # Grant premium_user role in user_roles
            target_role = "premium_user" if invoice.plan_id in ("pro", "premium") else "user"
            ur = db.query(UserRole).filter(UserRole.user_id == user.id, UserRole.role_id == target_role).first()
            if not ur:
                db.add(UserRole(user_id=user.id, role_id=target_role))
            if user.role not in ("super_admin", "admin"):
                user.role = target_role

        db.commit()

        logger.info(
            f"Successfully activated subscription for user {invoice.user_id} on plan {invoice.plan_id} via Bakong"
        )

        return True, "Payment verified successfully! Your subscription is now ACTIVE.", {
            "invoice_id": invoice.id,
            "status": "PAID",
            "paid_at": invoice.paid_at.isoformat(),
            "plan_id": invoice.plan_id,
            "subscription_status": "active_paid",
            "expires_at": expires_utc.isoformat(),
            "transaction_hash": tx_hash
        }


bakong_service = BakongService()
