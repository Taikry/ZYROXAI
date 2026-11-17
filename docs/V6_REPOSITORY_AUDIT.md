# ZYROX AI V6 — Repository Audit Report

**Date:** 2026-11-17  
**Project:** ZYROX AI — Real-Time Multi-Agent Intelligence V6  
**Auditor:** Lead Architect & Systems Engineer  
**Target Branch:** `main`  
**Head Commit:** `eade022`  

---

## 1. Executive Summary

This repository audit inspects the full ZYROX AI codebase (`taikry/`, `src/`, `tests/`, `docs/`, `scripts/`) to establish an empirical inventory of working features, broken features, security vulnerabilities, mock behaviors, and integration prerequisites before implementing the V6 production upgrades.

The repository is built on a high-performance **FastAPI (Python 3.12)** backend with **SQLAlchemy/PostgreSQL** persistence, an **M15 Wall-Clock Market Engine**, an **11-Agent Deep Research Fleet**, and a hybrid frontend consisting of a **React + Vite** marketing/landing application (`src/`, `dist/`) and a real-time **Fintech Trading Terminal** (`taikry/web/`).

---

## 2. Feature Classification Inventory

| Subsystem / Feature | File Path | Status | Evidence / Notes |
| :--- | :--- | :--- | :--- |
| **Telegram OIDC Authentication** | `taikry/saas/telegram_oidc.py` | `IMPLEMENTED` | PKCE S256, JWKS caching, atomic single-use state pop, 14 passing tests. |
| **Email/Password Auth & Trial** | `taikry/saas/auth_service.py` | `WORKING` | PBKDF2-HMAC-SHA256, 14-day trial auto-grant, rate-limiting on login. |
| **Role-Based Access Control (RBAC)** | `taikry/saas/security.py` | `PARTIAL` | `get_current_admin`, `get_current_super_admin` defined; requires enforcement across all admin endpoints. |
| **Dashboard Authentication Gate** | `taikry/api/app.py` | `PARTIAL` | `StaticFiles` mounted directly at `/dashboard`; missing server-side redirect gate for unauthenticated browsers. |
| **AI Chat Endpoint** | `taikry/api/routes.py` | `PARTIAL` | `POST /api/v1/ai/chat` permits anonymous fallback if token is absent; quota check bypasses unauthenticated requests. |
| **MT5 Bridge Authentication** | `taikry/data/mt5_receiver.py` | `BROKEN / INSECURE` | Hardcoded fallback token `"zyrox_mt5_bridge_secure_token_change_me"`; does not fail closed if `MT5_BRIDGE_TOKEN` is unset. |
| **100-Point Confluence Scorer** | `taikry/trading/confluence_scorer.py` | `WORKING` | 8-part weighted model (15/15/15/15/10/10/10/10), 75-point actionable gate, anti-inflation missing data rule. |
| **M15 Wall-Clock Scheduler** | `taikry/monitoring/engine.py` | `IMPLEMENTED` | Aligned to `:00`, `:15`, `:30`, `:45` UTC candle closes. In-process thread requires durable DB task locking. |
| **Market Data Providers** | `taikry/data/providers.py` | `PARTIAL` | OANDA v20, Yahoo Finance, GoldAPI, TWELVEDATA integrated; needs explicit quote classification enforcement. |
| **11-Agent Research Fleet** | `taikry/agents/deep_research_engine.py` | `WORKING` | 11 specialized agents, English + Natural Khmer synthesis, multi-model AnyRouter/Groq failover. |
| **Telegram Signal Delivery** | `taikry/saas/telegram_service.py` | `PARTIAL` | Bot outbox functional; Cambodia calendar day 4-signal cap requires atomic DB quota reservation. |
| **Google OAuth** | `taikry/saas/google_oauth.py` | `NEEDS_CONFIGURATION` | Client ID / Secret credentials required in `.env`; must display `NEEDS_CONFIGURATION` rather than mock. |
| **Phone OTP Authentication** | `taikry/saas/phone_otp.py` | `NEEDS_CONFIGURATION` | SMS provider (Twilio/AWS SNS) credentials required in `.env`. |
| **Bakong KHQR Payments** | `app/payments/` | `WORKING` | Deep link generation, MD5 hash verification, webhook processing. |
| **Vite Frontend Landing** | `src/`, `dist/` | `WORKING` | React 18 + TailwindCSS, responsive mobile sheet, modals, builds clean in 753ms. |
| **Fintech Terminal Web UI** | `taikry/web/app.js` | `WORKING` | Dual Khmer/English, chart rendering, terminal chat, audio alerts, startup loader resolved. |

---

## 3. High-Priority Deficiencies & Vulnerabilities

### A. Dashboard Authentication Gate Missing on Static Mount

- **Location:** `taikry/api/app.py:151`
- **Issue:** `app.mount("/dashboard", StaticFiles(directory=web_dir, html=True), name="dashboard")` serves `index.html` to any unauthenticated client without session cookie verification.
- **Remediation:** Implement server-side route handlers for `/dashboard`, `/dashboard/`, and `/dashboard/index.html` that validate the session via `authenticate_session(db, token)` and redirect unauthenticated requests to `/?auth=signin&return_to=/dashboard/`.

### B. AI Chat Anonymous Fallback Bypass

- **Location:** `taikry/api/routes.py:282-320`
- **Issue:** If `Authorization` header and `zyrox_session` cookie are absent, `chat_ai_endpoint` silently bypasses authentication and quota consumption, running LLM inference for anonymous users.
- **Remediation:** Enforce mandatory server-side authentication; raise `HTTPException(status_code=401, detail="Authentication required")` for unauthenticated requests.

### C. MT5 Insecure Default Secret & Open Fallback

- **Location:** `taikry/data/mt5_receiver.py:66`
- **Issue:** Falls back to hardcoded token `"zyrox_mt5_bridge_secure_token_change_me"` if `MT5_BRIDGE_TOKEN` is unset, exposing live bridge endpoints to unauthorized payloads.
- **Remediation:** Fail closed immediately if `MT5_BRIDGE_TOKEN` is missing or empty. Compare tokens using `hmac.compare_digest`.

### D. Quote Classification & Synthetic Spreads

- **Location:** `taikry/data/providers.py`, `taikry/trading/xauusd_signal_engine.py`
- **Issue:** Reference prices (e.g., Yahoo Finance) may be labeled as executable bid/ask without explicit classification.
- **Remediation:** Enforce explicit quote classifications: `REAL_BROKER_QUOTE`, `REFERENCE_PRICE`, `ESTIMATED_SPREAD`, `STALE`, `DISCONNECTED`, `UNAVAILABLE`. Never label estimated spreads as real broker quotes.

---

## 4. Preservation Invariant Checklist

- [x] DO NOT delete existing database models or migration history.
- [x] DO NOT delete existing multi-agent registry or deep research agents.
- [x] DO NOT remove Telegram bot webhook or OIDC login flow.
- [x] DO NOT replace FastAPI backend with a new framework.
- [x] DO NOT fabricate fake market quotes or synthetic win rates.
