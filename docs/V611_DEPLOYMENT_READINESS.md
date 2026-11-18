# ZYROX AI V6.1.1 — PRODUCTION DEPLOYMENT READINESS CHECKLIST

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** V6.1.1 Production Hardening  
**Target Platform:** Render Cloud Hosting (API/Web) + Windows Desktop (Exness MT5 Bridge)  
**Database:** PostgreSQL (Production) / SQLite (Local Dev)  
**Status:** READY FOR REVIEW (DO NOT DEPLOY WITHOUT APPROVAL)  

---

## 1. Safety & Deployment Gate Principles

1. **Feature Branch Isolation:** All V6.1.1 code resides exclusively on `feature/zyrox-v6.1.1-production-fixes`. Direct pushes to `main` are strictly forbidden.
2. **Analysis and Signals Only:** ZYROX AI is an intelligence and signal broadcast engine. No automated order placement on broker accounts occurs.
3. **Fail-Closed Architecture:** If any component (MT5 feed, database lock, confluence score, agent quorum) becomes unhealthy, signal generation halts safely.

---

## 2. Environment Variables Checklist

Ensure the following variables are configured in Render environment settings:

| Variable | Required | Description |
| :--- | :---: | :--- |
| `DATABASE_URL` | YES | PostgreSQL connection string (`postgresql://...`) |
| `SECRET_KEY` | YES | 32+ byte cryptographic secret for JWT signing and session security |
| `GOOGLE_CLIENT_ID` | YES | Google OAuth Web Client ID |
| `GOOGLE_CLIENT_SECRET` | YES | Google OAuth Client Secret |
| `GOOGLE_REDIRECT_URI` | YES | `https://taikry-ai-trading.onrender.com/api/v1/auth/google/callback` |
| `TELEGRAM_BOT_TOKEN` | YES | Official Telegram Bot API Token |
| `TELEGRAM_VIP_CHANNEL_ID`| YES | Target VIP Telegram Channel / Group ID |
| `REQUIRE_MT5_FOR_SIGNALS`| YES | Set to `true` in production to enforce Exness MT5 quote execution |
| `MIN_AI_SCORE_THRESHOLD`| YES | Set to `75` (enforces institutional confluence gate) |

---

## 3. Production Healthcheck Endpoints

| Endpoint | Method | Expected Output | Purpose |
| :--- | :---: | :--- | :--- |
| `/api/v1/health` | GET | `{"status": "HEALTHY", "db": "CONNECTED"}` | Verifies web server and database connectivity |
| `/api/v1/bridge/status` | GET | `{"status": "CONNECTED", "broker": "EXNESS", ...}` | Verifies Windows MT5 bridge tick stream |
| `/api/v1/auth/google/status` | GET | `{"configured": true}` | Verifies Google OAuth credential loading |
| `/api/v1/agents/telemetry` | GET | `{"status": "SUCCESS", "telemetry": [...]}` | Verifies agent fleet state |

---

## 4. Rollback Contingency Plan

If any critical operational anomaly occurs upon merging into `main`:
1. Revert to source commit `fbbc213`.
2. Redirections and database migrations are non-destructive (new columns are nullable).
3. The scheduler lock will automatically expire via its 120s TTL without causing deadlocks.
