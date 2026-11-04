# ZYROX AI — Comprehensive Platform Audit Report

**Generated:** November 2026  
**Repository Source of Truth:** `https://github.com/Taikry/Taikry-AI-Trading`  
**Production Deployment:** `https://zyroxai.onrender.com`  
**System Status:** Operational / Enterprise Grade  

---

## 1. Executive Summary
ZYROX AI is an institutional-grade quantitative market intelligence, multi-agent algorithmic research, technical analysis, and stateful trade lifecycle management platform. The application is built on **FastAPI (Python 3.12)**, **PostgreSQL / SQLAlchemy**, and **TradingView Lightweight Charts v4.2.1**, deployed on **Render** with **Telegram Bot API**, **MT5 Terminal Bridge**, and **ABA PayWay Gateway** integrations.

---

## 2. Repository & Architecture Audit

### 2.1 Backend Architecture
- **Framework:** FastAPI with Uvicorn ASGI server.
- **ORM / Persistence:** SQLAlchemy 2.0 with PostgreSQL in production and SQLite for isolated unit testing.
- **Migration Engine:** Automated versioned migrations with `system_versioned_migrations` tracking table. No collision with Schema Studio's `schema_migrations`.
- **API Surface:** Over 40 production endpoints covering:
  - Market discovery & explorer (`/api/v1/market-explorer/*`)
  - Real-time quote synchronization (`/api/v1/realtime/prices`, `/api/v1/market-data/*`)
  - Institutional technical indicators & SMC/ICT analysis (`/api/v1/indicators/*`)
  - Autonomous multi-agent consensus and round-table debates (`/api/v1/agents/*`)
  - Paper trading and risk surveillance (`/api/v1/paper-trades/*`)
  - ABA PayWay payment checkout & webhook processing (`/api/v1/payments/*`)
  - VIP subscriptions and Telegram membership management (`/api/v1/vip/*`)
  - Telegram webhook and bot interactivity (`/api/v1/telegram/*`)

### 2.2 Multi-Agent Quantitative Fleet
The platform orchestrates a fleet of specialized quantitative, technical, and structural agents:
1. **Market Data Quality Agent:** Validates quote freshness, detects synthetic/demo data, verifies spread sanity.
2. **Technical Analysis Agent:** Multi-period EMA fractals, Wilder's RSI, MACD momentum, ATR volatility.
3. **Multi-Timeframe Trend Agent:** Alignment across W1, D1, H4, H1, M15, and M5 timeframes.
4. **Institutional ICT / Smart Money Concepts Agent:** Order blocks, Fair Value Gaps (FVG), Optimal Trade Entry (OTE 61.8%–79%), liquidity pools.
5. **Quantitative Research Agent:** Mean-reversion probability, statistical z-scores, rolling volatility.
6. **Machine Learning Forecast Agent:** Predictive directional modeling with Brier calibration scores.
7. **Macro & Breaking News Agent:** Real-time high-impact news monitoring with automatic pre-news lockouts.
8. **Market Regime Detection Agent:** Categorizes market states (Trending, Range-Bound, High-Volatility Shock).
9. **Strategy Discovery & Backtesting Agent:** Evaluates historical win rates, profit factor, max drawdown.
10. **Counter-Analysis / Independent Critic Agent:** Adversarial challenger actively detecting bull/bear traps.
11. **Risk Guardian / Arbiter:** Deterministic 1:2.0+ R:R floor, 0.5% equity risk cap, spread tolerance checks.
12. **Consensus Coordinator:** Synthesizes institutional scores with a strict 80%–95% trade qualification gate.

### 2.3 Market Data Integrity
- **Gold (XAUUSD):** Primary asset class with broker digits, contract sizing, tick value, and spread tracking.
- **Forex (Major & Minor Pairs):** EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD.
- **Cryptocurrency:** BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, BNBUSDT.
- **Providers:** Multi-provider failover architecture combining MT5 Terminal Bridge, OANDA v20 REST, Binance Spot, and Yahoo Finance.
- **Licensing & Compliance:** Strictly enforces official licensed financial data feeds. Web scraping of third-party interfaces is prohibited.

### 2.4 Telegram Signal Engine Policy
- **Asset Scope:** Signals dispatched to Telegram are **strictly XAUUSD only**.
- **Daily Quota:** Hard daily limit of **4 signals per Cambodia calendar day (4/4)**.
- **Quality Gate:** Signals must achieve an **AI Consensus Score between 80% and 95%** with valid geometry (R:R >= 1:2.0).
- **Lifecycle Notifications:** Suppressed by default (`TELEGRAM_SEND_LIFECYCLE_EVENTS=false`) to eliminate lifecycle spam while maintaining internal audit logging.

### 2.5 Payment Infrastructure (ABA PayWay)
- Real HMAC-SHA512 with Base64 signature generation matching ABA PayWay Sandbox & Production specifications.
- 24-field purchase hash computation for payment initiation.
- Check Transaction-2 hash verification (`req_time + merchant_id + tran_id`).
- Real sandbox merchant credentials integrated: Merchant ID `ec479879`, Key `B10B32C154CB629C865E5BE34C1734697A9CC513`.

### 2.6 Deployment Health & Invariants
- **Render Production:** Auto-deploy on push to `main` branch.
- **Endpoints:** `/ping` returns HTTP 200 with service health status; `/dashboard/` serves the responsive UI.
- **Shadow Mode Invariant:** Automated live order execution on real broker accounts is **strictly disabled** (`is_shadow_mode = True`, `can_place_live_orders = False`).

