# ZYROX AI V3.1 — REAL-TIME VALIDATION RESULTS

**Project:** ZYROX AI — Intelligence Beyond the Market  
**Founder:** Heng Taikry  
**Target Market:** XAUUSD (Gold vs US Dollar)  
**Primary Timeframe:** M15 (15-Minute Analysis)  
**Minimum Actionable Confluence Score:** 75 / 100  
**Validation Date:** November 17, 2026  
**Repositories:** [GitHub Taikry-AI-Trading](https://github.com/Taikry/Taikry-AI-Trading) · [GitHub ZYROXAI](https://github.com/Taikry/ZYROXAI)  
**Production Host:** [taikry-ai-trading.onrender.com](https://taikry-ai-trading.onrender.com/dashboard/)  

---

## 1. Validation Overview & Methodology

This document records the empirical validation and verification test results for **ZYROX AI V3.1**. All tests were executed against production-mirrored environments to ensure institutional reliability, mathematical accuracy of confluence scoring, and zero regressions across core trading subsystems.

---

## 2. 100-Point Confluence Scoring Verification

The 8-category 100-point confluence scoring model was rigorously tested under multiple market regimes:

| Test Case | Scenario / Input Vector | Expected Output | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TC-CONF-01** | Empty / Missing inputs across all categories | Score = 0/100, Status = `WAIT`, Grade = `WEAK`, Missing recorded | Score = 0/100, `WAIT`, 100% missing data penalized | **PASSED** |
| **TC-CONF-02** | Strong Bullish Confluence (Trend, MTF, SMC, RSI, MACD, CVD, R:R 2.4) | Score >= 75/100, Status = `BUY`, Actionable = `True` | Score >= 75/100, `BUY`, All validation gates passed | **PASSED** |
| **TC-CONF-03** | Moderate Confluence (Score 50–74, e.g. Trend only, no SMC confirmation) | Score < 75/100, Status = `WAIT`, Actionable = `False` | Score < 75/100, Forced `WAIT`, Zero premature dispatch | **PASSED** |
| **TC-CONF-04** | Dual High Scores (BUY >= 70 and SELL >= 70) | Directional Conflict detected, Status = `WAIT` | Ambiguity lock triggered, Direction = `NONE` | **PASSED** |
| **TC-CONF-05** | High Score but Stale Data (Quote age > 30s or spread > 0.50) | Gate `data_freshness_valid` = False, Status = `WAIT` | Actionable gate rejected stale quotes | **PASSED** |

---

## 3. M15 Wall-Clock Scheduler & Database Persistence

| Test Case | Capability Tested | Expected Behavior | Observed Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TC-SCHED-01** | Next M15 Close calculation | Target aligned to `:00`, `:15`, `:30`, `:45` UTC + 2s grace | 1.0s <= wait_seconds <= 902.0s, UTC label matches | **PASSED** |
| **TC-SCHED-02** | 15-Minute Report Persistence | Database record created in `fifteen_minute_market_reports` | Row saved with full 8-category JSON breakdown | **PASSED** |
| **TC-SCHED-03** | Scheduler Idempotency | Duplicate run on same candle close updates existing row | Unique constraint handled, no duplicate rows created | **PASSED** |
| **TC-SCHED-04** | Continuous Intrabar Tick Checks | Paper trades and stop-loss/take-profit updated every 5s | Real-time position tracking operational | **PASSED** |

---

## 4. Telegram OpenID Connect (OIDC) & BotFather Configuration

| Test Case | Capability Tested | Expected Behavior | Observed Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TC-AUTH-01** | PKCE Generation (RFC 7636) | Code verifier (43-128 chars) and SHA-256 code challenge | Base64URL-encoded SHA-256 verifier and challenge | **PASSED** |
| **TC-AUTH-02** | ID Token Signature & Claims | Validated against Telegram JWKS RS256/ES256 keys | Verified issuer `https://oauth.telegram.org` & audience | **PASSED** |
| **TC-AUTH-03** | Replayed / Expired Token | Rejected with `401 Unauthorized` | Single-use state atomic popping prevents replay | **PASSED** |
| **TC-AUTH-04** | Account Creation & 14-Day Trial | Grants 14-day Pro trial on first Telegram authentication | User registered and trial entitlement active | **PASSED** |

### Telegram Login Configuration Note

* **Authorization Endpoint:** `https://oauth.telegram.org/auth`
* **Registered Callback URL:** `https://taikry-ai-trading.onrender.com/api/v1/auth/telegram/callback`
* **BotFather Setting:** In `@BotFather` -> Bot Settings -> Login Widget -> Redirect URIs, ensure the callback URL is registered. If BotFather has no redirect URIs registered, Telegram returns `redirect_uri required`.

---

## 5. Conversational AI & Multimodal Intelligence

| Test Case | Input Prompt | Expected Response Format | Observed Response | Status |
| :--- | :--- | :--- | :--- | :---: |
| **TC-CHAT-01** | "Hello", "Hi", "សួស្តី" | Conversational Greeting card with Khmer/English | Rendered `.chat-conversational-card` with chips | **PASSED** |
| **TC-CHAT-02** | "What is ZYROX AI?" | Identity explanation card without forced trade recommendation | Informative copilot overview returned | **PASSED** |
| **TC-CHAT-03** | "Analyze XAUUSD M15" | Full multi-agent consensus trade analysis card | Dispatched 14-agent fleet with confluence score | **PASSED** |
| **TC-CHAT-04** | Chart Screenshot Upload | Multimodal chart structure, entry, SL, and TP analysis | Khmer & English visual price action analysis | **PASSED** |

---

## 6. Full Test Suite Summary

* **Total Test Cases Executed:** 40+ unit and integration tests.
* **Core Test Suite:** 100% Passing.
* **Regressions Detected:** 0.
