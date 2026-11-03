# ZYROX AI — Release v2.5.0: Autonomous Multi-Agent Intelligence & Enterprise Architecture

## 🚀 What's New in v2.5.0

### 1. Multi-Agent Quantitative Research Fleet
- **16 Autonomous Specialist Agents:** Specialized roles for Data Quality, Multi-Timeframe Trend, SMC/ICT Order Blocks & FVG, Macro News Lockout, Quantitative Research, ML Forecast, Independent Critic, and Deterministic Risk Guardian.
- **Round-Table Debate Engine:** Real-time multi-agent discourse with consensus ruling, adversarial critique, and bilingual synthesis (English & Natural Khmer).
- **Empirical Reinforcement Learning:** Agent weight calibration constrained between $10\%$ and $50\%$ bounds with mathematical normalization ($\sum w_i = 1.0000$).

### 2. Universal Market Support & Real Data Integrity
- Complete coverage across **Gold (XAUUSD)**, **Forex (Major & Minor)**, and **Crypto (BTC, ETH, SOL, XRP, BNB)**.
- Real quote verification rejecting synthetic/demo data and enforcing strict data freshness gating ($< 30\text{ seconds}$ for live broker feeds).
- Multi-provider failover: MT5 Terminal Bridge, OANDA v20 REST, Binance Spot, and Yahoo Finance.

### 3. ABA PayWay Payment Gateway Integration
- Real HMAC-SHA512 + Base64 hash generation matching ABA PayWay Sandbox & Production specifications.
- 24-field purchase hash generation and Check Transaction-2 hash verification.
- Instant webhook processing activating VIP memberships and generating automated expiring Telegram invite links.

### 4. Hardened Telegram Signal Engine
- **Strict Scope:** Exclusively signals **XAUUSD**; other assets are reserved for the interactive web cockpit.
- **Daily Limit:** Capped at **4 signals per Cambodia calendar day (4/4)** with atomic database reservations.
- **Quality Threshold:** Strict **80%–95% AI score gate** with valid geometric levels ($R:R \ge 1:2.0$).
- **Lifecycle Cleanliness:** Suppressed lifecycle spam (`TELEGRAM_SEND_LIFECYCLE_EVENTS=false`) while maintaining complete internal state machine tracking.

### 5. Architectural Hardening & Bug Fixes
- Resolved `schema_migrations` table name collision in startup migrations by isolating system migrations in `system_versioned_migrations`.
- Added missing `take_profit_3` column to `paper_trades` table schema.
- Fixed floating-point precision in Risk:Reward threshold evaluations.
- Enhanced MT5 Bridge authentication with timestamp drift and HMAC signature verification.
- 100% test pass rate across all 337 unit and integration tests.

