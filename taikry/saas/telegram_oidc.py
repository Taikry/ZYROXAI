"""
Telegram OpenID Connect (OIDC) Authentication Service for ZYROX AI.
Implements:
- Telegram OpenID Connect Authorization Code Flow with PKCE (S256)
- Standard Endpoints:
    Authorization: https://oauth.telegram.org/auth
    Token:         https://oauth.telegram.org/token
    JWKS:          https://oauth.telegram.org/.well-known/jwks.json
    Issuer:        https://oauth.telegram.org
- Scopes: openid profile
- Cryptographically secure state, nonce, and PKCE verifier generation
- Server-side temporary authorization state cache with replay protection
- Backend-only authorization code exchange
- Cryptographic ID token signature verification via Telegram JWKS (RS256, ES256, EdDSA, ES256K)
- Validation of issuer, audience, expiration, issued-at time, nonce, and state
- Canonical user identification by Telegram's permanent subject ID (`sub`), NOT username
- Canonical user retrieval, registration with 14-day trial, and account linking
- Secure session issuance matching the existing ZYROX AI session cookie mechanism
"""

import os
import time
import json
import base64
import hashlib
import secrets
import logging
import datetime
from threading import Lock
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlencode, quote

import jwt
import httpx
from sqlalchemy.orm import Session

from taikry.config import (
    TELEGRAM_LOGIN_CLIENT_ID,
    TELEGRAM_LOGIN_CLIENT_SECRET,
    TELEGRAM_LOGIN_REDIRECT_URI,
    TELEGRAM_LOGIN_ISSUER,
    TELEGRAM_LOGIN_JWKS_URI,
    TELEGRAM_LOGIN_BOT_USERNAME,
    PUBLIC_APP_URL,
    INITIAL_PAPER_BALANCE
)
from taikry.database.models import (
    User,
    UserSession,
    TelegramLink,
    NotificationPreferences,
    AuditLog,
    UserRole
)
from taikry.saas.security import (
    generate_session_token,
    hash_password,
    hash_token
)
from taikry.saas.trial_service import grant_14_day_trial

logger = logging.getLogger("taikry.saas.telegram_oidc")

DEFAULT_AUTH_ENDPOINT = "https://oauth.telegram.org/auth"
DEFAULT_TOKEN_ENDPOINT = "https://oauth.telegram.org/token"
DEFAULT_JWKS_URI = "https://oauth.telegram.org/.well-known/jwks.json"
DEFAULT_ISSUER = "https://oauth.telegram.org"
DEFAULT_SCOPES = "openid profile"
SESSION_DURATION_DAYS = 30
STATE_TTL_SECONDS = 600  # 10 minutes


# =============================================================================
# PKCE & CRYPTOGRAPHIC HELPERS (RFC 7636)
# =============================================================================

def generate_pkce_pair() -> Tuple[str, str]:
    """
    Generates a cryptographically secure PKCE (code_verifier, code_challenge) pair.
    Uses SHA-256 (S256) and Base64URL encoding without padding.
    """
    # 64 bytes urlsafe gives an 86-character verifier, well within 43-128 chars
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return code_verifier, code_challenge


def generate_state_and_nonce() -> Tuple[str, str]:
    """Generates random secure URL-safe tokens for state and nonce."""
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    return state, nonce


# =============================================================================
# THREAD-SAFE SERVER-SIDE AUTHORIZATION STATE STORE
# =============================================================================

