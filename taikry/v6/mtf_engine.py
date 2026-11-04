"""
ZYROX AI V6 — Module 7: Multi-Timeframe Strategy Engine
======================================================
Coordinates hierarchical multi-timeframe analysis:
- Higher Timeframe (HTF): D1 / H4 -> Macro Trend & Structural Bias
- Setup Timeframe (SETUP): H1 / M15 -> Institutional Dealing Range & Key Zones
- Entry Timeframe (ENTRY): M15 / M5 -> Execution Confirmation & Trigger

Alignment States:
- FULL_ALIGNMENT: All 3 tiers agree directionally.
- PARTIAL_ALIGNMENT: HTF and Setup agree; Entry awaiting final trigger.
- CONFLICT: Entry conflicts directly with dominant HTF flow -> Yields WAIT or NO_TRADE.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from taikry.indicators.technical import calculate_ema

logger = logging.getLogger("zyrox.v6.mtf_engine")


class MultiTimeframeAnalysisResult(BaseModel):
    """Hierarchical MTF Alignment evaluation result."""
    htf_timeframe: str = "H4"
    htf_bias: str = "BULLISH"  # BULLISH, BEARISH, NEUTRAL
    setup_timeframe: str = "H1"
    setup_context: str = "PULLBACK_INTO_DISCOUNT"
    entry_timeframe: str = "M15"
    entry_confirmation: str = "CONFIRMED"  # CONFIRMED, PENDING, CONFLICT
    alignment_status: str = "FULL_ALIGNMENT"  # FULL_ALIGNMENT, PARTIAL_ALIGNMENT, CONFLICT
    can_execute: bool = True
    rationale: str = ""


class MultiTimeframeEngine:
    """Evaluates multi-timeframe harmony and detects structural conflicts."""

    def evaluate_alignment(
        self,
        htf_bias: str,
        setup_bias: str,
        entry_bias: str,
        htf_tf: str = "H4",
        setup_tf: str = "H1",
        entry_tf: str = "M15"
    ) -> MultiTimeframeAnalysisResult:
        """
        Determines alignment tier across the 3 hierarchical timeframes.
        """
        h_norm = htf_bias.upper()
        s_norm = setup_bias.upper()
        e_norm = entry_bias.upper()

        h_dir = "BULLISH" if "BULL" in h_norm else ("BEARISH" if "BEAR" in h_norm else "NEUTRAL")
        s_dir = "BULLISH" if "BULL" in s_norm else ("BEARISH" if "BEAR" in s_norm else "NEUTRAL")
        e_dir = "BULLISH" if "BULL" in e_norm else ("BEARISH" if "BEAR" in e_norm else "NEUTRAL")

        # Full alignment
        if h_dir == s_dir == e_dir and h_dir != "NEUTRAL":
            status = "FULL_ALIGNMENT"
            can_execute = True
            rationale = f"All 3 timeframes ({htf_tf}, {setup_tf}, {entry_tf}) in full {h_dir} harmony."
            entry_conf = "CONFIRMED"

        # Direct Conflict (e.g. HTF is Bearish, Entry attempts Buy)
        elif (h_dir == "BEARISH" and e_dir == "BULLISH") or (h_dir == "BULLISH" and e_dir == "BEARISH"):
            status = "CONFLICT"
            can_execute = False
            rationale = f"Severe conflict: Entry direction ({e_dir} on {entry_tf}) opposes dominant HTF flow ({h_dir} on {htf_tf}). Capital protection active."
            entry_conf = "CONFLICT"

        # Partial alignment (e.g. HTF and Setup agree, Entry is transitioning or neutral)
        elif h_dir == s_dir and h_dir != "NEUTRAL":
            status = "PARTIAL_ALIGNMENT"
            can_execute = True
            rationale = f"Macro {htf_tf} and Setup {setup_tf} agree on {h_dir}; {entry_tf} entry awaiting final confirmation candle."
            entry_conf = "PENDING"

        # Setup agrees with Entry but HTF is Neutral
        elif s_dir == e_dir and s_dir != "NEUTRAL":
            status = "PARTIAL_ALIGNMENT"
            can_execute = True
            rationale = f"Setup {setup_tf} and Entry {entry_tf} aligned on {s_dir}; HTF is currently neutral/rotational."
            entry_conf = "CONFIRMED"

        else:
            status = "CONFLICT"
            can_execute = False
            rationale = "Timeframes show fragmented or mixed signals. Wait for cleaner alignment."
            entry_conf = "CONFLICT"

        return MultiTimeframeAnalysisResult(
            htf_timeframe=htf_tf,
            htf_bias=h_dir,
            setup_timeframe=setup_tf,
            setup_context=f"Context aligned with {s_dir}",
            entry_timeframe=entry_tf,
            entry_confirmation=entry_conf,
            alignment_status=status,
            can_execute=can_execute,
            rationale=rationale
        )


v6_mtf_engine = MultiTimeframeEngine()

