"""
ZYROX AI V6 — Category J: Institutional Session Concepts Detector
=================================================================
Tracks:
- Asian Range Accumulation (00:00 - 05:00 UTC / 07:00 - 12:00 Cambodia)
- London Open Killzone (07:00 - 10:00 UTC / 14:00 - 17:00 Cambodia)
- New York AM Killzone (12:00 - 15:00 UTC / 19:00 - 22:00 Cambodia)
- ICT Silver Bullet (14:00 - 15:00 UTC / 21:00 - 22:00 Cambodia)
- London High & Low Benchmarks
- New York High & Low Benchmarks
- Session Range Expansion & Judas Swings
Configured strictly with explicit UTC and Asia/Phnom_Penh (UTC+7) timezones.
"""
from __future__ import annotations

import datetime
from typing import List, Dict, Any, Optional
import zoneinfo
import numpy as np
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.base import BaseConceptDetector
from taikry.indicators.ict_smc import get_ict_killzones, detect_amd_judas_swing, identify_swing_points


class SessionConceptsDetector(BaseConceptDetector):
    """Category J: Institutional Session Concepts Detector."""

    @property
    def category(self) -> ConceptCategory:
        return ConceptCategory.SESSION_CONCEPTS

    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        results: List[ConceptDetectionResult] = []
        if df is None or len(df) < 10:
            return results

        curr_p = float(df["close"].iloc[-1])
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        kh_tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
        now_kh = now_utc.astimezone(kh_tz)

        # 1. Active Killzones & Silver Bullet Status
        kz = get_ict_killzones(now_utc)
        active_zones = kz.get("active_killzones", [])
        is_sb = kz.get("is_silver_bullet", False)

        results.append(ConceptDetectionResult(
            concept_id="session_killzone_status",
            name=f"Institutional Killzone ({kz.get('current_label')})",
            category=self.category,
            detected=True,
            confidence=95 if is_sb else (90 if active_zones else 75),
            bias="HIGH_CONVICTION" if is_sb else ("ACTIVE_VOLUME" if active_zones else "OFF_HOURS"),
            timeframe=timeframe,
            levels={
                "utc_time": kz.get("current_utc_time"),
                "kh_time": now_kh.strftime("%H:%M KH"),
                "is_silver_bullet": is_sb
            },
            evidence=[
                f"Status: {kz.get('current_label')} (UTC: {kz.get('current_utc_time')}, Cambodia: {now_kh.strftime('%H:%M')}).",
                f"Next Session: {kz.get('next_killzone')}."
            ],
            chart_overlay={"type": "session_banner", "status": kz.get("current_label"), "color": kz.get("status_color")}
        ))

        # 2. Power of 3 (AMD) & Judas Swing
        swings = identify_swing_points(df, left=2, right=2)
        amd = detect_amd_judas_swing(df, swings, check_time=now_utc)
        judas = amd.get("judas_swing")

        if judas:
            is_bull_judas = "BULLISH" in judas.get("type", "")
            results.append(ConceptDetectionResult(
                concept_id="session_judas_swing",
                name=f"ICT Judas Swing Manipulation ({'Bullish Trap' if is_bull_judas else 'Bearish Trap'})",
                category=self.category,
                detected=True,
                confidence=90,
                bias="BULLISH" if is_bull_judas else "BEARISH",
                timeframe=timeframe,
                levels={"swept_extreme": judas.get("swept_extreme")},
                evidence=[judas.get("details", f"Price swept session extreme at {judas.get('swept_extreme')} and displaced.")],
                chart_overlay={"type": "judas_marker", "price": judas.get("swept_extreme"), "bias": "BULLISH" if is_bull_judas else "BEARISH"}
            ))
        else:
            results.append(ConceptDetectionResult(
                concept_id="session_amd_phase",
                name=f"Power of 3 (AMD) Phase: {amd.get('phase')}",
                category=self.category,
                detected=True,
                confidence=82,
                bias="NEUTRAL",
                timeframe=timeframe,
                levels={"range_high": amd.get("range_high"), "range_low": amd.get("range_low")},
                evidence=[f"Current session operating in {amd.get('phase')} cycle within [{amd.get('range_low'):.4f} - {amd.get('range_high'):.4f}]."],
                chart_overlay={"type": "amd_phase", "phase": amd.get("phase")}
            ))

        # 3. Session High / Low Extremes (last 24 bars)
        session_h = float(df["high"].tail(min(24, len(df))).max())
        session_l = float(df["low"].tail(min(24, len(df))).min())
        results.append(ConceptDetectionResult(
            concept_id="session_current_range",
            name="Intraday Session High / Low Bounds",
            category=self.category,
            detected=True,
            confidence=88,
            bias="NEUTRAL",
            timeframe=timeframe,
            levels={"session_high": session_h, "session_low": session_l, "session_range": round(session_h - session_l, 4)},
            evidence=[f"Active 24-bar session range: High {session_h:.4f}, Low {session_l:.4f} (Span: {session_h - session_l:.4f} pts)."],
            chart_overlay={"type": "session_bounds", "high": session_h, "low": session_l}
        ))

        return results

