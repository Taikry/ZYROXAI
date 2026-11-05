# ZYROX AI V4 — Canonical System Architecture

**Document Version:** 4.0.0-PROD  
**Last Updated:** 2026-11-05  
**Platform Scope:** Full Stack Real-Data AI Market Intelligence & Autonomous Trading System  
**Author:** Principal Software Architect & DevOps Lead  

---

## 1. System Overview & Core Philosophy

ZYROX AI V4 is designed as a **deterministic-first, multi-tier institutional intelligence platform**.
The core architecture enforces three non-negotiable operational principles:

1. **Deterministic Primacy:** All technical indicator values, market structure events (BOS/CHoCH), Smart Money Concepts (FVG, Order Blocks, Liquidity Sweeps), candidate trade geometry (Entry, Stop Loss, Take Profits), risk validation, and execution rules are calculated exclusively in deterministic Python.
2. **AI Advisory Role:** Frontier LLMs (Claude, OpenAI, Gemini, Groq, DeepSeek, AnyRouter) serve strictly as qualitative evaluators—synthesizing multi-agent evidence, detecting narrative contradictions, and explaining technical setups in bilingual English and Natural Khmer. AI agents are strictly forbidden from fabricating market prices, indicators, or trade levels.
3. **Verified Market Data Traceability:** Every price, candle, and spread shown in the user interface or evaluated by the engine has a documented, unbroken provenance chain. If market data feeds are unavailable, the system transparently reports `MARKET DATA UNAVAILABLE` and refuses to manufacture synthetic replacements.

---

## 2. High-Level Canonical Architecture Diagram

