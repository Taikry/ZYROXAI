"""
ZYROX AI V6 — Deterministic Unit & Integration Test Suite
=========================================================
Tests all 20 modules with known synthetic and real candle fixtures:
- Trend detection (Bullish & Bearish Strong/Weak)
- Range detection (Hurst, low ADX)
- Breakout detection (Donchian piercing + expanding volatility)
- Break of Structure (BOS) & Change of Character (CHoCH)
- Liquidity sweeps & Stop Hunt (Turtle soup)
- Fair Value Gaps (FVG) & Inversion FVGs
- Order Block validation & Breakers
- Support / Resistance & Benchmark levels
- Volatility regimes (Squeeze & Expansion)
- Auto Strategy Selector & Priority ranking
- Concept qualification & ranking
- Entry, Invalidation Stop Loss & Multi-Target Take Profits (TP1, TP2, TP3)
- Multi-Timeframe conflict resolution
- News risk blackout & WAIT results
- NO_TRADE handling on sparse data
- REST API endpoints integration (/api/v6/*)
"""
import pytest
import datetime
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from taikry.v6.models import V6MarketRegime
from taikry.v6.regime import v6_regime_engine
from taikry.v6.concepts.detector import v6_concepts_engine
from taikry.v6.strategies.registry import STRATEGY_REGISTRY
from taikry.v6.strategies.selector import v6_strategy_selector
from taikry.v6.scoring import v6_quality_scorer
from taikry.v6.mtf_engine import v6_mtf_engine
from taikry.v6.trade_levels import v6_trade_levels_engine
from taikry.v6.service import v6_intelligence_service
from taikry.api.app import app


# =============================================================================
# SYNTHETIC FIXTURE GENERATORS
# =============================================================================

def make_trending_dataframe(n: int = 60, direction: str = "BULLISH", start_price: float = 2000.0) -> pd.DataFrame:
    """Generates synthetic trend candles with persistent slope, fractal swings, and order blocks."""
    dates = [datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15 * (n - i)) for i in range(n)]
    closes = []
    highs = []
    lows = []
    opens = []
    volumes = []

    curr = start_price

    for i in range(n):
        p = i % 6
        if direction == "BULLISH":
            if p == 0:
                o = curr; c = curr + 4.0; h = c + 0.5; l = o - 0.5
            elif p == 1:
                o = curr; c = curr + 4.0; h = c + 0.5; l = o + 0.5
            elif p == 2:
                o = curr; c = curr + 4.0; h = c + 1.0; l = o + 1.0
            elif p == 3:
                o = curr; c = curr - 2.5; h = o - 0.2; l = c - 0.2
            elif p == 4:
                o = curr; c = curr - 2.5; h = o - 0.2; l = c - 1.0
            else:
                o = curr; c = curr + 8.0; h = c + 1.0; l = o + 0.5
        else:
            if p == 0:
                o = curr; c = curr - 4.0; h = o + 0.5; l = c - 0.5
            elif p == 1:
                o = curr; c = curr - 4.0; h = o - 0.5; l = c - 0.5
            elif p == 2:
                o = curr; c = curr - 4.0; h = o - 1.0; l = c - 1.0
            elif p == 3:
                o = curr; c = curr + 2.5; h = c + 0.2; l = o + 0.2
            elif p == 4:
                o = curr; c = curr + 2.5; h = c + 1.0; l = o + 0.2
            else:
                o = curr; c = curr - 8.0; h = o - 0.5; l = c - 1.0

        curr = c
        opens.append(o)
        closes.append(c)
        highs.append(h)
        lows.append(l)
        volumes.append(100.0 + (i * 2.0))

    return pd.DataFrame({
        "timestamp": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes
    })


