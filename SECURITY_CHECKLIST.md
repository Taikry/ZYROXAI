# ZYROX AI — Security & Operational Integrity Checklist

## 1. Secrets & Credentials Protection
- [x] **Zero Secret Leakage:** No plaintext API keys, tokens, or credentials are hardcoded or tracked in Git.
- [x] **Redaction Filters:** All logging outputs apply secret masking to scrub Telegram bot tokens, API keys, and authorization headers.
- [x] **Git Isolation:** `.env` is strictly listed in `.gitignore`. Only `.env.example` with non-secret placeholders is committed.

---

## 2. Authentication & Replay Attack Defense
- [x] **Constant-Time Comparison:** Webhook signatures and auth tokens utilize `hmac.compare_digest` to prevent timing attacks.
- [x] **Timestamp Drift Protection:** MT5 Bridge endpoints reject requests with timestamp drift $> 60\text{ seconds}$.
- [x] **Signature Deduping:** Requests cache signatures for $120\text{ seconds}$ to reject duplicate or replayed payloads.
- [x] **Session Expiration:** SaaS session tokens expire after 24 hours.

---

## 3. Trading & Execution Safety Invariants
- [x] **Shadow Mode Hardcoded:** `is_shadow_mode = True`, `can_place_live_orders = False`. Live broker execution calls unconditionally raise `PermissionError`.
- [x] **Daily Loss Circuit Breaker:** Daily losses are capped at $2.0\%$ of equity. Additional paper trades are blocked upon reaching the limit.
- [x] **Risk-to-Reward Ratio Floor:** Trade setups with $R:R < 1:2.0$ are strictly rejected by the Risk Guardian.
- [x] **Maximum Risk Per Trade:** Single-trade risk cannot exceed $0.5\%$ of equity.
- [x] **Spread Tolerance:** Trades are blocked if the bid/ask spread exceeds $20\%$ of the planned stop distance.

---

## 4. Payment & Telegram Policy Enforcement
- [x] **ABA PayWay HMAC-SHA512:** Strict signature verification on both client checkout and incoming IPN webhook.
- [x] **Telegram Single-Asset Invariant:** Automated Telegram alerts are restricted exclusively to `XAUUSD`.
- [x] **Hard Daily Limit:** At most 4 signals are broadcast to Telegram per Cambodia calendar day (4/4).
- [x] **Lifecycle Quietness:** Lifecycle event notifications (TP/SL/BE) are suppressed by default to prevent message spam.

