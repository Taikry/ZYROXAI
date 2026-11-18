"""
Google OAuth 2.0 Authentication Service for ZYROX AI SaaS Platform.
Implements:
- Standard Authorization Code Flow with PKCE (S256)
- State and Nonce anti-forgery validation with 10-minute TTL
- Server-side token exchange and Google JWKS ID Token signature verification
- Secure account linking by verified email address
- Auto-provisioning of 14-day Pro trial on new registration
- Returns NEEDS_CONFIGURATION status when Google Client credentials are absent
"""
import os
import time
import datetime
import base64
import hashlib
import secrets
import logging
import threading
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlencode
from sqlalchemy.orm import Session
import httpx
import jwt

from taikry.config import PUBLIC_APP_URL
from taikry.database.models import User, UserSession, AuditLog
from taikry.saas.security import generate_session_token, hash_password
from taikry.saas.trial_service import grant_14_day_trial

logger = logging.getLogger("taikry.saas.google_oauth")

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URI = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}
STATE_TTL_SECONDS = 600  # 10 minutes


def get_google_client_id() -> str:
    return os.getenv("GOOGLE_CLIENT_ID", "").strip()


def get_google_client_secret() -> str:
    return os.getenv("GOOGLE_CLIENT_SECRET", "").strip()


def is_google_auth_configured() -> bool:
    cid = get_google_client_id()
    secret = get_google_client_secret()
    return bool(cid and secret and len(cid) > 10 and len(secret) > 8)


def get_google_redirect_uri(base_url: Optional[str] = None) -> str:
    if base_url and ("localhost" in base_url or "127.0.0.1" in base_url):
        return f"{base_url.rstrip('/')}/api/v1/auth/google/callback"
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


def generate_pkce_pair() -> Tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


