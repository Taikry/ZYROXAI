"""
Payment Provider & Billing Adapter for ZYROX AI SaaS Platform.
Supports:
- NBC Bakong Open API & KHQR dynamic payment checkout
- Instant Base64 QR code rendering & Bakong mobile app deeplinks
- Idempotent transaction verification via POST /v1/check_transaction_by_md5
- Automated subscription activation and audit ledger persistence
- Strict rule: Never activates paid tier without verified provider confirmation
"""

import os
import uuid
import datetime
from decimal import Decimal
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from taikry.database.models import SubscriptionPlan, PaymentInvoice, UserSubscription
from taikry.saas.bakong_service import bakong_service


def _utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class BillingAdapter:
    """Central Billing & Checkout Adapter."""

    @staticmethod
    def is_gateway_configured() -> bool:
        """Returns True if a valid payment gateway (e.g. Bakong Open API) is configured."""
        return bakong_service.is_configured()

    @staticmethod
    def get_provider_status() -> Dict[str, Any]:
        """Returns provider status information."""
        return bakong_service.get_status()

    @staticmethod
    def create_checkout_session(
        db: Session,
        user_id: int,
        plan_id: str,
        return_url: str = "/dashboard/billing.html"
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Creates a payment checkout session.
        If Bakong Open API is configured, generates an EMVCo dynamic KHQR code with MD5 hash.
        If not configured, returns clear setup guidance.
        """
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        if not plan:
            return False, "Selected plan not found.", {}

        plan_amount = float(plan.amount or 0)
        if plan_amount <= 0:
            return False, "This is a free plan; no payment required.", {
                "configured": True,
                "plan_id": plan_id,
                "price_usd": 0.0,
                "status": "FREE_PLAN"
            }

        if not BillingAdapter.is_gateway_configured():
            status_info = bakong_service.get_status()
            missing = []
            if not status_info["has_account"]:
                missing.append("BAKONG_ACCOUNT_ID")
            if not status_info["has_token"]:
                missing.append("BAKONG_API_TOKEN")

            msg = f"Bakong Open API requires credentials ({', '.join(missing)}) to activate live checkout."
            return False, msg, {
                "configured": False,
                "provider": "bakong",
                "plan_id": plan_id,
                "plan_name": plan.name_en,
                "price_usd": plan_amount,
                "billing_interval": plan.billing_interval,
                "status": "PENDING_CREDENTIALS",
                "missing_configs": missing,
                "support_contact": "support@zyrox.ai"
            }

        # Check for existing pending invoice for this user and plan
        now_utc = _utc_now()
        existing_invoice = (
            db.query(PaymentInvoice)
            .filter(
                PaymentInvoice.user_id == user_id,
                PaymentInvoice.plan_id == plan_id,
                PaymentInvoice.status == "PENDING"
            )
            .first()
        )

        # If existing invoice has expired, expire it
        if existing_invoice and existing_invoice.expires_at and existing_invoice.expires_at < now_utc:
            existing_invoice.status = "EXPIRED"
            db.commit()
            existing_invoice = None

        if existing_invoice:
            invoice = existing_invoice
            # Regenerate fresh KHQR payload for existing invoice
            khqr_data = bakong_service.create_khqr_payload(
                amount=float(invoice.amount),
                currency=invoice.currency,
                bill_number=invoice.invoice_number
            )
            # Update checkout reference to match new MD5 if needed
            if invoice.checkout_reference != khqr_data["md5_hash"]:
                invoice.checkout_reference = khqr_data["md5_hash"]
                db.commit()
        else:
            # Create a new invoice
            invoice_num = f"ZYROX-{now_utc.strftime('%Y%m%d')}-{user_id}-{uuid.uuid4().hex[:6].upper()}"
            khqr_data = bakong_service.create_khqr_payload(
                amount=plan_amount,
                currency="USD",
                bill_number=invoice_num
            )

            expires_at = now_utc + datetime.timedelta(minutes=15)
            invoice = PaymentInvoice(
                user_id=user_id,
                plan_id=plan_id,
                invoice_number=invoice_num,
                amount=Decimal(str(plan_amount)).quantize(Decimal("0.01")),
                currency="USD",
                provider="bakong",
                status="PENDING",
                checkout_reference=khqr_data["md5_hash"],
                expires_at=expires_at,
                created_at=now_utc,
                updated_at=now_utc
            )
            db.add(invoice)
            db.commit()
            db.refresh(invoice)

        return True, "Bakong KHQR checkout generated successfully.", {
            "configured": True,
            "provider": "bakong",
            "invoice": {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "amount": float(invoice.amount),
                "currency": invoice.currency,
                "status": invoice.status,
                "expires_at": invoice.expires_at.isoformat() if invoice.expires_at else None
            },
            "checkout": {
                "url": f"/api/v1/payments/verify/{invoice.id}",
                "provider": "bakong",
                "khqr": khqr_data["khqr_string"],
                "md5": khqr_data["md5_hash"],
                "qr_image": khqr_data["qr_image_data"],
                "deeplink_web": khqr_data["deeplink_web"],
                "deeplink_app": khqr_data["deeplink_app"],
                "amount": float(invoice.amount),
                "currency": invoice.currency,
                "bill_number": invoice.invoice_number,
                "merchant_name": khqr_data["merchant_name"],
                "account_id": khqr_data["account_id"]
            }
        }

    @staticmethod
    def verify_invoice(
        db: Session,
        invoice_id: int,
        user_id: Optional[int] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Verifies invoice payment status via Bakong Open API.
        """
        return bakong_service.verify_and_fulfill_invoice(db, invoice_id, user_id=user_id)

    @staticmethod
    def process_webhook_event(
        db: Session,
        payload_bytes: bytes,
        signature_header: str
    ) -> Tuple[bool, str]:
        """
        Processes verified incoming webhook from payment gateway.
        """
        import json
        try:
            payload = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            return False, "Invalid JSON payload"

        md5_hash = payload.get("md5") or payload.get("hash")
        if not md5_hash:
            return False, "Missing md5 or hash in webhook payload"

        invoice = db.query(PaymentInvoice).filter(PaymentInvoice.checkout_reference == md5_hash).first()
        if not invoice:
            return False, f"No pending invoice found for hash {md5_hash}"

        ok, msg, data = bakong_service.verify_and_fulfill_invoice(db, invoice.id)
        return ok, msg


billing_adapter = BillingAdapter()
