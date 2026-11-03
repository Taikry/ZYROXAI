"""
ZYROX AI — Signal Quality Scoring Engine V3
===========================================
Calculates an explainable 0–100 setup quality score from 8 validated structural and quantitative factors:
1. Trend alignment (0–15)
2. Market structure confirmation (0–15)
3. Momentum & RSI/MACD confluence (0–15)
4. Volatility suitability & ATR buffer (0–10)
5. Entry quality & S/R proximity (0–15)
6. Risk-to-reward ratio (0–15)
7. News risk proximity (0–10)
8. Data freshness & quote fidelity (0–5)

Disclaims clearly: Internal confluence metric, not a probability of profit or guarantee.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from taikry.risk.models import SignalQualityBreakdown

logger = logging.getLogger("zyrox.risk.quality")


class SignalQualityScorer:
    """Calculates granular, transparent 8-factor signal quality scores."""

    def calculate_score(
        self,
        symbol: str,
        direction: str,
        rr_ratio: float,
        trend_aligned: bool = True,
        structure_confirmed: bool = True,
        momentum_aligned: bool = True,
        volatility_ok: bool = True,
        entry_quality_ok: bool = True,
        news_clear: bool = True,
        data_fresh: bool = True,
        ai_consensus_score: Optional[int] = None,
        advisories: Optional[list] = None
    ) -> SignalQualityBreakdown:
        """Computes factor-by-factor breakdown totaling 0 to 100."""
        # 1. Trend alignment (0–15)
        trend_score = 15 if trend_aligned else 5

        # 2. Market structure (0–15)
        structure_score = 15 if structure_confirmed else 6

        # 3. Momentum & Indicators (0–15)
        momentum_score = 15 if momentum_aligned else 7

        # 4. Volatility suitability (0–10)
        volatility_score = 10 if volatility_ok else 4

        # 5. Entry quality & S/R proximity (0–15)
        entry_score = 15 if entry_quality_ok else 8

        # 6. Risk-to-reward ratio (0–15)
        if rr_ratio >= 3.0:
            rr_score = 15
        elif rr_ratio >= 2.5:
            rr_score = 13
        elif rr_ratio >= 2.0:
            rr_score = 11
        elif rr_ratio >= 1.5:
            rr_score = 8
        else:
            rr_score = 3

        # 7. News risk proximity (0–10)
        news_score = 10 if news_clear else 2

        # 8. Data freshness (0–5)
        data_score = 5 if data_fresh else 0

        # Total sum
        total_score = trend_score + structure_score + momentum_score + volatility_score + entry_score + rr_score + news_score + data_score

        # Bound score between 0 and 100
        total_score = max(0, min(100, total_score))

        if total_score >= 85:
            grade = "ELITE"
        elif total_score >= 70:
            grade = "HIGH"
        else:
            grade = "STANDARD"

        explanation = (
            f"{grade} Quality Setup ({total_score}/100) — "
            f"Trend: {trend_score}/15, Structure: {structure_score}/15, Momentum: {momentum_score}/15, "
            f"R:R ({rr_ratio}:1): {rr_score}/15, Volatility: {volatility_score}/10, Entry: {entry_score}/15, "
            f"News: {news_score}/10, Data: {data_score}/5."
        )

        return SignalQualityBreakdown(
            total_score=total_score,
            grade=grade,
            trend_score=trend_score,
            structure_score=structure_score,
            momentum_score=momentum_score,
            volatility_score=volatility_score,
            entry_score=entry_score,
            risk_reward_score=rr_score,
            news_score=news_score,
            data_quality_score=data_score,
            explanation=explanation
        )


signal_quality_scorer = SignalQualityScorer()
