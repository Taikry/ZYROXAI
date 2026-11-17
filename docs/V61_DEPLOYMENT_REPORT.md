# ZYROX AI V6.1 — PRODUCTION DEPLOYMENT & ROLLOUT REPORT

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** 6.1.0-PROD  
**Target Branch:** `main`  
**Founder:** HENG TAIKRY  
**Date:** 2026-11-18  
**Status:** VERIFIED  

---

## 1. Deployment Topology

ZYROX AI is deployed as a dual-tier cloud application:

1. **Backend Application Server:** Python FastAPI web server running on Render (`taikry-ai-trading.onrender.com`).
2. **Database:** PostgreSQL (with SQLite compatibility for local dev/testing).
3. **Execution Layer:** Windows Desktop MT5 Bridge receiving real-time ticks from Exness broker.
4. **Outbox & Notification Layer:** Telegram Bot API (`Asia/Phnom_Penh` Cambodia timezone).
5. **Frontend Web Client:** Responsive React + Vite SPA and static trading terminal (`/dashboard/`).

---

## 2. Environment Variables & Credentials Matrix

| Variable | Scope | Status | Purpose |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Production | `CONFIGURED` | PostgreSQL database connection string |
| `TELEGRAM_BOT_TOKEN` | Production | `CONFIGURED` | Telegram notification dispatcher |
| `TELEGRAM_CHAT_ID` | Production | `CONFIGURED` | Primary VIP signal channel |
| `TELEGRAM_LOGIN_CLIENT_ID` | Production | `OPTIONAL` | Telegram OIDC login client |
| `GOOGLE_CLIENT_ID` | Production | `OPTIONAL` | Google OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Production | `OPTIONAL` | Google OAuth 2.0 Client Secret |
| `TWILIO_ACCOUNT_SID` | Production | `OPTIONAL` | Phone SMS OTP gateway |
| `TWILIO_AUTH_TOKEN` | Production | `OPTIONAL` | Twilio API authentication token |
| `TWILIO_PHONE_NUMBER` | Production | `OPTIONAL` | Originating SMS phone number |
| `EXNESS_MT5_TOKEN` | Production | `CONFIGURED` | Windows desktop bridge authentication |

---

## 3. Database Migrations Applied

The database migration ledger (`taikry/database/versioned_migrations.py`) executed all migrations up to:

* `0013_telegram_oidc_login`: Added `telegram_user_id` and unique index.
* `0014_v61_auth_credentials`: Added `google_user_id`, `phone_number` columns and created `phone_otp_challenges` table.

---

## 4. Production Health Verification

* Live Ping Check: `GET /ping` returns `{"status": "pong", "app": "ZYROX AI TRADING PRO", "version": "2.0.0"}`.
* Authentication Readiness:
  * `GET /api/v1/auth/google/status` -> returns `status: READY` or `NEEDS_CONFIGURATION` safely.
  * `GET /api/v1/auth/phone/status` -> returns `status: READY` or `NEEDS_CONFIGURATION` safely.
  * `GET /api/v1/auth/telegram/status` -> returns `status: READY` or `NEEDS_CONFIGURATION` safely.
* Startup Loader Safety:
  * The dashboard loader automatically dismisses within 400ms on auth callback and within 2.5s maximum under all network conditions.