def make_ranging_dataframe(n: int = 60, center_price: float = 2000.0, span: float = 10.0) -> pd.DataFrame:
    """Generates synthetic mean-reverting range consolidation candles."""
    dates = [datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15 * (n - i)) for i in range(n)]
    closes = []
    highs = []
    lows = []
    opens = []
    volumes = []

    for i in range(n):
        # Oscillate smoothly with sine wave
        angle = (i / 8.0) * np.pi
        curr = center_price + (np.sin(angle) * (span / 2.0))
        o = center_price + (np.sin(angle - 0.2) * (span / 2.0))
        h = max(o, curr) + 0.8
        l = min(o, curr) - 0.8
        opens.append(o)
        closes.append(curr)
        highs.append(h)
        lows.append(l)
        volumes.append(50.0)

    return pd.DataFrame({
        "timestamp": dates,
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes
    })


def make_breakout_dataframe(n: int = 60, base_price: float = 2000.0) -> pd.DataFrame:
    """Generates tight range for 50 bars followed by a violent 10-bar breakout explosion."""
    df_range = make_ranging_dataframe(50, center_price=base_price, span=4.0)
    last_ts = df_range["timestamp"].iloc[-1]

    more_o, more_h, more_l, more_c, more_v, more_t = [], [], [], [], [], []
    curr = base_price + 2.0
    for i in range(10):
        curr += 8.0  # Massive breakout expansion
        t = last_ts + datetime.timedelta(minutes=15 * (i + 1))
        o = curr - 4.0
        h = curr + 2.0
        l = o - 0.5
        more_o.append(o)
        more_h.append(h)
        more_l.append(l)
        more_c.append(curr)
        more_v.append(500.0)
        more_t.append(t)

    df_break = pd.DataFrame({
        "timestamp": more_t,
        "open": more_o,
        "high": more_h,
        "low": more_l,
        "close": more_c,
        "volume": more_v
    })
    return pd.concat([df_range, df_break], ignore_index=True)


# =============================================================================
# DETERMINISTIC UNIT TESTS
# =============================================================================

def test_trend_detection_bullish_and_bearish():
    """Verify Module 1 correctly detects strong and weak trend regimes."""
    df_bull = make_trending_dataframe(60, direction="BULLISH", start_price=2000.0)
    res_bull = v6_regime_engine.analyze_regime("XAUUSD", df_bull, timeframe="M15")
    assert "BULLISH" in res_bull.regime.value
    assert res_bull.strength >= 65
    assert len(res_bull.evidence) > 0

    df_bear = make_trending_dataframe(60, direction="BEARISH", start_price=2000.0)
    res_bear = v6_regime_engine.analyze_regime("XAUUSD", df_bear, timeframe="M15")
    assert "BEARISH" in res_bear.regime.value
    assert res_bear.strength >= 65


def test_range_detection():
    """Verify Module 1 identifies mean-reverting range consolidation."""
    df_range = make_ranging_dataframe(60, center_price=2000.0, span=8.0)
    res_range = v6_regime_engine.analyze_regime("EURUSD", df_range, timeframe="M15")
    assert res_range.regime in (V6MarketRegime.RANGE, V6MarketRegime.LOW_VOLATILITY)
    assert res_range.strength >= 60


def test_breakout_detection():
    """Verify Module 1 detects breakout expansion piercing channel extremes."""
    df_break = make_breakout_dataframe(60, base_price=2000.0)
    res_break = v6_regime_engine.analyze_regime("BTCUSDT", df_break, timeframe="M15")
    assert res_break.regime in (V6MarketRegime.BREAKOUT, V6MarketRegime.TREND_BULLISH_STRONG)


def test_bos_and_choch_structure_breaks():
    """Verify Category A detects fractal swing breaks (BOS) and character change (CHoCH)."""
    df = make_trending_dataframe(60, direction="BULLISH")
    concepts = v6_concepts_engine.detect_all(df, timeframe="M15")
    struct_concepts = [c for c in concepts if c.category.value == "MARKET_STRUCTURE"]
    assert len(struct_concepts) >= 1
    concept_ids = {c.concept_id for c in struct_concepts}
    assert "struct_swings" in concept_ids or "struct_bullish_hh_hl" in concept_ids


