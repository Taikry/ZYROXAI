# ZYROX AI V6 — Security Audit Report

**Date:** 2026-11-17  
**Project:** ZYROX AI — Real-Time Multi-Agent Intelligence V6  
**Auditor:** Cybersecurity & Infrastructure Engineering  
**Scope:** Authentication, Session Management, RBAC, API Protection, Webhook/Bridge Security  

---

## 1. Threat Modeling & Scope Overview

This security audit inspects all entry points, cryptographic primitives, credential storage mechanisms, session lifecycles, and authorization boundaries across ZYROX AI.

The audit identifies five primary attack vectors categorized as **Priority P0**:

1. **Vector A:** Unauthenticated Dashboard Access & Private Route Leakage
2. **Vector B:** Anonymous AI LLM Quota Bypass & Denial of Service
3. **Vector C:** Hardcoded MT5 Bridge Secret & Unauthenticated Market Injection
4. **Vector D:** Telegram OIDC Account Takeover & Token Impersonation
5. **Vector E:** Privilege Escalation & Inadequate RBAC Server Enforcement

---

## 2. Detailed Vulnerability Findings & Mitigations

### 2.1 Vulnerability P0-A: Unauthenticated Access to `/dashboard/`

- **Severity:** HIGH (CWE-306: Missing Authentication for Critical Function)
- **Current State:**

  ```python
  # taikry/api/app.py:151
  app.mount("/dashboard", StaticFiles(directory=web_dir, html=True), name="dashboard")
  ```

  Static files are served directly by Starlette without middleware inspection. Unauthenticated visitors direct-linking `/dashboard/` load the terminal frontend and client-side scripts.
- **Remediation Strategy:**
  1. Register explicit route handlers for `/dashboard`, `/dashboard/`, and `/dashboard/index.html`.
  2. Inspect incoming requests for `zyrox_session` or `session_token` cookie or `Authorization: Bearer` header.
  3. Validate token against `taikry.saas.auth_service.authenticate_session(db, token)`.
  4. If invalid or missing, issue an HTTP 307 redirect to `/?auth=signin&return_to=/dashboard/`.
  5. If valid, serve `index.html` via `FileResponse`.
  6. Retain public static asset serving for `/dashboard/styles.css`, `/dashboard/assets/*`, and JS scripts.

### 2.2 Vulnerability P0-B: Anonymous AI Chat Quota Bypass

- **Severity:** HIGH (CWE-862: Missing Authorization)
- **Current State:**

  ```python
  # taikry/api/routes.py:296-320
  token = authorization[7:].strip() if authorization ... else (zyrox_session or "").strip()
  if token:
      # validate and check quota
  # Proceeds unconditionally to chat_with_real_ai without token check!
  ```

  An attacker can omit the `Authorization` header and `zyrox_session` cookie to freely trigger costly multi-agent LLM invocations without consuming user quota or having an active subscription.
- **Remediation Strategy:**
  1. Require an authenticated user context via FastAPI `Depends(get_current_user)`.
  2. Reject missing or expired credentials with HTTP 401 Unauthorized.
  3. Enforce plan-level quota checks before dispatching queries to `chat_with_real_ai`.
  4. Return consistent error structures:

     ```json
     {"detail": "Authentication required. Please sign in to access AI Chat."}
     ```

### 2.3 Vulnerability P0-C: MT5 Bridge Default Credentials & Open Fallback

- **Severity:** CRITICAL (CWE-798: Use of Hard-coded Credentials)
- **Current State:**

  ```python
  # taikry/data/mt5_receiver.py:66
  expected_token = MT5_BRIDGE_TOKEN or "zyrox_mt5_bridge_secure_token_change_me"
  ```

  If `MT5_BRIDGE_TOKEN` is unset in production, any external actor knowing or guessing the default string can inject fabricated ticks and candle data into the platform.
- **Remediation Strategy:**
  1. Remove the hardcoded fallback token immediately.
  2. Fail closed: If `not MT5_BRIDGE_TOKEN or not MT5_BRIDGE_TOKEN.strip()`, reject all bridge requests with HTTP 503 / 401 (`MT5 bridge authentication is not configured`).
  3. Perform constant-time verification using `hmac.compare_digest`.
  4. Never log tokens or received secrets to stdout or logger.

### 2.4 Vulnerability P0-D: Telegram OIDC Authentication Verification

- **Severity:** MEDIUM (Audit & Hardening)
- **Current State:**
  - Implements PKCE S256 (`code_verifier`, `code_challenge`).
  - Implements state and nonce validation with 10-minute TTL and atomic popping.
  - Verifies ID token signature against Telegram JWKS.
  - Links account by permanent Telegram subject `sub` rather than mutable username.
- **Remediation Strategy:**
  - Ensure `TELEGRAM_LOGIN_CLIENT_SECRET` is never returned in public config endpoints.
  - Return `NEEDS_CONFIGURATION` when credentials are not yet configured.
  - Prevent duplicate or hostile account re-linking if an account is already tied to an existing email.

### 2.5 Vulnerability P0-E: Role-Based Access Control (RBAC) Enforcement

- **Severity:** HIGH (CWE-285: Improper Authorization)
- **Current State:**
  - `UserRole` model supports multiple roles (`super_admin`, `admin`, `user`).
  - Sensitive administrative endpoints must enforce `get_current_admin` or `get_current_super_admin` consistently.
- **Remediation Strategy:**
  1. Audit every administrative endpoint under `/api/v1/admin/*` to ensure `Depends(get_current_admin)` or `Depends(get_current_super_admin)` is attached.
  2. Prevent users from self-promoting by blocking role modification in user profile endpoints.
  3. Audit all administrative modifications in `AuditLog`.

---

## 3. Cryptographic & Credential Storage Audit

| Component | Standard Applied | Status |
| :--- | :--- | :--- |
| **Password Storage** | PBKDF2-HMAC-SHA256 (100,000 iterations + 32-byte salt) | `COMPLIANT` |
| **Session Tokens** | 256-bit URL-safe random, stored as SHA-256 hash | `COMPLIANT` |
| **PKCE Verifier** | RFC 7636 S256 Base64URL without padding | `COMPLIANT` |
| **MT5 Signature** | HMAC-SHA256 over timestamp + raw request body | `COMPLIANT` |
| **Cookie Security** | HttpOnly=True, SameSite=Lax, Secure=True on HTTPS | `COMPLIANT` |

---

## 4. Security Action Plan Matrix

| Action Item | Priority | Target File | Status |
| :--- | :--- | :--- | :--- |
| Enforce server-side authentication gate on `/dashboard/` | P0 | `taikry/api/app.py` | `SCHEDULED` |
| Require valid user session on `POST /api/v1/ai/chat` | P0 | `taikry/api/routes.py` | `SCHEDULED` |
| Fail closed on missing `MT5_BRIDGE_TOKEN` & remove default | P0 | `taikry/data/mt5_receiver.py` | `SCHEDULED` |
| Audit RBAC decorators on all admin routes | P0 | `taikry/api/saas_routes.py` | `SCHEDULED` |
| Verify cookie security flags and CSRF handling | P0 | `taikry/api/saas_routes.py` | `SCHEDULED` |
