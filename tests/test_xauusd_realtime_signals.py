"""
Unit tests for Real-Time XAUUSD Gold Signals and All Agent AI Fleet Telemetry.
"""
import pytest
from fastapi.testclient import TestClient
from taikry.api.app import app
from taikry.trading.xauusd_signal_engine import xauusd_signal_engine

client = TestClient(app)


def test_xauusd_live_analysis_endpoint():
    """Verify GET /api/v1/xauusd/signals/live-analysis returns real-time multi-agent data."""
    response = client.get("/api/v1/xauusd/signals/live-analysis")
    assert response.status_code == 200
    data = response.json()

    assert data.get("status") == "SUCCESS"
    assert data.get("symbol") == "XAUUSD"
    assert isinstance(data.get("verified_price"), (int, float))
    assert data.get("verified_price") > 0

    consensus = data.get("consensus", {})
    assert consensus.get("decision") in {"BUY", "SELL", "WAIT", "NO TRADE"}
    assert isinstance(consensus.get("confluence_score"), (int, float))

    agents = data.get("all_agents", [])
    assert isinstance(agents, list)
    assert len(agents) >= 8, f"Expected at least 8 registered agents, got {len(agents)}"

    # Check key agents exist
    agent_ids = {a.get("id") for a in agents}
    assert "technical_analyst" in agent_ids
    assert "ict_smc_analyst" in agent_ids
    assert "macro_analyst" in agent_ids
    assert "regime_detection_agent" in agent_ids
    assert "quantitative_research_agent" in agent_ids
    assert "ml_forecast_agent" in agent_ids

    # Each agent must contain icon, bias, confidence, and status
    for a in agents:
        assert "icon" in a
        assert a.get("bias") in {"BULLISH", "BEARISH", "NEUTRAL"}
        assert 0 <= float(a.get("confidence", 0)) <= 100
        assert a.get("status") in {"SUCCESS", "DEFERRED", "PENDING_CANDIDATE"}


def test_xauusd_realtime_engine_caching():
    """Verify in-memory 3.5s cache functions correctly to handle high-frequency UI polling."""
    first = xauusd_signal_engine.get_live_realtime_analysis(bypass_cache=True)
    assert first.get("status") == "SUCCESS"
    ts1 = first.get("timestamp")

    second = xauusd_signal_engine.get_live_realtime_analysis(bypass_cache=False)
    assert second.get("status") == "SUCCESS"
    ts2 = second.get("timestamp")
    assert ts1 == ts2, "Subsequent call within TTL should return cached object"


def test_xauusd_generate_signal_safe_execution():
    """Verify POST /api/v1/xauusd/signals/generate executes safely."""
    response = client.post("/api/v1/xauusd/signals/generate?dispatch_telegram=false")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") in {"APPROVED", "SUPPRESSED"}