```text
                     ┌────────────────────────────────────────────────────────┐
                     │                    EXTERNAL CLIENTS                    │
                     │  Web Browser (Desktop / Mobile) | Telegram User App    │
                     └───────────────────────────┬────────────────────────────┘
                                                 │ HTTPS / WSS / REST
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FASTAPI APPLICATION GATEWAY                                │
│                                                                                             │
│  ┌────────────────────────┐  ┌──────────────────────────┐  ┌─────────────────────────────┐  │
│  │   Auth & RBAC Filter   │  │  Entitlement & Quotas    │  │  Rate Limiting & Security   │  │
│  │  (PBKDF2 / Bearer /    │  │  (14-Day UTC Trial /     │  │  (Redis / Process Fallback / │  │
│  │   SHA-256 Session DB)  │  │   Pro / Premium Tiers)   │  │   Audit Logging Engine)     │  │
│  └───────────┬────────────┘  └────────────┬─────────────┘  └──────────────┬──────────────┘  │
└──────────────┼────────────────────────────┼───────────────────────────────┼─────────────────┘
               │                            │                               │
               ▼                            ▼                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  CORE SERVICE ORCHESTRATION                                 │
│                                                                                             │
│  ┌─────────────────────────────────┐               ┌──────────────────────────────────────┐  │
│  │  Multi-Provider Market Data     │               │  Multi-Agent AI Consensus Engine     │  │
│  │  Tier 1: Desktop MT5 Bridge     │               │  - Technical Analyst (EMA/RSI/ADX)   │  │
│  │  Tier 2: OANDA v20 REST Feed    │               │  - ICT/SMC Analyst (FVG/OB/Sweeps)   │  │
│  │  Tier 3: Binance Spot Book      │               │  - Macro/News Analyst (Events/DXY)   │  │
│  │  Tier 4: Institutional Spread   │◄──────────────┤  - Risk Validator (R:R >= 1:2.0)     │  │
│  │  Validation & Staleness Guards  │               │  - Market Regime Classifier (Hurst)  │  │
│  └────────────────┬────────────────┘               │  - 7 Specialist Analytical Agents    │  │
│                   │                                └──────────────────┬───────────────────┘  │
│                   ▼                                                   ▼                      │
│  ┌─────────────────────────────────┐               ┌──────────────────────────────────────┐  │
│  │  Deterministic Technical Engine │               │  Risk Management & Safety Engine     │  │
│  │  - NumPy / Pandas OHLC Bars     │               │  - Per-Trade Equity Risk Cap (1-2%)  │  │
│  │  - MTF Alignment (M1 to W1)     ├──────────────►│  - Spread Cost Ratio (< 20%)         │  │
│  │  - 7 Canonical Strategies       │               │  - Pre/Post News Event Blackouts     │  │
│  └─────────────────────────────────┘               │  - Daily Loss Circuit Breaker (2.5%) │  │
│                                                    └──────────────────┬───────────────────┘  │
│                                                                       │                      │
│                                                                       ▼                      │
│  ┌─────────────────────────────────┐               ┌──────────────────────────────────────┐  │
│  │  Signal Lifecycle & Execution   │               │  AI Copilot & Explanation Service    │  │
│  │  - CANDIDATE -> ACTIVE -> HIT/SL│               │  - Job-Grounded Context Pipeline     │  │
│  │  - Atomic DB Deduplication      ├──────────────►│  - Model Router (Local/Primary/Fail) │  │
│  │  - Telegram Dispatcher (Max 4/d)│               │  - Bilingual English/Khmer Output    │  │
│  └─────────────────────────────────┘               └──────────────────────────────────────┘  │
└───────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  PERSISTENCE & INFRASTRUCTURE                                │
│                                                                                             │
│  ┌─────────────────────────────────────────────────┐  ┌───────────────────────────────────┐  │
│  │  PostgreSQL 16 Enterprise Database (WAL Mode)   │  │  Upstream Integration Connectors  │  │
│  │  - 56 Tables with Foreign Keys & User Isolation │  │  - Windows Desktop MT5 Bridge     │  │
│  │  - Backtests, Trades, Journals & Learning Recs  │  │  - NBC Bakong Open API (EMVCo)    │  │
│  │  - Signal Lifecycles, Events & Audit Trails     │  │  - Economic Calendar Providers    │  │
│  └─────────────────────────────────────────────────┘  └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Module Breakdown & Architectural Contracts

### Module 1: Authentication & Authorization (RBAC)

* **Encryption Standards:** NIST-compliant PBKDF2-HMAC-SHA256 with 600,000 iterations and 128-bit cryptographically secure random salt. Passwords are never stored in plaintext.
* **Session Storage:** 256-bit URL-safe session tokens (`secrets.token_urlsafe(32)`). Raw tokens are delivered via HttpOnly cookies (`zyrox_session`) or Bearer headers. Only their SHA-256 hash is persisted in `user_sessions.token_hash`.
* **Role Hierarchy:**
  * `USER`: Access scoped strictly to personal analyses, watchlist, portfolio, paper trades, settings.
  * `PREMIUM_USER`: Elevated scan quotas, automated continuous radar, and institutional multi-target take profits.
  * `ADMIN`: User management, subscription overrides, payment audit, support operations, signal telemetry.
  * `SUPER_ADMIN`: Root privileges: manages admin accounts, edits global settings, views masked AI provider credentials (`[redacted]`), and manages feature flags.
* **FastAPI Middleware:** `require_role(["admin", "super_admin"])`, `require_permission(...)`, `get_current_user`.

### Module 2: Market Data Provider Architecture

* **Tier 1 (Preferred Metals Feed):** Windows Desktop Exness MT5 Bridge running on user PC, polling quotes via HTTP/JSON at `http://127.0.0.1:8001` or securely publishing over HTTPS to `/api/v1/bridge/mt5/publish` using token authentication.
* **Tier 2 (Forex & Metals REST):** OANDA v20 REST / Streaming API (`OANDA_API_TOKEN`).
* **Tier 3 (Crypto Spot):** Binance Spot Ticker and Order Book API.
* **Tier 4 (Institutional Reference Floor):** Spot Gold composite with verified broker spread floor ($0.25 on XAUUSD, $0.00015 on EURUSD, $1.50 on BTCUSDT).
* **Failure Guard:** When all feeds are unreachable, `price: 0.0, status: "UNAVAILABLE"` is emitted. Zero synthetic prices.

### Module 3: Technical Analysis & Market Structure Engine

