# ZYROX AI V6 — Integration Status Report

**Date:** 2026-11-17  
**Project:** ZYROX AI — Real-Time Multi-Agent Intelligence V6  
**Auditor:** Integrations & API Gateway Specialist  

---

## 1. External Services & Providers Status Matrix

| Integration | Provider / Protocol | Status | Required Credentials in `.env` | Failure Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **Exness MT5 Bridge** | Local TCP / HTTP WebSocket | `IMPLEMENTED` | `MT5_BRIDGE_TOKEN` | Fails closed; displays `DISCONNECTED` |
| **OANDA v20 REST** | Primary Reference Market Feed | `WORKING` | `OANDA_API_KEY`, `OANDA_ACCOUNT_ID` | Fallback to GoldAPI / TWELVEDATA |
| **GoldAPI.io** | Secondary Precious Metals Feed | `WORKING` | `GOLD_API_KEY` | Fallback to Yahoo Finance |
| **TWELVEDATA** | Tertiary Multi-Asset Feed | `WORKING` | `TWELVE_DATA_API_KEY` | Graceful degradation |
| **Yahoo Finance** | Non-Executable Reference Only | `WORKING` | None (Public HTTP) | Classified as `REFERENCE_PRICE` |
| **Telegram Bot API** | Signal Outbox & Notifications | `WORKING` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Logs warning; queues in outbox |
| **Telegram OIDC** | Web Login (OpenID Connect) | `IMPLEMENTED` | `TELEGRAM_LOGIN_CLIENT_ID`, `TELEGRAM_LOGIN_CLIENT_SECRET` | Returns `NEEDS_CONFIGURATION` |
| **Google OAuth2** | Web Login (Google Accounts) | `NEEDS_CONFIGURATION` | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` | Displays `NEEDS_CONFIGURATION` |
| **Phone SMS OTP** | Two-Factor & Phone Login | `NEEDS_CONFIGURATION` | `SMS_PROVIDER_API_KEY`, `SMS_SENDER_ID` | Displays `NEEDS_CONFIGURATION` |
| **Bakong KHQR** | Cambodian Real-Time Payments | `WORKING` | `BAKONG_MERCHANT_ID`, `BAKONG_API_KEY` | Fallback to manual QR |
| **Groq Cloud API** | Ultra-Fast LLM Inference | `WORKING` | `GROQ_API_KEY` | Failover to AnyRouter / OpenRouter |
| **AnyRouter API** | Multi-Model Routing & Budget | `WORKING` | `ANYROUTER_API_KEY` | Failover to Groq / Local |

---

## 2. Market Data Flow & Integrity Controls

```text
[Exness MT5 Windows Bridge] ---------> Classified as REAL_BROKER_QUOTE (Executable)
                                              |
[OANDA v20 / GoldAPI / 12Data] ------> Classified as REFERENCE_PRICE (Comparative)
                                              |
[Yahoo Finance] ---------------------> Classified as REFERENCE_PRICE (Non-executable)
                                              |
                                              v
                              +-------------------------------+
                              | Market Data Integrity Guard   |
                              | - Check freshness (< 30s)     |
                              | - Flag STALE if > 30s         |
                              | - Never label estimate as real|
                              +-------------------------------+
                                              |
                                              v
                              +-------------------------------+
                              | 100-Point Confluence Scorer   |
                              | Requires valid execution data |
                              | Score >= 75 for BUY / SELL    |
                              +-------------------------------+
```

---

## 3. Configuration Prerequisite Guide

For production activation on Render or dedicated VPS, the following environment variables must be populated in the Render Dashboard or `.env`:

### 3.1 Market Data & Broker

- `MT5_BRIDGE_TOKEN`: Cryptographically strong random token for the MT5 Windows Bridge.
- `OANDA_API_KEY`: API access token from OANDA fxTrade practice or live account.
- `GOLD_API_KEY`: API key from GoldAPI.io.

### 3.2 Authentication & Security

- `JWT_SECRET_KEY`: 256-bit secret for signing application JWT tokens.
- `TELEGRAM_LOGIN_CLIENT_ID`: Telegram Login widget / Bot ID from `@BotFather`.
- `TELEGRAM_LOGIN_CLIENT_SECRET`: Telegram Login secret key from `@BotFather`.
- `TELEGRAM_LOGIN_REDIRECT_URI`: e.g. `https://taikry-ai-trading.onrender.com/api/v1/auth/telegram/callback`.
- `GOOGLE_CLIENT_ID`: Google Cloud Console OAuth 2.0 Client ID (optional).
- `GOOGLE_CLIENT_SECRET`: Google Cloud Console OAuth 2.0 Client Secret (optional).

### 3.3 Artificial Intelligence Fleet

- `GROQ_API_KEY`: API key from console.groq.com.
- `ANYROUTER_API_KEY`: API key from AnyRouter dashboard.
