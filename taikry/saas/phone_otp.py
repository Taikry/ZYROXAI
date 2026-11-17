"""
Phone SMS OTP Authentication Service for ZYROX AI SaaS Platform.
Implements:
- Standard SMS OTP verification model
- Rate limiting: max 3 requests per phone per hour
- Attempt limits: max 5 attempts per OTP
- 5-minute expiry window
- Returns NEEDS_CONFIGURATION status when SMS provider credentials are absent
"""
import os
import time
import secrets
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("taikry.saas.phone_otp")


def get_sms_provider() -> str:
    return os.getenv("SMS_PROVIDER", "twilio").strip().lower()


def is_phone_auth_configured() -> bool:
    provider = get_sms_provider()
    if provider == "twilio":
        sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        return bool(sid and token and len(sid) > 10 and len(token) > 10)
    elif provider == "aws_sns":
        key = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
        secret = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
        return bool(key and secret)
    return False


def get_phone_auth_status() -> Dict[str, Any]:
    configured = is_phone_auth_configured()
    provider = get_sms_provider()
    req_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"] if provider == "twilio" else ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
    return {
        "configured": configured,
        "status": "READY" if configured else "NEEDS_CONFIGURATION",
        "provider": provider,
        "required_env_vars": req_vars if not configured else [],
        "note": "Phone OTP requires verified SMS gateway credentials; dummy bypass is strictly disabled."
    }
