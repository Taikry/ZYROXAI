# ZYROX AI V6.1.1 — AUTHENTICATION, OAUTH & SECURITY ARCHITECTURE

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** V6.1.1 Production Hardening  
**Supported Authentication Methods:** Email/Password, Google OAuth 2.0 (PKCE), Phone OTP, Telegram OIDC  
**Token Security:** Cryptographic Hash (SHA-256) Stored in Database, HTTP-Only Cookie  
**Status:** IMPLEMENTED & VERIFIED  

---

## 1. Executive Summary

ZYROX AI SaaS tier supports seamless, secure user authentication across web and mobile browsers. V6.1.1 hardened all authentication flows, resolved local development vs production redirect URI mismatches, and enforced strict cryptographic state validation.

---

## 2. Authentication Implementations

### 2.1 Google OAuth 2.0 with PKCE S256 (`taikry/saas/google_oauth.py`)

- **PKCE S256 Flow:** Generates high-entropy `code_verifier` and SHA-256 `code_challenge`.
- **State Token Validation:** Encodes cryptographic state with 10-minute TTL in cache. Replays and expired tokens are rejected.
- **Dynamic Redirect URI Detection:**  
  `get_google_redirect_uri(request)` detects `localhost` or `127.0.0.1` and uses `http://localhost:8000/api/v1/auth/google/callback`, while production traffic defaults to `https://taikry-ai-trading.onrender.com/api/v1/auth/google/callback`.
- **Auto-Provisioning:** New Google users are automatically registered and provisioned with a 14-day Pro trial.

### 2.2 Phone Number Authentication & SMS OTP (`taikry/saas/phone_otp.py`)

- **E.164 Standardization:** Normalizes phone formats (e.g. `+855968288832` for Cambodia).
- **Cryptographic Challenge:** Generates cryptographically secure 6-digit numeric codes with 5-minute expiration.
- **Rate Limiting:** Enforces cooldown windows and maximum retry attempts to block brute-force attacks.

### 2.3 Session & Token Management

- Passwords hashed with PBKDF2-HMAC-SHA256 using 100,000 iterations and 32-byte cryptographically secure salts.
- Session tokens are stored exclusively as SHA-256 hashes (`token_hash`) in the `user_sessions` table.
- Raw session tokens are delivered only via HTTP-only, `SameSite=Lax` secure cookies (`zyrox_session`).

---

## 3. Verification Suite

Tested and verified in `tests/test_v61_auth_flows.py`:
- `test_phone_e164_normalization`: Validates country code and local mobile prefix formatting.
- `test_phone_otp_generation_and_expiry`: Verifies 6-digit code generation, 5-minute TTL, and invalid code rejection.
- `test_phone_otp_rate_limiting`: Verifies rate limiting blocks excessive OTP requests.
- `test_google_oauth_pkce_generation`: Confirms `code_verifier` (43-128 chars) and matching S256 `code_challenge`.
- `test_google_oauth_state_cache`: Confirms state TTL and replay attack rejection.
- `test_google_redirect_uri_resolution`: Confirms dynamic port/host detection for local dev and production.
- `test_google_user_registration_auto_trial`: Confirms auto-provisioning of 14-day Pro trial on first Google login.
