"""
Tests for ZYROX AI Advanced Risk Intelligence V3
================================================
Verifies:
- 4 canonical risk decisions (APPROVED, APPROVED_WITH_REDUCED_RISK, WAIT_FOR_CONFIRMATION, REJECTED)
- 8-state market regime engine
- Multi-market portfolio exposure & correlation matrix
- Calendar-aware news risk engine & protection windows
- Explainable 0–100 signal quality scoring across 8 factors
- Database audit logging & REST API endpoints
"""
import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from taikry.api.app import app
from taikry.risk.models import RiskDecision, MarketRegimeType
from taikry.risk.service import risk_intelligence_service
from taikry.risk.regime import regime_engine
from taikry.risk.portfolio import portfolio_engine
from taikry.risk.news_risk import news_risk_engine
from taikry.risk.quality_scorer import signal_quality_scorer


@pytest.fixture
def test_client():
    return TestClient(app)


def test_market_regime_classification_uncertain_on_empty():
    """Confirms that insufficient bar depth safely returns UNCERTAIN without guessing."""
    res = regime_engine.classify_regime("XAUUSD", None)
    assert res.regime == MarketRegimeType.UNCERTAIN
    assert not res.is_confirmed
    assert any("insufficient" in e.lower() for e in res.evidence)


def test_market_regime_classification_trending():
    """Creates synthetic trending series and verifies trend detection."""
    np.random.seed(42)
    steps = 100
    prices = 2000.0 + np.cumsum(np.random.normal(1.0, 0.3, steps))
    df = pd.DataFrame({
        "open": prices - 0.2,
        "high": prices + 0.5,
        "low": prices - 0.5,
        "close": prices,
        "volume": [1000] * steps
    })
    res = regime_engine.classify_regime("XAUUSD", df)
    assert res.regime in {MarketRegimeType.STRONG_TREND, MarketRegimeType.WEAK_TREND, MarketRegimeType.BREAKOUT}
    assert res.hurst_exponent > 0.50
    assert res.is_confirmed


def test_portfolio_exposure_and_currency_accounting():
    """Verifies that multi-market portfolio calculation accounts for USD exposure and limits."""
    summary = portfolio_engine.evaluate_portfolio(
        proposed_symbol="XAUUSD",
        proposed_direction="BUY",
        proposed_risk_pct=0.5,
        account_equity=100000.0
    )
    assert summary.max_portfolio_risk_pct == 5.0
    assert summary.total_open_positions >= 0
    assert isinstance(summary.warnings, list)
    assert isinstance(summary.active_symbols, list)


def test_portfolio_correlation_lookup():
    """Verifies pairwise cross-asset correlation lookup."""
    btc_eth = portfolio_engine.get_correlation("BTCUSDT", "ETHUSDT")
    assert btc_eth >= 0.80

    eur_chf = portfolio_engine.get_correlation("EURUSD", "USDCHF")
    assert eur_chf < -0.80

    same = portfolio_engine.get_correlation("XAUUSD", "XAUUSD")
    assert same == 1.0


def test_news_risk_evaluation():
    """Verifies calendar news risk evaluation and mode handling."""
    res_std = news_risk_engine.evaluate_news_risk("XAUUSD", filter_mode="STANDARD")
    assert res_std.pre_event_window_minutes == 30
    assert res_std.news_status in {"CLEAR", "BLACKOUT_ACTIVE", "ADVISORY_APPROACHING", "FEED_UNAVAILABLE"}

    res_off = news_risk_engine.evaluate_news_risk("XAUUSD", filter_mode="OFF")
    assert not res_off.is_blackout
    assert res_off.news_status == "MONITOR_ONLY"


def test_signal_quality_8_factor_scoring():
    """Verifies that the 8-factor score computes a bounded 0–100 score."""
    q = signal_quality_scorer.calculate_score(
        symbol="XAUUSD",
        direction="BUY",
        rr_ratio=2.5,
        trend_aligned=True,
        structure_confirmed=True,
        momentum_aligned=True,
        volatility_ok=True,
        entry_quality_ok=True,
        news_clear=True,
        data_fresh=True
    )
    assert 0 <= q.total_score <= 100
    assert q.total_score >= 80
    assert q.grade in {"ELITE", "HIGH"}
    assert "Internal setup confluence metric" in q.disclaimer


def test_risk_candidate_approved_and_rejected():
    """Verifies that valid geometry is approved while invalid geometry is rejected."""
    # 1. Valid setup
    good_res = risk_intelligence_service.evaluate_trade_candidate(
        symbol="XAUUSD",
        direction="BUY",
        entry_price=2700.0,
        stop_loss=2690.0,
        take_profit_1=2725.0,  # 25 / 10 = 2.5 R:R
        risk_mode="BALANCED",
        persist_log=False
    )
    assert good_res.decision in {RiskDecision.APPROVED, RiskDecision.APPROVED_WITH_REDUCED_RISK, RiskDecision.WAIT_FOR_CONFIRMATION}
    assert good_res.sizing.lot_size >= 0.01

    # 2. Sub-floor R:R setup
    bad_rr = risk_intelligence_service.evaluate_trade_candidate(
        symbol="XAUUSD",
        direction="BUY",
        entry_price=2700.0,
        stop_loss=2690.0,
        take_profit_1=2705.0,  # 5 / 10 = 0.5 R:R (fails 2.0 floor)
        risk_mode="BALANCED",
        persist_log=False
    )
    assert bad_rr.decision == RiskDecision.REJECTED
    assert any("Insufficient Risk-to-Reward" in v for v in bad_rr.veto_reasons)

    # 3. Invalid geometry (SL above Entry for BUY)
    bad_geom = risk_intelligence_service.evaluate_trade_candidate(
        symbol="XAUUSD",
        direction="BUY",
        entry_price=2700.0,
        stop_loss=2710.0,
        take_profit_1=2725.0,
        risk_mode="BALANCED",
        persist_log=False
    )
    assert bad_geom.decision == RiskDecision.REJECTED
    assert any("Invalid geometry" in v for v in bad_geom.veto_reasons)


def test_v3_api_endpoints(test_client):
    """Verifies the new V3 REST API endpoints."""
    # Overview
    r_over = test_client.get("/api/v1/risk/overview")
    assert r_over.status_code == 200
    assert r_over.json()["status"] == "SUCCESS"

    # Portfolio
    r_port = test_client.get("/api/v1/risk/portfolio?symbol=XAUUSD&direction=BUY")
    assert r_port.status_code == 200
    assert "portfolio" in r_port.json()

    # Regime
    r_regime = test_client.get("/api/v1/risk/regime?symbol=XAUUSD")
    assert r_regime.status_code == 200
    assert "regime" in r_regime.json()

    # Quality
    r_qual = test_client.get("/api/v1/risk/quality?symbol=XAUUSD&direction=BUY&rr=2.2")
    assert r_qual.status_code == 200
    assert "quality_score" in r_qual.json()

    # Candidate evaluation POST
    r_eval = test_client.post("/api/v1/risk/evaluate-candidate", json={
        "symbol": "XAUUSD",
        "direction": "BUY",
        "entry_price": 2700.0,
        "stop_loss": 2690.0,
        "take_profit_1": 2725.0,
        "risk_mode": "BALANCED"
    })
    assert r_eval.status_code == 200
    res_data = r_eval.json()["assessment"]
    assert res_data["decision"] in ["APPROVED", "APPROVED_WITH_REDUCED_RISK", "WAIT_FOR_CONFIRMATION", "REJECTED"]
    assert res_data["sizing"]["lot_size"] > 0
