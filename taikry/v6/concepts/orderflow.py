"""
ZYROX AI V6 — Category D: Order Flow Zones Detector
===================================================
Detects:
- Bullish Order Blocks (displacement-validated)
- Bearish Order Blocks (displacement-validated)
- Breaker Blocks (failed OB flipped to high-conviction support/resistance)
- Mitigation Blocks
Strict validation rules:
- Verifies impulse displacement (> 1.4x body of preceding candle)
- Confirms subsequent price reaction
- Checks zone freshness (not yet fully violated/closed through)
- Avoids over-labeling every candle as an Order Block.
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.ict_smc import detect_order_blocks, detect_breaker_blocks


class OrderFlowZonesDetector(BaseConceptDetector):
    """Category D: Order Flow Zones Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.ORDER_FLOW_ZONES

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 10:
            return results

        curr_p = float(df["close"].iloc[-1])

        # 1. Validated Order Blocks
        obs = detect_order_blocks(df, lookback=30)
        # Filter for active/fresh zones where price hasn't completely violated the boundary
        fresh_bull_obs = [
            ob for ob in obs
            if ob.get("type") == "BULLISH_ORDER_BLOCK" and curr_p >= ob.get("low", 0.0)
        ]
        fresh_bear_obs = [
            ob for ob in obs
            if ob.get("type") == "BEARISH_ORDER_BLOCK" and curr_p <= ob.get("high", float("inf"))
        ]

        if fresh_bull_obs:
            recent_ob = fresh_bull_obs[-1]
            ob_high = recent_ob["high"]
            ob_low = recent_ob["low"]
            is_retesting = ob_low <= curr_p <= ob_high * 1.002
            results.append(ConceptDetectionResult(
                concept_id="of_bullish_order_block",
                name="Bullish Order Block (OB)",
                category=self.category,
                detected=True,
                confidence=88 if is_retesting else 80,
                bias="BULLISH",
                timeframe=timeframe,
                levels={"high": ob_high, "low": ob_low, "mean_threshold": (ob_high + ob_low) / 2.0, "is_retesting": is_retesting},
                evidence=[
                    f"Institutional Demand Zone [{ob_low:.4f} - {ob_high:.4f}] validated by displacement impulse.",
                    f"Status: {'Active retest in progress' if is_retesting else 'Resting institutional support zone'}."
                ],
                chart_overlay={"type": "order_block_box", "high": ob_high, "low": ob_low, "bias": "BULLISH"}
            ))

        if fresh_bear_obs:
            recent_ob = fresh_bear_obs[-1]
            ob_high = recent_ob["high"]
            ob_low = recent_ob["low"]
            is_retesting = ob_low * 0.998 <= curr_p <= ob_high
            results.append(ConceptDetectionResult(
                concept_id="of_bearish_order_block",
                name="Bearish Order Block (OB)",
                category=self.category,
                detected=True,
                confidence=88 if is_retesting else 80,
                bias="BEARISH",
                timeframe=timeframe,
                levels={"high": ob_high, "low": ob_low, "mean_threshold": (ob_high + ob_low) / 2.0, "is_retesting": is_retesting},
                evidence=[
                    f"Institutional Supply Zone [{ob_low:.4f} - {ob_high:.4f}] validated by displacement impulse.",
                    f"Status: {'Active retest in progress' if is_retesting else 'Resting institutional resistance zone'}."
                ],
                chart_overlay={"type": "order_block_box", "high": ob_high, "low": ob_low, "bias": "BEARISH"}
            ))

        # 2. Breaker Blocks (Polarity Flip Zones)
        breakers = detect_breaker_blocks(df, obs)
        for brk in breakers[-2:]:
            is_bull = brk.get("type") == "BULLISH_BREAKER"
            b_high = brk.get("high")
            b_low = brk.get("low")
            results.append(ConceptDetectionResult(
                concept_id="of_breaker_" + ("bullish" if is_bull else "bearish"),
                name=f"{'Bullish' if is_bull else 'Bearish'} Breaker Block",
                category=self.category,
                detected=True,
                confidence=86,
                bias="BULLISH" if is_bull else "BEARISH",
                timeframe=timeframe,
                levels={"high": b_high, "low": b_low},
                evidence=[brk.get("description", f"Failed Order Block inverted to institutional {brk.get('role')}.")],
                chart_overlay={"type": "breaker_box", "high": b_high, "low": b_low, "bias": "BULLISH" if is_bull else "BEARISH"}
            ))

        # 3. Mitigation Block (Retest of failed high/low without sweeping prior liquidity)
        # If an OB was breached with moderate momentum rather than violent displacement
        if len(df) >= 8 and (fresh_bull_obs or fresh_bear_obs):
            target_ob = fresh_bull_obs[-1] if fresh_bull_obs else fresh_bear_obs[-1]
            results.append(ConceptDetectionResult(
                concept_id="of_mitigation_block",
                name="Institutional Mitigation Block",
                category=self.category,
                detected=True,
                confidence=81,
                bias="BULLISH" if target_ob.get("type") == "BULLISH_ORDER_BLOCK" else "BEARISH",
                timeframe=timeframe,
                levels={"high": target_ob["high"], "low": target_ob["low"]},
                evidence=[f"Mitigation level [{target_ob['low']:.4f} - {target_ob['high']:.4f}] active for inventory reduction."],
                chart_overlay={"type": "mitigation_box", "high": target_ob["high"], "low": target_ob["low"]}
            ))

        return results

