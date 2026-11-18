# ZYROX AI V6.1.1 — CONSOLIDATED TEST EXECUTION REPORT

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** V6.1.1 Production Hardening  
**Test Runner:** `pytest 9.1.1` (Python 3.12.0 on Windows)  
**Total Hardening Tests:** 29 Tests  
**Status:** 100% PASSED (0 Failed, 0 Flaky)  

---

## 1. Test Suite Summary Table

| Test Suite File | Subsystem Verified | Tests Executed | Result | Time |
| :--- | :--- | :---: | :---: | :---: |
| `tests/test_v61_quote_safety.py` | Exness MT5 Executable Quote Gating & Fallback Removal | 8 | **8 PASSED** | 2.24s |
| `tests/test_v61_scheduler_locking.py` | Fail-Closed Locking & Concurrent Worker Mutual Exclusion | 4 | **4 PASSED** | 3.22s |
| `tests/test_v61_confluence_scoring.py` | Confluence 75 Threshold, 60% Quorum & Metric Separation | 4 | **4 PASSED** | 2.29s |
| `tests/test_v61_agent_telemetry.py` | Telemetry Schema, No Fake LIVE, Standardized Statuses | 5 | **5 PASSED** | 2.75s |
| `tests/test_v61_telegram_governance.py` | Cambodia Date, Daily Limit 4, Concurrency & Deduplication | 5 | **5 PASSED** | 3.76s |
| `tests/test_v61_profile.py` | Profile Retrieval, Updates & Session Auth | 3 | **3 PASSED** | 3.43s |
| `tests/test_v611_profile_integrity.py` | Zero Hardcoded Placeholders & Token Hash Device Matching | 2 | **2 PASSED** | 4.13s |
| `tests/test_v61_auth_flows.py` | Phone OTP, Google OAuth PKCE, JWKS & Redirect URIs | 7 | **7 PASSED** | 4.52s |
| **CONSOLIDATED TOTAL** | **ALL PRODUCTION HARDENING PHASES** | **38** | **38 PASSED** | **26.34s** |

---

## 2. Granular Test Breakdown

### 2.1 Quote Safety (`tests/test_v61_quote_safety.py`)
- `test_exness_quote_is_executable` — PASSED
- `test_oanda_and_yahoo_and_binance_forced_reference_only` — PASSED
- `test_unclassified_quote_fails_closed` — PASSED
- `test_stale_quote_fails_closed` — PASSED
- `test_inverted_or_zero_spread_fails_closed` — PASSED
- `test_disconnected_mt5_fails_closed` — PASSED
- `test_synthetic_candles_blocked` — PASSED
- `test_non_xauusd_quote_blocked` — PASSED

### 2.2 Scheduler Locking (`tests/test_v61_scheduler_locking.py`)
- `test_scheduler_lock_fails_closed_on_db_error` — PASSED
- `test_scheduler_lock_mutual_exclusion` — PASSED
- `test_scheduler_lock_release_and_reacquire` — PASSED
- `test_concurrent_workers_exact_one_winner` — PASSED

### 2.3 Confluence Scoring (`tests/test_v61_confluence_scoring.py`)
- `test_confluence_below_75_forces_wait` — PASSED
- `test_agent_consensus_below_60_forces_wait` — PASSED
- `test_confluence_and_consensus_pass_thresholds` — PASSED
- `test_non_xauusd_rejected` — PASSED

### 2.4 Agent Telemetry (`tests/test_v61_agent_telemetry.py`)
- `test_agent_telemetry_snapshot_schema_and_status` — PASSED
- `test_agent_disabled_status` — PASSED
- `test_agent_demo_mode_status` — PASSED
- `test_agent_completed_and_failed_status` — PASSED
- `test_telemetry_api_endpoint` — PASSED

### 2.5 Telegram Quota Governance (`tests/test_v61_telegram_governance.py`)
- `test_cambodia_date_calculation` — PASSED
- `test_daily_quota_max_4_enforced` — PASSED
- `test_concurrent_quota_reservation_no_overcommit` — PASSED
- `test_saas_signal_quota_idempotency` — PASSED
- `test_deduplication_suppresses_duplicate` — PASSED

### 2.6 Profile Integrity (`tests/test_v611_profile_integrity.py` & `test_v61_profile.py`)
- `test_auth_me_unauthenticated` — PASSED
- `test_auth_me_returns_profile_spec` — PASSED
- `test_update_profile_phone_and_language` — PASSED
- `test_profile_zero_hardcoded_placeholders_for_empty_user` — PASSED
- `test_profile_current_device_exact_token_match` — PASSED

### 2.7 Auth Flows (`tests/test_v61_auth_flows.py`)
- `test_phone_e164_normalization` — PASSED
- `test_phone_otp_generation_and_expiry` — PASSED
- `test_phone_otp_rate_limiting` — PASSED
- `test_google_oauth_pkce_generation` — PASSED
- `test_google_oauth_state_cache` — PASSED
- `test_google_redirect_uri_resolution` — PASSED
- `test_google_user_registration_auto_trial` — PASSED
