# ZYROX AI V6 — Implementation Plan

**Date:** 2026-11-17  
**Project:** ZYROX AI — Real-Time Multi-Agent Intelligence V6  
**Target Branch:** `main`  
**Execution Method:** Phase-by-phase incremental upgrades with continuous test verification  

---

## 1. Plan Overview & Architectural Directives

This implementation plan details the sequential execution of the 15 phases mandated for the ZYROX AI V6 production upgrade.

### Core Constraints
- **Preservation First:** Do not delete working features, existing multi-agent registry, Telegram outbox, or database schema.
- **Zero Fabrication:** Never generate synthetic prices labeled as executable broker quotes, fake agent confidence, or fabricated win rates.
- **Fail Closed:** Any security-sensitive integration without valid configuration must fail closed and report `NEEDS_CONFIGURATION`.
- **Institutional Risk Discipline:** Minimum 75/100 confluence score for actionable signals, maximum 4 actionable signals per Cambodia calendar day.

---

## 2. Phase-by-Phase Roadmap

### Phase 0: Complete Audit & Documentation Baseline
- **Goal:** Comprehensive inventory and documentation of repository state, security posture, integration gaps, and test baselines.
- **Deliverables:**
  - `docs/V6_REPOSITORY_AUDIT.md`
  - `docs/V6_SECURITY_AUDIT.md`
  - `docs/V6_IMPLEMENTATION_PLAN.md`
  - `docs/V6_INTEGRATION_STATUS.md`
  - `docs/V6_TEST_RESULTS.md`
  - `docs/V6_DEPLOYMENT_REPORT.md`

### Phase 1: Critical Security Fixes (Priority: P0)
1. **Dashboard Authentication Gate (`taikry/api/app.py`):**
   - Intercept `/dashboard`, `/dashboard/`, and `/dashboard/index.html`.
   - Validate session via `authenticate_session(db, token)`.
   - Redirect unauthenticated users to `/?auth=signin&return_to=/dashboard/`.
   - Preserve public landing assets and styles.
2. **AI Chat Authentication (`taikry/api/routes.py`):**
   - Require authenticated user session for `POST /api/v1/ai/chat`.
   - Enforce user plan quotas server-side; reject unauthenticated calls with HTTP 401.
3. **MT5 Bridge Authentication (`taikry/data/mt5_receiver.py`):**
   - Remove hardcoded default secret fallback.
   - Fail closed if `MT5_BRIDGE_TOKEN` is unset or empty.
   - Enforce constant-time secret comparison via `hmac.compare_digest`.
4. **RBAC & Admin Protection (`taikry/api/saas_routes.py`):**
   - Ensure all admin routes require `SUPER_ADMIN` or `ADMIN` role.
   - Protect sensitive administrative configuration and audit logging.

### Phase 2: XAUUSD Market Data Integrity (Priority: P1)
1. **Quote Classification Standard (`taikry/data/providers.py`, `taikry/data/mt5_receiver.py`):**
   - Enforce explicit quote classifications:
     - `REAL_BROKER_QUOTE`
     - `REFERENCE_PRICE`
     - `ESTIMATED_SPREAD`
     - `STALE`
     - `DISCONNECTED`
     - `UNAVAILABLE`
2. **Executable Gate:**
   - Prohibit labeling estimated spreads or reference feeds as executable broker quotes.
   - Block actionable signal generation if real broker execution data is disconnected or stale.

### Phase 3: Real-Time XAUUSD Monitoring & Durable Scheduler (Priority: P1)
1. **M15 Wall-Clock Alignment:**
   - Align scheduled analysis cycles with `:00`, `:15`, `:30`, `:45` UTC candle closes.
2. **Durable State Persistence:**
   - Persist analysis cycle state, last successful run, next run, and execution duration.
   - Prevent duplicate concurrent analysis cycles via database locking.
3. **Configurable Admin Defaults:**
   - Symbol: `XAUUSD`
   - Interval: `15 minutes`
   - Thresholds: `BUY >= 75`, `SELL >= 75`
   - Daily Actionable Telegram Cap: `4`
   - Auto Trade Execution: `false`

### Phase 4: 100-Point Confluence Scoring Engine (Priority: P1)
- Validate 8-part weighted scoring model:
  - Trend Alignment: 15 pts
  - Multi-Timeframe Confirmation: 15 pts
  - Market Structure: 15 pts
  - SMC/ICT Liquidity: 15 pts
  - Momentum: 10 pts
  - Volume & Volatility: 10 pts
  - Macro & Fundamentals: 10 pts
  - Risk/Reward Quality: 10 pts
- Anti-inflation rule: Missing metrics score 0 points; never interpolate missing indicators.
- Output decisions: `WAIT`, `HOLD`, `BUY`, `SELL`.

### Phase 5: Real AI Multi-Agent Fleet Statuses (Priority: P1)
- Expose actual backend lifecycle states for each agent:
  - `IDLE`, `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `SKIPPED`, `BLOCKED`.
- Eliminate synthetic frontend status animations or static unanimous consensus.

### Phase 6: Real-Time Streaming AI Chat (Priority: P2)
- Implement Server-Sent Events (SSE) streaming endpoint: `POST /api/v1/ai/chat/stream`.
- Stream real backend progression events:
  `Market Data -> Technical -> ICT/SMC -> Macro -> Risk -> Consensus -> Synthesis`.
- Support dual Khmer and English natural responses.

### Phase 7: Demo vs. Live Data Separation (Priority: P2)
- Strictly segregate demo fixtures from live market telemetry.
- Label all live components with verified data source, timestamp, and freshness indicator.

### Phase 8: Telegram Signal Delivery & Daily Cap Enforcement (Priority: P2)
- Enforce Cambodia calendar day (`Asia/Phnom_Penh`) cap of 4 new actionable BUY/SELL signals.
- Persistent deduplication surviving server restarts.
- Informational 15-minute reports do not consume actionable quota.

### Phase 9: Google OAuth & Phone OTP Configuration Gate
- Verify OAuth2 Authorization Code flow and SMS OTP service.
- Return `NEEDS_CONFIGURATION` when credentials are absent; avoid mock bypasses.

### Phase 10: Frontend & Mobile Terminal UX
- Preserve dark terminal aesthetic (black background, emerald accents).
- Render real loading skeletons, error states, and connection status badges.

### Phase 11: Database Persistence & Safe Migrations
- PostgreSQL as durable source of truth for users, sessions, cycles, signals, and audits.

### Phase 12: Automated Verification Testing
- Execute test suites covering security, market data, confluence scoring, scheduler, and AI chat.

### Phase 13: Deployment Readiness & Environment Hardening
- Validate `render.yaml`, environment secrets, health endpoints (`/ping`, `/health`), and graceful shutdown.

### Phase 14 & 15: Final Documentation & Git Synchronization
- Compile `docs/V6_FINAL_REPORT.md`.
- Commit changes and push cleanly to `origin/main` and `taikry/main`.
