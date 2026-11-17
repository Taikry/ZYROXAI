# ZYROX AI V3.1 — IMPLEMENTATION PLAN

**Target Architecture:** Real-Time Multi-Agent Intelligence Engine  
**Asset Focus:** XAUUSD (Gold vs US Dollar)  
**Timeframe:** M15 (15-Minute Analysis Cycle)  
**Threshold Gate:** Minimum Confluence Score 75 / 100  
**Founder:** Heng Taikry  
**Date:** November 17, 2026  

---

## 1. Architectural Blueprint & System Data Flow

```text
                                      [ Exness MT5 (Windows PC) ]
                                                   │
                                         (TLS Bridge Webhook)
                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 ZYROX AI BACKEND (FastAPI)                             │
│                                                                                        │
│   ┌────────────────────────────────┐            ┌──────────────────────────────────┐   │
│   │   Market Data Ingestion Engine │            │   11-Agent Pre-News Research     │   │
│   │   (MT5 Primary + OANDA / Yahoo)│            │   (Economic Calendar & Macro)    │   │
│   └────────────────┬───────────────┘            └─────────────────┬────────────────┘   │
│                    │                                              │                    │
│                    ▼                                              ▼                    │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                  14-Agent Multi-Specialist Intelligence Fleet                  │   │
│   │   - Technical Analyst (EMAs, RSI, MACD, ATR, BB)                               │   │
│   │   - ICT / SMC Analyst (Order Blocks, FVGs, Sweeps, OTE, Dealing Range)         │   │
│   │   - Macro & News Risk (DXY Index, Fed Watch, Blackout Windows)                 │   │
│   │   - Order Flow & CVD (Volume Delta, Institutional Accumulation)                │   │
│   │   - Fractal MTF Analyst (D1 / H4 / H1 / M15 / M5 alignment)                    │   │
│   │   - Risk Guardian (R:R >= 1:2.0 Floor, Capital Protection Rules)               │   │
│   └────────────────────────────────┬───────────────────────────────────────────────┘   │
│                                    │                                                   │
│                                    ▼                                                   │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                  Transparent Confluence Scoring Engine (100 Pts)               │   │
│   │   1. Trend Alignment (15 pts)            5. Momentum & Indicators (10 pts)     │   │
│   │   2. Multi-Timeframe Alignment (15 pts)  6. Volume & Volatility (10 pts)       │   │
│   │   3. Market Structure (15 pts)           7. News & Macro Context (10 pts)      │   │
│   │   4. Liquidity & SMC Confirmation (15)   8. Risk/Reward Viability (10 pts)     │   │
│   │   -------------------------------------------------------------------------    │   │
│   │   Score >= 75: Eligible for Actionable BUY/SELL (Subject to Mandatory Gates)   │   │
│   │   Score < 75: Strictly WAIT / HOLD (Capital Protection)                        │   │
│   └────────────────────────────────┬───────────────────────────────────────────────┘   │
│                                    │                                                   │
│                    ┌───────────────┴───────────────┐                                   │
│                    ▼                               ▼                                   │
│   ┌────────────────────────────────┐   ┌───────────────────────────────────────────┐   │
│   │  15-Minute M15 Candle Scheduler│   │      Continuous Tick Event Monitor        │   │
│   │  (:00, :15, :30, :45 close)    │   │      (BOS, CHoCH, Sweeps, Invalidation)   │   │
│   └────────────────┬───────────────┘   └───────────────────┬───────────────────────┘   │
│                    │                                       │                           │
│                    ▼                                       ▼                           │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                  Telegram Signal & Outbox Dispatch Controller                  │   │
│   │   - Hard Daily Cap: Max 4 Actionable BUY/SELL per Cambodia Day (UTC+7)         │   │
│   │   - Database Atomic Slot Reservation & Fingerprint Deduplication               │   │
│   │   - Informational Scheduled Reports stored on Dashboard (0 Quota Impact)       │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mathematical Scoring Model (100 Points Total)

Each direction (**BUY** and **SELL**) is scored independently from 0 to 100 based on concrete mathematical evidence. No points are ever awarded for missing data.

### Category 1: Trend Alignment (15 Points)

* **Bullish:** Price > EMA 20 > EMA 50 on M15 (+8 pts); Price > EMA 200 (+7 pts).
* **Bearish:** Price < EMA 20 < EMA 50 on M15 (+8 pts); Price < EMA 200 (+7 pts).

### Category 2: Multi-Timeframe Confirmation (15 Points)

* H4 Trend Aligned with proposed direction (+6 pts).
* H1 Trend Aligned with proposed direction (+5 pts).
* M5 Scalp Flow Aligned (+4 pts).

### Category 3: Market Structure (15 Points)

* Confirmed Higher High / Higher Low sequence for BUY; Lower High / Lower Low for SELL (+8 pts).
* Confirmed Break of Structure (BOS) or Change of Character (CHoCH) on M15 (+7 pts).

### Category 4: Liquidity & ICT/SMC Confirmation (15 Points)

* Price trading in Discount Zone (<50% dealing range) for BUY, or Premium Zone (>50%) for SELL (+5 pts).
* Interaction with qualified Unmitigated Order Block or Breaker Block (+5 pts).
* Confluence with Unmitigated Fair Value Gap (FVG) or recent liquidity sweep (+5 pts).

### Category 5: Momentum & Technical Indicators (10 Points)

* RSI(14) in healthy directional expansion (45–65 for Bullish; 35–55 for Bearish; no extreme exhaustion) (+5 pts).
* MACD Histogram positive & expanding for BUY, negative & expanding for SELL (+5 pts).

### Category 6: Volume & Volatility Conditions (10 Points)

* Cumulative Volume Delta (CVD) or tick activity confirms directional absorption (+5 pts).
* ATR(14) within normal volatility bounds (not in extreme spread expansion / dead market) (+5 pts).

### Category 7: News & Fundamental Macro Context (10 Points)

* US Dollar Index (DXY) inverse correlation aligned (DXY Bearish for Gold BUY, DXY Bullish for Gold SELL) (+6 pts).
* No high-impact red-folder blackout event occurring within ±30 minutes (+4 pts).

### Category 8: Risk/Reward Viability & Execution Quality (10 Points)

* Measured reward-to-risk ratio meets or exceeds the configured floor (>= 1.5:1 / 2.0:1) (+6 pts).
* Live spread is <= 0.35 points ($0.35/oz) with verified feed freshness (+4 pts).

**Total Possible Confluence Score:** **100 Points**.

---

## 3. Decision Matrix & Mandatory Validation Gates

| Confluence Score | Classification | Decision Output | Actionable Telegram Broadcast? |
| :---: | :---: | :---: | :---: |
| **0 – 49** | WEAK | `WAIT` | **NO** (Informational only) |
| **50 – 64** | DEVELOPING | `WAIT` | **NO** (Informational only) |
| **65 – 74** | POTENTIAL | `WAIT` (Awaiting Confirmation) | **NO** (Informational only) |
| **75 – 84** | STRONG CONFLUENCE | `BUY` or `SELL` (If all gates pass) | **YES** (Subject to 4/day limit) |
| **85 – 100** | VERY HIGH CONFLUENCE | `BUY` or `SELL` (If all gates pass) | **YES** (Subject to 4/day limit) |

### Mandatory Validation Gates (All must pass for BUY or SELL)

1. **Fresh Market Data:** Price feed must be `LIVE_FRESH` (age < 30s) and non-synthetic.
2. **Acceptable Spread:** Live bid/ask spread must be within acceptable institutional bounds.
3. **Valid Order Levels:** Directional mathematical relationship must strictly hold:
   * **BUY:** `Stop Loss < Entry Price < Take Profit 1 < Take Profit 2`
   * **SELL:** `Stop Loss > Entry Price > Take Profit 1 > Take Profit 2`
4. **Minimum Risk/Reward:** Net R:R must be >= 1.5:1 (default 2.0:1).
5. **No Directional Conflict:** If BUY and SELL scores are both >= 70, or agents are deadlocked in opposition, force `WAIT`.
6. **Daily Signal Quota:** Total actionable signals sent today must be < 4 for the Cambodia calendar date.

---

## 4. Step-by-Step Implementation Execution Order

* **Phase 1: Project Audit & Baseline Setup** (Completed in `docs/FINAL_SYSTEM_AUDIT.md`).
* **Phase 2: Confluence Scoring Engine (`taikry/trading/confluence_scorer.py`)** — Implement the 8-category 100-point model.
* **Phase 3: Integration into Signal Engine & Consensus** — Update `taikry/trading/xauusd_signal_engine.py` and `taikry/agents/consensus_engine.py` to use the 75/100 threshold and export score breakdowns.
* **Phase 4: Wall-Clock M15 Scheduler & Report Storage** — Update `taikry/monitoring/engine.py` and `taikry/database/models.py` to trigger on exact candle closes (:00, :15, :30, :45) and store `fifteen_minute_market_reports`.
* **Phase 5: Continuous Intrabar Event Monitor** — Add tick-by-tick structural event triggers (BOS, CHoCH, sweeps) with rate throttling.
* **Phase 6: Front-End Live Terminal & Decision Center Upgrade** — Connect M15 countdown, BUY/SELL score breakdown bars, and 15-minute report history.
* **Phase 7: Full Verification Suite & Production Validation** — Execute comprehensive pytest suite and record live execution metrics.
