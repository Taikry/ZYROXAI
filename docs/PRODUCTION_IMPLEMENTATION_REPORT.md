# ZYROX AI V3.1 — PRODUCTION IMPLEMENTATION REPORT

**Project:** ZYROX AI — Intelligence Beyond the Market  
**Founder:** Heng Taikry  
**Target Market:** XAUUSD (Gold vs US Dollar)  
**Primary Timeframe:** M15 (15-Minute Analysis)  
**Minimum Actionable Confluence Score:** 75 / 100  
**Implementation Date:** November 17, 2026  
**Repositories:** [GitHub Taikry-AI-Trading](https://github.com/Taikry/Taikry-AI-Trading) · [GitHub ZYROXAI](https://github.com/Taikry/ZYROXAI)  
**Production Host:** [taikry-ai-trading.onrender.com](https://taikry-ai-trading.onrender.com/dashboard/)  

---

## 1. Executive Summary

This report documents the production implementation of **ZYROX AI V3.1 Real-Time Multi-Agent Intelligence Engine** for institutional-grade XAUUSD Gold analysis. The system integrates real-time market data from Exness MT5, OANDA v20, and Yahoo Finance, processes signals through a 14-agent specialized intelligence fleet, scores candidates using an 8-category 100-point confluence model, and triggers analyses aligned to M15 candle closes.

All operations strictly enforce capital preservation, independent verification, atomic database quota reservations, and resilient fail-safes.

---

## 2. 100-Point Confluence Scoring Engine Architecture

The core of ZYROX AI V3.1 is the **Transparent 100-Point Confluence Scoring Engine** located at `taikry/trading/confluence_scorer.py`. Both BUY and SELL biases are evaluated independently from 0 to 100 based strictly on verified mathematical evidence.

### Category Weight Distribution

| Category | Weight | Primary Factors Evaluated |
| :--- | :---: | :--- |
| **1. Trend Alignment** | 15 Pts | M15 EMA 20/50 fast stack (+8), Institutional baseline EMA 200 (+7) |
| **2. Multi-Timeframe Confirmation** | 15 Pts | H4 Macro (+6), H1 Intermediate (+5), M5 Scalp flow (+4) |
| **3. Market Structure** | 15 Pts | Higher-High/Higher-Low or Lower-High/Lower-Low (+8), Confirmed BOS/CHoCH (+7) |
| **4. Liquidity & ICT/SMC** | 15 Pts | Discount/Premium zone (+5), Unmitigated Order Block/Breaker (+5), FVG/Liquidity Sweep (+5) |
| **5. Momentum & Indicators** | 10 Pts | RSI(14) expansion without exhaustion (+5), MACD Histogram directional expansion (+5) |
| **6. Volume & Volatility** | 10 Pts | Cumulative Volume Delta (CVD) absorption (+5), ATR(14) healthy volatility (+5) |
| **7. News & Macro Context** | 10 Pts | US Dollar Index (DXY) inverse alignment (+6), Economic calendar blackout clearance (+4) |
| **8. Risk/Reward & Execution** | 10 Pts | Reward-to-Risk ratio >= 1:1.5 / 1:2.0 floor (+6), Live spread <= $0.35/oz (+4) |
| **TOTAL CONFLUENCE** | **100 Pts** | **Sum of all 8 verified categories** |

### Decision Score Classifications

* **0 – 49 Points (WEAK):** Strictly `WAIT`. No actionable setup.
* **50 – 64 Points (DEVELOPING):** Strictly `WAIT`. Setup in early stage.
* **65 – 74 Points (POTENTIAL):** Strictly `WAIT (Awaiting Confirmation)`. Below actionable threshold.
* **75 – 84 Points (STRONG CONFLUENCE):** Actionable `BUY` or `SELL` subject to mandatory validation gates.
* **85 – 100 Points (VERY HIGH CONFLUENCE):** Prime institutional setup eligible for broadcast.

### Missing Data & Anti-Inflation Rule

In accordance with strict risk engineering:

* Any input that is unavailable, stale, or unverified is marked `UNKNOWN` and awarded **0 points**.
* No artificial normalization, default assumptions, or score inflation is permitted.
* If both BUY and SELL scores exceed 70, the system triggers a **Directional Conflict Lock** and outputs `WAIT`.

---

## 3. 15-Minute Wall-Clock Scheduler & Database Persistence

### Wall-Clock M15 Alignment

The durable background scheduler in `taikry/monitoring/engine.py` operates on exact UTC candle boundaries:

* Analysis runs at `00:00`, `00:15`, `00:30`, and `00:45` UTC.
* Incorporates a 2-second grace period (`:02`, `:17`, `:32`, `:47`) for broker bar finalization.
* Sleep timing dynamically synchronizes to the next boundary via `get_seconds_to_next_m15_close()`.

### Continuous Intrabar Surveillance

Between the scheduled 15-minute cycles:

* The monitoring loop checks incoming ticks every 5 seconds.
* Tracks open paper trades and evaluates stop-loss and take-profit hits.
* Evaluates structural invalidations with a mandatory 60-second event cooldown.

### Historical Report Persistence

Every scheduled 15-minute cycle generates a persistent record in the `fifteen_minute_market_reports` table, even when the market is in a `WAIT` or `HOLD` state:

* `candle_close_utc`: Canonical UTC label (e.g. `2026-11-17 11:15:00 UTC`).
* `decision_status`: `WAIT`, `HOLD`, `BUY`, or `SELL`.
* `confluence_buy_score` and `confluence_sell_score` (0–100).
* `category_scores`: Full JSON breakdown across the 8 categories.
* `report_en` and `report_kh`: Bilingual analysis briefings.

---

## 4. Telegram Signal Delivery & Deduplication

* **Daily Quota Cap:** Maximum 4 new actionable BUY/SELL signals per calendar day (`Asia/Phnom_Penh`).
* **Informational Reports:** Scheduled 15-minute briefings and market commentary consume **0 quota**.
* **Atomic Reservations:** Quotas are reserved atomically in PostgreSQL using `XAUUSDDailyQuotaReservation`.
* **State Survival:** Fingerprint deduplication survives application restarts.

---

## 5. Conversational AI & Multimodal Intelligence

* **Greeting & General Chat:** Implemented `classify_chat_intent` in `taikry/ai/llm_client.py`. Queries like "Hello" or general inquiries render a conversational greeting card in Khmer and English with quick suggestion chips, bypassing trade cards.
* **Multimodal Vision:** Traders can upload chart screenshots (`Ctrl+V` or camera button) to receive automated technical, SMC, and risk analysis.
