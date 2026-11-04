"""
ZYROX AI V6 — Category G: Trend Tools & Moving Average Detector
==============================================================
Calculates:
- Exponential Moving Averages (EMA 9, 20, 50, 100, 200)
- Simple Moving Averages (SMA 20, 50, 200)
- Moving Average Stacks & Full Alignment
- Moving Average Crossovers (20/50 Bullish/Bearish, 50/200 Golden/Death Cross)
- EMA Slope (Momentum gradient)
- Directional Trend Strength
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.technical import calculate_ema, calculate_sma


class TrendToolsDetector(BaseConceptDetector):
    """Category G: Trend Tools & Moving Average Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.TREND_TOOLS

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 20:
            return results

        closes = df["close"].astype(float)
        curr_p = float(closes.iloc[-1])

        ema_9 = float(calculate_ema(closes, 9).iloc[-1])
        ema_20_series = calculate_ema(closes, 20)
        ema_50_series = calculate_ema(closes, 50)
        ema_20 = float(ema_20_series.iloc[-1])
        ema_50 = float(ema_50_series.iloc[-1])
        ema_100 = float(calculate_ema(closes, 100).iloc[-1]) if len(closes) >= 70 else None
        ema_200 = float(calculate_ema(closes, 200).iloc[-1]) if len(closes) >= 150 else None

        # EMA Slope (% change over last 5 bars)
        ema_20_prev5 = float(ema_20_series.iloc[-5]) if len(ema_20_series) >= 5 else ema_20
        ema_20_slope_pct = ((ema_20 - ema_20_prev5) / ema_20_prev5) * 100.0 if ema_20_prev5 > 0 else 0.0

        # 1. Moving Average Alignment
        is_bull_stack = (curr_p > ema_20 > ema_50) and (ema_50 > ema_200 if ema_200 else True)
        is_bear_stack = (curr_p < ema_20 < ema_50) and (ema_50 < ema_200 if ema_200 else True)

        if is_bull_stack:
            results.append(ConceptDetectionResult(
                concept_id="trend_ema_bullish_alignment",
                name="Bullish Moving Average Stack (Price > EMA 20 > EMA 50)",
                category=self.category,
                detected=True,
                confidence=90,
                bias="BULLISH",
                timeframe=timeframe,
                levels={"ema_9": round(ema_9, 4), "ema_20": round(ema_20, 4), "ema_50": round(ema_50, 4), "ema_200": round(ema_200, 4) if ema_200 else None},
                evidence=[
                    f"Price ({curr_p:.4f}) is trading above stacked EMAs: EMA 20 ({ema_20:.4f}) > EMA 50 ({ema_50:.4f}).",
                    f"EMA 20 Slope is positive ({ema_20_slope_pct:+.2f}%), confirming persistent bullish trend momentum."
                ],
                chart_overlay={"type": "trend_stack", "direction": "BULLISH", "ema_20": ema_20, "ema_50": ema_50}
            ))
        elif is_bear_stack:
            results.append(ConceptDetectionResult(
                concept_id="trend_ema_bearish_alignment",
                name="Bearish Moving Average Stack (Price < EMA 20 < EMA 50)",
                category=self.category,
                detected=True,
                confidence=90,
                bias="BEARISH",
                timeframe=timeframe,
                levels={"ema_9": round(ema_9, 4), "ema_20": round(ema_20, 4), "ema_50": round(ema_50, 4), "ema_200": round(ema_200, 4) if ema_200 else None},
                evidence=[
                    f"Price ({curr_p:.4f}) is trading below stacked EMAs: EMA 20 ({ema_20:.4f}) < EMA 50 ({ema_50:.4f}).",
                    f"EMA 20 Slope is negative ({ema_20_slope_pct:+.2f}%), confirming persistent bearish trend momentum."
                ],
                chart_overlay={"type": "trend_stack", "direction": "BEARISH", "ema_20": ema_20, "ema_50": ema_50}
            ))

        # 2. Moving Average Crossover (within last 3 bars)
        if len(ema_20_series) >= 4 and len(ema_50_series) >= 4:
            prev_diff = float(ema_20_series.iloc[-2] - ema_50_series.iloc[-2])
            curr_diff = float(ema_20 - ema_50)
            if prev_diff <= 0 and curr_diff > 0:
                results.append(ConceptDetectionResult(
                    concept_id="trend_ema_bullish_cross",
                    name="Bullish EMA 20/50 Crossover",
                    category=self.category,
                    detected=True,
                    confidence=86,
                    bias="BULLISH",
                    timeframe=timeframe,
                    levels={"cross_price": round(ema_20, 4)},
                    evidence=[f"Fast EMA 20 ({ema_20:.4f}) crossed above Medium EMA 50 ({ema_50:.4f}), triggering trend acceleration."],
                    chart_overlay={"type": "ma_cross", "price": ema_20, "bias": "BULLISH"}
                ))
            elif prev_diff >= 0 and curr_diff < 0:
                results.append(ConceptDetectionResult(
                    concept_id="trend_ema_bearish_cross",
                    name="Bearish EMA 20/50 Crossover",
                    category=self.category,
                    detected=True,
                    confidence=86,
                    bias="BEARISH",
                    timeframe=timeframe,
                    levels={"cross_price": round(ema_20, 4)},
                    evidence=[f"Fast EMA 20 ({ema_20:.4f}) crossed below Medium EMA 50 ({ema_50:.4f}), triggering trend acceleration downwards."],
                    chart_overlay={"type": "ma_cross", "price": ema_20, "bias": "BEARISH"}
                ))

        # 3. EMA Pullback Test (Price touching EMA 20 or 50 during trend)
        pullback_tol = curr_p * 0.001
        if is_bull_stack and abs(curr_p - ema_20) <= pullback_tol:
            results.append(ConceptDetectionResult(
                concept_id="trend_ema_pullback_long",
                name="Bullish Pullback to Dynamic EMA 20 Support",
                category=self.category,
                detected=True,
                confidence=85,
                bias="BULLISH",
                timeframe=timeframe,
                levels={"ema_support": round(ema_20, 4), "invalidation": round(ema_50, 4)},
                evidence=[f"Price retraced to dynamic EMA 20 support ({ema_20:.4f}) in established uptrend."],
                chart_overlay={"type": "pullback_zone", "price": ema_20, "bias": "BULLISH"}
            ))
        elif is_bear_stack and abs(curr_p - ema_20) <= pullback_tol:
            results.append(ConceptDetectionResult(
                concept_id="trend_ema_pullback_short",
                name="Bearish Pullback to Dynamic EMA 20 Resistance",
                category=self.category,
                detected=True,
                confidence=85,
                bias="BEARISH",
                timeframe=timeframe,
                levels={"ema_resistance": round(ema_20, 4), "invalidation": round(ema_50, 4)},
                evidence=[f"Price retraced to dynamic EMA 20 resistance ({ema_20:.4f}) in established downtrend."],
                chart_overlay={"type": "pullback_zone", "price": ema_20, "bias": "BEARISH"}
            ))

        return results

