# ZYROX AI V6.1.1 — REPOSITORY AUDIT & BASELINE SPECIFICATION

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** V6.1.1 Production Hardening  
**Repository:** https://github.com/Taikry/ZYROXAI  
**Source Commit SHA:** `fbbc213` (main)  
**Feature Branch:** `feature/zyrox-v6.1.1-production-fixes`  
**Founder:** HENG TAIKRY  
**Date:** 2026-11-18  
**Audit Status:** COMPLETE & VERIFIED  

---

## 1. Executive Summary

This document establishes the formal codebase audit for the ZYROX AI V6.1.1 production hardening upgrade. Prior to implementation, every core subsystem was audited to identify security risks, concurrency race conditions, data falsification vulnerabilities, and reliability bottlenecks.

The ZYROX AI platform is an institutional AI-driven financial intelligence engine specializing strictly in XAUUSD (Gold). All architectural modifications in V6.1.1 are non-destructive and incremental, preserving existing working functionality while enforcing zero-tolerance safety gates across quotes, locking, scoring, and user profiles.

---

## 2. Architectural Subsystem Inventory

| Subsystem | Core Files | Responsibility | Audit Verdict |
| :--- | :--- | :--- | :--- |
| **Market Data Providers** | `taikry/data/providers.py` | MT5 Exness quotes, OANDA, Binance, Yahoo | Hardened: Only Exness MT5 quotes can be `REAL_BROKER_QUOTE`/`is_executable=True`. |
| **Signal Engine** | `taikry/trading/xauusd_signal_engine.py` | Consensus synthesis, level calculation, persistence | Hardened: Removed unsafe classification fallback; separated technical confluence from agent vote consensus. |
| **Scheduler Engine** | `taikry/monitoring/engine.py` | 15-minute scheduled candle close analysis | Hardened: Fail-closed lock on database error; added atomic `release_scheduler_lock`. |
| **Agent Registry & Fleet** | `taikry/agents/registry.py` | 17 institutional agent adapters | Hardened: Standardized status enum; removed synthetic delays/LIVE fabrication; added `get_telemetry_snapshot()`. |
| **Telegram Delivery** | `taikry/saas/signal_quota_service.py`, `taikry/trading/xauusd_signal_engine.py` | Cambodia timezone (UTC+7) daily quota (max 4) | Verified: Atomic SQL update with idempotency key deduplication. |
| **SaaS & Authentication** | `taikry/saas/google_oauth.py`, `taikry/saas/phone_otp.py`, `taikry/api/saas_routes.py` | Google OAuth (PKCE S256), Phone OTP, JWT/cookie auth | Hardened: Localhost vs Render redirect detection; removed fake profile placeholders. |
| **User Profile & Device History** | `taikry/api/saas_routes.py`, `taikry/web/app.js` | Account settings, session devices, plan badges | Hardened: Zero hardcoded placeholders; real DB session tracking; exact token hash matching. |
| **Web Frontend** | `taikry/web/index.html`, `taikry/web/app.js`, `taikry/web/styles.css` | UI/UX dashboard, profile tab, danger zone | Hardened: Inline styles refactored to CSS classes; responsive mobile/desktop layout. |

---

## 3. Critical Vulnerabilities Remediated in V6.1.1

1. **Unsafe Quote Promotion Fallback:**  
   Previously, quotes without explicit classification were promoted to `REAL_BROKER_QUOTE` if `bid > 0 and ask > bid`. This allowed non-broker reference feeds to inadvertently generate actionable signals. Fixed to fail-closed as `UNAVAILABLE` and `is_executable=False`.
2. **Fail-Open Scheduler Lock:**  
   `acquire_scheduler_lock()` caught database exceptions and returned `True`, allowing multiple parallel workers to execute on the same candle. Fixed to fail-closed (`return False`).
3. **Confluence and Consensus Conflation:**  
   Agent vote percentages were previously blended with technical scores via `max(confluence, fallback)`. Splitted into two independent gates: `confluence_score >= 75` AND `agent_consensus_pct >= 60.0%`.
4. **Hardcoded User Profile Placeholders:**  
   The profile endpoint had hardcoded fallbacks to "Heng Taikry", "0968288832", "@heng_taikry", "Jul 06, 2026", and fabricated Safari device sessions. Replaced with real database fields and empty session lists when no sessions exist.
