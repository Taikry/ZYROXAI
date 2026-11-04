# ZYROX AI — Render Production Deployment Runbook

## 1. Production Service Overview
- **Service Name:** `zyroxai`
- **Public URL:** `https://zyroxai.onrender.com` (or custom domain e.g. `https://zyroxai.com`)
- **Dashboard URL:** `https://zyroxai.onrender.com/dashboard/`
- **Healthcheck Path:** `/ping`
- **Environment:** Python 3.12 (Linux 64-bit)
- **Host Region:** Singapore (or Frankfurt / Oregon)

---

## 2. Environment Variables Specification

| Environment Variable | Required | Description | Example / Default |
|:---|:---:|:---|:---|
| `PYTHON_VERSION` | Yes | Runtime Python version | `3.12.0` |
| `SECRET_KEY` | Yes | App session signature key | `<64-char-hex>` |
| `DATABASE_URL` | Yes | PostgreSQL connection URI | `postgresql://...` |
| `PUBLIC_APP_URL` | Yes | Primary public domain URL | `https://zyroxai.onrender.com` |
| `TELEGRAM_ENABLED` | Yes | Master toggle for bot | `true` |
| `TELEGRAM_BOT_TOKEN` | Yes | Official BotFather token | `123456789:ABC...` |
| `TELEGRAM_CHAT_ID` | Yes | Primary alerts channel ID | `-1004341134868` |
| `TELEGRAM_SEND_LIFECYCLE_EVENTS` | Yes | Suppress TP/SL notification spam | `false` |
| `MAX_DAILY_XAUUSD_SIGNALS` | Yes | Daily signal limit hard cap | `4` |
| `PAYWAY_MERCHANT_ID` | Yes | ABA PayWay merchant ID | `ec479879` |
| `PAYWAY_PUBLIC_KEY` | Yes | ABA PayWay public key | `B10B32C154CB...` |
| `PAYWAY_API_URL` | Yes | ABA PayWay purchase endpoint | `https://checkout-sandbox.payway.com.kh/...` |
| `PAYWAY_CHECK_TRANSACTION_URL` | Yes | ABA PayWay transaction check | `https://checkout-sandbox.payway.com.kh/...` |

---

## 3. Health Checks & Verification Commands

### 3.1 Ping Endpoint Verification
```bash
curl -i https://zyroxai.onrender.com/ping
```
Expected HTTP Response:
```json
HTTP/1.1 200 OK
Content-Type: application/json

{"status":"pong","app":"ZYROX AI TRADING PRO","version":"2.0.0"}
```

### 3.2 Web Dashboard Verification
```bash
curl -I https://zyroxai.onrender.com/dashboard/
```
Expected HTTP Response: `200 OK`

---

## 4. Zero-Downtime Rolling Restarts & Emergency Pause

- **To Pause Telegram Sends Immediately:**
  Set `TELEGRAM_ENABLED=false` in Render Environment and trigger a restart. Web APIs, charts, and analysis will continue functioning without sending Telegram alerts.
- **To Silence Lifecycle Spam Only:**
  Ensure `TELEGRAM_SEND_LIFECYCLE_EVENTS=false` is set.
- **To Roll Back a Deployment:**
  Use the Render Dashboard "Rollback" feature to revert to the previous successful deploy hash. Database migrations are backwards-compatible (all added columns are nullable).

