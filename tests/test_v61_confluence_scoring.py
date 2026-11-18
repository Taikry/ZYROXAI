"""
Tests for Phase D: Unified Confluence Scoring & Agent Consensus Separation.
Verifies:
- Confluence score (0-100 technical) is separated from agent consensus (0-100% agreement).
- BUY/SELL requires confluence_score >= 75 AND agent_consensus_pct >= 60.0%.
- If confluence_score < 75, signal forces WAIT.
- If agent_consensus_pct < 60.0%, signal forces WAIT.
- Non-XAUUSD symbol requests are strictly rejected.
"""
import pytest
from unittest.mock import MagicMock, patch
from taikry.trading.xauusd_signal_engine import XAUUSDSignalEngine
from taikry.trading.confluence_scorer import ConfluenceScoreResult


def _mock_confluence_result(score: int, is_actionable: bool = True):
    return ConfluenceScoreResult(
        symbol="XAUUSD",
        timeframe="M15",
        buy_score=score,
        sell_score=20,
        status="BUY" if is_actionable else "WAIT",
        direction="BUY",
        selected_score=score,
        grade="STRONG CONFLUENCE" if score >= 75 else "MODERATE CONFLUENCE",
        category_breakdown={},
        supporting_reasons=["Bullish alignment"],
        contradicting_reasons=[],
        missing_confirmations=[],
        validation_gates={"min_score_passed": score >= 75, "risk_reward_valid": True, "data_freshness_valid": True},
        is_actionable=is_actionable,
    )


def _mock_adapters():
    voters = ["technical_analyst", "ict_smc_analyst", "macro_analyst", "orderflow_sentiment_analyst"]
    adapters = []
    for vid in voters:
        m = MagicMock()
        m.metadata.agent_id = vid
        adapters.append(m)
    return adapters


def _base_agent_outputs():
    return {
        "technical_analyst": {
            "status": "SUCCESS",
            "bias": "BULLISH",
            "confidence": 85.0,
            "contributes_to_consensus": True,
            "key_levels": {"support": 2640.0, "resistance": 2660.0, "atr": 3.5, "atr_14": 3.5},
            "evidence": ["Bullish trend structure"],
        },
        "ict_smc_analyst": {
            "status": "SUCCESS",
            "bias": "BULLISH",
            "confidence": 80.0,
            "contributes_to_consensus": True,
            "key_price_zones": {"order_block": 2645.0},
            "evidence": ["Bullish order block confirmed"],
        },
        "macro_analyst": {
            "status": "SUCCESS",
            "bias": "BULLISH",
            "confidence": 75.0,
            "contributes_to_consensus": True,
            "evidence": ["DXY weakening"],
        },
        "orderflow_sentiment_analyst": {
            "status": "SUCCESS",
            "bias": "BULLISH",
            "confidence": 70.0,
            "contributes_to_consensus": True,
            "evidence": ["Positive CVD delta"],
        },
        "risk_validator": {
            "status": "SUCCESS",
            "decision": "APPROVE",
            "contributes_to_consensus": False,
        },
    }


def test_confluence_below_75_forces_wait():
    engine = XAUUSDSignalEngine()
    agent_outputs = _base_agent_outputs()

    with patch("taikry.trading.xauusd_signal_engine.calculate_confluence_scores") as mock_calc, \
         patch("taikry.trading.xauusd_signal_engine.agent_registry.get_adapter") as mock_adapter, \
         patch.object(engine, "discover_eligible_agents", return_value=_mock_adapters()):
        # Mock risk validator
        rv = MagicMock()
        rv.execute.return_value = {"decision": "APPROVE", "status": "SUCCESS"}
        mock_adapter.return_value = rv

        # Return score 74 (below 75 threshold)
        mock_calc.return_value = _mock_confluence_result(74, is_actionable=False)

        res = engine.synthesize_consensus(
            symbol="XAUUSD",
            verified_price=2650.0,
            agent_outputs=agent_outputs,
            multi_tf_data={},
            spread_price=0.20,
        )
        print("DEBUG RES:", res)
        assert res["decision"] == "WAIT"
        assert res["confluence_score"] == 74
        assert "Confluence score 74/100 below 75/100 threshold" in res["rejection_reason"]


def test_agent_consensus_below_60_forces_wait():
    engine = XAUUSDSignalEngine()
    agent_outputs = _base_agent_outputs()
    # Modify votes so consensus is under 60%
    agent_outputs["technical_analyst"]["bias"] = "BULLISH"
    agent_outputs["ict_smc_analyst"]["bias"] = "BULLISH"
    agent_outputs["macro_analyst"]["bias"] = "NEUTRAL"
    agent_outputs["orderflow_sentiment_analyst"]["bias"] = "BEARISH"

    with patch("taikry.trading.xauusd_signal_engine.calculate_confluence_scores") as mock_calc, \
         patch("taikry.trading.xauusd_signal_engine.agent_registry.get_adapter") as mock_adapter, \
         patch.object(engine, "discover_eligible_agents", return_value=_mock_adapters()):
        rv = MagicMock()
        rv.execute.return_value = {"decision": "APPROVE", "status": "SUCCESS"}
        mock_adapter.return_value = rv

        mock_calc.return_value = _mock_confluence_result(85, is_actionable=True)

        res = engine.synthesize_consensus(
            symbol="XAUUSD",
            verified_price=2650.0,
            agent_outputs=agent_outputs,
            multi_tf_data={},
            spread_price=0.20,
        )
        print("DEBUG RES:", res)
        assert res["decision"] == "WAIT"
        assert res["agent_consensus_pct"] < 60.0
        assert "below 60% quorum" in res["rejection_reason"]


def test_confluence_and_consensus_pass_thresholds():
    engine = XAUUSDSignalEngine()
    agent_outputs = _base_agent_outputs()

    with patch("taikry.trading.xauusd_signal_engine.calculate_confluence_scores") as mock_calc, \
         patch("taikry.trading.xauusd_signal_engine.agent_registry.get_adapter") as mock_adapter, \
         patch.object(engine, "discover_eligible_agents", return_value=_mock_adapters()):
        rv = MagicMock()
        rv.execute.return_value = {"decision": "APPROVE", "status": "SUCCESS", "is_approved": True, "is_execution_viable": True}
        mock_adapter.return_value = rv

        # Both score >= 75 and consensus >= 60%
        mock_calc.return_value = _mock_confluence_result(82, is_actionable=True)

        res = engine.synthesize_consensus(
            symbol="XAUUSD",
            verified_price=2650.0,
            agent_outputs=agent_outputs,
            multi_tf_data={},
            spread_price=0.20,
        )

        assert res["decision"] == "BUY"
        assert res["confluence_score"] == 82
        assert res["agent_consensus_pct"] >= 60.0
        assert res["confluence_score"] != res["agent_consensus_pct"]  # Separate metrics


def test_non_xauusd_rejected():
    engine = XAUUSDSignalEngine()
    agent_outputs = _base_agent_outputs()

    res = engine.synthesize_consensus(
        symbol="EURUSD",
        verified_price=1.0850,
        agent_outputs=agent_outputs,
        multi_tf_data={},
    )
    assert res["decision"] == "NO TRADE"
    assert "EURUSD" in res["rejection_reason"]
    assert res["confluence_score"] == 0
    assert res["agent_consensus_pct"] == 0.0
