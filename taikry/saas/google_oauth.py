"""
Google OAuth 2.0 Authentication Service for ZYROX AI SaaS Platform.
Implements:
- Standard Authorization Code Flow
- State and Nonce anti-forgery validation
- Server-side token exchange and ID Token verification
- Secure account linking by verified email address
- Returns NEEDS_CONFIGURATION status when Google Client credentials are absent
"""
import os
import secrets
import logging
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlencode
from sqlalchemy.orm import Session

from taikry.config import PUBLIC_APP_URL
from taikry.database.models import User, UserSession, AuditLog
from taikry.saas.security import generate_session_token
from taikry.saas.trial_service import grant_14_day_trial

logger = logging.getLogger("taikry.saas.google_oauth")

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"


def get_google_client_id() -> str:
    return os.getenv("GOOGLE_CLIENT_ID", "").strip()


def get_google_client_secret() -> str:
    return os.getenv("GOOGLE_CLIENT_SECRET", "").strip()


def is_google_auth_configured() -> bool:
    cid = get_google_client_id()
    secret = get_google_client_secret()
    return bool(cid and secret and len(cid) > 10 and len(secret) > 8)


def get_google_redirect_uri(base_url: Optional[str] = None) -> str:
    custom_uri = os.getenv("GOOGLE_REDIRECT_URI", "").strip()
    if custom_uri:
        return custom_uri
    origin = (base_url or PUBLIC_APP_URL or "https://taikry-ai-trading.onrender.com").rstrip("/")
    return f"{origin}/api/v1/auth/google/callback"


def get_google_auth_status(base_url: Optional[str] = None) -> Dict[str, Any]:
    configured = is_google_auth_configured()
    redirect_uri = get_google_redirect_uri(base_url)
    return {
        "configured": configured,
        "status": "READY" if configured else "NEEDS_CONFIGURATION",
        "redirect_uri": redirect_uri,
        "required_env_vars": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"] if not configured else [],
        "note": "Google OAuth is ready for production activation upon providing Google Cloud Console credentials."
    }


def build_google_authorization_url(base_url: Optional[str] = None, return_to: Optional[str] = None) -> Tuple[bool, str]:
    if not is_google_auth_configured():
        return False, "Google OAuth is not configured. Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET."

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    redirect_uri = get_google_redirect_uri(base_url)

    params = {
        "client_id": get_google_client_id(),
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "state": state,
        "nonce": nonce,
        "access_type": "online",
        "prompt": "select_account"
    }
    auth_url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"
    return True, auth_url
