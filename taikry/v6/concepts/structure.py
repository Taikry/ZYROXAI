"""
ZYROX AI V6 — Category A: Market Structure Detector
===================================================
Detects:
- Higher High (HH) / Higher Low (HL)
- Lower High (LH) / Lower Low (LL)
- Break of Structure (BOS Bullish / Bearish)
- Change of Character (CHoCH Bullish / Bearish)
- Market Structure Shift (MSS)
- Swing Highs & Swing Lows
- Internal vs External Structure
- Trend Continuation / Trend Reversal
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.ict_smc import identify_swing_points, detect_structure_breaks


class MarketStructureDetector(BaseConceptDetector):
    """Category A: Market Structure Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.MARKET_STRUCTURE

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 15:
            return results

        curr_p = float(df["close"].iloc[-1])
        swings = identify_swing_points(df, left=2, right=2)
        shs = swings.get("swing_highs", [])
        sls = swings.get("swing_lows", [])

        # 1. Swing Highs & Swing Lows
        if shs and sls:
            recent_sh = shs[-1]
            recent_sl = sls[-1]
            results.append(ConceptDetectionResult(
                concept_id="struct_swings",
                name="Fractal Swing High / Low",
                category=self.category,
                detected=True,
                confidence=90,
                bias="NEUTRAL",
                timeframe=timeframe,
                levels={"swing_high": recent_sh["price"], "swing_low": recent_sl["price"]},
                evidence=[f"Recent confirmed Swing High at {recent_sh['price']:.4f}, Swing Low at {recent_sl['price']:.4f}."],
                chart_overlay={"type": "levels", "high": recent_sh["price"], "low": recent_sl["price"]}
            ))

        # 2. HH / HL or LH / LL Sequence
        if len(shs) >= 2 and len(sls) >= 2:
            is_bull_seq = shs[-1]["price"] > shs[-2]["price"] and sls[-1]["price"] > sls[-2]["price"]
            is_bear_seq = shs[-1]["price"] < shs[-2]["price"] and sls[-1]["price"] < sls[-2]["price"]

            if is_bull_seq:
                results.append(ConceptDetectionResult(
                    concept_id="struct_bullish_hh_hl",
                    name="Bullish Structure (Higher Highs & Higher Lows)",
                    category=self.category,
                    detected=True,
                    confidence=88,
                    bias="BULLISH",
                    timeframe=timeframe,
                    levels={"last_hh": shs[-1]["price"], "last_hl": sls[-1]["price"], "invalidation": sls[-1]["price"]},
                    evidence=[
                        f"Consecutive Higher Highs ({shs[-2]['price']:.4f} -> {shs[-1]['price']:.4f}) and Higher Lows ({sls[-2]['price']:.4f} -> {sls[-1]['price']:.4f}).",
                        f"Structural invalidation point: {sls[-1]['price']:.4f}."
                    ],
                    chart_overlay={"type": "trend_structure", "direction": "UP", "invalidation": sls[-1]["price"]}
                ))
            elif is_bear_seq:
                results.append(ConceptDetectionResult(
                    concept_id="struct_bearish_lh_ll",
                    name="Bearish Structure (Lower Highs & Lower Lows)",
                    category=self.category,
                    detected=True,
                    confidence=88,
                    bias="BEARISH",
                    timeframe=timeframe,
                    levels={"last_lh": shs[-1]["price"], "last_ll": sls[-1]["price"], "invalidation": shs[-1]["price"]},
                    evidence=[
                        f"Consecutive Lower Highs ({shs[-2]['price']:.4f} -> {shs[-1]['price']:.4f}) and Lower Lows ({sls[-2]['price']:.4f} -> {sls[-1]['price']:.4f}).",
                        f"Structural invalidation point: {shs[-1]['price']:.4f}."
                    ],
                    chart_overlay={"type": "trend_structure", "direction": "DOWN", "invalidation": shs[-1]["price"]}
                ))

        # 3. BOS (Break of Structure) & CHoCH (Change of Character)
        struct = detect_structure_breaks(df, swings)
        bos = struct.get("bos")
        choch = struct.get("choch")

        if bos:
            is_bull_bos = bos.get("type") == "BULLISH_BOS"
            results.append(ConceptDetectionResult(
                concept_id="struct_bos",
                name=f"Break of Structure ({bos.get('type')})",
                category=self.category,
                detected=True,
                confidence=86,
                bias="BULLISH" if is_bull_bos else "BEARISH",
                timeframe=timeframe,
                levels={"bos_level": bos.get("level")},
                evidence=[f"Candle closed beyond previous key swing level at {bos.get('level'):.4f}, confirming trend continuation momentum."],
                chart_overlay={"type": "horizontal_line", "price": bos.get("level"), "label": bos.get("type")}
            ))

        if choch:
            is_bull_choch = choch.get("type") == "BULLISH_CHOCH"
            results.append(ConceptDetectionResult(
                concept_id="struct_choch",
                name=f"Change of Character ({choch.get('type')})",
                category=self.category,
                detected=True,
                confidence=84,
                bias="BULLISH" if is_bull_choch else "BEARISH",
                timeframe=timeframe,
                levels={"choch_level": choch.get("level")},
                evidence=[f"Change of Character at {choch.get('level'):.4f} broke established structural flow, indicating institutional trend reversal transition."],
                chart_overlay={"type": "horizontal_line", "price": choch.get("level"), "label": choch.get("type")}
            ))

        # 4. Market Structure Shift (MSS)
        # MSS occurs when an aggressive displacement candle breaks the most recent opposite swing
        if len(shs) >= 1 and len(sls) >= 1 and len(df) >= 3:
            latest_c = df.iloc[-1]
            prev_c = df.iloc[-2]
            body_range = abs(latest_c["close"] - latest_c["open"])
            avg_body = np.mean(abs(df["close"].tail(10) - df["open"].tail(10)))

            if body_range > 1.5 * avg_body:
                if latest_c["close"] > shs[-1]["price"] and prev_c["close"] <= shs[-1]["price"]:
                    results.append(ConceptDetectionResult(
                        concept_id="struct_mss_bullish",
                        name="Bullish Market Structure Shift (MSS)",
                        category=self.category,
                        detected=True,
                        confidence=85,
                        bias="BULLISH",
                        timeframe=timeframe,
                        levels={"shift_level": shs[-1]["price"]},
                        evidence=[f"Aggressive impulse candle closed above key swing high ({shs[-1]['price']:.4f}) with displacement."],
                        chart_overlay={"type": "mss", "price": shs[-1]["price"], "bias": "BULLISH"}
                    ))
                elif latest_c["close"] < sls[-1]["price"] and prev_c["close"] >= sls[-1]["price"]:
                    results.append(ConceptDetectionResult(
                        concept_id="struct_mss_bearish",
                        name="Bearish Market Structure Shift (MSS)",
                        category=self.category,
                        detected=True,
                        confidence=85,
                        bias="BEARISH",
                        timeframe=timeframe,
                        levels={"shift_level": sls[-1]["price"]},
                        evidence=[f"Aggressive impulse candle closed below key swing low ({sls[-1]['price']:.4f}) with displacement."],
                        chart_overlay={"type": "mss", "price": sls[-1]["price"], "bias": "BEARISH"}
                    ))

        return results