class TelegramAuthStateStore:
    """
    Stores temporary OIDC authorization states on the server.
    Enforces TTL expiration and single-use atomic popping to prevent replay attacks.
    """
    def __init__(self, ttl_seconds: int = STATE_TTL_SECONDS):
        self._states: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self._ttl = ttl_seconds

    def store(
        self,
        state: str,
        nonce: str,
        code_verifier: str,
        redirect_uri: str,
        return_to: Optional[str] = None
    ) -> None:
        now = time.time()
        self._purge_expired(now)
        with self._lock:
            self._states[state] = {
                "nonce": nonce,
                "code_verifier": code_verifier,
                "redirect_uri": redirect_uri,
                "return_to": return_to or "/dashboard/",
                "created_at": now,
                "expires_at": now + self._ttl
            }

    def pop(self, state: str) -> Optional[Dict[str, Any]]:
        """
        Atomically retrieves and removes the state.
        Returns None if state does not exist or has expired.
        """
        if not state:
            return None
        now = time.time()
        with self._lock:
            entry = self._states.pop(state, None)
            if not entry:
                return None
            if entry["expires_at"] < now:
                return None
            return entry

    def _purge_expired(self, now: float) -> None:
        with self._lock:
            expired_keys = [k for k, v in self._states.items() if v["expires_at"] < now]
            for k in expired_keys:
                self._states.pop(k, None)

    def count(self) -> int:
        with self._lock:
            return len(self._states)


auth_state_store = TelegramAuthStateStore()


# =============================================================================
# JWKS CACHE & ID TOKEN VALIDATOR
# =============================================================================

class TelegramJWKSCache:
    """
    Fetches and caches Telegram's JWKS public keys.
    Refreshes automatically when cache expires or an unknown kid is encountered.
    """
    def __init__(self, jwks_uri: Optional[str] = None, ttl_seconds: int = 3600):
        self.jwks_uri = jwks_uri or TELEGRAM_LOGIN_JWKS_URI or DEFAULT_JWKS_URI
        self.ttl = ttl_seconds
        self._keys_by_kid: Dict[str, Any] = {}
        self._raw_keys: List[Dict[str, Any]] = []
        self._last_fetched: float = 0.0
        self._lock = Lock()

    def get_key_by_kid(self, kid: str, force_refresh: bool = False) -> Optional[Any]:
        now = time.time()
        needs_fetch = force_refresh or (now - self._last_fetched > self.ttl) or (kid not in self._keys_by_kid)

        if needs_fetch:
            self._fetch()

        return self._keys_by_kid.get(kid)

    def get_raw_keys(self) -> List[Dict[str, Any]]:
        if not self._raw_keys or (time.time() - self._last_fetched > self.ttl):
            self._fetch()
        return self._raw_keys

    def _fetch(self) -> None:
        with self._lock:
            try:
                headers = {
                    "Accept": "application/json",
                    "User-Agent": "ZYROX-AI-Telegram-OIDC/2.0"
                }
                with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                    resp = client.get(self.jwks_uri, headers=headers)
                    resp.raise_for_status()
                    data = resp.json()

                raw_keys = data.get("keys", [])
                parsed_keys = {}
                for k in raw_keys:
                    key_id = k.get("kid")
                    if key_id:
                        try:
                            pyjwk = jwt.PyJWK(k)
                            parsed_keys[key_id] = pyjwk.key
                        except Exception as parse_err:
                            logger.warning(f"Failed to parse JWK key {key_id}: {parse_err}")

                self._keys_by_kid = parsed_keys
                self._raw_keys = raw_keys
                self._last_fetched = time.time()
                logger.info(f"Successfully loaded {len(parsed_keys)} Telegram JWKS signing keys")
            except Exception as e:
                logger.error(f"Failed to fetch Telegram JWKS from {self.jwks_uri}: {e}")
                if not self._keys_by_kid:
                    raise


jwks_cache = TelegramJWKSCache()


# =============================================================================
# CORE CONFIGURATION & STATUS
# =============================================================================

def is_telegram_login_configured() -> bool:
    """Returns True if Telegram Login Client ID is configured."""
    return bool(TELEGRAM_LOGIN_CLIENT_ID and TELEGRAM_LOGIN_CLIENT_ID.strip())


def get_configured_bot_username() -> str:
    """Returns the configured Telegram Login bot username without leading @."""
    bot = (TELEGRAM_LOGIN_BOT_USERNAME or "zyroxloginbot").strip().lstrip("@")
    return bot or "zyroxloginbot"