class GoogleStateCache:
    """Thread-safe in-memory cache for Google OAuth state, nonce, and PKCE verifier."""
    def __init__(self, ttl_seconds: int = STATE_TTL_SECONDS):
        self.ttl = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def store(self, state: str, nonce: str, code_verifier: str, return_to: str = "/dashboard/") -> None:
        with self._lock:
            now = time.time()
            self._purge_expired(now)
            self._cache[state] = {
                "nonce": nonce,
                "code_verifier": code_verifier,
                "return_to": return_to or "/dashboard/",
                "created_at": now,
                "expires_at": now + self.ttl
            }

    def pop(self, state: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            now = time.time()
            self._purge_expired(now)
            entry = self._cache.pop(state, None)
            if entry and entry.get("expires_at", 0) > now:
                return entry
            return None

    def _purge_expired(self, now: float) -> None:
        expired = [k for k, v in self._cache.items() if v.get("expires_at", 0) <= now]
        for k in expired:
            self._cache.pop(k, None)


google_state_cache = GoogleStateCache()


class GoogleJWKSCache:
    """Thread-safe cache for Google OAuth public signing certs."""
    def __init__(self, jwks_uri: str = GOOGLE_JWKS_URI, ttl_seconds: int = 3600):
        self.jwks_uri = jwks_uri
        self.ttl = ttl_seconds
        self._keys_by_kid: Dict[str, Any] = {}
        self._last_fetched: float = 0.0
        self._lock = threading.Lock()

    def get_key_by_kid(self, kid: str, force_refresh: bool = False) -> Optional[Any]:
        now = time.time()
        needs_fetch = force_refresh or (now - self._last_fetched > self.ttl) or (kid not in self._keys_by_kid)
        if needs_fetch:
            self._fetch()
        return self._keys_by_kid.get(kid)

    def _fetch(self) -> None:
        with self._lock:
            try:
                headers = {"Accept": "application/json", "User-Agent": "ZYROX-AI-Google-OAuth/2.0"}
                with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                    resp = client.get(self.jwks_uri, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()
                raw_keys = data.get("keys", [])
                parsed = {}
                for k in raw_keys:
                    key_id = k.get("kid")
                    if key_id:
                        try:
                            parsed[key_id] = jwt.PyJWK(k).key
                        except Exception as e:
                            logger.warning(f"Failed to parse Google JWK {key_id}: {e}")
                self._keys_by_kid = parsed
                self._last_fetched = time.time()
                logger.info(f"Loaded {len(parsed)} Google JWKS signing keys")
            except Exception as e:
                logger.error(f"Failed to fetch Google JWKS: {e}")
                if not self._keys_by_kid:
                    raise


google_jwks_cache = GoogleJWKSCache()


def build_google_authorization_url(base_url: Optional[str] = None, return_to: Optional[str] = None) -> Tuple[bool, str]:
    if not is_google_auth_configured():
        return False, "Google OAuth is not configured. Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET."

    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier, challenge = generate_pkce_pair()
    safe_return_to = return_to if (return_to and return_to.startswith("/") and not return_to.startswith("//")) else "/dashboard/"

    google_state_cache.store(state, nonce, verifier, safe_return_to)
    redirect_uri = get_google_redirect_uri(base_url)

    params = {
        "client_id": get_google_client_id(),
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "state": state,
        "nonce": nonce,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "access_type": "online",
        "prompt": "select_account"
    }
    auth_url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"
    return True, auth_url


def exchange_google_code_for_tokens(code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
    if not is_google_auth_configured():
        return False, {"error": "Google OAuth is not configured"}

    primary_secret = get_google_client_secret()
    candidate_secrets = [primary_secret]
    # Fault-tolerance for letter 'O' vs digit '0' in Google client secret
    if primary_secret.startswith("GOCSPX-O"):
        candidate_secrets.append("GOCSPX-0" + primary_secret[9:])
    elif primary_secret.startswith("GOCSPX-0"):
        candidate_secrets.append("GOCSPX-O" + primary_secret[9:])

    last_error = None
    for sec in candidate_secrets:
        payload = {
            "client_id": get_google_client_id(),
            "client_secret": sec,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        if code_verifier:
            payload["code_verifier"] = code_verifier

        try:
            with httpx.Client(timeout=12.0) as client:
                resp = client.post(GOOGLE_TOKEN_ENDPOINT, data=payload)
                data = resp.json()
                if resp.status_code == 200 and "id_token" in data:
                    return True, data
                err_msg = data.get("error_description") or data.get("error") or f"HTTP {resp.status_code}"
                last_error = err_msg
                if "invalid_client" not in str(err_msg).lower():
                    break
        except Exception as e:
            logger.error(f"Google token exchange network error: {e}")
            last_error = str(e)
            break

    return False, {"error": f"Token exchange failed: {last_error or 'Unknown error'}"}


def verify_google_id_token(id_token_str: str, expected_nonce: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
    try:
        unverified_header = jwt.get_unverified_header(id_token_str)
        kid = unverified_header.get("kid")
        if not kid:
            return False, {"error": "Google ID token missing kid in header"}

        key = google_jwks_cache.get_key_by_kid(kid)
        if not key:
            key = google_jwks_cache.get_key_by_kid(kid, force_refresh=True)
        if not key:
            return False, {"error": f"No matching Google signing key found for kid: {kid}"}

        claims = jwt.decode(
            id_token_str,
            key=key,
            algorithms=["RS256"],
            audience=get_google_client_id(),
            options={"verify_aud": True, "verify_exp": True, "verify_iss": False}
        )

        iss = claims.get("iss")
        if iss not in GOOGLE_ISSUERS:
            return False, {"error": f"Invalid token issuer: {iss}"}

        if expected_nonce and claims.get("nonce") != expected_nonce:
            return False, {"error": "Google nonce mismatch anti-forgery check failed"}

        if not claims.get("email_verified", False):
            return False, {"error": "Google account email is not verified"}

        return True, claims
    except jwt.ExpiredSignatureError:
        return False, {"error": "Google ID token has expired"}
    except jwt.InvalidTokenError as e:
        return False, {"error": f"Google ID token signature verification failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error validating Google ID token: {e}")
        return False, {"error": f"Internal token verification error: {str(e)}"}


def authenticate_or_register_google_user(
    db: Session,
    claims: Dict[str, Any],
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    current_user: Optional[User] = None
) -> Tuple[bool, Optional[User], Optional[str], bool, str]:
    """
    Finds or creates a User from validated Google claims.
    Returns: (success, user, session_token, is_new_user, error_msg)
    """
    google_sub = str(claims.get("sub") or "").strip()
    email = str(claims.get("email") or "").strip().lower()
    full_name = str(claims.get("name") or claims.get("given_name") or email.split("@")[0]).strip()

    if not google_sub or not email:
        return False, None, None, False, "Missing sub or email in Google claims"

    is_new = False
    target_user = None

    # Case 1: Active authenticated user linking their Google account
    if current_user and current_user.is_active:
        current_user.google_user_id = google_sub
        target_user = current_user
        logger.info(f"Linked Google sub {google_sub} to active user {target_user.email}")
    else:
        # Case 2: Match by existing google_user_id
        target_user = db.query(User).filter(User.google_user_id == google_sub, User.deleted_at.is_(None)).first()

        # Case 3: Match by verified email
        if not target_user:
            target_user = db.query(User).filter(User.email == email, User.deleted_at.is_(None)).first()
            if target_user:
                target_user.google_user_id = google_sub
                target_user.is_verified = True
                logger.info(f"Linked existing user {email} to Google sub {google_sub}")

        # Case 4: Provision new user
        if not target_user:
            is_new = True
            random_pw = secrets.token_urlsafe(32)
            pwd_hash, salt = hash_password(random_pw)
            target_user = User(
                email=email,
                google_user_id=google_sub,
                full_name=full_name,
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

            # Provision 14-day Pro trial for new accounts
            try:
                grant_14_day_trial(db, target_user.id)
            except Exception as e:
                logger.warning(f"Failed to auto-grant 14-day Pro trial: {e}")

    # Issue server-side session
    token_str, token_hash = generate_session_token()
    now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    expires_at = now_utc + datetime.timedelta(days=30)
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
        action="GOOGLE_OAUTH_LOGIN" if not is_new else "GOOGLE_OAUTH_REGISTER",
        ip_address=client_ip,
        details={"google_sub": google_sub, "email": email, "is_new_user": is_new}
    )
    db.add(audit)
    db.commit()

    return True, target_user, token_str, is_new, ""
