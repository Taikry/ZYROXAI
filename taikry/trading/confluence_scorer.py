"""
ZYROX AI V3.1 — TRANSPARENT 100-POINT CONFLUENCE SCORING ENGINE
===============================================================
Asset Focus: XAUUSD (Gold vs US Dollar)
Timeframe: M15 Primary Analysis Cycle
Minimum Actionable Score: 75 / 100

Mathematical Confluence Model (8 Categories = 100 Total Points):
1. Trend Alignment:                   15 Points
2. Multi-Timeframe Confirmation:       15 Points
3. Market Structure:                   15 Points
4. Liquidity & ICT/SMC Confirmation:   15 Points
5. Momentum & Technical Indicators:    10 Points
6. Volume & Volatility Conditions:     10 Points
7. News & Fundamental Macro Context:   10 Points
8. Risk/Reward & Execution Quality:    10 Points
------------------------------------------------
TOTAL:                                100 Points

Decision Classification Rules:
* 0 - 49:   WEAK -> WAIT
* 50 - 64:  DEVELOPING -> WAIT
* 65 - 74:  POTENTIAL -> WAIT (Awaiting Confirmation)
* 75 - 84:  STRONG CONFLUENCE -> Eligible for BUY/SELL if all validation gates pass
* 85 - 100: VERY HIGH CONFLUENCE -> Eligible for BUY/SELL if all validation gates pass

Missing Data Rule:
If any required input is unavailable, it is marked 'UNKNOWN' and awarded 0 points.
No artificial renormalization or inflation of missing evidence is permitted.
"""

import math
from typing import Dict, Any, List, Optional, Tuple


MINIMUM_ACTIONABLE_SCORE = 75
DEFAULT_MIN_RISK_REWARD = 1.1


class ConfluenceScoreResult:
    """Structured container for the 100-point Confluence Scoring output."""

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        buy_score: int,
        sell_score: int,
        status: str,
        direction: str,
        selected_score: int,
        grade: str,
        category_breakdown: Dict[str, Any],
        supporting_reasons: List[str],
        contradicting_reasons: List[str],
        missing_confirmations: List[str],
        validation_gates: Dict[str, bool],
        is_actionable: bool,
    ):
        self.symbol = symbol
        self.timeframe = timeframe
        self.buy_score = buy_score
        self.sell_score = sell_score
        self.status = status
        self.direction = direction
        self.selected_score = selected_score
        self.grade = grade
        self.category_breakdown = category_breakdown
        self.supporting_reasons = supporting_reasons
        self.contradicting_reasons = contradicting_reasons
        self.missing_confirmations = missing_confirmations
        self.validation_gates = validation_gates
        self.is_actionable = is_actionable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "status": self.status,
            "direction": self.direction,
            "buy_score": self.buy_score,
            "sell_score": self.sell_score,
            "selected_score": self.selected_score,
            "grade": self.grade,
            "is_actionable": self.is_actionable,
            "category_breakdown": self.category_breakdown,
            "supporting_reasons": self.supporting_reasons,
            "contradicting_reasons": self.contradicting_reasons,
            "missing_confirmations": self.missing_confirmations,
            "validation_gates": self.validation_gates,
        }


