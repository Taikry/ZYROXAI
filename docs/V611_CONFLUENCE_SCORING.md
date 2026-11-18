# ZYROX AI V6.1.1 — UNIFIED CONFLUENCE SCORING & CONSENSUS SEPARATION

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** V6.1.1 Production Hardening  
**Target Instrument:** XAUUSD Only  
**Primary Execution Gating:** 75/100 Confluence Score & 60% Agent Quorum  
**Status:** IMPLEMENTED & VERIFIED  

---

## 1. Executive Summary

In institutional quantitative analysis, mixing subjective agent voting percentages directly into mathematical indicator scoring introduces severe bias and distorts risk metrics.

Under ZYROX AI V6.1.1:
1. **Confluence Score** and **Agent Consensus** are strictly separated into two distinct, observable metrics.
2. An actionable `BUY` or `SELL` signal requires **BOTH**:
   - `confluence_score >= 75 / 100` (Pure technical alignment from the 8-category confluence scorer)
   - `agent_consensus_pct >= 60.0%` (Institutional agent quorum)
3. If either gate fails, the decision is strictly forced to `WAIT` with an explicit diagnostic rejection reason.

---

## 2. Metric Specifications

| Metric | Source Engine | Range | Threshold Gate | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `confluence_score` | `taikry/trading/confluence_scorer.py` | `0 - 100` (Integer) | **>= 75** | Evaluates technical structure: Trend, SMC liquidity, Order flow delta, ATR, Risk:Reward geometry. |
| `agent_consensus_pct` | `taikry/trading/xauusd_signal_engine.py` | `0.0 - 100.0%` (Float) | **>= 60.0%** | Measures the weighted agreement ratio among participating autonomous voter agents. |

---

## 3. Implementation in `xauusd_signal_engine.py`

```python
# 1. Pure 100-point technical score from confluence engine (never mixed with agent votes)
confluence_score = int(confluence_res.selected_score)

# 2. Agent consensus ratio across participating specialists
raw_agent_ratio = 100.0 * max(buy_weight, sell_weight) / total_participant_weight if total_participant_weight else 0.0
agent_consensus_pct = max(0.0, min(100.0, raw_agent_ratio))

# Gate 1: Confluence score must meet 75/100 threshold
if confluence_score < 75:
    return {
        "decision": "WAIT",
        "confluence_score": confluence_score,
        "agent_consensus_pct": round(agent_consensus_pct, 1),
        "score": confluence_score,
        "confluence_breakdown": confluence_res.to_dict(),
        "rejection_reason": f"Confluence score {confluence_score}/100 below 75/100 threshold.",
        "evidence": all_evidence,
    }

# Gate 2: Agent consensus must reach 60% quorum
if agent_consensus_pct < 60.0:
    return {
        "decision": "WAIT",
        "confluence_score": confluence_score,
        "agent_consensus_pct": round(agent_consensus_pct, 1),
        "score": confluence_score,
        "confluence_breakdown": confluence_res.to_dict(),
        "rejection_reason": f"Agent consensus {agent_consensus_pct:.1f}% below 60% quorum.",
        "evidence": all_evidence,
    }
```

---

## 4. Verification Suite

Tested and verified in `tests/test_v61_confluence_scoring.py`:
- `test_confluence_below_75_forces_wait`: Score 74 with 100% agent consensus outputs `WAIT`.
- `test_agent_consensus_below_60_forces_wait`: Confluence score 85 with 50% consensus outputs `WAIT`.
- `test_confluence_and_consensus_pass_thresholds`: Score 82 with >= 60% consensus outputs `BUY` with distinct separated metric fields.
- `test_non_xauusd_rejected`: Instrument "EURUSD" rejected with `NO TRADE`.
