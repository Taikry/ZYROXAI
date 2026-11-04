"""
ZYROX AI V6 — Module 4: Formal Strategy Registry
================================================
Defines 14 institutional strategies with complete execution contracts:
- Strategy ID & Name
- Supported Market Regimes
- Supported Symbols & Timeframes
- Required Concepts
- Entry Rules
- Stop Loss Rules (Invalidation-based)
- Take Profit Rules (Multi-target structure)
- Invalidation Rules
- Minimum Risk/Reward Thresholds
- Required Confirmations
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from taikry.v6.models import V6MarketRegime


class StrategyDefinition(BaseModel):
    """Complete specification of an institutional trading strategy."""
    strategy_id: str
    name: str
    description: str
    supported_regimes: List[V6MarketRegime]
    supported_symbols: List[str] = Field(default_factory=lambda: ["ALL"])
    supported_timeframes: List[str] = Field(default_factory=lambda: ["M5", "M15", "H1", "H4", "D1"])
    required_concepts: List[str]
    entry_rules: List[str]
    stop_loss_rules: List[str]
    take_profit_rules: List[str]
    invalidation_rules: List[str]
    min_risk_reward: float = 1.5
    required_confirmations: List[str]


STRATEGY_REGISTRY: Dict[str, StrategyDefinition] = {
    # 1. TREND PULLBACK
    "TREND_PULLBACK": StrategyDefinition(
        strategy_id="TREND_PULLBACK",
        name="Institutional Trend Pullback",
        description="Enters shallow retracements into dynamic EMA 20/50 support or Fair Value Gaps in strong persistent trends.",
        supported_regimes=[
            V6MarketRegime.TREND_BULLISH_STRONG,
            V6MarketRegime.TREND_BULLISH_WEAK,
            V6MarketRegime.TREND_BEARISH_STRONG,
            V6MarketRegime.TREND_BEARISH_WEAK,
        ],
        required_concepts=["trend_ema_bullish_alignment", "trend_ema_bearish_alignment", "struct_bullish_hh_hl", "struct_bearish_lh_ll", "imb_bullish_fvg", "imb_bearish_fvg"],
        entry_rules=[
            "Wait for price to retrace into dynamic EMA 20 or unmitigated FVG zone.",
            "Verify lower-timeframe rejection candle (Pin Bar or Engulfing) before triggering entry."
        ],
        stop_loss_rules=[
            "Place Stop Loss strictly behind the pullback swing extreme or FVG invalidation boundary plus 1 ATR buffer."
        ],
        take_profit_rules=[
            "TP1: Nearest swing high/low liquidity.",
            "TP2: Previous major daily/weekly structure extreme.",
            "TP3: Fibonacci 1.618 trend extension target."
        ],
        invalidation_rules=[
            "Candle closes beyond structural Higher Low (for longs) or Lower High (for shorts)."
        ],
        min_risk_reward=1.8,
        required_confirmations=["EMA stack alignment", "HTF trend agreement", "Rejection candle"]
    ),

    # 2. STRUCTURE CONTINUATION
    "STRUCTURE_CONTINUATION": StrategyDefinition(
        strategy_id="STRUCTURE_CONTINUATION",
        name="Market Structure Break & Continuation",
        description="Capitalizes on clean Break of Structure (BOS) with displacement, targeting the next external liquidity pool.",
        supported_regimes=[
            V6MarketRegime.TREND_BULLISH_STRONG,
            V6MarketRegime.TREND_BEARISH_STRONG,
            V6MarketRegime.BREAKOUT
        ],
        required_concepts=["struct_bos", "struct_mss_bullish", "struct_mss_bearish"],
        entry_rules=[
            "Confirm candle close beyond key swing extreme.",
            "Enter on subsequent retest of the broken structural level."
        ],
        stop_loss_rules=[
            "Place Stop Loss below/above the origin candle of the displacement breakout."
        ],
        take_profit_rules=[
            "TP1: 1.5x risk distance.",
            "TP2: Next major HTF swing liquidity pool.",
            "TP3: Dealing range extension."
        ],
        invalidation_rules=[
            "Price immediately falls back inside previous swing structure, indicating a false break trap."
        ],
        min_risk_reward=2.0,
        required_confirmations=["Confirmed BOS candle close", "Volume expansion"]
    ),

    # 3. BREAKOUT RETEST
    "BREAKOUT_RETEST": StrategyDefinition(
        strategy_id="BREAKOUT_RETEST",
        name="Breakout Retest & Value Acceptance",
        description="Enters retests of broken key horizontal boundaries or session extremes once accepted by smart money.",
        supported_regimes=[
            V6MarketRegime.BREAKOUT,
            V6MarketRegime.TREND_BULLISH_STRONG,
            V6MarketRegime.TREND_BEARISH_STRONG
        ],
        required_concepts=["pa_breakout_continuation", "sr_benchmark_levels", "of_breaker_bullish", "of_breaker_bearish"],
        entry_rules=[
            "Allow initial breakout to complete without FOMO chase.",
            "Enter Limit order at the retest boundary of the broken level."
        ],
        stop_loss_rules=[
            "Place Stop Loss safely beyond the retest rejection wick."
        ],
        take_profit_rules=[
            "TP1: Breakout impulse high/low.",
            "TP2: Next benchmark resistance/support level.",
            "TP3: 2.5x initial risk."
        ],
        invalidation_rules=[
            "Candle closes back inside original channel by more than 1 ATR."
        ],
        min_risk_reward=1.8,
        required_confirmations=["Retest hold without violation", "Volume confirmation"]
    ),

    # 4. EMA PULLBACK
    "EMA_PULLBACK": StrategyDefinition(
        strategy_id="EMA_PULLBACK",
        name="Dynamic EMA Trend Ride",
        description="Trades systematic pullbacks into EMA 20 with EMA 50 acting as maximum structural boundary.",
        supported_regimes=[
            V6MarketRegime.TREND_BULLISH_STRONG,
            V6MarketRegime.TREND_BEARISH_STRONG
        ],
        required_concepts=["trend_ema_pullback_long", "trend_ema_pullback_short", "trend_ema_bullish_alignment", "trend_ema_bearish_alignment"],
        entry_rules=["Enter when price touches dynamic EMA 20 with confirming wick rejection."],
        stop_loss_rules=["Place Stop Loss beyond EMA 50 dynamic line."],
        take_profit_rules=[
            "TP1: Previous swing high/low.",
            "TP2: Trailing along EMA 20 until close below."
        ],
        invalidation_rules=["Candle body closes beyond EMA 50."],
        min_risk_reward=1.5,
        required_confirmations=["EMA slope > 0.05%", "No opposing higher timeframe divergence"]
    ),

    # 5. RANGE SUPPORT RESISTANCE
    "RANGE_SUPPORT_RESISTANCE": StrategyDefinition(
        strategy_id="RANGE_SUPPORT_RESISTANCE",
        name="Horizontal Range Rotation (POC Mean Reversion)",
        description="Fades extremes of sideways consolidation ranges back toward the Point of Control (POC) equilibrium.",
        supported_regimes=[
            V6MarketRegime.RANGE,
            V6MarketRegime.LOW_VOLATILITY
        ],
        required_concepts=["sr_premium_discount_equilibrium", "vol_compression_squeeze", "pa_doji", "mom_exhaustion_overbought", "mom_exhaustion_oversold"],
        entry_rules=[
            "Buy at Value Area Low (VAL) or range support after rejection wick.",
            "Sell at Value Area High (VAH) or range resistance after rejection wick."
        ],
        stop_loss_rules=["Place Stop Loss 0.5 ATR beyond range high/low."],
        take_profit_rules=[
            "TP1: Range Equilibrium (50% midpoint / POC).",
            "TP2: Opposite range boundary."
        ],
        invalidation_rules=["Strong breakout candle closes completely outside range boundaries."],
        min_risk_reward=1.5,
        required_confirmations=["Rejection wick at boundary", "Stochastic or RSI overbought/oversold"]
    ),

    # 6. LIQUIDITY SWEEP REVERSAL
    "LIQUIDITY_SWEEP_REVERSAL": StrategyDefinition(
        strategy_id="LIQUIDITY_SWEEP_REVERSAL",
        name="Liquidity Sweep & Turtle Soup Reversal",
        description="Captures violent reversals immediately after smart money triggers retail stop orders beyond key highs or lows.",
        supported_regimes=[
            V6MarketRegime.RANGE,
            V6MarketRegime.REVERSAL_TRANSITION,
            V6MarketRegime.HIGH_VOLATILITY
        ],
        required_concepts=["liq_sweep_bsl", "liq_sweep_ssl", "liq_stophunt_bearish", "liq_stophunt_bullish", "pa_false_breakout_high", "pa_false_breakout_low"],
        entry_rules=[
            "Confirm that price spiked beyond prior swing high/low and closed back inside.",
            "Enter immediately on the close of the sweep candle."
        ],
        stop_loss_rules=["Place Stop Loss beyond the absolute wick tip of the liquidity sweep."],
        take_profit_rules=[
            "TP1: Dealing range 50% equilibrium.",
            "TP2: Opposite resting liquidity pool (BSL or SSL)."
        ],
        invalidation_rules=["New candle breaks the sweep extreme."],
        min_risk_reward=2.0,
        required_confirmations=["Clear wick rejection", "Close back inside range"]
    ),

    # 7. FALSE BREAKOUT
    "FALSE_BREAKOUT": StrategyDefinition(
        strategy_id="FALSE_BREAKOUT",
        name="False Breakout Trap (Spring & Upthrust)",
        description="Exploits failed breakouts piercing key 20-bar Donchian or session levels without follow-through.",
        supported_regimes=[
            V6MarketRegime.RANGE,
            V6MarketRegime.REVERSAL_TRANSITION
        ],
        required_concepts=["pa_false_breakout_high", "pa_false_breakout_low"],
        entry_rules=["Enter in opposite direction upon candle closing back inside the range."],
        stop_loss_rules=["Place Stop Loss beyond false breakout spike high/low."],
        take_profit_rules=["TP1: Range POC.", "TP2: Opposite side of consolidation."],
        invalidation_rules=["Price pushes back out and closes beyond fakeout high."],
        min_risk_reward=1.8,
        required_confirmations=["Failed close outside boundary", "Volume divergence"]
    ),

    # 8. BREAKOUT CONFIRMATION
    "BREAKOUT_CONFIRMATION": StrategyDefinition(
        strategy_id="BREAKOUT_CONFIRMATION",
        name="Explosive Momentum Breakout Confirmation",
        description="Trades aggressive trend inception when price bursts out of tight compression with expanding volatility.",
        supported_regimes=[
            V6MarketRegime.BREAKOUT
        ],
        required_concepts=["vol_expansion_active", "pa_breakout_continuation", "struct_bos"],
        entry_rules=["Enter Market order upon confirmed candle close outside 20-bar Donchian channel."],
        stop_loss_rules=["Place Stop Loss behind previous candle midpoint or dynamic EMA 20."],
        take_profit_rules=[
            "TP1: 2.0x risk.",
            "TP2: 3.5x risk or until momentum divergence."
        ],
        invalidation_rules=["Reversal candle closes back below breakout boundary."],
        min_risk_reward=2.0,
        required_confirmations=["ADX rising > 25", "BB Width expanding"]
    ),

    # 9. VOLATILITY EXPANSION
    "VOLATILITY_EXPANSION": StrategyDefinition(
        strategy_id="VOLATILITY_EXPANSION",
        name="Post-Compression Expansion Wave",
        description="Rides the explosive wave emerging directly from low-volatility squeeze contractions.",
        supported_regimes=[
            V6MarketRegime.BREAKOUT,
            V6MarketRegime.LOW_VOLATILITY
        ],
        required_concepts=["vol_compression_squeeze", "vol_expansion_active"],
        entry_rules=["Enter on breakout candle from tight Bollinger squeeze."],
        stop_loss_rules=["Opposite Bollinger Band boundary."],
        take_profit_rules=["TP1: 2x ATR span.", "TP2: 4x ATR span."],
        invalidation_rules=["Immediate mean reversion back into squeeze center."],
        min_risk_reward=2.0,
        required_confirmations=["Bandwidth expansion > 0.8%"]
    ),

    # 10. CHOCH REVERSAL
    "CHOCH_REVERSAL": StrategyDefinition(
        strategy_id="CHOCH_REVERSAL",
        name="Institutional Change of Character Reversal",
        description="Trades early trend shifts signaled by structural Change of Character against tired trends.",
        supported_regimes=[
            V6MarketRegime.REVERSAL_TRANSITION
        ],
        required_concepts=["struct_choch", "of_breaker_bullish", "of_breaker_bearish", "imb_ifvg_bullish", "imb_ifvg_bearish"],
        entry_rules=[
            "Wait for CHoCH confirmation candle close.",
            "Enter Limit order on the first pullback into the newly created Breaker or IFVG."
        ],
        stop_loss_rules=["Beyond the origin swing extreme preceding the CHoCH."],
        take_profit_rules=[
            "TP1: Previous major swing high/low.",
            "TP2: Unmitigated HTF order block."
        ],
        invalidation_rules=["Price violates origin swing level."],
        min_risk_reward=2.2,
        required_confirmations=["Confirmed CHoCH close", "Breaker or FVG confluence"]
    ),

    # 11. MOMENTUM DIVERGENCE
    "MOMENTUM_DIVERGENCE": StrategyDefinition(
        strategy_id="MOMENTUM_DIVERGENCE",
        name="Multi-Oscillator Momentum Divergence",
        description="Counter-trend reversal setup triggered when price prints a new extreme unsupported by RSI/MACD momentum.",
        supported_regimes=[
            V6MarketRegime.REVERSAL_TRANSITION,
            V6MarketRegime.RANGE
        ],
        required_concepts=["mom_regular_bullish_divergence", "mom_regular_bearish_divergence", "mom_exhaustion_overbought", "mom_exhaustion_oversold"],
        entry_rules=["Enter upon candlestick reversal confirmation following divergence signal."],
        stop_loss_rules=["Beyond divergence price extreme plus 1 ATR."],
        take_profit_rules=["TP1: EMA 20 dynamic mean.", "TP2: EMA 50 trend anchor."],
        invalidation_rules=["New high/low closes strongly in direction of old trend."],
        min_risk_reward=1.8,
        required_confirmations=["Clear divergence angle", "Reversal candlestick pattern"]
    ),

    # 12. VOLATILITY ADJUSTED SETUP
    "VOLATILITY_ADJUSTED_SETUP": StrategyDefinition(
        strategy_id="VOLATILITY_ADJUSTED_SETUP",
        name="High-Volatility Wide Boundary Setup",
        description="Operates during elevated volatility regimes by widening technical invalidation and reducing position sizing.",
        supported_regimes=[
            V6MarketRegime.HIGH_VOLATILITY
        ],
        required_concepts=["vol_expansion_active", "vol_atr_baseline"],
        entry_rules=["Enter only at confirmed structural extremes with reduced lot sizing."],
        stop_loss_rules=["Wider SL based on 2.0x ATR distance to prevent premature whip."],
        take_profit_rules=["TP1: 2.0x risk.", "TP2: 3.5x risk."],
        invalidation_rules=["Violation of wider ATR invalidation boundary."],
        min_risk_reward=2.0,
        required_confirmations=["Reduced risk sizing applied", "No imminent high-impact news"]
    ),

    # 13. COMPRESSION BREAKOUT
    "COMPRESSION_BREAKOUT": StrategyDefinition(
        strategy_id="COMPRESSION_BREAKOUT",
        name="Compression Squeeze Inception",
        description="Positions for high-velocity breakout out of ultra-low volatility coils.",
        supported_regimes=[
            V6MarketRegime.LOW_VOLATILITY
        ],
        required_concepts=["vol_compression_squeeze", "pa_inside_bar"],
        entry_rules=["Place stop orders beyond compression highs and lows or enter on initial close outside."],
        stop_loss_rules=["Midpoint of compression band."],
        take_profit_rules=["TP1: 2x ATR.", "TP2: 4x ATR."],
        invalidation_rules=["Whipsaw back into center of band."],
        min_risk_reward=2.0,
        required_confirmations=["BB width < 0.35%"]
    ),

    # 14. NEWS WAIT
    "NEWS_WAIT": StrategyDefinition(
        strategy_id="NEWS_WAIT",
        name="Macroeconomic Event Risk Capital Protection",
        description="Enforces zero-exposure stand down during high-impact news events to preserve trader capital.",
        supported_regimes=[
            V6MarketRegime.NEWS_VOLATILITY,
            V6MarketRegime.UNCERTAIN
        ],
        required_concepts=[],
        entry_rules=["DO NOT ENTER. Await post-news volatility settlement."],
        stop_loss_rules=["N/A - Protection Active."],
        take_profit_rules=["N/A - Protection Active."],
        invalidation_rules=["Event blackout window elapsed."],
        min_risk_reward=1.0,
        required_confirmations=["Post-news spread normalization"]
    ),
}

