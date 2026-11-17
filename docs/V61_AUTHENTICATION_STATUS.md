# ZYROX AI V6.1 — AUTHENTICATION SUBSYSTEMS STATUS REPORT

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** 6.1.0-PROD  
**Target Branch:** `main`  
**Founder:** HENG TAIKRY  
**Date:** 2026-11-18  
**Status:** VERIFIED  

---

## 1. Authentication Modalities Overview

ZYROX AI V6.1 supports four distinct authentication pathways, designed for cross-device convenience while enforcing strict enterprise security.

| Modality | Method | Status | Auto Trial Provisioning | Session Duration |
| :--- | :--- | :--- | :--- | :--- |
| **Telegram Login** | OAuth 2.0 / OIDC Authorization Code | `VERIFIED` | 14-Day Pro Trial | 30 Days |
| **Google OAuth 2.0** | Authorization Code Flow with PKCE | `VERIFIED` | 14-Day Pro Trial | 30 Days |
| **Phone SMS OTP** | Twilio REST API + Salted SHA-256 | `VERIFIED` | 14-Day Pro Trial | 30 Days |
| **Email & Password** | PBKDF2-HMAC-SHA256 (100k rounds) | `VERIFIED` | 14-Day Pro Trial | 30 Days |

---

## 2. Subsystem Detailed Analysis

### 2.1 Google OAuth 2.0 PKCE Engine

* **Source:** `taikry/saas/google_oauth.py`, `taikry/api/saas_routes.py`
* **Status:** `VERIFIED` (Code complete and unit-tested)
* **Configuration Requirements:**
  * `GOOGLE_CLIENT_ID`
  * `GOOGLE_CLIENT_SECRET`
  * Optional: `GOOGLE_REDIRECT_URI` (defaults to `/api/v1/auth/google/callback`)
* **Readiness State:**
  * When credentials are provided in environment: Status is `READY`.
  * When credentials are missing: Endpoints gracefully report `NEEDS_CONFIGURATION` without crashing.

### 2.2 Phone SMS OTP Verification Engine

* **Source:** `taikry/saas/phone_otp.py`, `taikry/api/saas_routes.py`
* **Status:** `VERIFIED` (Code complete and unit-tested)
* **Configuration Requirements:**
  * `TWILIO_ACCOUNT_SID`
  * `TWILIO_AUTH_TOKEN`
  * `TWILIO_PHONE_NUMBER`
* **Features:**
  * E.164 phone normalization (including Cambodian `+855` local prefix conversion).
  * 6-digit cryptographic random code.
  * Salted SHA-256 storage with attempt limiting and cooldown enforcement.
* **Readiness State:**
  * When credentials are provided in environment: Status is `READY`.
  * When credentials are missing: Returns `NEEDS_CONFIGURATION` with friendly setup instructions.

### 2.3 Telegram OIDC Login

* **Source:** `taikry/saas/telegram_oidc.py`, `taikry/api/saas_routes.py`
* **Status:** `VERIFIED`
* **Configuration Requirements:**
  * `TELEGRAM_LOGIN_CLIENT_ID`
  * `TELEGRAM_LOGIN_CLIENT_SECRET`
  * `TELEGRAM_BOT_USERNAME`

---

## 3. Dashboard Startup Loader Resolution

A critical bug where browser redirects from authentication callbacks (`?auth_success=telegram&new_user=1`) caused the dashboard startup loader to freeze indefinitely was resolved:

1. **Inline Fail-Safe Dismisser:** `taikry/web/index.html` features an inline script directly after the loader element that unconditionally hides and removes the loader after at most 2.5 seconds.
2. **Fast-Path Auth Callback:** If `window.location.search` contains `auth_success` or `auth_error`, dismissal occurs in under 400ms.
3. **Emergency Bypass Control:** If the loader is active for more than 1.2s, an emergency bypass button `⚡ Open Dashboard / បើកផ្ទាំងបញ្ជា` appears.
4. **Style Override:** Loader dismissal applies inline `style.opacity = "0"`, `style.pointerEvents = "none"`, and `style.display = "none"`, eliminating reliance on external stylesheets.
