# ZYROX AI — Comprehensive REST API Documentation

## 1. Core Service & Health Endpoints

### `GET /ping`
- **Description:** Basic liveness probe.
- **Response:** `{"status": "ok", "service": "taikry-ai-trading"}`

### `GET /api/v1/system/info`
- **Description:** System identity, active features, strategy version, and operational flags.
- **Response:**
  ```json
  {
    "brand_name": "ZYROX AI",
    "tagline": "Read the Market. Own Your Edge.",
    "strategy_version": "v2.5.0",
    "mt5_bridge": {"status": "DISCONNECTED"},
    "bilingual": {"en": "Institutional AI Trading Intelligence", "kh": "ប្រព័ន្ធវៃឆ្លាតជួញដូរបែបស្ថាប័ន TAIKRY AI"}
  }
  ```

---

## 2. Market Intelligence & Real-Time Data

### `GET /api/v1/realtime/prices`
- **Description:** Returns real-time quotes, spread points, bid/ask, and data freshness across all watchlist instruments.

### `GET /api/v1/market-explorer/symbols`
- **Description:** Filterable, searchable symbol directory supporting Asset Classes (`Gold`, `Forex`, `Crypto`), aliases, and broker digits.

### `GET /api/v1/market-data/alignment`
- **Description:** Diagnostic endpoint auditing TradingView reference alignment, quote types (`SPOT_MID` vs `FUTURES_LAST`), and data feed licensing.

---

## 3. Quantitative Analysis & AI Debate

### `POST /api/v1/analyze`
- **Description:** Runs multi-timeframe consensus analysis on a specific symbol.
- **Request:** `{"symbol": "XAUUSD", "timeframe": "M15"}`
- **Response:**
  ```json
  {
    "symbol": "XAUUSD",
    "market_bias": "BULLISH",
    "setup_status": "APPROVE",
    "ai_score": 88,
    "entry_price": 2720.0,
    "stop_loss": 2708.0,
    "take_profit_1": 2744.0,
    "risk_reward_ratio": "1:2.0",
    "report_english": "...",
    "report_khmer": "..."
  }
  ```

### `GET /api/v1/agents/debate`
- **Description:** Conducts a live round-table debate among the 16 specialized agents for a requested asset.
- **Query Params:** `?symbol=XAUUSD&timeframe=M15`

### `POST /api/v1/agents/deep-analysis`
- **Description:** Executes 7-agent deep analysis workflow with pre-flight freshness gating, critic audit, and full observable telemetry trace.

---

## 4. Payment Gateway (ABA PayWay)

### `POST /api/v1/payments/aba/checkout`
- **Description:** Generates HMAC-SHA512 24-field purchase hash and pre-signed checkout payload for ABA PayWay.
- **Request:**
  ```json
  {
    "req_time": "20261103173000",
    "tran_id": "ZYROX-TX-001",
    "amount": 49.00,
    "payment_option": "abapay",
    "return_url": "https://taikry-ai-trading.onrender.com/dashboard/#plans",
    "continue_success_url": "https://taikry-ai-trading.onrender.com/dashboard/#plans"
  }
  ```
- **Response:** `{"status": "SUCCESS", "checkout_url": "...", "hash": "..."}`

### `POST /api/v1/payments/aba/webhook`
- **Description:** Real-time IPN webhook from ABA PayWay with signature verification and automatic subscription provisioning.

---

## 5. VIP Memberships & Subscriptions

### `GET /api/v1/vip/tiers`
- **Description:** Returns pricing, signal quotas, and bilingual feature lists for PRO, VIP, and LIFETIME tiers.

### `POST /api/v1/vip/grant`
- **Description:** Grants membership and returns a single-use expiring Telegram channel invite link.

---

## 6. Telegram Bot & Webhook

### `POST /api/v1/telegram/webhook`
- **Description:** Inbound webhook processing user commands (`/start`, `/gold`, `/debate`, `/risk`, `/vip`, `/myplan`) and inline button callback queries (`scan:XAUUSD`, `debate:XAUUSD`, `calendar:news`).

