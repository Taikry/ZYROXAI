# ZYROX AI — System Architecture & Data Flow

## 1. High-Level Architecture Overview

ZYROX AI is architected into layered, modular subsystems designed for high concurrency, zero lookahead bias, strict data verification, and deterministic risk management.

```mermaid
flowchart TD
    subgraph Data Layer
        MT5[MT5 Terminal Bridge] --> MDE[Multi-Provider Market Data Engine]
        OANDA[OANDA v20 REST] --> MDE
        BINANCE[Binance Spot REST/WS] --> MDE
        CAL[Economic Calendar Provider] --> MDE
    end

    subgraph Quantitative Core
        MDE --> DFV[Data Quality & Freshness Validator]
        DFV --> FLEET[Specialized Agent Fleet: 16 Agents]
        FLEET --> DEBATE[Round-Table Multi-Agent Debate]
        DEBATE --> CRITIC[Independent Critic & Trap Detection]
        CRITIC --> RISK[Deterministic Risk Guardian]
        RISK --> CONSENSUS[Consensus Coordinator: 80-95% Gate]
    end

    subgraph Execution & Surveillance
        CONSENSUS --> PAPER[Paper Trading & Risk Surveillance]
        CONSENSUS --> STATE[Signal Lifecycle State Machine]
        STATE --> TELEGRAM[Telegram Signal Engine: XAUUSD Only, 4/day]
    end

    subgraph Platform Services
        PAY[ABA PayWay Gateway] --> VIP[VIP Membership Manager]
        VIP --> TELEGRAM
        API[FastAPI Application] --> UI[SaaS Cockpit & TradingView Engine]
    end
```

---

## 2. Multi-Agent Orchestration & Consensus Flow

1. **Snapshot Isolation:** A single historical candle snapshot spanning `W1`, `D1`, `H4`, `H1`, `M15`, and `M5` is captured simultaneously.
2. **Specialist Evaluation:** Technical, ICT/SMC, Macro, and Quantitative specialists evaluate the market snapshot in parallel without cross-talk or bias leakage.
3. **Round-Table Debate:** The agents submit structured claims and debate market structure, order flow alignment, and liquidity dynamics.
4. **Independent Critic Audit:** An adversarial critic actively attempts to invalidate the trade idea by checking for overbought/oversold exhaustion traps, high-impact news windows, and liquidity grabs.
5. **Deterministic Risk Guardian:**
   - Enforces minimum Risk-to-Reward ratio ($\ge 1:2.0$).
   - Caps risk at $0.5\%$ of account equity.
   - Computes exact position size: $\text{Lots} = \frac{\text{Equity} \times 0.005}{\text{Stop Distance} \times \text{Contract Size}}$.
   - Verifies spread cost ($\le 20\%$ of stop distance).
6. **Consensus Score Gate:** Synthesizes confluence into an institutional score. Only setups scoring between $80\%$ and $95\%$ are approved.

---

## 3. Signal Lifecycle State Machine

Signals transition through an explicit, persistent finite state machine with database audit logging:

```mermaid
stateDiagram-v2
    [*] --> WAITING_CONFIRMATION
    WAITING_CONFIRMATION --> ACTIVE : Price reaches entry zone
    WAITING_CONFIRMATION --> INVALIDATED : Price breaches SL before entry fill
    WAITING_CONFIRMATION --> EXPIRED : Validity window elapsed (4h default)
    ACTIVE --> TARGET_HIT : Price touches TP1 / TP2 / TP3
    ACTIVE --> STOP_HIT : Price breaches Stop Loss
    ACTIVE --> CLOSED : Manual closure or weekend settlement
    TARGET_HIT --> CLOSED : All targets reached
    STOP_HIT --> [*]
    INVALIDATED --> [*]
    EXPIRED --> [*]
    CLOSED --> [*]
```

---

## 4. Payment & Subscription Architecture (ABA PayWay)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as FastAPI Backend
    participant ABA as ABA PayWay Gateway
    participant VIP as VIP Manager
    participant Tele as Telegram Bot

    User->>Frontend: Select VIP Plan (e.g. Pro, VIP, Lifetime)
    Frontend->>API: POST /api/v1/payments/aba/checkout
    API->>API: Generate HMAC-SHA512 Purchase Hash (24 fields)
    API-->>Frontend: Return Payment URL & Form Payload
    Frontend->>ABA: Submit Checkout Form
    User->>ABA: Complete Payment via ABA Mobile / KHQR
    ABA->>API: POST /api/v1/payments/aba/webhook (Instant Notification)
    API->>API: Verify HMAC-SHA512 Signature & Check Transaction-2
    API->>VIP: Activate Subscription & Generate Expiring Telegram Link
    VIP->>Tele: Dispatch Bilingual Access Link to User
    API-->>ABA: Return HTTP 200 OK
```

---

## 5. Security & Isolation Boundaries

- **Zero Secret Exposure:** API keys, webhook secrets, database credentials, and bot tokens are strictly isolated in environment variables. Redaction filters scrub sensitive tokens from all logs.
- **Constant-Time Cryptography:** All API token comparisons, HMAC verifications, and webhook authentication checks utilize `hmac.compare_digest` to prevent timing attacks.
- **Replay Attack Defense:** MT5 bridge requests require timestamp headers within $\pm 60\text{ seconds}$ and cache request signatures for $120\text{ seconds}$.
- **Shadow Mode Invariant:** Automated live broker order placement is strictly disabled at the source code level to safeguard user capital.

