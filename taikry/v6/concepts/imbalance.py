"""
ZYROX AI V6 — Category C: Imbalance & Fair Value Gap Detector
============================================================
Detects:
- Fair Value Gaps (Bullish & Bearish FVG, unmitigated / mitigated status)
- Inversion Fair Value Gaps (IFVG Support/Resistance flips)
- Balanced Price Ranges (BPR overlapping gaps)
- Price Gaps & Volume Imbalances
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.ict_smc import detect_fair_value_gaps, detect_inversion_fair_value_gaps


class ImbalanceDetector(BaseConceptDetector):
    """Category C: Imbalance & Fair Value Gap Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.IMBALANCE

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 6:
            return results

        curr_p = float(df["close"].iloc[-1])

        # 1. Standard 3-candle Fair Value Gaps (FVG)
        fvgs = detect_fair_value_gaps(df, lookback=30)
        unmitigated_fvgs = [f for f in fvgs if not f.get("mitigated")]

        # Look for most recent unmitigated bullish & bearish gaps
        bull_fvgs = [f for f in unmitigated_fvgs if f.get("type") == "BULLISH_FVG"]
        bear_fvgs = [f for f in unmitigated_fvgs if f.get("type") == "BEARISH_FVG"]

        if bull_fvgs:
            recent_bull = bull_fvgs[-1]
            top = recent_bull["top"]
            bot = recent_bull["bottom"]
            is_testing = bot <= curr_p <= top
            results.append(ConceptDetectionResult(
                concept_id="imb_bullish_fvg",
                name="Bullish Fair Value Gap (FVG)",
                category=self.category,
                detected=True,
                confidence=86 if is_testing else 78,
                bias="BULLISH",
                timeframe=timeframe,
                levels={"top": top, "bottom": bot, "midpoint": (top + bot) / 2.0, "is_testing": is_testing},
                evidence=[
                    f"Unmitigated Bullish Imbalance [{bot:.4f} - {top:.4f}].",
                    f"Status: {'Active retest / mitigation fill underway' if is_testing else 'Resting institutional demand zone'}."
                ],
                chart_overlay={"type": "fvg_box", "top": top, "bottom": bot, "bias": "BULLISH"}
            ))

        if bear_fvgs:
            recent_bear = bear_fvgs[-1]
            top = recent_bear["top"]
            bot = recent_bear["bottom"]
            is_testing = bot <= curr_p <= top
            results.append(ConceptDetectionResult(
                concept_id="imb_bearish_fvg",
                name="Bearish Fair Value Gap (FVG)",
                category=self.category,
                detected=True,
                confidence=86 if is_testing else 78,
                bias="BEARISH",
                timeframe=timeframe,
                levels={"top": top, "bottom": bot, "midpoint": (top + bot) / 2.0, "is_testing": is_testing},
                evidence=[
                    f"Unmitigated Bearish Imbalance [{bot:.4f} - {top:.4f}].",
                    f"Status: {'Active retest / mitigation fill underway' if is_testing else 'Resting institutional supply zone'}."
                ],
                chart_overlay={"type": "fvg_box", "top": top, "bottom": bot, "bias": "BEARISH"}
            ))

        # 2. Inversion Fair Value Gaps (IFVG) & Balanced Price Ranges (BPR)
        ifvgs_data = detect_inversion_fair_value_gaps(df, lookback=min(40, len(df)))
        inversion_list = ifvgs_data.get("inversion_fvgs", [])
        bpr_list = ifvgs_data.get("balanced_price_ranges", [])

        for ifvg in inversion_list[-2:]:
            is_bull = ifvg.get("type") == "BULLISH_INVERSION_FVG"
            results.append(ConceptDetectionResult(
                concept_id="imb_ifvg_" + ("bullish" if is_bull else "bearish"),
                name=f"{'Bullish' if is_bull else 'Bearish'} Inversion FVG (IFVG)",
                category=self.category,
                detected=True,
                confidence=85,
                bias="BULLISH" if is_bull else "BEARISH",
                timeframe=timeframe,
                levels={"top": ifvg.get("top"), "bottom": ifvg.get("bottom")},
                evidence=[ifvg.get("description_en", f"Imbalance flipped to institutional {ifvg.get('role')}.")],
                chart_overlay={"type": "ifvg_box", "top": ifvg.get("top"), "bottom": ifvg.get("bottom"), "bias": "BULLISH" if is_bull else "BEARISH"}
            ))

        for bpr in bpr_list[-1:]:
            results.append(ConceptDetectionResult(
                concept_id="imb_bpr",
                name="Balanced Price Range (BPR)",
                category=self.category,
                detected=True,
                confidence=84,
                bias="NEUTRAL_MAGNET",
                timeframe=timeframe,
                levels={"top": bpr.get("top"), "bottom": bpr.get("bottom")},
                evidence=[bpr.get("description_en", "Overlapping imbalances acting as high-speed fair value magnet.")],
                chart_overlay={"type": "bpr_box", "top": bpr.get("top"), "bottom": bpr.get("bottom")}
            ))

        # 3. Bar-to-Bar Gap (Weekend / session opening price gap)
        if len(df) >= 2:
            prev_close = float(df["close"].iloc[-2])
            curr_open = float(df["open"].iloc[-1])
            gap_points = abs(curr_open - prev_close)
            if gap_points > (curr_p * 0.0015):  # > 0.15% gap
                gap_dir = "GAP_UP" if curr_open > prev_close else "GAP_DOWN"
                results.append(ConceptDetectionResult(
                    concept_id="imb_opening_gap",
                    name=f"Price Opening Gap ({gap_dir})",
                    category=self.category,
                    detected=True,
                    confidence=80,
                    bias="BULLISH" if gap_dir == "GAP_UP" else "BEARISH",
                    timeframe=timeframe,
                    levels={"gap_high": max(prev_close, curr_open), "gap_low": min(prev_close, curr_open)},
                    evidence=[f"Unfilled session price gap between {min(prev_close, curr_open):.4f} and {max(prev_close, curr_open):.4f}."],
                    chart_overlay={"type": "gap_box", "high": max(prev_close, curr_open), "low": min(prev_close, curr_open)}
                ))

        return results

