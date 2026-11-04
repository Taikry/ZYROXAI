"""
ZYROX AI V6 — Module 6: Setup Quality Scoring Engine
====================================================
Computes an explainable 0–100 setup quality score from 7 structural dimensions:
1. Market Regime Fit (0–20)
2. Higher Timeframe Alignment (0–20)
3. Structure Confirmation (0–20)
4. Concept Quality & Freshness (0–15)
5. Volatility Suitability (0–10)
6. Risk-to-Reward Potential (0–10)
7. News Risk Proximity (0–5)

Classification Tiers:
- 85–100: HIGH QUALITY
- 70–84: VALID SETUP
- 55–69: WATCHLIST
- Below 55: REJECTED

Explicitly disclaimed: Internal setup confluence metric, not a probability of profit or guarantee.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, Optional
from taikry.v6.models import SetupQualityScore, V6MarketRegime

logger = logging.getLogger("zyrox.v6.scoring")


class SetupQualityScorer:
    """Calculates granular, transparent 7-factor setup quality scores."""

    def score_setup(
        self,
        regime: V6MarketRegime,
        strategy_id: Optional[str],
        htf_alignment: str = "FULL_ALIGNMENT",  # FULL_ALIGNMENT, PARTIAL_ALIGNMENT, CONFLICT
        has_bos_choch: bool = True,
        concepts_count: int = 3,
        volatility_ok: bool = True,
        rr_ratio: float = 2.0,
        news_clear: bool = True,
        custom_weights: Optional[Dict[str, int]] = None
    ) -> SetupQualityScore:
        """Computes 0-100 rubric factor-by-factor."""
        w = custom_weights or {}

        # 1. Market Regime Fit (0–20)
        max_regime = w.get("max_regime", 20)
        if regime in (V6MarketRegime.TREND_BULLISH_STRONG, V6MarketRegime.TREND_BEARISH_STRONG, V6MarketRegime.BREAKOUT):
            regime_fit = max_regime
        elif regime in (V6MarketRegime.RANGE, V6MarketRegime.REVERSAL_TRANSITION):
            regime_fit = int(max_regime * 0.85)
        elif regime in (V6MarketRegime.TREND_BULLISH_WEAK, V6MarketRegime.TREND_BEARISH_WEAK, V6MarketRegime.LOW_VOLATILITY):
            regime_fit = int(max_regime * 0.70)
        elif regime == V6MarketRegime.HIGH_VOLATILITY:
            regime_fit = int(max_regime * 0.50)
        else:  # NEWS_VOLATILITY or UNCERTAIN
            regime_fit = 0

        # 2. Higher Timeframe Alignment (0–20)
        max_htf = w.get("max_htf", 20)
        if htf_alignment == "FULL_ALIGNMENT":
            htf_score = max_htf
        elif htf_alignment == "PARTIAL_ALIGNMENT":
            htf_score = int(max_htf * 0.65)
        else:
            htf_score = 4

        # 3. Structure Confirmation (0–20)
        max_struct = w.get("max_struct", 20)
        struct_score = max_struct if has_bos_choch else int(max_struct * 0.40)

        # 4. Concept Quality & Confluence (0–15)
        max_concept = w.get("max_concept", 15)
        if concepts_count >= 4:
            concept_score = max_concept
        elif concepts_count >= 2:
            concept_score = int(max_concept * 0.80)
        elif concepts_count == 1:
            concept_score = int(max_concept * 0.50)
        else:
            concept_score = 0

        # 5. Volatility Suitability (0–10)
        max_vol = w.get("max_vol", 10)
        vol_score = max_vol if volatility_ok else 3

        # 6. Risk-to-Reward Ratio (0–10)
        max_rr = w.get("max_rr", 10)
        if rr_ratio >= 3.0:
            rr_score = max_rr
        elif rr_ratio >= 2.0:
            rr_score = int(max_rr * 0.85)
        elif rr_ratio >= 1.5:
            rr_score = int(max_rr * 0.60)
        else:
            rr_score = 2

        # 7. News Risk Proximity (0–5)
        max_news = w.get("max_news", 5)
        news_score = max_news if news_clear else 0

        total = regime_fit + htf_score + struct_score + concept_score + vol_score + rr_score + news_score
        total = max(0, min(100, total))

        if total >= 85:
            classification = "HIGH_QUALITY"
        elif total >= 70:
            classification = "VALID_SETUP"
        elif total >= 55:
            classification = "WATCHLIST"
        else:
            classification = "REJECTED"

        explanation = (
            f"{classification} Setup ({total}/100) — "
            f"Regime: {regime_fit}/20, HTF: {htf_score}/20, Structure: {struct_score}/20, "
            f"Concepts ({concepts_count}): {concept_score}/15, Volatility: {vol_score}/10, "
            f"R:R ({rr_ratio:.2f}:1): {rr_score}/10, News: {news_score}/5."
        )

        return SetupQualityScore(
            total_score=total,
            classification=classification,
            regime_fit_score=regime_fit,
            htf_alignment_score=htf_score,
            structure_confirmation_score=struct_score,
            concept_quality_score=concept_score,
            volatility_suitability_score=vol_score,
            risk_reward_score=rr_score,
            news_risk_score=news_score,
            explanation=explanation
        )


v6_quality_scorer = SetupQualityScorer()

