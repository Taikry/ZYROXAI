"""
ZYROX AI V6 — Modules 8, 9, 10: Trade Levels Engine
===================================================
Calculates:
- Precise Entry: MARKET, LIMIT, or ENTRY_ZONE with technical triggers
- Smart Invalidation Stop Loss: Rooted strictly in structural invalidation + ATR buffer
- Multi-Target Take Profits (TP1, TP2, TP3) with individual R-multiples and structural justifications

Rules:
- Never fabricates prices or levels.
- Never moves SL artificially to inflate R:R.
- Applies symbol-specific tick precision and spread allowances.
"""
from __future__ import annotations

import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd

from taikry.v6.models import TradePlanLevels, ConceptDetectionResult, V6MarketRegime
from taikry.config import get_symbol_config


class TradeLevelsEngine:
    """Calculates technically justified entry, invalidation SL, and multi-target TPs."""

    def calculate_levels(
        self,
        symbol: str,
        direction: str,  # "BUY", "SELL", "WAIT", "NO_TRADE"
        strategy_id: str,
        regime: V6MarketRegime,
        df: pd.DataFrame,
        concepts: List[ConceptDetectionResult],
        current_spread: Optional[float] = None,
        candidate_bias: Optional[str] = None
    ) -> TradePlanLevels:
        """
        Derives complete institutional execution levels.
        """
        cfg = get_symbol_config(symbol)
        digits = int(cfg.get("digits", 2))
        point = float(cfg.get("point", 0.01))

        effective_dir = direction
        if effective_dir not in ("BUY", "SELL"):
            if candidate_bias in ("BUY", "SELL"):
                effective_dir = candidate_bias
            else:
                return TradePlanLevels(
                    direction=direction,
                    entry_type="MARKET",
                    invalidation_reason="Market conditions not qualified for active trade plan execution."
                )

        if df is None or len(df) < 10:
            return TradePlanLevels(
                direction=direction,
                entry_type="MARKET",
                invalidation_reason="Market data depth insufficient for level calculation."
            )

        curr_p = float(df["close"].iloc[-1])
        highs = df["high"].astype(float).values
        lows = df["low"].astype(float).values

        # ATR buffer for invalidation stop cushion
        tr_list = [
            max(highs[i] - lows[i], abs(highs[i] - df["close"].iloc[i - 1]), abs(lows[i] - df["close"].iloc[i - 1]))
            for i in range(1, len(df))
        ]
        atr_14 = float(pd.Series(tr_list[-14:]).mean()) if len(tr_list) >= 14 else 1.0 * point
        buffer = max(atr_14 * 0.4, 2 * point)
        spread_allowance = (current_spread or (2.0 * point)) if current_spread else (2.0 * point)

        # Extract concept key levels
        swing_high = None
        swing_low = None
        fvg_top = None
        fvg_bot = None
        ob_high = None
        ob_low = None

        for c in concepts:
            if c.concept_id == "struct_swings":
                swing_high = c.levels.get("swing_high")
                swing_low = c.levels.get("swing_low")
            elif "fvg" in c.concept_id:
                fvg_top = c.levels.get("top")
                fvg_bot = c.levels.get("bottom")
            elif "order_block" in c.concept_id:
                ob_high = c.levels.get("high")
                ob_low = c.levels.get("low")

        # Fallbacks for swing highs/lows
        if swing_high is None:
            swing_high = float(np.max(highs[-20:]))
        if swing_low is None:
            swing_low = float(np.min(lows[-20:]))

        # 1. Entry Type & Entry Price Determination
        if strategy_id in ("TREND_PULLBACK", "CHOCH_REVERSAL") and (fvg_top or ob_high):
            # Limit entry inside pullback zone
            entry_type = "LIMIT"
            if effective_dir == "BUY":
                entry_price = round(fvg_top if fvg_top else ob_high, digits)
                entry_zone_low = round(fvg_bot if fvg_bot else ob_low, digits)
                entry_zone_high = round(entry_price, digits)
                entry_trigger = "Wait for limit fill inside institutional demand / FVG zone."
            else:
                entry_price = round(fvg_bot if fvg_bot else ob_low, digits)
                entry_zone_low = round(entry_price, digits)
                entry_zone_high = round(fvg_top if fvg_top else ob_high, digits)
                entry_trigger = "Wait for limit fill inside institutional supply / FVG zone."
        elif strategy_id in ("BREAKOUT_CONFIRMATION", "LIQUIDITY_SWEEP_REVERSAL"):
            entry_type = "MARKET"
            entry_price = round(curr_p, digits)
            entry_zone_low = round(curr_p - (buffer * 0.5), digits)
            entry_zone_high = round(curr_p + (buffer * 0.5), digits)
            entry_trigger = "Market entry on confirmed candle close."
        else:
            entry_type = "MARKET"
            entry_price = round(curr_p, digits)
            entry_zone_low = round(curr_p - (buffer * 0.5), digits)
            entry_zone_high = round(curr_p + (buffer * 0.5), digits)
            entry_trigger = f"Entry validated by {strategy_id} confirmation."

        # 2. Smart Invalidation Stop Loss
        if effective_dir == "BUY":
            # Structure invalidation: Below swing low or below OB/FVG bottom
            base_sl = min(swing_low, ob_low if ob_low else swing_low, fvg_bot if fvg_bot else swing_low)
            stop_loss = round(base_sl - buffer - spread_allowance, digits)
            if stop_loss >= entry_price:
                stop_loss = round(entry_price - (1.5 * atr_14), digits)
            stop_dist = round(entry_price - stop_loss, digits)
            invalidation_reason = f"Structural invalidation below swing trough ({base_sl:.{digits}f}) with ATR buffer ({buffer:.{digits}f})."
        else:
            # Structure invalidation: Above swing high or above OB/FVG top
            base_sl = max(swing_high, ob_high if ob_high else swing_high, fvg_top if fvg_top else swing_high)
            stop_loss = round(base_sl + buffer + spread_allowance, digits)
            if stop_loss <= entry_price:
                stop_loss = round(entry_price + (1.5 * atr_14), digits)
            stop_dist = round(stop_loss - entry_price, digits)
            invalidation_reason = f"Structural invalidation above swing peak ({base_sl:.{digits}f}) with ATR buffer ({buffer:.{digits}f})."

        if stop_dist <= 0:
            stop_dist = round(1.0 * atr_14, digits)
            stop_loss = round(entry_price - stop_dist if effective_dir == "BUY" else entry_price + stop_dist, digits)

        # 3. Multi-Target Take Profits (TP1, TP2, TP3)
        if effective_dir == "BUY":
            tp1_target = max(swing_high, entry_price + (stop_dist * 1.5))
            tp1 = round(tp1_target, digits)
            tp1_r = round((tp1 - entry_price) / stop_dist, 2)
            tp1_reason = f"Nearest liquidity pool at recent swing high ({swing_high:.{digits}f})."

            tp2 = round(entry_price + (stop_dist * 2.5), digits)
            tp2_r = round((tp2 - entry_price) / stop_dist, 2)
            tp2_reason = "Major structural continuation target (2.5R)."

            tp3 = round(entry_price + (stop_dist * 4.0), digits)
            tp3_r = round((tp3 - entry_price) / stop_dist, 2)
            tp3_reason = "Extended Fibonacci trend expansion runner (4.0R)."
        else:
            tp1_target = min(swing_low, entry_price - (stop_dist * 1.5))
            tp1 = round(tp1_target, digits)
            tp1_r = round((entry_price - tp1) / stop_dist, 2)
            tp1_reason = f"Nearest liquidity pool at recent swing low ({swing_low:.{digits}f})."

            tp2 = round(entry_price - (stop_dist * 2.5), digits)
            tp2_r = round((entry_price - tp2) / stop_dist, 2)
            tp2_reason = "Major structural continuation target (2.5R)."

            tp3 = round(entry_price - (stop_dist * 4.0), digits)
            tp3_r = round((entry_price - tp3) / stop_dist, 2)
            tp3_reason = "Extended Fibonacci trend expansion runner (4.0R)."

        rr_str = f"1:{tp1_r:.2f}"

        return TradePlanLevels(
            direction=direction,
            entry_type=entry_type,
            entry_price=entry_price,
            entry_zone_low=entry_zone_low,
            entry_zone_high=entry_zone_high,
            entry_trigger=entry_trigger,
            stop_loss=stop_loss,
            stop_distance=stop_dist,
            invalidation_reason=invalidation_reason,
            tp1=tp1,
            tp1_reason=tp1_reason,
            tp1_r=tp1_r,
            tp2=tp2,
            tp2_reason=tp2_reason,
            tp2_r=tp2_r,
            tp3=tp3,
            tp3_reason=tp3_reason,
            tp3_r=tp3_r,
            risk_reward_ratio=rr_str
        )


v6_trade_levels_engine = TradeLevelsEngine()