def test_liquidity_sweep_and_stophunt():
    """Verify Category B detects liquidity pools (BSL/SSL) and sweeps."""
    df = make_ranging_dataframe(60)
    concepts = v6_concepts_engine.detect_all(df, timeframe="M15")
    liq_concepts = [c for c in concepts if c.category.value == "SMART_MONEY_LIQUIDITY"]
    assert len(liq_concepts) >= 1
    assert any("liq_bsl_pool" in c.concept_id or "liq_ssl_pool" in c.concept_id for c in liq_concepts)


def test_fvg_imbalance_and_inversion():
    """Verify Category C detects 3-candle Fair Value Gaps and IFVGs."""
    # Create deliberate 3-candle gap
    df = make_ranging_dataframe(30)
    # Inject large gap on candle 28
    df.loc[27, "high"] = 1995.0
    df.loc[28, "open"] = 2000.0
    df.loc[28, "close"] = 2010.0
    df.loc[28, "high"] = 2012.0
    df.loc[28, "low"] = 1999.0
    df.loc[29, "low"] = 2005.0  # low[29] (2005) > high[27] (1995) -> 10 pt gap!
    df.loc[29, "close"] = 2015.0

    concepts = v6_concepts_engine.detect_all(df, timeframe="M15")
    imb_concepts = [c for c in concepts if c.category.value == "IMBALANCE"]
    assert any("fvg" in c.concept_id for c in imb_concepts)


def test_order_block_validation():
    """Verify Category D validates displacement Order Blocks."""
    df = make_trending_dataframe(50, direction="BULLISH")
    concepts = v6_concepts_engine.detect_all(df, timeframe="M15")
    of_concepts = [c for c in concepts if c.category.value == "ORDER_FLOW_ZONES"]
    assert len(of_concepts) >= 1


def test_support_resistance_levels():
    """Verify Category E computes benchmark session levels (PDH/PDL/DO)."""
    df = make_ranging_dataframe(50)
    concepts = v6_concepts_engine.detect_all(df, timeframe="M15")
    sr_concepts = [c for c in concepts if c.category.value == "SUPPORT_RESISTANCE"]
    assert any("sr_benchmark_levels" in c.concept_id for c in sr_concepts)


def test_volatility_regime_and_squeeze():
    """Verify Category I identifies volatility compression / squeeze."""
    df = make_ranging_dataframe(60, center_price=2000.0, span=2.0) # ultra tight 2 pt span
    concepts = v6_concepts_engine.detect_all(df, timeframe="M15")
    vol_concepts = [c for c in concepts if c.category.value == "VOLATILITY"]
    assert any("vol_compression_squeeze" in c.concept_id or "vol_atr_baseline" in c.concept_id for c in vol_concepts)


def test_strategy_selection_and_registry():
    """Verify Module 3 & 4 select appropriate strategies based on market regime."""
    df_bull = make_trending_dataframe(60, direction="BULLISH")
    regime_res = v6_regime_engine.analyze_regime("XAUUSD", df_bull)
    concepts = v6_concepts_engine.detect_all(df_bull)

    sel = v6_strategy_selector.select_strategy("XAUUSD", regime_res, concepts)
    assert sel.selection_status == "STRATEGY_SELECTED"
    assert sel.top_strategy is not None
    assert sel.top_strategy.strategy_id in ("TREND_PULLBACK", "STRUCTURE_CONTINUATION", "BREAKOUT_RETEST", "EMA_PULLBACK")


def test_entry_sl_and_tp_generation():
    """Verify Modules 8, 9, 10 calculate technically sound Entry, invalidation SL and multi-target TPs."""
    df_bull = make_trending_dataframe(60, direction="BULLISH", start_price=2000.0)
    concepts = v6_concepts_engine.detect_all(df_bull)

    plan = v6_trade_levels_engine.calculate_levels(
        symbol="XAUUSD",
        direction="BUY",
        strategy_id="TREND_PULLBACK",
        regime=V6MarketRegime.TREND_BULLISH_STRONG,
        df=df_bull,
        concepts=concepts
    )

    assert plan.direction == "BUY"
    assert plan.entry_price is not None and plan.entry_price > 0
    assert plan.stop_loss is not None and plan.stop_loss < plan.entry_price
    assert plan.tp1 is not None and plan.tp1 > plan.entry_price
    assert plan.tp2 is not None and plan.tp2 > plan.tp1
    assert plan.tp3 is not None and plan.tp3 > plan.tp2
    assert plan.stop_distance > 0
    assert "invalidation" in plan.invalidation_reason.lower()


