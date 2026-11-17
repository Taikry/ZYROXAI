# ZYROX AI V6.1 — AI AGENT TELEMETRY & SSE STREAMING REPORT

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** 6.1.0-PROD  
**Target Branch:** `main`  
**Founder:** HENG TAIKRY  
**Date:** 2026-11-18  
**Status:** VERIFIED  

---

## 1. Executive Summary

This report documents the real AI agent telemetry and real-time streaming endpoints in **ZYROX AI V6.1**. All synthetic `setTimeout` simulations, fabricated constants, and hardcoded confidence values have been audited and replaced with authentic execution metrics sourced directly from the Python agent registry and model adapters.

---

## 2. Dynamic Agent Registry & Lifecycle Telemetry

The ZYROX AI fleet consists of specialized autonomous agents managed by the centralized `AgentRegistry` (`taikry/agents/registry.py`):

| Agent ID | Specialization | Role | Default Model | Real-Time Telemetry |
| :--- | :--- | :--- | :--- | :--- |
| `market_regime` | Macro & Volatility | Regime Classification | `deepseek-chat` | Latency, execution count, last run |
| `smc_structure` | Order Flow & Liquidity | SMC / ICT Confluence | `deepseek-chat` | Latency, execution count, last run |
| `multi_tf` | Higher Timeframe Bias | MTF Alignment | `deepseek-chat` | Latency, execution count, last run |
| `candlestick` | Price Action Patterns | Wick / Rejection Geometry | `gemini-1.5-flash` | Latency, execution count, last run |
| `sentiment` | News & Catalyst Filter | Sentiment Analysis | `gemini-1.5-flash` | Latency, execution count, last run |
| `risk_guardian` | Risk & Lot Sizing | Execution Validation | `local-rules-engine` | Latency, execution count, last run |
| `consensus_engine` | Neural Synthesis | 100-Point Confluence | `claude-3-5-sonnet` | Confluence matrix, weights, vetoes |

---

## 3. Server-Sent Events (SSE) Streaming Endpoints

### 3.1 Streaming AI Chat (`/api/v1/ai/chat/stream`)

* **Protocol:** HTTP/1.1 SSE (`text/event-stream`).
* **Authentication:** Enforced via `zyrox_session` cookie or `Authorization: Bearer` header.
* **Payload Structure:**

```json
event: message
data: {"chunk": "Based on current M15 Gold market structure...", "done": false}

event: complete
data: {"total_tokens": 342, "latency_ms": 618.5, "model": "deepseek-chat"}
```

* **Guarantees:** No synthetic delays. Chunks are yielded directly from the underlying LLM provider stream.

### 3.2 Registry Telemetry API (`/api/v1/agents/registry`)

* **Endpoint:** `GET /api/v1/agents/registry`
* **Response Payload:**
  * Catalog of all registered agents.
  * Individual execution counters and error tallies.
  * Rolling average latency per agent.
  * Assigned model provider (`DeepSeek`, `Gemini`, `Claude`, `OpenAI`).

---

## 4. Frontend & Live/Demo Separation

1. **Live Terminal vs. Demo Backtest:**
   * Signals produced by the real-time broker feed are badged with `LIVE BROKER SIGNAL` and display real broker quote provenance.
   * Static promotional samples in `src/data/signals.ts` are explicitly identified as `DEMO_SIGNALS` for UI demonstration only.
2. **Interactive Pipeline Inspector:**
   * In `src/sections/AgentsSection.tsx`, the workflow visualizer is explicitly marked with `DEMO ARCHITECTURE PREVIEW` so visitors understand it represents the algorithmic pipeline structure.