* **Indicators:** EMA (20, 50, 200), RSI (14), MACD (12, 26, 9), ATR (14), ADX (14), Bollinger Bands (20, 2), Stochastic (14, 3, 3).
* **Market Structure:** Swing Highs/Lows fractals, Break of Structure (BOS), Change of Character (CHoCH), Market Structure Shift (MSS).
* **Smart Money Concepts (SMC):** Buy-side/Sell-side liquidity sweeps, Fair Value Gaps (FVG) and Inversion FVGs, Bullish/Bearish Order Blocks, Premium vs Discount dealing ranges, Optimal Trade Entry (OTE 62%–79%).
* **Multi-Timeframe Integration:** M1, M5, M15, M30, H1, H4, D1, W1.

### Module 4: Strategy Library & Best Setup Engine

Evaluates 7 canonical institutional strategies:

1. `TREND_PULLBACK`: Shallow retracements into EMA 20/50 in harmony with HTF order flow.
2. `BREAKOUT_RETEST`: Clean retests of broken key structure or dealing range boundaries.
3. `LIQUIDITY_SWEEP_REVERSAL`: Stop-run purge beyond previous session highs/lows with aggressive rejection wicks.
4. `ORDER_BLOCK_REACTION`: Precision mitigation of institutional order blocks in discount/premium zones.
5. `FVG_REACTION`: Imbalance fills within unmitigated fair value gaps.
6. `RANGE_REVERSAL`: Mean-reversion fades back to Point of Control (POC) equilibrium from value area extremes.
7. `MOMENTUM_CONTINUATION`: Volume-backed breakout continuation following tight Bollinger Band squeezes.

* **Outcome Contract:** Returns `BUY`, `SELL`, `WAIT`, or `NO_TRADE`.

### Module 5: News & Macroeconomic Risk Engine

* **Traceable Upstream Feeds:** `ShowMyTrades` and `FairEconomy` XML/JSON feeds.
* **Catalyst Mapping:** Categorizes events into FOMC, CPI, PPI, NFP, GDP, Central Bank Interest Rates, Retail Sales, Unemployment.
* **Safety Blackout Windows:** Configurable pre-event and post-event blackout windows (default 30 mins before, 15 mins after).
* **States:** `NEWS_SAFE`, `NEWS_CAUTION`, `HIGH_IMPACT_EVENT_NEAR`, `TRADING_BLOCKED`.

### Module 6: Risk Management & Capital Protection

* **Risk Profiles:** Conservative (1%), Balanced (1.5%), Aggressive (2%), Custom.
* **Rules Enforced:**
  * Minimum Risk-to-Reward ratio: $\ge 1:2.0$.
  * Spread Cost Ratio: $\le 20\%$ of target stop distance.
  * Position sizing based on verified lot multiplier (100 for XAUUSD, 100,000 for standard FX).
  * Maximum Daily Loss limit: 2.5% of equity (circuit breaker disables further trades for the day).

### Module 7: Telegram Signal Engine & Deduplication

* **Delivery Cap:** Maximum 4 new signals per calendar day.
* **Atomic Deduplication:** Persistent idempotency key (`signal_id:event_type:transition_index`) in PostgreSQL database. Survives server restarts.
* **Lifecycle Machine:** `CANDIDATE` $\rightarrow$ `WAITING_CONFIRMATION` $\rightarrow$ `ACTIVE` $\rightarrow$ `TARGET_HIT` (TP1/2/3) $\rightarrow$ `STOP_HIT` / `CLOSED` / `INVALIDATED` / `EXPIRED`.

### Module 8: Subscriptions, Trials & Payments

* **14-Day Free Trial:** Server-enforced UTC timestamps. Deduplicated per user/email via `TrialGrantRecord`.
* **National Bank of Cambodia Bakong Open API:** EMVCo KHQR dynamic QR generation with CRC16-CCITT checksum. Server-side payment verification via `POST /v1/check_transaction_by_md5`.
* **Zero Client Trust:** Frontend success callbacks are never used to activate subscriptions. Subscriptions are activated exclusively upon server verification with NBC Bakong.

---

## 4. Multi-Tenant User Data Isolation

All private records require explicit `user_id == current_user.id` SQL filters:

* `PaperTrade` (User paper trades & journal)
* `MarketAnalysisJob` (Personal analysis jobs)
* `UserWatchlist` & `UserWatchlistItem` (Custom watchlist)
* `UserSubscription` & `PaymentInvoice` (Billing history)
* `TelegramLink` & `NotificationPreferences` (User settings)
* `SupportTicket` (Personal customer support requests)
