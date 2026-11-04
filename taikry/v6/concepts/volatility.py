"""
ZYROX AI V6 — Category I: Volatility Detector
=============================================
Calculates:
- Average True Range (ATR 14) & Relative ATR %
- Rolling ATR 100-bar Percentile Rank
- Bollinger Bands (20, 2.0 std dev) & Bandwidth %
Detects:
- Volatility Compression / Squeeze (BB width < 0.35%)
- Volatility Expansion (Band breakout)
- Volatility Spikes (Single-bar range > 2.5x ATR)
- Low Volatility Regimes
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.technical import calculate_atr, calculate_bollinger_bands


class VolatilityDetector(BaseConceptDetector):
    """Category I: Volatility Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.VOLATILITY

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 20:
            return results

        closes = df["close"].astype(float)
        highs = df["high"].astype(float)
        lows = df["low"].astype(float)
        curr_p = float(closes.iloc[-1])

        # ATR & ATR Percentile
        atr_series = calculate_atr(df, period=14)
        atr_14 = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0
        atr_pct = (atr_14 / curr_p) * 100.0 if curr_p > 0 else 0.0

        atr_pct_series = (atr_series / closes.replace(0, np.nan)) * 100.0
        rolling_window = atr_pct_series.tail(min(len(df), 100))
        atr_percentile = float(pd.Series(rolling_window).rank(pct=True).iloc[-1] * 100.0) if len(rolling_window) >= 15 else 50.0

        # Bollinger Bands & Bandwidth
        bb = calculate_bollinger_bands(closes, period=20, num_std=2.0)
        bb_upper = float(bb["bb_upper"].iloc[-1])
        bb_lower = float(bb["bb_lower"].iloc[-1])
        bb_middle = float(bb["bb_middle"].iloc[-1])
        bb_width_pct = ((bb_upper - bb_lower) / bb_middle * 100.0) if bb_middle > 0 else 1.0

        # Single-candle spike check
        latest_candle_range = float(highs.iloc[-1] - lows.iloc[-1])
        is_spike = latest_candle_range > (2.5 * atr_14) if atr_14 > 0 else False

        # 1. Volatility Compression / Squeeze (BB Width < 0.35%)
        if bb_width_pct < 0.38 or atr_percentile < 20.0:
            results.append(ConceptDetectionResult(
                concept_id="vol_compression_squeeze",
                name="Volatility Compression Squeeze",
                category=self.category,
                detected=True,
                confidence=91,
                bias="BREAKOUT_PENDING",
                timeframe=timeframe,
                levels={"bb_upper": round(bb_upper, 4), "bb_lower": round(bb_lower, 4), "bb_width_pct": round(bb_width_pct, 2)},
                evidence=[
                    f"Bollinger Bands tightly compressed (Width: {bb_width_pct:.2f}%, ATR percentile: {atr_percentile:.1f}%).",
                    f"Severe liquidity coiling between {bb_lower:.4f} and {bb_upper:.4f}; explosive expansion imminent."
                ],
                chart_overlay={"type": "squeeze_box", "upper": bb_upper, "lower": bb_lower}
            ))

        # 2. Volatility Expansion
        elif bb_width_pct > 1.10 and atr_percentile > 75.0:
            results.append(ConceptDetectionResult(
                concept_id="vol_expansion_active",
                name="Volatility Expansion Phase",
                category=self.category,
                detected=True,
                confidence=86,
                bias="VOLATILE",
                timeframe=timeframe,
                levels={"atr_14": round(atr_14, 4), "bb_width_pct": round(bb_width_pct, 2)},
                evidence=[f"Market volatility expanding rapidly (BB Width: {bb_width_pct:.2f}%, ATR: {atr_14:.4f} pts)."],
                chart_overlay={"type": "expansion_active", "width": bb_width_pct}
            ))

        # 3. Volatility Spike
        if is_spike:
            results.append(ConceptDetectionResult(
                concept_id="vol_abnormal_spike",
                name="Abnormal Single-Bar Volatility Spike",
                category=self.category,
                detected=True,
                confidence=92,
                bias="HIGH_RISK",
                timeframe=timeframe,
                levels={"spike_range": round(latest_candle_range, 4), "atr_multiple": round(latest_candle_range / (atr_14 + 1e-8), 1)},
                evidence=[f"Latest bar range ({latest_candle_range:.4f}) exceeded {(latest_candle_range / (atr_14 + 1e-8)):.1f}x normal ATR. Spread blowout caution advised."],
                chart_overlay={"type": "spike_warning", "price": curr_p}
            ))

        # 4. Standard ATR Baseline Level
        results.append(ConceptDetectionResult(
            concept_id="vol_atr_baseline",
            name="Quantitative ATR Volatility Gauge",
            category=self.category,
            detected=True,
            confidence=95,
            bias="NEUTRAL",
            timeframe=timeframe,
            levels={"atr_14": round(atr_14, 4), "atr_pct": round(atr_pct, 3), "atr_percentile": round(atr_percentile, 1)},
            evidence=[f"ATR 14 is {atr_14:.4f} pts ({atr_pct:.2f}% of price, {atr_percentile:.1f}th percentile)."],
            chart_overlay={"type": "atr_stat", "atr": atr_14}
        ))

        return results

