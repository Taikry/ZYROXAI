"""
Phone SMS OTP Authentication Service for ZYROX AI SaaS Platform.
Implements:
- E.164 international phone number normalization and validation
- Cryptographically secure 6-digit OTP generation using secrets
- Salted SHA-256 storage (never logs or returns raw OTP)
- Strict rate limiting: max 3 requests/hour per phone, max 5/hour per IP, 60s cooldown
- Attempt limit: max 5 verification attempts before challenge invalidation
- 5-minute expiry window
- Real Twilio SMS gateway integration
- Returns NEEDS_CONFIGURATION status when Twilio credentials are absent
- Auto-provisions 14-day Pro trial on new phone registration
"""
import os
import re
import time
import secrets
import hashlib
import logging
import datetime
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import httpx

from taikry.database.models import User, UserSession, AuditLog, PhoneOTPChallenge
from taikry.saas.security import generate_session_token, hash_password
from taikry.saas.trial_service import grant_14_day_trial

logger = logging.getLogger("taikry.saas.phone_otp")

E164_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")
OTP_EXPIRY_SECONDS = 300  # 5 minutes
COOLDOWN_SECONDS = 60    # 1 minute between sends
MAX_ATTEMPTS = 5


def get_sms_provider() -> str:
    return os.getenv("SMS_PROVIDER", "twilio").strip().lower()


def get_twilio_credentials() -> Tuple[str, str, str]:
    sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_num = os.getenv("TWILIO_PHONE_NUMBER", "").strip()
    return sid, token, from_num


def is_phone_auth_configured() -> bool:
    provider = get_sms_provider()
    if provider == "twilio":
        sid, token, from_num = get_twilio_credentials()
        return bool(sid and token and from_num and len(sid) > 10 and len(token) > 10)
    return False


def get_phone_auth_status() -> Dict[str, Any]:
    configured = is_phone_auth_configured()
    provider = get_sms_provider()
    req_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"] if provider == "twilio" else []
    return {
        "configured": configured,
        "status": "READY" if configured else "NEEDS_CONFIGURATION",
        "provider": provider,
        "required_env_vars": req_vars if not configured else [],
        "note": "Phone OTP requires verified SMS gateway credentials; dummy bypass is strictly disabled."
    }


def normalize_e164_phone(raw_phone: str) -> Optional[str]:
    """Validates and formats an international phone number to E.164 standard."""
    if not raw_phone:
        return None
    cleaned = re.sub(r"[\s\-\(\)\.]", "", str(raw_phone).strip())
    if not cleaned.startswith("+"):
        if cleaned.startswith("855"):  # Cambodia default prefix handling
            cleaned = "+" + cleaned
        elif cleaned.startswith("0") and len(cleaned) in (9, 10):  # Local Cambodia 012 -> +85512
            cleaned = "+855" + cleaned[1:]
        elif cleaned.startswith("1") and len(cleaned) == 11:  # US/Canada 1xxx -> +1xxx
            cleaned = "+" + cleaned

    if E164_REGEX.match(cleaned):
        return cleaned
    return None


def generate_secure_otp() -> Tuple[str, str, str]:
    """Generates 6-digit cryptographic OTP, random salt, and salted SHA-256 hash."""
    code = f"{secrets.randbelow(900000) + 100000}"
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + code).encode("utf-8")).hexdigest()
    return code, salt, digest


def send_twilio_sms(to_phone: str, message: str) -> Tuple[bool, str]:
    """Sends SMS via Twilio REST API."""
    sid, token, from_num = get_twilio_credentials()
    if not is_phone_auth_configured():
        return False, "SMS provider credentials are not configured"

    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    data = {
        "To": to_phone,
        "From": from_num,
        "Body": message
    }
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, data=data, auth=(sid, token))
            if resp.status_code in (200, 201):
                logger.info(f"Twilio SMS dispatched successfully to {to_phone[:6]}***")
                return True, "SMS sent successfully"
            resp_data = resp.json()
            err_msg = resp_data.get("message") or f"Twilio HTTP {resp.status_code}"
            logger.error(f"Twilio API error: {err_msg}")
            return False, f"SMS delivery failed: {err_msg}"
    except Exception as e:
        logger.error(f"Twilio network connection error: {e}")
        return False, f"Network error sending SMS: {str(e)}"


