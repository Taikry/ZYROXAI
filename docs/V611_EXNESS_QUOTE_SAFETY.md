# ZYROX AI V6.1.1 — EXNESS MT5 REAL-TIME DATA SAFETY SPECIFICATION

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** V6.1.1 Production Hardening  
**Target Instrument:** XAUUSD Only  
**Primary Executable Source:** Exness MT5 Terminal (Windows Desktop Bridge)  
**Reference-Only Feeds:** OANDA, Binance, Yahoo Finance  
**Status:** IMPLEMENTED & VERIFIED  

---

## 1. High-Priority Safety Mandate (P0)

In algorithmic trade analysis, market quote provenance is paramount. Executing or broadcasting trade signals calculated against estimated, delayed, or cross-broker reference data risks severe slippage, stop-out distortion, and capital loss.

Under ZYROX AI V6.1.1:
1. **Exness MT5 is the ONLY executable quote source.**
2. All non-Exness sources are classified strictly as `REFERENCE_PRICE` with `is_executable=False`.
3. Every invalid, stale, disconnected, or synthetic quote **fails closed** immediately, blocking signal generation.

---

## 2. Quote Classification Matrix

| Source Provider | Symbol Target | Classification | Is Executable | Actionable Signals Allowed |
| :--- | :--- | :--- | :--- | :--- |
| **Exness MT5 Bridge** | `XAUUSD`, `XAUUSDm` | `REAL_BROKER_QUOTE` | `True` | **YES** (if quote is fresh and spread is valid) |
| **OANDA REST API** | `XAU_USD` | `REFERENCE_PRICE` | `False` | **NO** (Reference/context only) |
| **Binance WebSocket** | `PAXGUSDT` | `REFERENCE_PRICE` | `False` | **NO** (Reference/context only) |
| **Yahoo Finance** | `GC=F` | `REFERENCE_PRICE` | `False` | **NO** (Reference/context only) |
| **Unclassified / Missing**| Any | `UNAVAILABLE` | `False` | **NO** (Fails closed) |

---

## 3. Implementation Details

### 3.1 Strict Provider Classification (`taikry/data/providers.py`)

`build_quote_record()` enforces source string inspection:
```python
is_exness_mt5 = ("EXNESS" in source.upper() or "MT5" in source.upper())
classification = QuoteClassification.REAL_BROKER_QUOTE if is_exness_mt5 else QuoteClassification.REFERENCE_PRICE
is_executable = bool(is_exness_mt5 and bid > 0 and ask > bid)
```
In `get_verified_quote()`, OANDA and Binance providers explicitly set:
```python
quote["quote_classification"] = QuoteClassification.REFERENCE_PRICE
quote["is_executable"] = False
```

### 3.2 Removal of Unsafe Fallback (`taikry/trading/xauusd_signal_engine.py`)

Previously, `xauusd_signal_engine.py` contained lines that promoted unclassified quotes if `bid > 0 and ask > bid`. This fallback has been completely removed and replaced with a strict fail-closed gate:
```python
if not quote_classification:
    quote_classification = QuoteClassification.UNAVAILABLE
    is_executable = False

if quote_classification != QuoteClassification.REAL_BROKER_QUOTE or not is_executable:
    return {
        "success": False,
        "error": f"Actionable XAUUSD signal generation requires a verified live executable broker quote (current classification: {quote_classification}).",
        "canonical_symbol": canonical_symbol,
        "status": "BLOCKED_NO_EXECUTABLE_QUOTE"
    }
```

---

## 4. Verification Suite

The safety specifications are verified by unit tests in `tests/test_v61_quote_safety.py`:
- `test_exness_quote_is_executable`: Confirms Exness MT5 yields `REAL_BROKER_QUOTE` and `is_executable=True`.
- `test_oanda_and_yahoo_and_binance_forced_reference_only`: Confirms secondary feeds cannot be executable.
- `test_unclassified_quote_fails_closed`: Verifies missing classification fails closed as `UNAVAILABLE`.
- `test_stale_quote_fails_closed`: Verifies quote older than 30 seconds is marked `STALE` and blocked.
- `test_inverted_or_zero_spread_fails_closed`: Verifies `bid >= ask` or `spread <= 0` is rejected.
