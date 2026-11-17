# ZYROX AI V5 — End-to-End System Integration Matrix

**Document:** `docs/INTEGRATION_STATUS.md`  
**Date:** 2026-11-17  
**System:** ZYROX AI Autonomous Trading Intelligence Platform  
**Integration Status:** All End-to-End Flows Fully Wired & Verified  

---

## 1. System Integration Overview

This document maps the complete integration topology connecting the User Interface layers (React 19 Landing Page and Web Terminal), the FastAPI Application Backend, the 14-Agent Consensus Fleet, Market Data Pipelines, Payment Providers, and Notification Channels.

```mermaid
flowchart TD
    subgraph UI["User Interface Layer"]
        A1["React 19 Landing Page<br/>(Hero, 3D Orb, Founder)"]
        A2["Web Trading Terminal<br/>(Lightweight Charts, Order Flow)"]
        A3["Admin & Super Admin<br/>(RBAC, Feature Flags)"]
    end

    subgraph API["FastAPI Gateway & Auth"]
        B1["Session Security & PBKDF2<br/>(/api/v1/auth/*)"]
        B2["Market Analysis Router<br/>(/api/v1/analyze, /best-setup)"]
        B3["Billing & Entitlements<br/>(/api/v1/billing/*)"]
    end

    subgraph AI["14-Agent Consensus Fleet"]
        C1["Technical & SMC Analysts<br/>(ICT, Trend, Volatility)"]
        C2["Macro & Sentiment<br/>(DXY, Yields, Orderflow)"]
        C3["Counter-Critic & ML<br/>(Devil's Advocate, Time-Series)"]
        C4["Risk Gate & Consensus<br/>(8-Factor Scoring, Quorum)"]
    end

    subgraph DATA["Market Data Providers"]
        D1["Desktop MT5 Bridge<br/>(Pusher & Receiver)"]
        D2["OANDA v20 REST<br/>(Gold & FX Quotes)"]
        D3["Binance Ticker Feed<br/>(Live Crypto Quotes)"]
        D4["Economic Calendar<br/>(ShowMyTrades, FairEconomy)"]
    end

    subgraph PAY["Payments & Billing"]
        E1["NBC Bakong KHQR<br/>(EMVCo Dynamic QR)"]
        E2["ABA PayWay<br/>(Sandbox & Deep Links)"]
    end

    subgraph NOTIFY["Notifications & Mini App"]
        F1["Telegram VIP Broadcast<br/>(Idempotent Channel Delivery)"]
        F2["Telegram Mini App SDK<br/>(In-Chat Trading Terminal)"]
    end

    UI --> API
    API --> AI
    API --> DATA
    API --> PAY
    API --> NOTIFY
    DATA --> AI
```

---

## 2. End-to-End Workflow Integration Matrices

### Workflow 1: Live Market Ingestion & Consensus Signal Generation
```mermaid
sequenceDiagram
    participant M as Market Feed (MT5/OANDA)
    participant Q as Quote Engine & Freshness Filter
    participant A as 14-Agent Fleet
    participant R as Risk Validator
    participant C as Consensus Engine
    participant T as Telegram Dispatcher
    participant DB as PostgreSQL Database

    M->>Q: Ingest live tick (Bid / Ask)
    Q->>Q: Validate timestamp freshness (<= 60s)
    Q->>A: Trigger parallel agent evaluation
    A->>A: ICT/SMC, Trend, Macro, ML & Orderflow compute
    A->>R: Transmit candidate trade setup
    R->>R: Audit 8 risk factors (Min 1:1.5 R:R, Max Drawdown)
    R->>C: Submit risk-approved candidate
    C->>C: Calculate weighted quorum (Agreement >= 60%)
    C->>DB: Atomically persist signal record
    C->>T: Dispatch bilingual alert (Khmer + English)
    T->>T: Enforce daily cap (<= 4 signals/day) & deduplicate
```

* **Integration State:** `FULLY INTEGRATED & OPERATIONAL`
* **Test Verification:** `test_full_consensus_engine_gold`, `test_xauusd_realtime_signals.py`, `test_telegram_duplicate_prevention.py`.

---

### Workflow 2: User Onboarding & 14-Day Free Trial Auto-Grant
```mermaid
sequenceDiagram
    participant U as Trader (Browser)
    participant UI as React / Auth Modal
    participant API as FastAPI Auth Router
    participant S as Security & PBKDF2 Service
    participant T as Trial Service
    participant DB as PostgreSQL Database

    U->>UI: Enter email, password, optional referral
    UI->>API: POST /api/v1/auth/signup
    API->>S: Hash password (600,000 PBKDF2 iterations)
    API->>DB: Create User record
    API->>T: Auto-grant 14-day Free Trial
    T->>DB: Insert subscription (status: ACTIVE, expires: UTC + 14d)
    API->>S: Generate 256-bit cryptographically secure session
    API-->>UI: Set HttpOnly, Secure, SameSite=Lax cookie
    UI-->>U: Instant redirect to full dashboard access
```

