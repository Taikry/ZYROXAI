# ZYROX AI V4 — Complete API Contracts Specification

**Version:** 4.0.0-PROD  
**Base URL:** `https://taikry-ai-trading.onrender.com` (or `http://localhost:8000`)  
**Format:** REST / JSON (UTF-8)  
**Security:** Bearer Token / HttpOnly Session Cookie (`zyrox_session`)  

---

## 1. Health & Diagnostic Endpoints

### `GET /ping`
* **Description:** Production health check used by Render load balancer and uptime monitors.
* **Authentication:** None.
* **Response (200 OK):**
```json
{
  "status": "pong",
  "app": "ZYROX AI TRADING PRO",
  "version": "2.0.0"
}
```

---

## 2. Market Data & Pricing Contracts

### `GET /api/v1/prices/realtime?symbols={symbols}`
* **Description:** Retrieves verified real-time quotes with institutional bid/ask spread and data provenance.
* **Parameters:** `symbols` (comma-separated, e.g. `XAUUSD,EURUSD,BTCUSDT`).
* **Authentication:** None.
* **Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "count": 2,
  "prices": {
    "XAUUSD": {
      "symbol": "XAUUSD",
      "price": 4029.07,
      "bid": 4028.95,
      "ask": 4029.20,
      "spread": 0.25,
      "source": "FALLBACK_YAHOO_FINANCE:PAXG-USD",
      "quote_type": "SPOT_MID",
      "provider": "Yahoo Finance (Fallback)",
      "verified": true,
      "freshness": "LIVE_FRESH",
      "execution_quote_available": true,
      "execution_quote_provider": "Institutional Verified (OANDA (Spot))",
      "execution_quote_source": "INSTITUTIONAL_FEED",
      "quote_kind": "EXECUTABLE_BID_ASK",
      "age_minutes": 0.8,
      "timestamp": "2026-11-04T15:26:29+00:00"
    }
  },
  "timestamp_utc": "2026-11-04T15:27:19.122113"
}
```

---

## 3. Best Setup & Consensus Analysis Contracts

### `GET /api/v1/best-setup?symbol={symbol}&timeframe={tf}`
* **Description:** Evaluates multi-timeframe regime, technical indicators, and SMC concepts to produce a candidate setup.
* **Parameters:** `symbol` (default `XAUUSD`), `timeframe` (default `M15`).
* **Authentication:** Optional (authenticated users receive elevated quotas).
* **Response (200 OK):**
```json
{
  "symbol": "XAUUSD",
  "direction": "WAIT",
  "data_timestamp": "2026-11-04T15:26:29+00:00",
  "provider": "Yahoo Finance (Fallback)",
  "timeframes": ["M15", "H1", "H4"],
  "market_regime": "SQUEEZE_COMPRESSION",
  "strategy": "TREND_PULLBACK",
  "concepts": ["FVG_MITIGATION", "OTE_SWEET_SPOT"],
  "entry": null,
  "stop_loss": null,
  "take_profits": [],
  "quality_score": 74,
  "evidence": [
    "EMA 20/50 compressed in tight range",
    "High impact economic news blackout active"
  ],
  "warnings": [
    "Consensus suppressed execution due to ISM PMI news window"
  ]
}
```

---

## 4. Multi-Agent AI Chat & Copilot Contracts

### `POST /api/v1/ai/chat`
* **Description:** Real AI Copilot integrating multi-agent consensus, verified quote context, and multimodal chart vision.
* **Authentication:** Optional (rate-limited per session / IP).
* **Request Body:**
```json
{
  "query": "Why is the market WAIT on XAUUSD?",
  "symbol": "XAUUSD",
  "timeframe": "15m",
  "provider": "auto",
  "image_base64": null,
  "history": []
}
```
* **Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "provider": "gemini",
  "model": "gemini-2.5-flash",
  "latency_ms": 780,
  "symbol": "XAUUSD",
  "timeframe": "15m",
  "market_context": {
    "price": 4029.07,
    "price_source": "FALLBACK_YAHOO_FINANCE:PAXG-USD",
    "price_freshness": "LIVE_FRESH"
  },
  "smart_analysis": {
    "synthesis_summary_en": "Consensus is on HOLD because price is compressing near Point of Control with upcoming high-impact USD economic catalyst.",
    "synthesis_summary_kh": "ទីផ្សារស្ថិតក្នុងស្ថានភាពរង់ចាំ (HOLD) ដោយសារតម្លៃកំពុងបង្ហាប់ជិតចំណុច POC និងមានព្រឹត្តិការណ៍សេដ្ឋកិច្ច USD ជិតមកដល់។",
    "technical_causes": ["EMA 20/50 flat", "RSI neutral at 51.2"],
    "smc_causes": ["Unmitigated FVG at 4016.50", "Sell-side liquidity sweep pending"],
    "macro_causes": ["ISM PMI release scheduled within pre-news window"],
    "risk_causes": ["Spread ratio within safe 0.25 floor"]
  },
  "trade_execution": {
    "action": "HOLD",
    "status": "NO_APPROVED_SETUP",
    "confidence": 72,
    "entry_price": null,
    "stop_loss": null,
    "take_profit_1": null,
    "risk_reward_ratio": "N/A"
  }
}
```

---

## 5. Authentication & User Profile Contracts

### `POST /api/v1/auth/signup`
* **Request:** `{ "email": "trader@example.com", "password": "SecurePassword123!", "full_name": "Pro Trader" }`
* **Response (200 OK):**
```json
{
  "success": true,
  "message": "Account created successfully. 14-day free trial activated.",
  "data": {
    "user_id": 42,
    "email": "trader@example.com",
    "full_name": "Pro Trader",
    "trial_granted": true
  }
}
```

### `POST /api/v1/auth/login`
* **Request:** `{ "email": "trader@example.com", "password": "SecurePassword123!" }`
* **Response (200 OK):** Sets HttpOnly cookie `zyrox_session` and returns session details.

---

## 6. Payments & KHQR Contracts

### `POST /api/v1/billing/checkout`
* **Request:** `{ "plan_id": "pro", "currency": "USD" }`
* **Response (200 OK):**
```json
{
  "status": "SUCCESS",
  "invoice": {
    "invoice_id": 105,
    "invoice_number": "INV-2026-105",
    "amount": 29.00,
    "currency": "USD",
    "status": "PENDING",
    "khqr": {
      "khqr_string": "00020101021230...",
      "md5_hash": "a1b2c3d4e5f6...",
      "qr_image_data": "data:image/png;base64,iVBORw0KGgo...",
      "deeplink_app": "bakong://pay?qr=..."
    }
  }
}
```

### `POST /api/v1/billing/verify/{invoice_id}`
* **Description:** Verifies payment server-side directly against the National Bank of Cambodia Bakong Open API.
* **Response (200 OK):** Returns payment verification outcome and extended subscription dates.
