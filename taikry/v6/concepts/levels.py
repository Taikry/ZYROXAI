"""
ZYROX AI V6 — Category E: Support & Resistance Detector
=======================================================
Detects:
- Horizontal Support & Resistance Levels
- Supply & Demand Equilibrium Zones
- Previous Day High (PDH) & Previous Day Low (PDL)
- Previous Week High (PWH) & Previous Week Low (PWL)
- Previous Month High (PMH) & Previous Month Low (PML)
- Daily Open (DO) & Weekly Open (WO)
- Classical Floor Pivot Points (Pivot, R1, S1, R2, S2)
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.technical import calculate_session_levels
from taikry.indicators.ict_smc import compute_premium_discount


class SupportResistanceDetector(BaseConceptDetector):
    """Category E: Support & Resistance Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.SUPPORT_RESISTANCE

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 10:
            return results

        curr_p = float(df["close"].iloc[-1])

        # 1. Benchmark Session Levels: DO, PDH, PDL, PWH, PWL, Pivots
        session_levels = calculate_session_levels(df)
        if session_levels:
            pdh = session_levels.get("previous_day_high")
            pdl = session_levels.get("previous_day_low")
            pwh = session_levels.get("previous_week_high")
            pwl = session_levels.get("previous_week_low")
            do = session_levels.get("daily_open")
            pivot = session_levels.get("pivot_point")
            r1 = session_levels.get("resistance_1")
            s1 = session_levels.get("support_1")

            results.append(ConceptDetectionResult(
                concept_id="sr_benchmark_levels",
                name="Key Session Benchmark Levels (PDH/PDL/DO)",
                category=self.category,
                detected=True,
                confidence=92,
                bias="BULLISH" if do and curr_p > do else "BEARISH",
                timeframe=timeframe,
                levels={
                    "daily_open": do,
                    "previous_day_high": pdh,
                    "previous_day_low": pdl,
                    "previous_week_high": pwh,
                    "previous_week_low": pwl,
                    "pivot": pivot,
                    "r1": r1,
                    "s1": s1
                },
                evidence=[
                    f"Daily Open at {do:.4f} (Price currently {'ABOVE' if do and curr_p > do else 'BELOW'} DO).",
                    f"Previous Day High (PDH): {pdh:.4f}, Previous Day Low (PDL): {pdl:.4f}.",
                    f"Floor Pivot: {pivot:.4f} (R1: {r1:.4f}, S1: {s1:.4f})."
                ],
                chart_overlay={"type": "session_levels", "do": do, "pdh": pdh, "pdl": pdl}
            ))

        # 2. Monthly Benchmark High/Low (from extended history or lookback)
        lookback_month = min(len(df), 300)
        pmh = float(df["high"].tail(lookback_month).max())
        pml = float(df["low"].tail(lookback_month).min())
        results.append(ConceptDetectionResult(
            concept_id="sr_monthly_range",
            name="Macro Range Extremes (PMH / PML)",
            category=self.category,
            detected=True,
            confidence=88,
            bias="NEUTRAL",
            timeframe=timeframe,
            levels={"previous_month_high": pmh, "previous_month_low": pml},
            evidence=[f"Major multi-week range high at {pmh:.4f}, range low at {pml:.4f}."],
            chart_overlay={"type": "macro_bounds", "high": pmh, "low": pml}
        ))

        # 3. Supply & Demand Equilibrium (50% Dealing Range)
        prem_disc = compute_premium_discount(df, lookback=min(50, len(df)))
        if prem_disc:
            eq = prem_disc.get("equilibrium", curr_p)
            zone = prem_disc.get("current_zone", "EQUILIBRIUM")
            results.append(ConceptDetectionResult(
                concept_id="sr_premium_discount_equilibrium",
                name=f"Dealing Range {zone} Zone (50% Equilibrium)",
                category=self.category,
                detected=True,
                confidence=85,
                bias="BULLISH_DISCOUNT" if zone == "DISCOUNT" else ("BEARISH_PREMIUM" if zone == "PREMIUM" else "NEUTRAL"),
                timeframe=timeframe,
                levels={"equilibrium_50": eq, "range_high": prem_disc.get("range_high"), "range_low": prem_disc.get("range_low")},
                evidence=[
                    f"Institutional dealing range 50% Equilibrium at {eq:.4f}.",
                    f"Current price is positioned in {zone} ({prem_disc.get('position_percent', 50):.1f}% of range)."
                ],
                chart_overlay={"type": "equilibrium_line", "price": eq, "zone": zone}
            ))

        return results