def get_default_redirect_uri(base_url: Optional[str] = None) -> str:
    """
    Returns the canonical redirect URI.
    Uses TELEGRAM_LOGIN_REDIRECT_URI if set, otherwise derives from request base_url or PUBLIC_APP_URL.
    """
    if TELEGRAM_LOGIN_REDIRECT_URI and TELEGRAM_LOGIN_REDIRECT_URI.strip():
        return TELEGRAM_LOGIN_REDIRECT_URI.strip()

    origin = (base_url or PUBLIC_APP_URL or "https://taikry-ai-trading.onrender.com").rstrip("/")
    return f"{origin}/api/v1/auth/telegram/callback"


def get_telegram_login_status(base_url: Optional[str] = None) -> Dict[str, Any]:
    """Returns public configuration status and registration details for BotFather."""
    configured = is_telegram_login_configured()
    bot_username = get_configured_bot_username()
    redirect_uri = get_default_redirect_uri(base_url)

    allowed_urls = [
        redirect_uri,
        "https://taikry-ai-trading.onrender.com/api/v1/auth/telegram/callback",
        "https://zyroxai.onrender.com/api/v1/auth/telegram/callback",
        "http://localhost:8000/api/v1/auth/telegram/callback",
        "http://127.0.0.1:8000/api/v1/auth/telegram/callback"
    ]
    # Deduplicate while preserving order
    deduped_urls = list(dict.fromkeys(allowed_urls))

    return {
        "configured": configured,
        "status": "READY" if configured else "NEEDS_CONFIGURATION",
        "bot_username": bot_username,
        "issuer": TELEGRAM_LOGIN_ISSUER or DEFAULT_ISSUER,
        "authorization_endpoint": DEFAULT_AUTH_ENDPOINT,
        "token_endpoint": DEFAULT_TOKEN_ENDPOINT,
        "jwks_uri": TELEGRAM_LOGIN_JWKS_URI or DEFAULT_JWKS_URI,
        "current_redirect_uri": redirect_uri,
        "allowed_callback_urls": deduped_urls,
        "required_env_vars": [
            "TELEGRAM_LOGIN_CLIENT_ID",
            "TELEGRAM_LOGIN_CLIENT_SECRET",
            "TELEGRAM_LOGIN_REDIRECT_URI"
        ] if not configured else []
    }


# =============================================================================
# AUTHORIZATION URL GENERATOR
# =============================================================================

def build_telegram_authorization_url(
    base_url: Optional[str] = None,
    return_to: Optional[str] = None,
    explicit_redirect_uri: Optional[str] = None
) -> Tuple[str, str]:
    """
    Constructs the Telegram OpenID Connect authorization URL with PKCE (S256).
    Stores state, nonce, and code_verifier securely on the server.
    Returns (authorization_url, state).
    """
    if not is_telegram_login_configured():
        raise ValueError("Telegram Login is not configured. Missing TELEGRAM_LOGIN_CLIENT_ID.")

    code_verifier, code_challenge = generate_pkce_pair()
    state, nonce = generate_state_and_nonce()
    redirect_uri = explicit_redirect_uri or get_default_redirect_uri(base_url)

    # Store state securely on the server
    auth_state_store.store(
        state=state,
        nonce=nonce,
        code_verifier=code_verifier,
        redirect_uri=redirect_uri,
        return_to=return_to
    )

    params = {
        "client_id": TELEGRAM_LOGIN_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": DEFAULT_SCOPES,
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "bot_username": get_configured_bot_username()
    }

    auth_url = f"{DEFAULT_AUTH_ENDPOINT}?{urlencode(params)}"
    return auth_url, state


# =============================================================================
# TOKEN EXCHANGE & ID TOKEN VALIDATION
# =============================================================================

