import pytest
from fastapi.testclient import TestClient
from taikry.api.app import app
from taikry.agents.consensus_engine import ai_consensus_engine
from taikry.agents.risk_validator import risk_validator_agent

client = TestClient(app)

def test_risk_validator_smart_trading_and_scalping():
    """Verify risk_validator produces smart_trading levels and handles SCALPING style."""
    agent1_rep = {
        "bias": "BULLISH",
        "confidence": 85,
        "entry_price": 2650.0,
        "stop_loss": 2640.0,
        "take_profit_1": 2670.0,
        "take_profit_2": 2690.0,
        "key_price_levels": {"atr": 5.0, "rsi": 55.0},
    }
    agent2_rep = {"bias": "BULLISH", "confidence": 80}
    agent3_rep = {"bias": "BULLISH", "confidence": 75}

    res = risk_validator_agent.validate(
        symbol="XAUUSD",
        verified_price=2650.0,
        price_timestamp=None,
        agent1_report=agent1_rep,
        agent2_report=agent2_rep,
        agent3_report=agent3_rep,
        simulated_equity=10000.0,
        trade_style="SCALPING",
        risk_mode="AGGRESSIVE",
    )

    assert "smart_trading" in res
    smart = res["smart_trading"]
    assert "breakeven_trigger" in smart
    assert "partial_take_profit" in smart
    assert "runner_take_profit" in smart
    assert "recommended_lots" in smart
    assert smart["trade_style"] == "SCALPING"
    assert smart["scalp_suitability"] in {"HIGH", "MODERATE"}


def test_api_best_setup_supports_scalping_and_direction():
    """Verify /api/v1/best-setup supports SCALPING and returns dual directional setups."""
    response = client.get("/api/v1/best-setup?category=FOREX&trade_style=SCALPING&direction=ALL")
    assert response.status_code == 200
    data = response.json()
    assert data["trade_style"] == "SCALPING"
    assert data["direction_filter"] == "ALL"
    assert "best_setup" in data
    assert "best_long" in data
    assert "best_short" in data
    assert "long_count" in data
    assert "short_count" in data
    assert isinstance(data["setups"], list)

    # Test filtering specifically for LONG
    res_long = client.get("/api/v1/best-setup?category=FOREX&trade_style=SCALPING&direction=LONG")
    assert res_long.status_code == 200
    data_long = res_long.json()
    assert data_long["direction_filter"] == "LONG"
    for s in data_long["setups"]:
        dir_val = str(s.get("proposed_direction") or "").upper()
        bias_val = str(s.get("market_bias") or "").upper()
        assert "BUY" in dir_val or "LONG" in dir_val or "BULL" in bias_val

    # Test filtering specifically for SHORT
    res_short = client.get("/api/v1/best-setup?category=FOREX&trade_style=SCALPING&direction=SHORT")
    assert res_short.status_code == 200
    data_short = res_short.json()
    assert data_short["direction_filter"] == "SHORT"
    for s in data_short["setups"]:
        dir_val = str(s.get("proposed_direction") or "").upper()
        bias_val = str(s.get("market_bias") or "").upper()
        assert "SELL" in dir_val or "SHORT" in dir_val or "BEAR" in bias_val


def test_api_analyze_accepts_scalping_style():
    """Verify /api/v1/analyze accepts trade_style='SCALPING' without error."""
    payload = {
        "symbol": "XAUUSD",
        "timeframe": "M5",
        "trade_style": "SCALPING",
        "force_fresh": False,
        "llm_provider": "quant",
    }
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["trade_style"] == "SCALPING"
    assert "smart_trading" in data
    assert "smart_analysis" in data
    assert "smart_trading" in data["smart_analysis"]

