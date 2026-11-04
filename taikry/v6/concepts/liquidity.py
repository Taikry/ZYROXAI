"""
ZYROX AI V6 — Category B: Smart Money & Liquidity Detector
==========================================================
Detects:
- Liquidity Sweeps (Buy-side / Sell-side)
- Buy-side Liquidity (BSL)
- Sell-side Liquidity (SSL)
- Equal Highs (EQH) & Equal Lows (EQL)
- Inducement (IDM)
- Stop Hunt Pattern (Turtle Soup / Judas Trap)
- Liquidity Pools
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.ict_smc import identify_swing_points, detect_liquidity_sweeps


class LiquidityDetector(BaseConceptDetector):
    """Category B: Smart Money & Liquidity Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.SMART_MONEY_LIQUIDITY

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 15:
            return results

        curr_p = float(df["close"].iloc[-1])
        swings = identify_swing_points(df, left=2, right=2)
        shs = swings.get("swing_highs", [])
        sls = swings.get("swing_lows", [])

        # 1. BSL & SSL Liquidity Pools
        if shs:
            bsl_level = float(max(sh["price"] for sh in shs[-3:]))
            results.append(ConceptDetectionResult(
                concept_id="liq_bsl_pool",
                name="Buy-side Liquidity Pool (BSL)",
                category=self.category,
                detected=True,
                confidence=85,
                bias="BEARISH_MAGNET" if curr_p < bsl_level else "SWEPT",
                timeframe=timeframe,
                levels={"bsl_price": bsl_level},
                evidence=[f"Resting buy stops clustered above recent swing peak at {bsl_level:.4f}."],
                chart_overlay={"type": "liquidity_pool", "price": bsl_level, "label": "BSL"}
            ))

        if sls:
            ssl_level = float(min(sl["price"] for sl in sls[-3:]))
            results.append(ConceptDetectionResult(
                concept_id="liq_ssl_pool",
                name="Sell-side Liquidity Pool (SSL)",
                category=self.category,
                detected=True,
                confidence=85,
                bias="BULLISH_MAGNET" if curr_p > ssl_level else "SWEPT",
                timeframe=timeframe,
                levels={"ssl_price": ssl_level},
                evidence=[f"Resting sell stops clustered below recent swing trough at {ssl_level:.4f}."],
                chart_overlay={"type": "liquidity_pool", "price": ssl_level, "label": "SSL"}
            ))

        # 2. Liquidity Sweeps
        sweeps = detect_liquidity_sweeps(df, swings)
        for sweep in sweeps:
            is_bsl_sweep = "BUY_SIDE" in sweep.get("type", "")
            results.append(ConceptDetectionResult(
                concept_id="liq_sweep_" + ("bsl" if is_bsl_sweep else "ssl"),
                name="Liquidity Sweep (" + ("BSL" if is_bsl_sweep else "SSL") + ")",
                category=self.category,
                detected=True,
                confidence=89,
                bias="BEARISH" if is_bsl_sweep else "BULLISH",
                timeframe=timeframe,
                levels={"swept_level": sweep.get("swept_level")},
                evidence=[sweep.get("details", f"Price pierced liquidity at {sweep.get('swept_level')} and rejected.")],
                chart_overlay={"type": "sweep_marker", "price": sweep.get("swept_level"), "bias": "BEARISH" if is_bsl_sweep else "BULLISH"}
            ))

        # 3. Equal Highs (EQH) & Equal Lows (EQL)
        if len(shs) >= 2:
            p1 = shs[-1]["price"]
            p2 = shs[-2]["price"]
            tolerance = curr_p * 0.0008  # 0.08% tolerance for double tops
            if abs(p1 - p2) <= tolerance:
                results.append(ConceptDetectionResult(
                    concept_id="liq_eqh",
                    name="Equal Highs (EQH) Liquidity Magnet",
                    category=self.category,
                    detected=True,
                    confidence=84,
                    bias="BULLISH_MAGNET",
                    timeframe=timeframe,
                    levels={"eqh_price": round((p1 + p2) / 2.0, 4)},
                    evidence=[f"Double top Equal Highs at {p1:.4f} and {p2:.4f} creating high-probability buy stop liquidity pool."],
                    chart_overlay={"type": "equal_level", "price": (p1 + p2) / 2.0, "label": "EQH"}
                ))

        if len(sls) >= 2:
            p1 = sls[-1]["price"]
            p2 = sls[-2]["price"]
            tolerance = curr_p * 0.0008
            if abs(p1 - p2) <= tolerance:
                results.append(ConceptDetectionResult(
                    concept_id="liq_eql",
                    name="Equal Lows (EQL) Liquidity Magnet",
                    category=self.category,
                    detected=True,
                    confidence=84,
                    bias="BEARISH_MAGNET",
                    timeframe=timeframe,
                    levels={"eql_price": round((p1 + p2) / 2.0, 4)},
                    evidence=[f"Double bottom Equal Lows at {p1:.4f} and {p2:.4f} creating high-probability sell stop liquidity pool."],
                    chart_overlay={"type": "equal_level", "price": (p1 + p2) / 2.0, "label": "EQL"}
                ))

        # 4. Stop Hunt Pattern (Turtle Soup)
        # Candle wicks beyond previous swing high/low by > 0.05% but closes firmly within previous range
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        if shs and latest["high"] > shs[-1]["price"] and latest["close"] < shs[-1]["price"]:
            upper_wick = latest["high"] - max(latest["open"], latest["close"])
            if upper_wick > abs(latest["close"] - latest["open"]):
                results.append(ConceptDetectionResult(
                    concept_id="liq_stophunt_bearish",
                    name="Bearish Stop-Hunt / Turtle Soup Trap",
                    category=self.category,
                    detected=True,
                    confidence=87,
                    bias="BEARISH",
                    timeframe=timeframe,
                    levels={"hunt_extreme": float(latest["high"]), "invalidation": float(latest["high"])},
                    evidence=[f"Price spiked through swing high {shs[-1]['price']:.4f} up to {latest['high']:.4f} and aggressively rejected (Turtle Soup)."],
                    chart_overlay={"type": "trap", "price": latest["high"], "bias": "BEARISH"}
                ))
        elif sls and latest["low"] < sls[-1]["price"] and latest["close"] > sls[-1]["price"]:
            lower_wick = min(latest["open"], latest["close"]) - latest["low"]
            if lower_wick > abs(latest["close"] - latest["open"]):
                results.append(ConceptDetectionResult(
                    concept_id="liq_stophunt_bullish",
                    name="Bullish Stop-Hunt / Turtle Soup Trap",
                    category=self.category,
                    detected=True,
                    confidence=87,
                    bias="BULLISH",
                    timeframe=timeframe,
                    levels={"hunt_extreme": float(latest["low"]), "invalidation": float(latest["low"])},
                    evidence=[f"Price dipped through swing low {sls[-1]['price']:.4f} down to {latest['low']:.4f} and aggressively rejected (Turtle Soup)."],
                    chart_overlay={"type": "trap", "price": latest["low"], "bias": "BULLISH"}
                ))

        return results

