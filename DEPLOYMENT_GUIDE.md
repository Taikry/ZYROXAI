# ZYROX AI — Comprehensive Deployment & Operations Guide

## 1. System Requirements & Prerequisites
- **Python:** Version 3.10+ (Python 3.12 Recommended)
- **Database:** PostgreSQL 14+ (or SQLite for isolated local testing)
- **Memory:** Minimum 1 GB RAM, 2 GB+ Recommended for multi-agent workloads
- **Disk:** Minimum 500 MB free space
- **Operating System:** Windows, macOS, or Linux (Debian / Ubuntu / Alpine)

---

## 2. Local Environment Setup

### 2.1 Clone Repository & Virtual Environment
```bash
git clone https://github.com/Taikry/Taikry-AI-Trading.git
cd Taikry-AI-Trading

python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2.2 Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in the necessary credentials:
- `SECRET_KEY`: Random 64-character secret
- `DATABASE_URL`: PostgreSQL connection string (defaults to SQLite if omitted)
- `TELEGRAM_BOT_TOKEN`: Token from @BotFather
- `TELEGRAM_CHAT_ID`: Primary channel/chat ID
- `PAYWAY_MERCHANT_ID`: ABA PayWay merchant ID
- `PAYWAY_PUBLIC_KEY`: ABA PayWay public key

### 2.3 Run Database Migrations
Migrations are applied automatically at server startup through `taikry/database/versioned_migrations.py`.
To run migrations explicitly:
```bash
python -m taikry.database.versioned_migrations
```

### 2.4 Start Local Server
```bash
uvicorn taikry.api.app:app --host 0.0.0.0 --port 8000 --reload
```
Access the application at `http://127.0.0.1:8000/dashboard/`.

---

## 3. Production Deployment (Render)

### 3.1 Render Blueprint Configuration (`render.yaml`)
The project includes a production blueprint `render.yaml` declaring the web service and environment variables:
```yaml
services:
  - type: web
    name: taikry-ai-trading
    runtime: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn taikry.api.app:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /ping
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: TELEGRAM_ENABLED
        value: "true"
      - key: TELEGRAM_SEND_LIFECYCLE_EVENTS
        value: "false"
      - key: MAX_DAILY_XAUUSD_SIGNALS
        value: "4"
      - key: PAYWAY_API_URL
        value: "https://checkout-sandbox.payway.com.kh/api/payment-gateway/v1/payments/purchase"
      - key: PAYWAY_CHECK_TRANSACTION_URL
        value: "https://checkout-sandbox.payway.com.kh/api/payment-gateway/v1/payments/check-transaction-2"
      - key: PAYWAY_MERCHANT_ID
        value: "ec479879"
      - key: PAYWAY_PUBLIC_KEY
        value: "B10B32C154CB629C865E5BE34C1734697A9CC513"
```

### 3.2 Automated Git Deployment
Pushing to the `main` branch triggers an automated build and zero-downtime rolling deployment on Render.
```bash
git push origin main
```

---

## 4. Verification & Health Monitoring

### 4.1 Health Check Endpoints
- **HTTP GET `/ping`:** Returns `{"status": "ok", "service": "taikry-ai-trading"}`
- **HTTP GET `/api/v1/system/info`:** Reports brand, version, active modules, and strategy version
- **HTTP GET `/api/v1/telegram/status`:** Reports Telegram bot connection, chat IDs, and daily quota status

### 4.2 Logging & Incident Response
View live application logs in Render Dashboard or via Render CLI:
```bash
render logs -s taikry-ai-trading
```
