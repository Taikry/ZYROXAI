"""
ZYROX AI V6 — Category H: Momentum & Divergence Detector
========================================================
Calculates:
- RSI 14 (Overbought > 70, Oversold < 30)
- MACD (Line, Signal, Histogram Expansion / Contraction)
- ADX 14 (Trend conviction strength)
- Fast & Slow Stochastic (%K, %D)
Detects:
- Momentum Trend Confirmation
- Regular Bullish & Bearish Divergence
- Momentum Exhaustion / Weakening
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.technical import (
    calculate_rsi,
    calculate_macd,
    calculate_dmi_adx,
    calculate_stochastic
)


class MomentumDetector(BaseConceptDetector):
    """Category H: Momentum & Divergence Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.MOMENTUM

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 25:
            return results

        closes = df["close"].astype(float)
        curr_p = float(closes.iloc[-1])

        rsi_series = calculate_rsi(closes, period=14)
        rsi_val = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0

        macd_dict = calculate_macd(closes, fast=12, slow=26, signal=9)
        macd_hist = float(macd_dict["macd_hist"].iloc[-1])
        macd_hist_prev = float(macd_dict["macd_hist"].iloc[-2])
        is_hist_expanding = abs(macd_hist) > abs(macd_hist_prev)

        dmi = calculate_dmi_adx(df, period=14)
        adx_val = float(dmi["adx"].dropna().iloc[-1]) if not dmi["adx"].dropna().empty else 15.0

        stoch = calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3)
        stoch_k = float(stoch["stoch_k"].iloc[-1])
        stoch_d = float(stoch["stoch_d"].iloc[-1])

        # 1. Momentum Confirmation
        if rsi_val >= 55.0 and macd_hist > 0 and is_hist_expanding and adx_val >= 22.0:
            results.append(ConceptDetectionResult(
                concept_id="mom_bullish_confirmation",
                name="Bullish Momentum Acceleration Confirmation",
                category=self.category,
                detected=True,
                confidence=88,
                bias="BULLISH",
                timeframe=timeframe,
                levels={"rsi": round(rsi_val, 1), "macd_hist": round(macd_hist, 4), "adx": round(adx_val, 1)},
                evidence=[
                    f"RSI ({rsi_val:.1f}) in bullish expansion territory above 55.",
                    f"MACD Histogram expanding positively ({macd_hist:.4f} > {macd_hist_prev:.4f}) with ADX {adx_val:.1f}."
                ],
                chart_overlay={"type": "momentum_status", "bias": "BULLISH", "rsi": rsi_val}
            ))
        elif rsi_val <= 45.0 and macd_hist < 0 and is_hist_expanding and adx_val >= 22.0:
            results.append(ConceptDetectionResult(
                concept_id="mom_bearish_confirmation",
                name="Bearish Momentum Acceleration Confirmation",
                category=self.category,
                detected=True,
                confidence=88,
                bias="BEARISH",
                timeframe=timeframe,
                levels={"rsi": round(rsi_val, 1), "macd_hist": round(macd_hist, 4), "adx": round(adx_val, 1)},
                evidence=[
                    f"RSI ({rsi_val:.1f}) in bearish expansion territory below 45.",
                    f"MACD Histogram expanding negatively ({macd_hist:.4f} < {macd_hist_prev:.4f}) with ADX {adx_val:.1f}."
                ],
                chart_overlay={"type": "momentum_status", "bias": "BEARISH", "rsi": rsi_val}
            ))

        # 2. Regular Bullish & Bearish Divergence
        # Compare price low vs RSI low over last 20 bars
        if len(df) >= 20:
            p_slice = closes.iloc[-20:].values
            r_slice = rsi_series.iloc[-20:].values

            # Bullish Divergence: Price Lower Low while RSI Higher Low
            min_p_idx = int(np.argmin(p_slice))
            if min_p_idx < len(p_slice) - 3:
                # If subsequent price made new low or close to it, but RSI increased
                recent_p_min = p_slice[-1]
                earlier_p_min = p_slice[min_p_idx]
                recent_r = r_slice[-1]
                earlier_r = r_slice[min_p_idx]

                if recent_p_min <= earlier_p_min and recent_r > earlier_r + 3.0 and recent_r < 45.0:
                    results.append(ConceptDetectionResult(
                        concept_id="mom_regular_bullish_divergence",
                        name="Regular Bullish RSI Divergence",
                        category=self.category,
                        detected=True,
                        confidence=87,
                        bias="BULLISH",
                        timeframe=timeframe,
                        levels={"divergence_price": curr_p, "rsi_val": round(rsi_val, 1)},
                        evidence=[f"Price printed lower low ({recent_p_min:.4f} <= {earlier_p_min:.4f}) while RSI printed higher low ({recent_r:.1f} > {earlier_r:.1f})."],
                        chart_overlay={"type": "divergence", "bias": "BULLISH", "price": curr_p}
                    ))

            # Bearish Divergence: Price Higher High while RSI Lower High
            max_p_idx = int(np.argmax(p_slice))
            if max_p_idx < len(p_slice) - 3:
                recent_p_max = p_slice[-1]
                earlier_p_max = p_slice[max_p_idx]
                recent_r = r_slice[-1]
                earlier_r = r_slice[max_p_idx]

                if recent_p_max >= earlier_p_max and recent_r < earlier_r - 3.0 and recent_r > 55.0:
                    results.append(ConceptDetectionResult(
                        concept_id="mom_regular_bearish_divergence",
                        name="Regular Bearish RSI Divergence",
                        category=self.category,
                        detected=True,
                        confidence=87,
                        bias="BEARISH",
                        timeframe=timeframe,
                        levels={"divergence_price": curr_p, "rsi_val": round(rsi_val, 1)},
                        evidence=[f"Price printed higher high ({recent_p_max:.4f} >= {earlier_p_max:.4f}) while RSI printed lower high ({recent_r:.1f} < {earlier_r:.1f})."],
                        chart_overlay={"type": "divergence", "bias": "BEARISH", "price": curr_p}
                    ))

        # 3. Momentum Weakening / Exhaustion
        if rsi_val >= 72.0 and stoch_k >= 80.0:
            results.append(ConceptDetectionResult(
                concept_id="mom_exhaustion_overbought",
                name="Overbought Momentum Exhaustion",
                category=self.category,
                detected=True,
                confidence=82,
                bias="BEARISH_WARNING",
                timeframe=timeframe,
                levels={"rsi": round(rsi_val, 1), "stoch_k": round(stoch_k, 1)},
                evidence=[f"Extreme overbought exhaustion (RSI: {rsi_val:.1f}, Stoch: {stoch_k:.1f}). Long chase risk elevated."],
                chart_overlay={"type": "exhaustion_badge", "price": curr_p, "bias": "BEARISH"}
            ))
        elif rsi_val <= 28.0 and stoch_k <= 20.0:
            results.append(ConceptDetectionResult(
                concept_id="mom_exhaustion_oversold",
                name="Oversold Momentum Exhaustion",
                category=self.category,
                detected=True,
                confidence=82,
                bias="BULLISH_WARNING",
                timeframe=timeframe,
                levels={"rsi": round(rsi_val, 1), "stoch_k": round(stoch_k, 1)},
                evidence=[f"Extreme oversold exhaustion (RSI: {rsi_val:.1f}, Stoch: {stoch_k:.1f}). Short chase risk elevated."],
                chart_overlay={"type": "exhaustion_badge", "price": curr_p, "bias": "BULLISH"}
            ))

        return results

