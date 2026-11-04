# ZYROX AI V4 — Integration Gap & Remediation Report

**Date:** 2026-11-05  
**Scope:** Complete Architecture, Frontend/Backend Bridges, Deployment & Security  

---

## 1. Executive Summary

This report identifies architectural and operational gaps between the local development environment, the Windows MT5 bridge, the Render production cloud container, and external payment/broker networks. Remediation steps are prioritized by operational risk.

---

## 2. Identified Integration Gaps & Remediation

### Gap 1: Desktop MT5 Terminal to Cloud Render Network Traversal
* **Description:** Render runs on isolated Linux cloud containers in Singapore (`singapore` region). It cannot directly connect to a local private Windows PC running MetaTrader 5 on `127.0.0.1:8001` through an inbound connection due to NAT and dynamic IP assignment.
* **Current State:**
  * The local development environment polls `http://127.0.0.1:8001` via `mt5_receiver.py`.
  * The production Render deployment automatically falls back to OANDA v20, Binance Spot, and Yahoo Finance spot composite with verified spread floors ($0.25).
* **Remediation Plan:**
  * Implement an outbound HTTPS bridge client on the Windows PC (`scripts/run_mt5_bridge.py` or `scripts/mt5_cloud_pusher.py`).
  * The Windows pusher reads quotes from the local MT5 terminal and makes authenticated `POST` requests to the production cloud endpoint `/api/v1/bridge/mt5/publish` with an encrypted Bearer token (`MT5_BRIDGE_TOKEN`).
  * The backend stores the newest pushed tick and verifies timestamp freshness.
* **Risk Level:** `MEDIUM` (Currently mitigated by Tier 2 & Tier 4 fallback feeds).

---

### Gap 2: ABA PayWay Live Merchant Credentials vs Sandbox
* **Description:** The system has full support for NBC Bakong Open API (KHQR EMVCo dynamic QR generation with server-side MD5 check). ABA PayWay is implemented in sandbox mode with RSA encryption (`taikry/saas/billing_adapter.py`), but production merchant onboarding requires live merchant credentials.
* **Current State:**
  * Bakong KHQR handles domestic Cambodian QR payments natively across all 40+ Bakong member banks (including ABA, Acleda, Canadia, Sathapana).
  * ABA PayWay is available in sandbox.
* **Remediation Plan:**
  * Keep Bakong KHQR as the primary default gateway (`PAYMENT_PROVIDER=bakong`).
  * When ABA PayWay live merchant ID and RSA private key are issued, populate `ABA_PAYWAY_MERCHANT_ID` and `ABA_PAYWAY_RSA_PRIVATE_KEY` in Render environment variables.
* **Risk Level:** `LOW` (Bakong KHQR completely covers the payment requirement).

---

### Gap 3: Missing Dedicated Short-Lived Access Token Refresh Endpoint
* **Description:** Currently, user sessions use a single 30-day SHA-256 hashed session token stored in `user_sessions`. While secure against database dumps, industry best practices encourage short-lived access tokens (e.g. 1 hour) with rotating refresh tokens.
* **Remediation Plan:**
  * Add `/api/v1/auth/refresh` endpoint in `taikry/api/saas_routes.py`.
  * Maintain full backward compatibility with the existing HttpOnly cookie session mechanism.
* **Risk Level:** `LOW`.

---

### Gap 4: Frontend Button State Transitions & Duplicate Click Debouncing
* **Description:** While all 223 buttons in `index.html` are mapped to live JavaScript functions, button state transitions (`IDLE` $\rightarrow$ `LOADING` $\rightarrow$ `SUCCESS` / `ERROR`) currently rely on ad-hoc text swaps (`innerHTML = 'Analyzing...'`) without a formal state machine class.
* **Remediation Plan:**
  * Introduce standardized CSS utility classes (`.zyrox-btn-loading`, `.zyrox-btn-disabled`, `.zyrox-btn-success`).
  * Add automatic debouncing guards preventing duplicate network requests during active fetch calls.
* **Risk Level:** `LOW`.

---

### Gap 5: Dedicated Visual Heatmap & Journal Views
* **Description:**
  * The Market Screener in Section 2 is a list-based table rather than a visual tile-based heatmap grid with color intensity matching momentum.
  * The Trading Journal is accessible via the paper trading ledger, but lacks a dedicated full-page view featuring trade chart screenshots and tag analytics.
* **Remediation Plan:**
  * Add tile-based Heatmap grid view to Section 2.
  * Add dedicated Journal review modal with tags, notes, and emotional classification.
* **Risk Level:** `LOW`.

---

## 3. Prioritized Remediation Roadmap

| Priority | Action Item | Target File(s) | Risk of Change |
| :---: | :--- | :--- | :---: |
| **P1** | Add `qrcode[pil]>=7.4.2` to `requirements.txt` for clean container builds | `requirements.txt` | `NONE` |
| **P2** | Add `/api/v1/auth/refresh` token refresh endpoint | `taikry/api/saas_routes.py` | `LOW` |
| **P3** | Outbound Windows MT5 HTTPS cloud pusher script | `scripts/mt5_cloud_pusher.py` | `LOW` |
| **P4** | Standardized `.zyrox-btn-loading` CSS classes & debouncing | `taikry/web/styles.css`, `taikry/web/app.js` | `LOW` |
| **P5** | Visual Heatmap tile grid formatting | `taikry/web/index.html`, `taikry/web/app.js` | `LOW` |
