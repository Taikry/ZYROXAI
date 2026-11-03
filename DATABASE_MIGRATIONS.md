# ZYROX AI — Database Migrations & Schema Architecture

## 1. Migration System Architecture
ZYROX AI utilizes an automated startup migration system located in `taikry/database/versioned_migrations.py`.
- **System Version Tracking Table:** `system_versioned_migrations` (renamed from `schema_migrations` to avoid collisions with Schema Studio's user-facing schema migration tool).
- **Dialect Independence:** All migrations execute transparently across PostgreSQL in production and SQLite in test environments.
- **Backwards Compatibility:** All column additions are strictly non-destructive (nullable columns with optional defaults). No existing production tables or columns are dropped.

---

## 2. Core Database Schema & Models

### 2.1 Signal & Lifecycle Tables
- **`xauusd_telegram_signals`:** Stores all generated XAUUSD signals with Cambodiadate, direction, entry, stop loss, take profit targets, AI confluence score, and delivery audit history.
- **`xauusd_daily_quota_reservations`:** Provides atomic daily quota slot enforcement per Cambodia calendar date to enforce the 4 signals/day limit.
- **`signal_lifecycles`:** Tracks finite state machine status (`WAITING_CONFIRMATION`, `ACTIVE`, `TARGET_HIT`, `STOP_HIT`, `INVALIDATED`, `EXPIRED`, `CLOSED`).
- **`signal_lifecycle_events`:** Idempotent delivery log with SHA256 idempotency keys (`{signal_id}:{event_type}:{transition_index}`).

### 2.2 Trading & Paper Execution Tables
- **`paper_trades`:** Simulated paper trade ledger recording symbol, direction, entry price, stop loss, take profits (`take_profit_1`, `take_profit_2`, `take_profit_3`), volume in lots, slippage, realized PnL, and exit reason.
- **`trade_journal_entries`:** Multi-agent retrospective trade reviews with qualitative post-mortem notes.

### 2.3 Learning & Optimization Tables
- **`agent_learning_weights`:** Persists empirical weights for the 16 quantitative agents, recalibrated dynamically via gradient ascent upon trade outcome resolution.
- **`system_alert_autofixes`:** Self-healing event audit log tracking automated diagnostic checks and remediations.

### 2.4 Payments & SaaS Subscriptions
- **`aba_payway_transactions`:** Real-time log of ABA PayWay transaction hashes, status codes, amounts, and webhook responses.
- **`vip_subscriptions`:** User membership records with tier (`PRO`, `VIP`, `LIFETIME`), validity windows, expiring invite links, and renewal tracking.
- **`vip_invite_links`:** Ledger of one-time expiring Telegram invite links created via `createChatInviteLink`.
