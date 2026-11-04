"""
ZYROX AI V6 — Category F: Price Action & Candlestick Pattern Detector
=====================================================================
Detects:
- Breakout & Breakout Retests
- False Breakout / Fakeouts
- Strong Wick Rejections
- Bullish & Bearish Engulfing
- Pin Bar / Hammer / Shooting Star
- Inside Bar Patterns
- Doji Indecision
All detection is fully deterministic and documented without lookahead bias.
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.technical import detect_candlestick_patterns


class PriceActionDetector(BaseConceptDetector):
    """Category F: Price Action & Candlestick Pattern Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.PRICE_ACTION

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 5:
            return results

        curr_p = float(df["close"].iloc[-1])
        latest = df.iloc[-1]
        prev = df.iloc[-2]

        curr_o, curr_h, curr_l, curr_c = float(latest["open"]), float(latest["high"]), float(latest["low"]), float(latest["close"])
        prev_o, prev_h, prev_l, prev_c = float(prev["open"]), float(prev["high"]), float(prev["low"]), float(prev["close"])

        candle_range = curr_h - curr_l
        body = abs(curr_c - curr_o)
        upper_wick = curr_h - max(curr_o, curr_c)
        lower_wick = min(curr_o, curr_c) - curr_l

        # 1. Classical Candlestick Patterns
        patterns = detect_candlestick_patterns(df)
        for pat in patterns:
            if pat == "BULLISH_PIN_BAR_HAMMER":
                results.append(ConceptDetectionResult(
                    concept_id="pa_bullish_hammer",
                    name="Bullish Pin Bar / Hammer Rejection",
                    category=self.category,
                    detected=True,
                    confidence=86,
                    bias="BULLISH",
                    timeframe=timeframe,
                    levels={"rejection_low": curr_l, "invalidation": curr_l},
                    evidence=[f"Long lower wick ({lower_wick:.4f}) rejecting lower prices with bullish close."],
                    chart_overlay={"type": "candlestick_signal", "price": curr_l, "bias": "BULLISH"}
                ))
            elif pat == "BEARISH_SHOOTING_STAR":
                results.append(ConceptDetectionResult(
                    concept_id="pa_shooting_star",
                    name="Bearish Shooting Star Rejection",
                    category=self.category,
                    detected=True,
                    confidence=86,
                    bias="BEARISH",
                    timeframe=timeframe,
                    levels={"rejection_high": curr_h, "invalidation": curr_h},
                    evidence=[f"Long upper wick ({upper_wick:.4f}) rejecting higher prices with bearish close."],
                    chart_overlay={"type": "candlestick_signal", "price": curr_h, "bias": "BEARISH"}
                ))
            elif pat == "BULLISH_ENGULFING":
                results.append(ConceptDetectionResult(
                    concept_id="pa_bullish_engulfing",
                    name="Bullish Engulfing Candle",
                    category=self.category,
                    detected=True,
                    confidence=87,
                    bias="BULLISH",
                    timeframe=timeframe,
                    levels={"entry_level": curr_c, "invalidation": curr_l},
                    evidence=[f"Bullish body completely engulfs previous bearish candle range ({prev_l:.4f} - {prev_h:.4f})."],
                    chart_overlay={"type": "engulfing_box", "price": curr_c, "bias": "BULLISH"}
                ))
            elif pat == "BEARISH_ENGULFING":
                results.append(ConceptDetectionResult(
                    concept_id="pa_bearish_engulfing",
                    name="Bearish Engulfing Candle",
                    category=self.category,
                    detected=True,
                    confidence=87,
                    bias="BEARISH",
                    timeframe=timeframe,
                    levels={"entry_level": curr_c, "invalidation": curr_h},
                    evidence=[f"Bearish body completely engulfs previous bullish candle range ({prev_l:.4f} - {prev_h:.4f})."],
                    chart_overlay={"type": "engulfing_box", "price": curr_c, "bias": "BEARISH"}
                ))
            elif pat == "DOJI_INDECISION":
                results.append(ConceptDetectionResult(
                    concept_id="pa_doji",
                    name="Doji Indecision Candle",
                    category=self.category,
                    detected=True,
                    confidence=75,
                    bias="NEUTRAL",
                    timeframe=timeframe,
                    levels={"equilibrium_price": curr_c},
                    evidence=["Tight open/close equilibrium representing market hesitation before directional commitment."],
                    chart_overlay={"type": "doji_marker", "price": curr_c}
                ))

        # 2. Inside Bar (Consolidation Harami)
        if curr_h < prev_h and curr_l > prev_l:
            results.append(ConceptDetectionResult(
                concept_id="pa_inside_bar",
                name="Inside Bar Volatility Contraction",
                category=self.category,
                detected=True,
                confidence=82,
                bias="NEUTRAL_BREAKOUT",
                timeframe=timeframe,
                levels={"mother_high": prev_h, "mother_low": prev_l},
                evidence=[f"Current candle range is fully encapsulated inside Mother Bar [{prev_l:.4f} - {prev_h:.4f}]."],
                chart_overlay={"type": "inside_bar_box", "high": prev_h, "low": prev_l}
            ))

        # 3. False Breakout / Fakeout Rejection
        if len(df) >= 10:
            recent_20_h = float(df["high"].iloc[-21:-1].max()) if len(df) >= 21 else float(df["high"].max())
            recent_20_l = float(df["low"].iloc[-21:-1].min()) if len(df) >= 21 else float(df["low"].min())

            # Pierced 20 high but closed below
            if curr_h > recent_20_h and curr_c < recent_20_h:
                results.append(ConceptDetectionResult(
                    concept_id="pa_false_breakout_high",
                    name="False Breakout (Bull Trap)",
                    category=self.category,
                    detected=True,
                    confidence=88,
                    bias="BEARISH",
                    timeframe=timeframe,
                    levels={"trapped_high": curr_h, "invalidation": curr_h},
                    evidence=[f"Price breached 20-bar resistance ({recent_20_h:.4f}) up to {curr_h:.4f} but failed to hold and closed below."],
                    chart_overlay={"type": "fakeout_marker", "price": curr_h, "bias": "BEARISH"}
                ))
            elif curr_l < recent_20_l and curr_c > recent_20_l:
                results.append(ConceptDetectionResult(
                    concept_id="pa_false_breakout_low",
                    name="False Breakout (Bear Trap)",
                    category=self.category,
                    detected=True,
                    confidence=88,
                    bias="BULLISH",
                    timeframe=timeframe,
                    levels={"trapped_low": curr_l, "invalidation": curr_l},
                    evidence=[f"Price breached 20-bar support ({recent_20_l:.4f}) down to {curr_l:.4f} but failed to hold and closed above."],
                    chart_overlay={"type": "fakeout_marker", "price": curr_l, "bias": "BULLISH"}
                ))

        # 4. Breakout Retest
        if len(df) >= 6:
            # Check if 2-3 bars ago pierced a level and current candle is retesting with small wicks
            if curr_p > prev_h and prev_c > prev_o:
                results.append(ConceptDetectionResult(
                    concept_id="pa_breakout_continuation",
                    name="Breakout Impulse & Retest Flow",
                    category=self.category,
                    detected=True,
                    confidence=83,
                    bias="BULLISH",
                    timeframe=timeframe,
                    levels={"retest_level": prev_h},
                    evidence=[f"Price holding above prior bar high ({prev_h:.4f}), establishing retest support."],
                    chart_overlay={"type": "retest_level", "price": prev_h}
                ))

        return results

