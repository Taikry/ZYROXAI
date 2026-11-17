# ZYROX AI V6 — Deployment Report

**Date:** 2026-11-17  
**Project:** ZYROX AI — Real-Time Multi-Agent Intelligence V6  
**Infrastructure Target:** Render Cloud (Web Service + Background Worker + PostgreSQL)  
**Repository:** `https://github.com/Taikry/ZYROXAI` (Branch: `main`)  

---

## 1. Hosting Architecture & Service Blueprint

The ZYROX AI platform is architected for continuous 24/7 high-availability deployment on **Render**:

```
                                  [Internet]
                                      |
                                      v
                         [Render Managed HTTPS Proxy]
                                      |
               +----------------------+----------------------+
               |                                             |
               v                                             v
     [Render Web Service]                         [Render Static / CDN]
     - FastAPI ASGI Server (Uvicorn)              - Vite Production Build
     - Port 8000 / $PORT                          - dist/ compiled bundle
     - Dynamic REST APIs                          - Landing page assets
     - Webhook Receivers (MT5, Bakong)
               |
               +----------------------+
               |                      |
               v                      v
     [PostgreSQL Database]     [Background Worker / Scheduler]
     - Durable Source of Truth - 15-Minute M15 Candle Monitor
     - Users, Sessions, Trades - Multi-Agent Deep Research Fleet
     - Confluence Scoring Logs - Telegram Signal Dispatcher
```

---

## 2. Render Blueprint Specification (`render.yaml`)

```yaml
services:
  - type: web
    name: zyrox-ai-web
    env: python
    region: singapore
    plan: starter
    buildCommand: "pip install -r requirements.txt && npm install && npm run build"
    startCommand: "uvicorn taikry.api.app:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /ping
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: NODE_VERSION
        value: 20.x
      - key: ENVIRONMENT
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: zyrox-postgres
          property: connectionString
      - key: AUTO_START_MONITORING
        value: "true"
      - key: PUBLIC_APP_URL
        value: https://taikry-ai-trading.onrender.com

databases:
  - name: zyrox-postgres
    plan: starter
    region: singapore
    databaseName: zyrox_prod
    user: zyrox_admin
```

---

## 3. High-Availability & Free-Tier Keep-Alive Measures

- **Self-Ping Heartbeat:**
  - `taikry/api/app.py` initiates a background daemon thread that pings `GET /ping` every 5–10 minutes to prevent Render free-tier sleep mode when traffic is low.
- **Graceful Shutdown:**
  - Lifespan context manager stops the market monitoring thread and closes database connection pools cleanly on SIGTERM/SIGINT.
- **Fail-Safe Startup:**
  - If external market data feeds are temporarily unreachable or credentials are unpopulated, the server boots in degraded mode rather than crashing.

---

## 4. Environment Variables Checklist for Production

| Variable Name | Required | Default / Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | Yes | PostgreSQL connection string (`postgresql://...`) |
| `JWT_SECRET_KEY` | Yes | Cryptographic secret for signing auth tokens |
| `MT5_BRIDGE_TOKEN` | Yes | Token for authenticating incoming Windows MT5 quotes |
| `TELEGRAM_BOT_TOKEN` | Optional | Telegram Bot token for sending trading signals |
| `TELEGRAM_CHAT_ID` | Optional | Target chat / channel ID for signal distribution |
| `GROQ_API_KEY` | Optional | API key for high-speed Groq LLM inference |
| `ANYROUTER_API_KEY` | Optional | Multi-model routing key |
| `AUTO_START_MONITORING` | No | `"true"` to start background M15 scheduler |
| `PORT` | No | Automatically injected by Render (default `8000`) |
