# ZYROX AI V6.1 — MARKET DATA SAFETY & QUOTE CLASSIFICATION REPORT

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** 6.1.0-PROD  
**Target Branch:** `main`  
**Founder:** HENG TAIKRY  
**Date:** 2026-11-18  
**Status:** VERIFIED  

---

## 1. Executive Summary

This report documents the quote classification hierarchy and fail-safe safety mechanisms enforced in **ZYROX AI V6.1**. Actionable trading signals for **XAUUSD Gold** strictly require an authentic, fresh, and executable broker quote. All synthetic fallback spreads (`spread_est = 0.25`) have been completely deleted from the production pipeline.

---

## 2. Market Data Classification Hierarchy

Market data feeds in ZYROX AI V6.1 are categorized into six mutually exclusive states:

| Classification | Executable | Description | Actionable Signals Allowed |
| :--- | :--- | :--- | :--- |
| `REAL_BROKER_QUOTE` | `True` | Authentic bid/ask quote directly from Exness MT5 bridge or OANDA v20 REST. Bid > 0, Ask > Bid, age < 30s. | **YES** |
| `REFERENCE_PRICE` | `False` | Midpoint or indicative price without verified real-time broker bid/ask quotes. | **NO (BLOCKED)** |
| `ESTIMATED_SPREAD` | `False` | Price augmented with institutional average spread; prohibited from trade execution. | **NO (BLOCKED)** |
| `STALE` | `False` | Quote received more than 30 seconds ago. | **NO (BLOCKED)** |
| `DISCONNECTED` | `False` | Desktop MT5 bridge or broker socket is disconnected. | **NO (BLOCKED)** |
| `UNAVAILABLE` | `False` | Provider returned None, non-finite price, or zero bid/ask. | **NO (BLOCKED)** |

---

## 3. Explicit Rejection Error Codes

When market data fails to meet the stringent executable broker standard, the signal engine fails closed and returns one of the following exact error codes:

```text
1. BLOCKED_NO_EXECUTABLE_QUOTE
   - Triggered when classification != REAL_BROKER_QUOTE or is_executable is False.
   - Message: "Actionable XAUUSD signal generation requires a verified live executable broker quote."

2. BLOCKED_ESTIMATED_SPREAD
   - Triggered when quote carries an estimated spread instead of real broker liquidity.
   - Message: "The market quote has an estimated spread; actionable signal generation is blocked for risk safety."

3. BLOCKED_REFERENCE_ONLY
   - Triggered when quote is an indicative or reference price.
   - Message: "The market quote is a reference price only; actionable signal generation is blocked for risk safety."

4. BLOCKED_STALE_FEED
   - Triggered when tick age exceeds 30.0 seconds.
   - Message: "The market data feed is STALE; actionable signal generation is blocked for risk safety."

5. BLOCKED_DISCONNECTED_FEED
   - Triggered when the broker terminal/socket connection is lost.
   - Message: "The market data feed is DISCONNECTED; actionable signal generation is blocked for risk safety."
```

---

## 4. Elimination of Synthetic Fallback Spreads

In earlier iterations, `taikry/trading/xauusd_signal_engine.py` contained a synthetic spread constructor:

```python
# PERMANENTLY REMOVED IN V6.1:
if verified_price > 0:
    spread_est = 0.25
    quote_price = verified_price
    bid = round(quote_price - spread_est / 2.0, 2)
    ask = round(quote_price + spread_est / 2.0, 2)
    quote_source = "REFERENCE_PRICE_ESTIMATED"
```

**Resolution in V6.1:**
This code block has been **completely deleted**. In its place, any quote where `bid <= 0` or `ask <= bid` immediately raises `BLOCKED_NO_EXECUTABLE_QUOTE`.

---

## 5. Automated Verification Results

Unit tests in `tests/test_v61_quote_safety.py` verified all six scenarios:

* `test_quote_record_forces_is_executable_false_for_non_broker_quotes`: `PASSED`
* `test_engine_blocks_estimated_spread`: `PASSED`
* `test_engine_blocks_reference_only_quote`: `PASSED`
* `test_engine_blocks_stale_feed`: `PASSED`
* `test_engine_blocks_disconnected_feed`: `PASSED`
* `test_engine_blocks_non_executable_or_unavailable`: `PASSED`