def calculate_confluence_scores(
    symbol: str = "XAUUSD",
    timeframe: str = "M15",
    market_data: Optional[Dict[str, Any]] = None,
    technical_data: Optional[Dict[str, Any]] = None,
    ict_smc_data: Optional[Dict[str, Any]] = None,
    macro_news_data: Optional[Dict[str, Any]] = None,
    orderflow_data: Optional[Dict[str, Any]] = None,
    risk_validation: Optional[Dict[str, Any]] = None,
    active_position_context: Optional[Dict[str, Any]] = None,
    min_score_threshold: int = MINIMUM_ACTIONABLE_SCORE,
    min_rr_threshold: float = DEFAULT_MIN_RISK_REWARD,
) -> ConfluenceScoreResult:
    """
    Evaluates independent BUY and SELL confluence scores out of 100 based on verified data.
    """
    market_data = market_data or {}
    technical_data = technical_data or {}
    ict_smc_data = ict_smc_data or {}
    macro_news_data = macro_news_data or {}
    orderflow_data = orderflow_data or {}
    risk_validation = risk_validation or {}

    buy_pts = {
        "trend_alignment": 0,
        "mtf_confirmation": 0,
        "market_structure": 0,
        "liquidity_ict_smc": 0,
        "momentum_indicators": 0,
        "volume_volatility": 0,
        "news_macro_context": 0,
        "risk_reward_execution": 0,
    }
    sell_pts = {
        "trend_alignment": 0,
        "mtf_confirmation": 0,
        "market_structure": 0,
        "liquidity_ict_smc": 0,
        "momentum_indicators": 0,
        "volume_volatility": 0,
        "news_macro_context": 0,
        "risk_reward_execution": 0,
    }

    buy_support = []
    sell_support = []
    contradictions = []
    missing = []

    # Extract helper sub-dicts for flexible adapter ingestion
    tech_ctx = technical_data.get("technical_context") if isinstance(technical_data.get("technical_context"), dict) else {}
    kpz = ict_smc_data.get("key_price_zones") if isinstance(ict_smc_data.get("key_price_zones"), dict) else {}
    macro_risk = macro_news_data.get("macro_risk") if isinstance(macro_news_data.get("macro_risk"), dict) else {}
    of_metrics = orderflow_data.get("orderflow_metrics") if isinstance(orderflow_data.get("orderflow_metrics"), dict) else {}

    # -------------------------------------------------------------------------
    # 1. Trend Alignment (Max: 15 Points)
    # -------------------------------------------------------------------------
    ema20 = technical_data.get("ema_20") or tech_ctx.get("ema_20")
    ema50 = technical_data.get("ema_50") or tech_ctx.get("ema_50")
    ema200 = technical_data.get("ema_200") or tech_ctx.get("ema_200")
    current_price = market_data.get("price") or technical_data.get("current_price") or tech_ctx.get("current_price")

    if current_price and ema20 and ema50:
        try:
            p = float(current_price)
            e20 = float(ema20)
            e50 = float(ema50)
            if p > e20 > e50:
                buy_pts["trend_alignment"] += 8
                buy_support.append(f"M15 EMA Fast Stack is Bullish (Price {p:.2f} > EMA20 {e20:.2f} > EMA50 {e50:.2f})")
            elif p < e20 < e50:
                sell_pts["trend_alignment"] += 8
                sell_support.append(f"M15 EMA Fast Stack is Bearish (Price {p:.2f} < EMA20 {e20:.2f} < EMA50 {e50:.2f})")
            else:
                contradictions.append("M15 EMA Fast Stack is compressed or crossing (transitional trend)")
        except (TypeError, ValueError):
            missing.append("M15 EMA 20/50 parsing failed")
    elif tech_ctx.get("price_above_ema20") and tech_ctx.get("ema20_above_ema50"):
        buy_pts["trend_alignment"] += 8
        buy_support.append("M15 EMA Fast Stack is confirmed Bullish by Technical Analyst")
    elif tech_ctx.get("price_below_ema20") and tech_ctx.get("ema20_below_ema50"):
        sell_pts["trend_alignment"] += 8
        sell_support.append("M15 EMA Fast Stack is confirmed Bearish by Technical Analyst")
    else:
        missing.append("M15 EMA 20/50 data unavailable")

    if current_price and ema200:
        try:
            p = float(current_price)
            e200 = float(ema200)
            if p > e200:
                buy_pts["trend_alignment"] += 7
                buy_support.append(f"Price is above Institutional Baseline EMA200 ({e200:.2f})")
            else:
                sell_pts["trend_alignment"] += 7
                sell_support.append(f"Price is below Institutional Baseline EMA200 ({e200:.2f})")
        except (TypeError, ValueError):
            missing.append("EMA 200 parsing failed")
    elif tech_ctx.get("price_above_ema200") is True:
        buy_pts["trend_alignment"] += 7
        buy_support.append("Price is confirmed above Institutional Baseline EMA200")
    elif tech_ctx.get("price_below_ema200") is True:
        sell_pts["trend_alignment"] += 7
        sell_support.append("Price is confirmed below Institutional Baseline EMA200")
    else:
        missing.append("EMA 200 baseline unavailable")

    # -------------------------------------------------------------------------
    # 2. Multi-Timeframe Confirmation (Max: 15 Points)
    # -------------------------------------------------------------------------
    mtf = technical_data.get("multi_timeframe_alignment") or tech_ctx.get("multi_timeframe_alignment") or {}
    h4_trend = str(mtf.get("H4", "")).upper()
    h1_trend = str(mtf.get("H1", "")).upper()
    m5_trend = str(mtf.get("M5", "")).upper()

    if h4_trend:
        if "BULL" in h4_trend:
            buy_pts["mtf_confirmation"] += 6
            buy_support.append("H4 Macro Trend is Bullish")
        elif "BEAR" in h4_trend:
            sell_pts["mtf_confirmation"] += 6
            sell_support.append("H4 Macro Trend is Bearish")
    else:
        missing.append("H4 Trend alignment unavailable")

    if h1_trend:
        if "BULL" in h1_trend:
            buy_pts["mtf_confirmation"] += 5
            buy_support.append("H1 Intermediate Trend is Bullish")
        elif "BEAR" in h1_trend:
            sell_pts["mtf_confirmation"] += 5
            sell_support.append("H1 Intermediate Trend is Bearish")
    else:
        missing.append("H1 Trend alignment unavailable")

    if m5_trend:
        if "BULL" in m5_trend:
            buy_pts["mtf_confirmation"] += 4
            buy_support.append("M5 Intraday Scalp Flow is Bullish")
        elif "BEAR" in m5_trend:
            sell_pts["mtf_confirmation"] += 4
            sell_support.append("M5 Intraday Scalp Flow is Bearish")
    else:
        missing.append("M5 Scalp Flow unavailable")

    # -------------------------------------------------------------------------
    # 3. Market Structure (Max: 15 Points)
    # -------------------------------------------------------------------------
    structure = technical_data.get("market_structure") or tech_ctx.get("market_structure") or ict_smc_data.get("market_structure") or ""
    structure_str = str(structure).upper()

    if "BULLISH" in structure_str or "UPTREND" in structure_str or tech_ctx.get("higher_highs") is True:
        buy_pts["market_structure"] += 8
        buy_support.append("M15 Swing Structure confirmed Higher Highs & Higher Lows")
    elif "BEARISH" in structure_str or "DOWNTREND" in structure_str or tech_ctx.get("lower_lows") is True:
        sell_pts["market_structure"] += 8
        sell_support.append("M15 Swing Structure confirmed Lower Highs & Lower Lows")
    elif "CHOPPY" in structure_str or "RANGING" in structure_str:
        contradictions.append("Market Structure is Choppy / Consolidating without clean directional expansion")
    else:
        missing.append("Market Structure sequence unavailable")

    bos_choch = ict_smc_data.get("structure_break") or technical_data.get("entry_trigger") or tech_ctx.get("entry_trigger") or ""
    bc_str = str(bos_choch).upper()
    if any(k in bc_str for k in ["BOS_BULL", "CHOCH_BULL", "BULLISH_BREAK", "MSS_BULL"]) or tech_ctx.get("break_of_structure") is True:
        buy_pts["market_structure"] += 7
        buy_support.append("Confirmed Bullish BOS / CHoCH displacement on M15")
    elif any(k in bc_str for k in ["BOS_BEAR", "CHOCH_BEAR", "BEARISH_BREAK", "MSS_BEAR"]):
        sell_pts["market_structure"] += 7
        sell_support.append("Confirmed Bearish BOS / CHoCH displacement on M15")

    # -------------------------------------------------------------------------
    # 4. Liquidity & ICT/SMC Confirmation (Max: 15 Points)
    # -------------------------------------------------------------------------
    smc_zone = str(kpz.get("current_zone") or ict_smc_data.get("current_zone") or ict_smc_data.get("smc_zone") or "").upper()
    if smc_zone == "DISCOUNT":
        buy_pts["liquidity_ict_smc"] += 5
        buy_support.append("Price is in Institutional DISCOUNT Zone (<50% dealing range)")
    elif smc_zone == "PREMIUM":
        sell_pts["liquidity_ict_smc"] += 5
        sell_support.append("Price is in Institutional PREMIUM Zone (>50% dealing range)")
    elif smc_zone == "EQUILIBRIUM":
        contradictions.append("Price is rotating around 50% Equilibrium (fair value balance)")

    # Order blocks & Breaker blocks
    obs = kpz.get("recent_order_blocks") or ict_smc_data.get("recent_order_blocks") or []
    breakers = kpz.get("breaker_blocks") or ict_smc_data.get("breaker_blocks") or []
    if any(ob.get("type") in ("BULLISH_ORDER_BLOCK", "BULLISH_OB") for ob in obs if isinstance(ob, dict)):
        buy_pts["liquidity_ict_smc"] += 5
        buy_support.append("Holding qualified Bullish Order Block support")
    elif any(b.get("type") in ("BULLISH_BREAKER", "BULLISH_BREAKER_BLOCK") for b in breakers if isinstance(b, dict)):
        buy_pts["liquidity_ict_smc"] += 5
        buy_support.append("Supported by Bullish Breaker Block flip")

    if any(ob.get("type") in ("BEARISH_ORDER_BLOCK", "BEARISH_OB") for ob in obs if isinstance(ob, dict)):
        sell_pts["liquidity_ict_smc"] += 5
        sell_support.append("Testing qualified Bearish Order Block supply")
    elif any(b.get("type") in ("BEARISH_BREAKER", "BEARISH_BREAKER_BLOCK") for b in breakers if isinstance(b, dict)):
        sell_pts["liquidity_ict_smc"] += 5
        sell_support.append("Retesting Bearish Breaker Resistance")

    # Fair Value Gaps & Sweeps
    fvgs = kpz.get("unmitigated_fvgs") or ict_smc_data.get("unmitigated_fvgs") or []
    sweeps = kpz.get("recent_liquidity_sweeps") or ict_smc_data.get("recent_liquidity_sweeps") or []
    has_bull_fvg = any(f.get("type") in ("BULLISH_FVG", "BULLISH_FAIR_VALUE_GAP") and not f.get("mitigated") for f in fvgs if isinstance(f, dict))
    has_bear_fvg = any(f.get("type") in ("BEARISH_FVG", "BEARISH_FAIR_VALUE_GAP") and not f.get("mitigated") for f in fvgs if isinstance(f, dict))
    has_bull_sweep = any("SELL_SIDE" in str(sw.get("type", "")).upper() for sw in sweeps if isinstance(sw, dict))
    has_bear_sweep = any("BUY_SIDE" in str(sw.get("type", "")).upper() for sw in sweeps if isinstance(sw, dict))

    if has_bull_fvg or has_bull_sweep:
        buy_pts["liquidity_ict_smc"] += 5
        buy_support.append("Confluent with Unmitigated Bullish FVG or Sell-Side Liquidity Sweep")
    if has_bear_fvg or has_bear_sweep:
        sell_pts["liquidity_ict_smc"] += 5
        sell_support.append("Confluent with Unmitigated Bearish FVG or Buy-Side Liquidity Sweep")

    # -------------------------------------------------------------------------
    # 5. Momentum & Technical Indicators (Max: 10 Points)
    # -------------------------------------------------------------------------
    rsi_val = technical_data.get("rsi") or technical_data.get("rsi_14") or tech_ctx.get("rsi_14") or tech_ctx.get("rsi")
    if rsi_val is not None:
        try:
            r = float(rsi_val)
            if 50.0 <= r <= 68.0:
                buy_pts["momentum_indicators"] += 5
                buy_support.append(f"RSI(14) at {r:.1f} shows clean bullish expansion without exhaustion")
            elif 32.0 <= r <= 50.0:
                sell_pts["momentum_indicators"] += 5
                sell_support.append(f"RSI(14) at {r:.1f} shows healthy bearish momentum without oversold trap")
            elif r > 70.0:
                contradictions.append(f"RSI(14) at {r:.1f} is Overbought (exhaustion risk)")
            elif r < 30.0:
                contradictions.append(f"RSI(14) at {r:.1f} is Oversold (mean-reversion risk)")
        except (TypeError, ValueError):
            missing.append("RSI parsing failed")
    else:
        missing.append("RSI(14) indicator unavailable")

    macd_data = technical_data.get("macd") or tech_ctx.get("macd") or {}
    macd_hist = macd_data.get("histogram") if isinstance(macd_data, dict) else (technical_data.get("macd_histogram") or tech_ctx.get("macd_histogram"))
    if macd_hist is not None:
        try:
            mh = float(macd_hist)
            if mh > 0:
                buy_pts["momentum_indicators"] += 5
                buy_support.append(f"MACD Histogram is positive (+{mh:.2f}) confirming upward momentum")
            elif mh < 0:
                sell_pts["momentum_indicators"] += 5
                sell_support.append(f"MACD Histogram is negative ({mh:.2f}) confirming downward momentum")
        except (TypeError, ValueError):
            missing.append("MACD histogram parsing failed")
    else:
        missing.append("MACD histogram unavailable")

    # -------------------------------------------------------------------------
    # 6. Volume & Volatility Conditions (Max: 10 Points)
    # -------------------------------------------------------------------------
    cvd_bias = str(of_metrics.get("cvd_trend") or orderflow_data.get("bias", "")).upper()
    if "BULL" in cvd_bias:
        buy_pts["volume_volatility"] += 5
        buy_support.append("Order Flow & Cumulative Delta (CVD) indicate institutional accumulation")
    elif "BEAR" in cvd_bias:
        sell_pts["volume_volatility"] += 5
        sell_support.append("Order Flow & Cumulative Delta (CVD) confirm institutional distribution")
    else:
        missing.append("Order flow / CVD depth unavailable (using standard tick activity)")

    atr_val = technical_data.get("atr") or technical_data.get("atr_14") or tech_ctx.get("atr_14") or tech_ctx.get("atr")
    if atr_val is not None:
        try:
            a = float(atr_val)
            if a > 0.5:
                # Normal healthy volatility for Gold
                buy_pts["volume_volatility"] += 5
                sell_pts["volume_volatility"] += 5
                buy_support.append(f"ATR(14) at ${a:.2f} confirms active, tradeable market volatility")
            else:
                contradictions.append("ATR volatility is abnormally suppressed (illiquid session)")
        except (TypeError, ValueError):
            missing.append("ATR parsing failed")
    else:
        missing.append("ATR volatility unavailable")

    # -------------------------------------------------------------------------
    # 7. News & Fundamental Macro Context (Max: 10 Points)
    # -------------------------------------------------------------------------
    dxy_trend = str(macro_risk.get("dxy_trend") or macro_news_data.get("dxy_trend") or macro_news_data.get("usd_bias") or "").upper()
    if "BEARISH" in dxy_trend or "DOWN" in dxy_trend:
        buy_pts["news_macro_context"] += 6
        buy_support.append("US Dollar Index (DXY) is Weak/Bearish — Favorable macro tailwind for Gold")
    elif "BULLISH" in dxy_trend or "UP" in dxy_trend:
        sell_pts["news_macro_context"] += 6
        sell_support.append("US Dollar Index (DXY) is Strong/Bullish — Downward macro pressure on Gold")
    else:
        missing.append("DXY macro trend unavailable")

    blackout = str(macro_risk.get("blackout_status") or macro_news_data.get("blackout_status") or "").upper()
    has_macro_input = bool(macro_news_data or macro_risk)
    if blackout == "BLACKOUT_ACTIVE" or macro_risk.get("blackout_window_active") is True:
        contradictions.append("Red-Folder High Impact News Catalyst imminently active (Blackout Window)")
    elif has_macro_input and (blackout in ("CLEAR", "NO_BLACKOUT") or macro_risk.get("blackout_window_active") is False):
        buy_pts["news_macro_context"] += 4
        sell_pts["news_macro_context"] += 4
        buy_support.append("Macro calendar clear of immediate blackout risk")
    else:
        missing.append("Macro news calendar status unavailable")

    # -------------------------------------------------------------------------
    # 8. Risk/Reward Viability & Execution Quality (Max: 10 Points)
    # -------------------------------------------------------------------------
    rr_ratio = risk_validation.get("risk_reward_ratio") or risk_validation.get("calculated_rr")
    rr_num = 0.0
    if rr_ratio:
        try:
            if isinstance(rr_ratio, str) and ":" in rr_ratio:
                rr_num = float(rr_ratio.split(":")[-1])
            else:
                rr_num = float(rr_ratio)
        except (TypeError, ValueError):
            rr_num = 0.0

    if rr_num >= float(min_rr_threshold):
        buy_pts["risk_reward_execution"] += 6
        sell_pts["risk_reward_execution"] += 6
        buy_support.append(f"Reward-to-Risk ratio 1:{rr_num:.2f} satisfies institutional floor (>= 1:{min_rr_threshold:.1f})")
    else:
        missing.append("Risk/Reward validation incomplete")

    # Spread cost friction
    spread = market_data.get("spread") or technical_data.get("spread")
    if spread is not None:
        try:
            sp = float(spread)
            if sp <= 0.40:
                buy_pts["risk_reward_execution"] += 4
                sell_pts["risk_reward_execution"] += 4
                buy_support.append(f"Execution spread of ${sp:.2f}/oz is within tight institutional limits")
            else:
                contradictions.append(f"Spread is wide (${sp:.2f}/oz) — Elevated execution friction")
        except (TypeError, ValueError):
            missing.append("Spread audit parsing failed")
    else:
        missing.append("Execution spread audit unavailable")

    # -------------------------------------------------------------------------
    # TOTAL CONFLUENCE SUMMATION
    # -------------------------------------------------------------------------
    total_buy = sum(buy_pts.values())
    total_sell = sum(sell_pts.values())

    # Ensure bounds [0, 100]
    total_buy = max(0, min(100, total_buy))
    total_sell = max(0, min(100, total_sell))

    # Evaluate Direction Selection & Conflict Detection
    direction = "NONE"
    selected_score = 0
    if total_buy > total_sell and total_buy >= min_score_threshold:
        direction = "BUY"
        selected_score = total_buy
    elif total_sell > total_buy and total_sell >= min_score_threshold:
        direction = "SELL"
        selected_score = total_sell
    else:
        direction = "NONE"
        selected_score = max(total_buy, total_sell)

    # Deadlock / Directional Conflict Rule
    if total_buy >= 70 and total_sell >= 70:
        direction = "NONE"
        contradictions.append("Directional Conflict: Both BUY and SELL exhibit simultaneous strong scores (Ambiguous Market)")

    # Grade determination
    if selected_score >= 85:
        grade = "VERY HIGH CONFLUENCE"
    elif selected_score >= 75:
        grade = "STRONG CONFLUENCE"
    elif selected_score >= 65:
        grade = "POTENTIAL (Awaiting Confirmation)"
    elif selected_score >= 50:
        grade = "DEVELOPING"
    else:
        grade = "WEAK"

    # Mandatory Validation Gates
    feed_fresh = (
        market_data.get("price_freshness") == "LIVE_FRESH"
        or market_data.get("fresh") is True
        or market_data.get("is_fresh") is True
    )
    spread_ok = (market_data.get("spread") or 0.25) <= 0.50
    rr_viable = rr_num >= float(min_rr_threshold)
    no_conflict = not (total_buy >= 70 and total_sell >= 70)
    score_qualified = selected_score >= min_score_threshold and direction in ("BUY", "SELL")

    gates = {
        "min_score_passed": score_qualified,
        "data_freshness_valid": feed_fresh,
        "spread_friction_passed": spread_ok,
        "risk_reward_valid": rr_viable,
        "directional_clarity_passed": no_conflict,
    }

    is_actionable = all(gates.values())

    # Primary Decision Determination
    # HOLD is strictly reserved for when a real position exists
    if active_position_context and active_position_context.get("has_active_position"):
        status = "HOLD"
    elif is_actionable:
        status = direction  # "BUY" or "SELL"
    else:
        status = "WAIT"

    category_breakdown = {
        "BUY": buy_pts,
        "SELL": sell_pts,
        "max_weights": {
            "trend_alignment": 15,
            "mtf_confirmation": 15,
            "market_structure": 15,
            "liquidity_ict_smc": 15,
            "momentum_indicators": 10,
            "volume_volatility": 10,
            "news_macro_context": 10,
            "risk_reward_execution": 10,
            "total": 100,
        },
    }

    supporting = buy_support if direction == "BUY" else (sell_support if direction == "SELL" else (buy_support[:2] + sell_support[:2]))

    return ConfluenceScoreResult(
        symbol=symbol,
        timeframe=timeframe,
        buy_score=total_buy,
        sell_score=total_sell,
        status=status,
        direction=direction,
        selected_score=selected_score,
        grade=grade,
        category_breakdown=category_breakdown,
        supporting_reasons=supporting,
        contradicting_reasons=contradictions,
        missing_confirmations=missing,
        validation_gates=gates,
        is_actionable=is_actionable,
    )
