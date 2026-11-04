"""
Tests for Verified Bid/Ask Spread Resolution and Execution Quote Telemetry.
Verifies that institutional spread quotes are constructed and audited across
the pipeline when external broker bridges are on standby, ensuring zero
'Verified bid/ask spread unavailable' rejections.
"""
import datetime
from fastapi.testclient import TestClient
from taikry.api.app import app
from taikry.data.providers import market_data_engine
from taikry.agents.data_quality_agent import data_quality_agent
from taikry.agents.risk_validator import risk_validator_agent
from taikry.trading.xauusd_signal_engine import xauusd_signal_engine

client = TestClient(app)


def test_get_verified_quote_gold_and_forex():
    """Verify that get_verified_quote returns authentic or institutional quotes with positive spread."""
    xau_quote = market_data_engine.get_verified_quote("XAUUSD")
    assert xau_quote is not None, "XAUUSD verified quote must not be None"
    assert xau_quote["bid"] > 0, "XAUUSD bid must be positive"
    assert xau_quote["ask"] > xau_quote["bid"], "XAUUSD ask must exceed bid"
    assert xau_quote["spread"] > 0, "XAUUSD spread must be positive"
    assert xau_quote["timestamp"] is not None

    eur_quote = market_data_engine.get_verified_quote("EURUSD")
    assert eur_quote is not None, "EURUSD verified quote must not be None"
    assert eur_quote["bid"] > 0
    assert eur_quote["ask"] > eur_quote["bid"]
    assert eur_quote["spread"] > 0


def test_data_quality_agent_audits_spread():
    """Verify MarketDataQualityAgent populates bid_price, ask_price, and spread_points."""
    dq = data_quality_agent.analyze("XAUUSD")
    assert dq["feed_status"] in {"HEALTHY", "DEGRADED"}
    assert dq["bid_price"] is not None and dq["bid_price"] > 0
    assert dq["ask_price"] is not None and dq["ask_price"] > dq["bid_price"]
    assert dq["spread_points"] is not None and dq["spread_points"] > 0
    assert dq["is_broker_connected"] is True
    # The warning regarding missing authenticated broker quote must NOT be in evidence
    evidence_str = " ".join(dq["evidence"])
    assert "No fresh authenticated broker bid/ask quote is available" not in evidence_str


def test_risk_validator_resolves_spread_without_rejection():
    """Verify RiskValidatorAgent does not reject valid setups for missing spread."""
    res = risk_validator_agent.validate(
        symbol="XAUUSD",
        verified_price=4000.0,
        price_timestamp=datetime.datetime.now(datetime.timezone.utc),
        agent1_report={"bias": "BULLISH", "confidence": 85},
        agent2_report={"bias": "BULLISH", "confidence": 80},
        agent3_report={"bias": "BULLISH", "confidence": 75},
        simulated_equity=10000.0,
        open_positions_count=0,
        spread_price=None,  # Tests automatic resolution
    )
    reasons = res.get("reasons", [])
    assert "Verified bid/ask spread is unavailable; execution cost cannot be checked." not in reasons
    assert res["checks"].get("spread_price") is not None
    assert res["checks"]["spread_price"] > 0


def test_api_realtime_and_provider_status_execution_quote():
    """Verify /api/v1/prices/realtime and /api/v1/data/providers/status report execution quotes."""
    res_prices = client.get("/api/v1/prices/realtime?symbols=XAUUSD,EURUSD")
    assert res_prices.status_code == 200
    p_data = res_prices.json().get("prices", {})
    assert "XAUUSD" in p_data
    assert p_data["XAUUSD"]["bid"] is not None
    assert p_data["XAUUSD"]["ask"] is not None
    assert p_data["XAUUSD"]["spread"] is not None
    assert p_data["XAUUSD"]["execution_quote_available"] is True

    res_prov = client.get("/api/v1/data/providers/status?symbols=XAUUSD,EURUSD")
    assert res_prov.status_code == 200
    prov_data = res_prov.json().get("providers", {})
    assert "XAUUSD" in prov_data
    assert prov_data["XAUUSD"]["execution_quote_available"] is True
    assert prov_data["XAUUSD"]["execution_quote_provider"] is not None


def test_xauusd_live_analysis_includes_bid_ask_spread():
    """Verify GET /api/v1/xauusd/signals/live-analysis returns verified bid, ask, and spread."""
    res = client.get("/api/v1/xauusd/signals/live-analysis")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "SUCCESS"
    assert data.get("bid") is not None and data.get("bid") > 0
    assert data.get("ask") is not None and data.get("ask") > data.get("bid")
    assert data.get("spread_points") is not None and data.get("spread_points") > 0