def exchange_code_for_tokens(
    code: str,
    code_verifier: str,
    redirect_uri: str,
    token_endpoint: Optional[str] = None,
    http_client: Optional[httpx.Client] = None
) -> Dict[str, Any]:
    """
    Exchanges authorization code and PKCE code_verifier for tokens at Telegram's token endpoint.
    Performs exchange strictly on the backend.
    """
    endpoint = token_endpoint or DEFAULT_TOKEN_ENDPOINT
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": TELEGRAM_LOGIN_CLIENT_ID,
        "code_verifier": code_verifier
    }
    if TELEGRAM_LOGIN_CLIENT_SECRET:
        payload["client_secret"] = TELEGRAM_LOGIN_CLIENT_SECRET

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "User-Agent": "ZYROX-AI-Telegram-OIDC/2.0"
    }

    if http_client:
        resp = http_client.post(endpoint, data=payload, headers=headers)
        if resp.status_code >= 400:
            raise ValueError(f"Telegram token exchange failed ({resp.status_code}): {resp.text}")
        return resp.json()

    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        resp = client.post(endpoint, data=payload, headers=headers)
        if resp.status_code >= 400:
            raise ValueError(f"Telegram token exchange failed ({resp.status_code}): {resp.text}")
        return resp.json()


def validate_id_token(
    id_token: str,
    expected_nonce: str,
    expected_client_id: Optional[str] = None,
    expected_issuer: Optional[str] = None,
    jwks_provider: Optional[TelegramJWKSCache] = None,
    signing_key_override: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Validates Telegram ID token:
    1. Signature using Telegram JWKS public key
    2. Issuer matches https://oauth.telegram.org
    3. Audience matches TELEGRAM_LOGIN_CLIENT_ID
    4. Token is not expired and issued-at is valid
    5. Nonce matches the session nonce
    6. Identifies account by stable subject (sub)
    """
    client_id = expected_client_id or TELEGRAM_LOGIN_CLIENT_ID
    issuer = expected_issuer or TELEGRAM_LOGIN_ISSUER or DEFAULT_ISSUER

    if not id_token:
        raise ValueError("Missing ID token")

    # Read unverified header to get kid and alg
    try:
        header = jwt.get_unverified_header(id_token)
    except Exception as e:
        raise ValueError(f"Invalid JWT header format: {e}")

    alg = header.get("alg")
    kid = header.get("kid")

    if not alg:
        raise ValueError("Missing algorithm (alg) in ID token header")

    allowed_algorithms = ["RS256", "ES256", "EdDSA", "ES256K"]
    if alg not in allowed_algorithms:
        raise ValueError(f"Unsupported algorithm '{alg}'. Expected one of {allowed_algorithms}")

    # Determine verification key
    if signing_key_override:
        public_key = signing_key_override
    else:
        provider = jwks_provider or jwks_cache
        if not kid:
            raise ValueError("Missing key ID (kid) in ID token header")
        public_key = provider.get_key_by_kid(kid)
        if not public_key:
            # Try a forced refresh once
            public_key = provider.get_key_by_kid(kid, force_refresh=True)
            if not public_key:
                raise ValueError(f"Signing key with kid '{kid}' not found in Telegram JWKS")

    # Decode and verify JWT
    try:
        claims = jwt.decode(
            id_token,
            key=public_key,
            algorithms=[alg],
            audience=client_id,
            issuer=issuer,
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
                "verify_iat": True
            }
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Telegram ID token has expired")
    except jwt.InvalidIssuerError:
        raise ValueError(f"Invalid token issuer. Expected '{issuer}'")
    except jwt.InvalidAudienceError:
        raise ValueError(f"Invalid token audience. Expected client ID '{client_id}'")
    except jwt.InvalidSignatureError:
        raise ValueError("Invalid Telegram ID token signature")
    except Exception as decode_err:
        raise ValueError(f"ID token verification failed: {decode_err}")

    # Validate nonce
    token_nonce = claims.get("nonce")
    if not token_nonce or token_nonce != expected_nonce:
        raise ValueError(f"Nonce mismatch. Expected '{expected_nonce}', got '{token_nonce}'")

    # Validate subject (sub)
    sub = claims.get("sub")
    if not sub:
        raise ValueError("Missing stable subject (sub) in ID token claims")

    return claims


# =============================================================================
# USER RETRIEVAL, CREATION & ACCOUNT LINKING
# =============================================================================

def authenticate_or_create_telegram_user(
    db: Session,
    claims: Dict[str, Any],
    current_user: Optional[User] = None,
    ip_address: Optional[str] = None
) -> Tuple[bool, str, Optional[User], bool]:
    """
    Identifies or creates a canonical ZYROX AI user account from verified Telegram claims.
    Always uses Telegram's stable numeric subject ID (`sub`), NOT username.

    Returns: (success, message, user_object, is_new_user)
    """
    sub = str(claims.get("sub", "")).strip()
    if not sub:
        return False, "Missing Telegram subject identifier (sub).", None, False

    username = claims.get("preferred_username") or claims.get("username")
    first_name = claims.get("given_name") or claims.get("first_name")
    last_name = claims.get("family_name") or claims.get("last_name")
    full_name_candidate = claims.get("name")
    if not full_name_candidate:
        if first_name and last_name:
            full_name_candidate = f"{first_name} {last_name}".strip()
        elif first_name:
            full_name_candidate = first_name.strip()
        elif username:
            full_name_candidate = f"@{username.lstrip('@')}"
        else:
            full_name_candidate = f"Telegram User {sub[:6]}"

    now_utc = datetime.datetime.now(datetime.timezone.utc)

    # Case A: Current user is already logged in -> Account Linking
    if current_user and current_user.is_active:
        # Check if sub is already linked to another different user
        conflict_user = db.query(User).filter(
            User.telegram_user_id == sub,
            User.id != current_user.id,
            User.deleted_at == None
        ).first()
        if conflict_user:
            return False, "This Telegram account is already linked to another ZYROX AI account.", None, False

        # Link to current user
        current_user.telegram_user_id = sub
        current_user.updated_at = now_utc

        # Update or create TelegramLink entry
        tg_link = db.query(TelegramLink).filter(TelegramLink.user_id == current_user.id).first()
        if not tg_link:
            tg_link = TelegramLink(
                user_id=current_user.id,
                telegram_chat_id=sub,
                telegram_username=username,
                telegram_first_name=first_name,
                is_linked=True,
                linked_at=now_utc,
                created_at=now_utc
            )
            db.add(tg_link)
        else:
            tg_link.telegram_chat_id = sub
            if username:
                tg_link.telegram_username = username
            if first_name:
                tg_link.telegram_first_name = first_name
            tg_link.is_linked = True
            tg_link.linked_at = now_utc
            tg_link.unlinked_at = None

        audit = AuditLog(
            actor_user_id=current_user.id,
            action="TELEGRAM_ACCOUNT_LINKED_OIDC",
            target_type="user",
            target_id=str(current_user.id),
            details={"telegram_sub": sub, "username": username},
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(current_user)
        return True, "Telegram account linked successfully.", current_user, False

    # Case B: Look up existing user by stable telegram_user_id (sub)
    existing_user = db.query(User).filter(
        User.telegram_user_id == sub,
        User.deleted_at == None
    ).first()

    # Fallback lookup: Check if user has an existing TelegramLink with this chat ID
    if not existing_user:
        existing_link = db.query(TelegramLink).filter(
            TelegramLink.telegram_chat_id == sub,
            TelegramLink.is_linked == True
        ).first()
        if existing_link:
            candidate = db.query(User).filter(
                User.id == existing_link.user_id,
                User.deleted_at == None
            ).first()
            if candidate:
                existing_user = candidate
                existing_user.telegram_user_id = sub
                db.commit()

    if existing_user:
        if not existing_user.is_active:
            return False, "This account has been deactivated or suspended.", None, False

        # Keep profile name updated if missing
        if not existing_user.full_name and full_name_candidate:
            existing_user.full_name = full_name_candidate
            db.commit()

        # Update TelegramLink metadata
        tg_link = db.query(TelegramLink).filter(TelegramLink.user_id == existing_user.id).first()
        if tg_link:
            if username and tg_link.telegram_username != username:
                tg_link.telegram_username = username
            if first_name and tg_link.telegram_first_name != first_name:
                tg_link.telegram_first_name = first_name
            tg_link.is_linked = True
            tg_link.linked_at = now_utc
            db.commit()

        audit = AuditLog(
            actor_user_id=existing_user.id,
            action="TELEGRAM_LOGIN_SUCCESS_OIDC",
            target_type="user",
            target_id=str(existing_user.id),
            details={"telegram_sub": sub, "username": username},
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        return True, "Login successful.", existing_user, False

    # Case C: New Account Registration
    canonical_email = f"tg_{sub}@telegram.zyrox.ai"
    # Ensure email is unique in case of edge collisions
    candidate_email = canonical_email
    counter = 1
    while db.query(User).filter(User.email == candidate_email).first():
        candidate_email = f"tg_{sub}_{counter}@telegram.zyrox.ai"
        counter += 1

    # Generate cryptographic random password so raw password login without setting one is blocked
    random_secret_pass = secrets.token_hex(32)
    hashed_pwd, salt = hash_password(random_secret_pass)

    new_user = User(
        telegram_user_id=sub,
        email=candidate_email,
        hashed_password=hashed_pwd,
        salt=salt,
        full_name=full_name_candidate,
        role="user",
        is_verified=True,  # Identity is verified by Telegram OIDC
        is_active=True,
        language="en",
        timezone="Asia/Phnom_Penh",
        terms_accepted_at=now_utc,
        terms_version="v1.0",
        privacy_accepted_at=now_utc,
        created_at=now_utc,
        updated_at=now_utc
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 1. Assign default 'user' role in user_roles table
    existing_ur = db.query(UserRole).filter(
        UserRole.user_id == new_user.id,
        UserRole.role_id == "user"
    ).first()
    if not existing_ur:
        try:
            db.add(UserRole(user_id=new_user.id, role_id="user"))
            db.commit()
        except Exception:
            db.rollback()

    # 2. Automatically grant 14-day institutional free trial
    grant_ok, grant_msg, _ = grant_14_day_trial(db, new_user)

    # 3. Create TelegramLink record
    tg_link = TelegramLink(
        user_id=new_user.id,
        telegram_chat_id=sub,
        telegram_username=username,
        telegram_first_name=first_name,
        is_linked=True,
        linked_at=now_utc,
        created_at=now_utc
    )
    db.add(tg_link)

    # 4. Default notification preferences
    notif_prefs = NotificationPreferences(
        user_id=new_user.id,
        ai_analysis_completed=True,
        signal_generated=True,
        signal_invalidated=True,
        macro_events=True,
        daily_summary=True,
        trial_expiration_reminders=True,
        subscription_status_changes=True,
        system_announcements=True
    )
    db.add(notif_prefs)

    # 5. Audit Log
    audit = AuditLog(
        actor_user_id=new_user.id,
        action="TELEGRAM_SIGNUP_SUCCESS_OIDC",
        target_type="user",
        target_id=str(new_user.id),
        details={"telegram_sub": sub, "username": username, "trial_granted": grant_ok},
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
    db.refresh(new_user)

    return True, "Account registered successfully via Telegram with 14-day free trial.", new_user, True


def issue_telegram_session(
    db: Session,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Tuple[str, datetime.datetime]:
    """
    Creates an authenticated 30-day session for the user.
    Returns (raw_session_token, expires_at_utc).
    """
    raw_token, token_hash = generate_session_token()
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    expires_utc = now_utc + datetime.timedelta(days=SESSION_DURATION_DAYS)

    session = UserSession(
        user_id=user.id,
        token_hash=token_hash,
        ip_address=ip_address,
        user_agent=user_agent[:250] if user_agent else None,
        expires_at=expires_utc,
        created_at=now_utc,
        last_seen_at=now_utc
    )
    db.add(session)
    db.commit()

    return raw_token, expires_utc