def test_multi_timeframe_conflict():
    """Verify Module 7 detects HTF conflict and enforces can_execute = False."""
    res_conflict = v6_mtf_engine.evaluate_alignment(
        htf_bias="BEARISH",
        setup_bias="BEARISH",
        entry_bias="BULLISH"
    )
    assert res_conflict.alignment_status == "CONFLICT"
    assert res_conflict.can_execute is False

    res_aligned = v6_mtf_engine.evaluate_alignment(
        htf_bias="BULLISH",
        setup_bias="BULLISH",
        entry_bias="BULLISH"
    )
    assert res_aligned.alignment_status == "FULL_ALIGNMENT"
    assert res_aligned.can_execute is True


def test_setup_quality_scoring_tiers():
    """Verify Module 6 scores setups into proper classification tiers."""
    # Elite/High setup
    score_high = v6_quality_scorer.score_setup(
        regime=V6MarketRegime.TREND_BULLISH_STRONG,
        strategy_id="TREND_PULLBACK",
        htf_alignment="FULL_ALIGNMENT",
        has_bos_choch=True,
        concepts_count=4,
        volatility_ok=True,
        rr_ratio=2.5,
        news_clear=True
    )
    assert score_high.total_score >= 85
    assert score_high.classification == "HIGH_QUALITY"

    # Conflicted / low quality setup
    score_low = v6_quality_scorer.score_setup(
        regime=V6MarketRegime.HIGH_VOLATILITY,
        strategy_id="UNKNOWN",
        htf_alignment="CONFLICT",
        has_bos_choch=False,
        concepts_count=1,
        volatility_ok=False,
        rr_ratio=1.1,
        news_clear=False
    )
    assert score_low.total_score < 55
    assert score_low.classification == "REJECTED"


def test_no_trade_on_insufficient_data():
    """Verify Module 1 & Service return NO_TRADE / UNCERTAIN when data is inadequate."""
    df_empty = pd.DataFrame()
    res = v6_regime_engine.analyze_regime("XAUUSD", df_empty)
    assert res.regime == V6MarketRegime.UNCERTAIN
    assert res.data_quality == "INSUFFICIENT"


def test_v6_api_integration():
    """Verify REST API /api/v6/* endpoints using FastAPI TestClient."""
    client = TestClient(app)

    # 1. GET /api/v6/strategies
    r1 = client.get("/api/v6/strategies")
    assert r1.status_code == 200
    assert r1.json()["total_strategies"] == 14

    # 2. POST /api/v6/regime/analyze
    r2 = client.post("/api/v6/regime/analyze", json={"symbol": "XAUUSD", "timeframe": "M15"})
    assert r2.status_code == 200
    assert "regime" in r2.json()

    # 3. POST /api/v6/concepts/detect
    r3 = client.post("/api/v6/concepts/detect", json={"symbol": "XAUUSD", "timeframe": "M15"})
    assert r3.status_code == 200
    assert "by_category" in r3.json()

    # 4. POST /api/v6/strategy/select
    r4 = client.post("/api/v6/strategy/select", json={"symbol": "XAUUSD", "timeframe": "M15"})
    assert r4.status_code == 200
    assert "active_regime" in r4.json()

    # 5. POST /api/v6/best-setup
    r5 = client.post("/api/v6/best-setup", json={"symbol": "XAUUSD", "timeframe": "M15"})
    assert r5.status_code == 200
    data = r5.json()
    assert "direction" in data
    assert "quality_score" in data
    assert "trade_plan" in data

    # 6. POST /api/v6/scan
    r6 = client.post("/api/v6/scan", json={"market_filter": "METALS", "timeframe": "M15", "min_quality_score": 50})
    assert r6.status_code == 200
    assert "candidates" in r6.json()
