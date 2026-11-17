# ZYROX AI — Intelligence Beyond The Market

> **Next-Generation Multi-Market AI Trading Intelligence Platform**  
> Founded & Engineered by **HENG TAIKRY**  
> Secondary Tagline: *Smarter Analysis. Better Decisions.*

[![Build Status](https://img.shields.io/badge/build-passing-00E59B?style=for-the-badge&logo=vite)](https://github.com/Taikry/Taikry-AI-Trading)
[![React](https://img.shields.io/badge/React-19-00E59B?style=for-the-badge&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-00E59B?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-00E59B?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Render](https://img.shields.io/badge/Deploy-Render-00E59B?style=for-the-badge&logo=render)](https://render.com/)

---

## 🌐 Live Identity & Official Channels

* **Platform Name:** ZYROX AI
* **Founder & Lead AI Engineer:** [HENG TAIKRY](https://www.facebook.com/share/1Eya5WXJXB/?mibextid=wwXIfr)
* **GitHub Repository:** [https://github.com/Taikry/Taikry-AI-Trading](https://github.com/Taikry/Taikry-AI-Trading)
* **Facebook Official:** [https://www.facebook.com/share/1Eya5WXJXB/?mibextid=wwXIfr](https://www.facebook.com/share/1Eya5WXJXB/?mibextid=wwXIfr)
* **TikTok Official:** [https://www.tiktok.com/@hengtaikry](https://www.tiktok.com/@hengtaikry)

---

## 🚀 Key Platform Capabilities

1. **Autonomous Multi-Agent Consensus (6 Neural Agents):**
   * **Market Analysis Agent:** Macro regime classification, volume profiles, and institutional liquidity density.
   * **Technical Analysis Agent:** Triple EMA alignment (20/50/200), multi-timeframe RSI momentum divergence, and ATR bands.
   * **ICT Concepts Agent:** Algorithmic detection of Order Blocks, Fair Value Gaps (FVG), Liquidity Sweeps, and BOS / CHoCH structural shifts.
   * **Risk Management Agent:** Enforces mathematical R:R thresholds (≥ 1:2.0), lot sizing, and drawdown breakers.
   * **Signal Validation Agent:** 80% consensus weighted voting arbiter before any alert authorization.
   * **Market News Intelligence Agent:** NLP sentiment parsing of high-impact releases (CPI, NFP, FOMC) with automated blackout shields.

2. **Interactive Market Dashboard:**
   * Multi-asset coverage across **Commodities (Gold XAUUSD, Silver)**, **Crypto (BTC, ETH, SOL)**, and **Forex Majors (EURUSD, GBPUSD)**.
   * Responsive interactive candlestick charts with timeframe selector (`1M`, `5M`, `15M`, `1H`, `4H`, `1D`), live simulated ticks, and toggleable SMC/ICT overlays.

3. **Bilingual Localization (Khmer 🇰🇭 + English 🇬🇧):**
   * Persistent language switcher saving choice in local storage.
   * Full high-fidelity translations across all sections with native Khmer Unicode font support (`Kantumruy Pro`).

4. **Institutional Signal Telemetry:**
   * Real-time demonstration preview with Entry, Stop-Loss, TP1, TP2, TP3, R:R calculation, and multi-factor confluence checklist.

5. **Founder & Developer Portfolio:**
   * Verified profile showcasing **HENG TAIKRY** using authentic uploaded profile & workstation photographs, skill badges, and direct verified social channels.

6. **Interactive Sandbox Terminal:**
   * "Launch ZYROX AI" modal providing live simulation of the multi-agent consensus pipeline with step-by-step verification.

---

## 🛠️ Technology Stack

* **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Framer Motion, Lucide Icons, Recharts.
* **Backend:** Python 3.12, FastAPI, Uvicorn asynchronous event loop.
* **Database & Persistence:** PostgreSQL 16 (Render Managed Database), SQLAlchemy ORM, Alembic migrations.
* **Market Integration:** MetaTrader 5 (MT5) Streaming Bridge, OANDA REST API, Binance WebSockets.
* **Notifications:** Asynchronous Telegram Bot dispatch with bilingual Markdown reports.

---

## 💻 Local Development Setup

### 1. Frontend Development (React + Vite)

```bash
# Clone the repository
git clone https://github.com/Taikry/Taikry-AI-Trading.git
cd Taikry-AI-Trading

# Install dependencies
npm install

# Start development server
npm run dev
# -> Opens http://localhost:3000

# Build for production
npm run build
# -> Compiles optimized static assets to dist/
```

### 2. Backend Development (FastAPI + Python)

```bash
# Set up Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Python requirements
pip install -r requirements.txt

# Launch FastAPI backend & terminal
python main.py --server --port 8000
```

---

## ☁️ Deployment Guide (Render)

This repository is pre-configured for **Render Static Site** or **Render Web Service (Docker)**.

### Option A: Render Static Site (Recommended for Landing Page)

1. Connect your GitHub repository to Render.
2. Select **New Static Site**.
3. Configure the following settings:
   * **Name:** `zyrox-landing`
   * **Build Command:** `npm install && npm run build`
   * **Publish Directory:** `dist`
4. Deploy! Render will build the Vite React application and serve it via global CDN with instant routing.

### Option B: Render Blueprint Deployment (`render.yaml`)

The included [`render.yaml`](file:///d:/test%20post%20webhook/render.yaml) automatically provisions:

* `zyroxai` (Docker Web Service for FastAPI Backend & Database)
* `taikry-market-database` (PostgreSQL 16 Database)

---

## 🛡️ Risk Disclaimer

> **ZYROX AI provides analytical tools and educational market insights. Trading financial markets involves substantial risk of loss. No profit or trading outcome is guaranteed. Past performance is not indicative of future market results.**

---

© 2026 ZYROX AI. All Rights Reserved. Designed & Developed by **HENG TAIKRY**.
