"""
Unit tests for ZYROX AI V3.1 100-Point Confluence Scoring Engine & 15-Minute Report Persistence.
"""
import pytest
from taikry.trading.confluence_scorer import calculate_confluence_scores, MINIMUM_ACTIONABLE_SCORE
from taikry.database.session import SessionLocal, init_db
from taikry.database.models import FifteenMinuteMarketReport
from taikry.monitoring.engine import _save_fifteen_minute_report, get_seconds_to_next_m15_close


def test_confluence_scorer_missing_data_rule():
    """All empty inputs must produce 0 points and mark status as WAIT with WEAK grade."""
    res = calculate_confluence_scores(
        symbol="XAUUSD",
        timeframe="M15",
        market_data={},
        technical_data={},
        ict_smc_data={},
        macro_news_data={},
        orderflow_data={},
        risk_validation={}
    )
    assert res.buy_score == 0
    assert res.sell_score == 0
    assert res.selected_score == 0
    assert res.status == "WAIT"
    assert res.grade == "WEAK"
    assert res.is_actionable is False
    assert len(res.missing_confirmations) > 0


def test_confluence_scorer_strong_bullish_passes_75_threshold():
    """A qualified setup with high technical and SMC confluence scores >= 75 and is actionable."""
    market_data = {"price": 2650.00, "spread": 0.20, "is_fresh": True}
    technical_data = {
        "technical_context": {
            "m15_trend": "BULLISH",
            "market_structure": "BULLISH",
            "price_above_ema20": True,
            "ema20_above_ema50": True,
            "price_above_ema200": True,
            "rsi_14": 56.0,
            "macd_histogram": 1.25,
            "atr_14": 3.50,
            "higher_highs": True,
            "break_of_structure": True
        },
        "multi_timeframe_alignment": {"H4": "BULLISH", "H1": "BULLISH", "M5": "BULLISH"}
    }
    ict_smc_data = {
        "key_price_zones": {
            "current_zone": "DISCOUNT",
            "in_ote_zone": True,
            "recent_order_blocks": [{"type": "BULLISH_OB", "unmitigated": True}],
            "unmitigated_fvgs": [{"type": "BULLISH_FVG", "unmitigated": True}],
            "recent_liquidity_sweeps": [{"type": "SELL_SIDE_LIQUIDITY_SWEPT"}]
        }
    }
    macro_news_data = {
        "macro_risk": {"dxy_trend": "BEARISH", "blackout_window_active": False}
    }
    orderflow_data = {
        "orderflow_metrics": {"cvd_trend": "BULLISH", "institutional_absorption": True}
    }
    risk_validation = {
        "decision": "APPROVE",
        "entry_price": 2650.00,
        "stop_loss": 2645.00,
        "take_profit_1": 2662.00,
        "take_profit_2": 2675.00,
        "calculated_rr": 2.40,
        "min_rr_threshold": 1.50
    }

    res = calculate_confluence_scores(
        symbol="XAUUSD",
        timeframe="M15",
        market_data=market_data,
        technical_data=technical_data,
        ict_smc_data=ict_smc_data,
        macro_news_data=macro_news_data,
        orderflow_data=orderflow_data,
        risk_validation=risk_validation,
        min_score_threshold=75
    )

    assert res.buy_score >= 75
    assert res.status == "BUY"
    assert res.direction == "BUY"
    assert res.is_actionable is True
    assert res.grade in ("STRONG CONFLUENCE", "VERY HIGH CONFLUENCE")
    assert res.validation_gates["min_score_passed"] is True
    assert res.validation_gates["risk_reward_valid"] is True
    assert res.validation_gates["data_freshness_valid"] is True


def test_confluence_scorer_below_75_forces_wait():
    """Score between 50 and 74 must strictly output WAIT."""
    market_data = {"price": 2650.00, "spread": 0.20, "is_fresh": True}
    technical_data = {
        "technical_context": {
            "m15_trend": "BULLISH",
            "price_above_ema20": True,
            "rsi_14": 52.0,
        },
        "multi_timeframe_alignment": {"H4": "BULLISH"}
    }
    ict_smc_data = {
        "key_price_zones": {"current_zone": "DISCOUNT"}
    }
    risk_validation = {
        "decision": "APPROVE",
        "entry_price": 2650.00,
        "stop_loss": 2646.00,
        "take_profit_1": 2658.00,
        "calculated_rr": 2.00
    }

    res = calculate_confluence_scores(
        symbol="XAUUSD",
        timeframe="M15",
        market_data=market_data,
        technical_data=technical_data,
        ict_smc_data=ict_smc_data,
        risk_validation=risk_validation,
        min_score_threshold=75
    )

    assert res.buy_score < 75
    assert res.status == "WAIT"
    assert res.is_actionable is False


def test_wall_clock_m15_seconds_calculation():
    """get_seconds_to_next_m15_close must return a positive number <= 902 seconds."""
    wait_sec, label = get_seconds_to_next_m15_close()
    assert 1.0 <= wait_sec <= 905.0
    assert "UTC" in label


def test_save_fifteen_minute_report_persistence():
    """_save_fifteen_minute_report creates and updates records in fifteen_minute_market_reports table."""
    init_db()
    candle_label = "2026-11-17 12:00:00 UTC"
    report_dict = {
        "setup_status": "WAIT",
        "market_bias": "NEUTRAL",
        "verified_price": 2655.50,
        "data_quality": {"spread": 0.25},
        "ai_score": 60,
        "confluence_score": {
            "buy_score": 60,
            "sell_score": 35,
            "selected_score": 60,
            "grade": "DEVELOPING",
            "is_actionable": False,
            "category_breakdown": {"trend_alignment": {"buy_points": 8}},
            "supporting_reasons": ["EMA 20 > EMA 50"],
            "contradicting_reasons": [],
            "missing_confirmations": ["Macro blackout"]
        },
        "report_english": "Test report EN",
        "report_khmer": "Test report KH"
    }

    success = _save_fifteen_minute_report(report_dict, candle_label)
    assert success is True

    db = SessionLocal()
    try:
        row = db.query(FifteenMinuteMarketReport).filter(
            FifteenMinuteMarketReport.candle_close_utc == candle_label
        ).first()
        assert row is not None
        assert row.symbol == "XAUUSD"
        assert row.decision_status == "WAIT"
        assert row.selected_score == 60
        assert row.market_price == 2655.50
        assert row.category_scores is not None
        assert "trend_alignment" in row.category_scores
    finally:
        db.close()