def request_phone_otp(
    db: Session,
    phone_raw: str,
    client_ip: Optional[str] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates phone, enforces rate limits, creates challenge and dispatches SMS.
    Returns: (success, error_or_success_message, metadata)
    """
    phone = normalize_e164_phone(phone_raw)
    if not phone:
        return False, "Invalid phone number format. Please provide international E.164 format (e.g. +85512345678).", {}

    if not is_phone_auth_configured():
        return False, "Phone SMS service is not configured on this server.", {"status": "NEEDS_CONFIGURATION"}

    now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    one_hour_ago = now_utc - datetime.timedelta(hours=1)
    cooldown_threshold = now_utc - datetime.timedelta(seconds=COOLDOWN_SECONDS)

    # Cooldown check on phone
    recent_phone_otp = db.query(PhoneOTPChallenge).filter(
        PhoneOTPChallenge.phone_number == phone,
        PhoneOTPChallenge.created_at >= cooldown_threshold
    ).order_by(PhoneOTPChallenge.created_at.desc()).first()
    if recent_phone_otp:
        wait_seconds = int((recent_phone_otp.created_at + datetime.timedelta(seconds=COOLDOWN_SECONDS) - now_utc).total_seconds())
        return False, f"Please wait {max(1, wait_seconds)} seconds before requesting a new code.", {"cooldown_seconds": max(1, wait_seconds)}

    # Hourly rate limit per phone (max 3)
    hourly_phone_count = db.query(PhoneOTPChallenge).filter(
        PhoneOTPChallenge.phone_number == phone,
        PhoneOTPChallenge.created_at >= one_hour_ago
    ).count()
    if hourly_phone_count >= 3:
        return False, "Too many SMS requests for this phone number. Please try again in 1 hour.", {"rate_limited": True}

    # Hourly rate limit per IP (max 5)
    if client_ip:
        hourly_ip_count = db.query(PhoneOTPChallenge).filter(
            PhoneOTPChallenge.client_ip == client_ip,
            PhoneOTPChallenge.created_at >= one_hour_ago
        ).count()
        if hourly_ip_count >= 5:
            return False, "Too many requests from your IP address. Please try again later.", {"rate_limited": True}

    # Invalidate previous unused challenges for this phone
    db.query(PhoneOTPChallenge).filter(
        PhoneOTPChallenge.phone_number == phone,
        PhoneOTPChallenge.is_used.is_(False)
    ).update({"is_used": True}, synchronize_session=False)

    # Generate OTP
    code, salt, digest = generate_secure_otp()
    expires_at = now_utc + datetime.timedelta(seconds=OTP_EXPIRY_SECONDS)

    challenge = PhoneOTPChallenge(
        phone_number=phone,
        otp_hash=digest,
        salt=salt,
        attempts=0,
        max_attempts=MAX_ATTEMPTS,
        expires_at=expires_at,
        is_used=False,
        client_ip=client_ip
    )
    db.add(challenge)
    db.commit()

    # Dispatch SMS
    sms_text = f"Your ZYROX AI verification code is: {code}. Valid for 5 minutes. Do not share this code."
    dispatched, send_msg = send_twilio_sms(phone, sms_text)
    if not dispatched:
        return False, send_msg, {}

    return True, "Verification code sent to your phone via SMS.", {
        "phone": f"{phone[:4]}***{phone[-2:]}",
        "expires_in_seconds": OTP_EXPIRY_SECONDS
    }


def verify_phone_otp_challenge(
    db: Session,
    phone_raw: str,
    code_raw: str,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    current_user: Optional[User] = None
) -> Tuple[bool, Optional[User], Optional[str], bool, str]:
    """
    Verifies submitted OTP code against stored salted hash.
    Returns: (success, user, session_token, is_new_user, error_message)
    """
    phone = normalize_e164_phone(phone_raw)
    code = str(code_raw or "").strip()

    if not phone or not code or len(code) != 6 or not code.isdigit():
        return False, None, None, False, "Invalid phone number or 6-digit code format"

    now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

    challenge = db.query(PhoneOTPChallenge).filter(
        PhoneOTPChallenge.phone_number == phone,
        PhoneOTPChallenge.is_used.is_(False)
    ).order_by(PhoneOTPChallenge.created_at.desc()).first()

    if not challenge:
        return False, None, None, False, "No active verification code found for this phone number. Please request a new code."

    if challenge.expires_at < now_utc:
        challenge.is_used = True
        db.commit()
        return False, None, None, False, "Verification code has expired. Please request a new code."

    if challenge.attempts >= challenge.max_attempts:
        challenge.is_used = True
        db.commit()
        return False, None, None, False, "Maximum verification attempts exceeded. Please request a new code."

    # Validate hash
    expected_digest = hashlib.sha256((challenge.salt + code).encode("utf-8")).hexdigest()
    if not secrets.compare_digest(challenge.otp_hash, expected_digest):
        challenge.attempts += 1
        remaining = max(0, challenge.max_attempts - challenge.attempts)
        db.commit()
        if remaining == 0:
            challenge.is_used = True
            db.commit()
            return False, None, None, False, "Invalid verification code. Maximum attempts reached. Please request a new code."
        return False, None, None, False, f"Invalid verification code. {remaining} attempt(s) remaining."

    # Code matches! Mark challenge as used
    challenge.is_used = True

    is_new = False
    target_user = None

    # Link to authenticated user if session active
    if current_user and current_user.is_active:
        current_user.phone_number = phone
        target_user = current_user
        logger.info(f"Linked phone {phone} to authenticated user {target_user.email}")
    else:
        # Match by phone number
        target_user = db.query(User).filter(User.phone_number == phone, User.deleted_at.is_(None)).first()

        # Provision new user if not found
        if not target_user:
            is_new = True
            synthetic_email = f"phone_{phone.replace('+', '')}@phone.zyrox.ai"
            random_pw = secrets.token_urlsafe(32)
            pwd_hash, salt = hash_password(random_pw)
            target_user = User(
                email=synthetic_email,
                phone_number=phone,
                full_name=f"User {phone[-4:]}",
                hashed_password=pwd_hash,
                salt=salt,
                role="USER",
                is_verified=True,
                is_active=True,
                language="en",
                timezone="Asia/Phnom_Penh"
            )
            db.add(target_user)
            db.flush()

            try:
                grant_14_day_trial(db, target_user.id)
            except Exception as e:
                logger.warning(f"Failed to auto-grant trial for phone user: {e}")

    # Issue session token
    token_str, token_hash = generate_session_token()
    now_utc_sess = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    expires_at = now_utc_sess + datetime.timedelta(days=30)
    session_record = UserSession(
        user_id=target_user.id,
        token_hash=token_hash,
        ip_address=client_ip[:45] if client_ip else None,
        user_agent=user_agent[:255] if user_agent else None,
        expires_at=expires_at
    )
    db.add(session_record)

    audit = AuditLog(
        actor_user_id=target_user.id,
        action="PHONE_OTP_LOGIN" if not is_new else "PHONE_OTP_REGISTER",
        ip_address=client_ip,
        details={"phone": phone, "is_new_user": is_new}
    )
    db.add(audit)
    db.commit()

    return True, target_user, token_str, is_new, ""