* **Integration State:** `FULLY INTEGRATED & OPERATIONAL`
* **Test Verification:** `test_user_sign_up_and_trial_auto_grant`, `test_login_and_authenticated_me`, `test_trial_expiration_server_enforcement`.

---

### Workflow 3: Cambodian Domestic Payment Lifecycle (Bakong KHQR)
```mermaid
sequenceDiagram
    participant U as Trader
    participant UI as Billing Portal
    participant API as Billing API
    participant BK as Bakong Service
    participant BN as National Bank of Cambodia
    participant DB as PostgreSQL Database

    U->>UI: Select Plan (Trader Pro $49/mo)
    UI->>API: POST /api/v1/billing/checkout (provider: bakong)
    API->>BK: Generate EMVCo TLV payload with CRC16
    BK-->>UI: Return KHQR QR Image & MD5 Hash
    U->>U: Scan QR using ABA / Acleda / Bakong Mobile App
    U->>BN: Authorize payment transfer
    API->>BN: Poll /v1/check_transaction_by_md5
    BN-->>API: Status: SUCCESS (Transaction Confirmed)
    API->>DB: Update Subscription to ACTIVE (expires: +30 days)
    API->>DB: Log transaction audit record
    API-->>UI: Display payment confirmed modal
```

* **Integration State:** `FULLY INTEGRATED & OPERATIONAL`
* **Test Verification:** `test_crc16_and_tlv_calculation`, `test_khqr_payload_generation`, `test_bakong_checkout_and_verification_lifecycle`.

---

### Workflow 4: MT5 Desktop to Cloud HTTPS Bridge
```mermaid
sequenceDiagram
    participant EA as Windows MT5 Terminal (EA)
    participant P as Local Pusher (scripts/mt5_cloud_pusher.py)
    participant CL as Render Cloud Gateway (/api/v1/bridge/mt5/publish)
    participant DB as Server-Side Quote Memory
    participant UI as Web Trading Terminal (Lightweight Charts)

    EA->>P: Expose tick on http://127.0.0.1:8001
    P->>P: Read Bid, Ask, Spread, Timestamp
    P->>CL: HTTPS POST with Bearer MT5_BRIDGE_TOKEN
    CL->>CL: Verify Bearer Token authenticity
    CL->>CL: Verify timestamp freshness (<= 60s)
    CL->>DB: Cache newest verified quote
    DB-->>UI: Stream real-time price updates to chart and ticker
```

* **Integration State:** `FULLY INTEGRATED & OPERATIONAL`
* **Test Verification:** `test_mt5_bridge_tick_ingestion_and_status`, `test_mt5_symbol_normalization`, `test_stale_feed_blocks_actionable_signals`.

---

## 3. End-to-End Component Status Summary

| Integration Vector | Connected Components | Protocol / Mechanism | Operational Status |
| :--- | :--- | :--- | :---: |
| **Landing Page $\rightarrow$ Backend** | `React 19 SPA` $\rightarrow$ `FastAPI` | Fetch API / JSON REST | `ACTIVE` |
| **Dashboard $\rightarrow$ Charts** | `Lightweight Charts` $\rightarrow$ `Chart API` | REST & Polling / SMC Feed | `ACTIVE` |
| **Backend $\rightarrow$ MT5 Desktop** | `FastAPI Bridge` $\leftarrow$ `Local Pusher` | HTTPS Inverted Push | `ACTIVE` |
| **Backend $\rightarrow$ AI Fleet** | `API Router` $\rightarrow$ `Consensus Engine` | In-process Async Quorum | `ACTIVE` |
| **Backend $\rightarrow$ Telegram** | `Signal Engine` $\rightarrow$ `Telegram Bot API` | HTTPS REST + Idempotency | `ACTIVE` |
| **Backend $\rightarrow$ Bakong KHQR** | `Billing Adapter` $\rightarrow$ `NBC Open API` | EMVCo CRC16 + MD5 Poll | `ACTIVE` |
| **Backend $\rightarrow$ ABA PayWay** | `Billing Adapter` $\rightarrow$ `ABA Gateway` | HMAC-SHA512 + Deep Links | `ACTIVE (Sandbox)` |
| **Backend $\rightarrow$ Database** | `FastAPI` $\rightarrow$ `PostgreSQL 16` | SQLAlchemy 2.0 Pool | `ACTIVE` |
| **Backend $\rightarrow$ Cache/Lock** | `Security` $\rightarrow$ `Redis / Memory` | Thread-safe fallback | `ACTIVE` |

