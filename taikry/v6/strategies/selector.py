"""
ZYROX AI V6 — Module 3: Auto Strategy Selector
==============================================
Autonomous decision engine matching live market regime and detected technical concepts
to the highest-probability strategy in the formal registry.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from taikry.v6.models import V6MarketRegime, ConceptDetectionResult, RegimeAnalysisResult
from taikry.v6.strategies.registry import STRATEGY_REGISTRY, StrategyDefinition

logger = logging.getLogger("zyrox.v6.strategies.selector")


class StrategySelectionCandidate(BaseModel):
    """Ranked candidate strategy with explainable fitness metrics."""
    strategy_id: str
    name: str
    fit_score: int = Field(ge=0, le=100)
    regime_match: bool
    matched_concepts_count: int
    matched_concepts: List[str] = Field(default_factory=list)
    missing_concepts: List[str] = Field(default_factory=list)
    rationale: str
    strategy_definition: Dict[str, Any]


class AutoStrategySelectorResult(BaseModel):
    """Output of Auto Strategy Selector."""
    active_regime: V6MarketRegime
    top_strategy: Optional[StrategySelectionCandidate]
    ranked_candidates: List[StrategySelectionCandidate] = Field(default_factory=list)
    selection_status: str  # STRATEGY_SELECTED, NO_QUALIFIED_STRATEGY, NEWS_STANDBY, UNCERTAIN_STANDBY
    rationale: str


class AutoStrategySelector:
    """The Autonomous Strategy Selector for ZYROX AI V6."""

    def select_strategy(
        self,
        symbol: str,
        regime_result: RegimeAnalysisResult,
        detected_concepts: List[ConceptDetectionResult],
        timeframe: str = "M15"
    ) -> AutoStrategySelectorResult:
        """
        Filters and ranks strategies according to regime compatibility and concept confluences.
        """
        regime = regime_result.regime
        detected_ids = {c.concept_id for c in detected_concepts if c.detected}

        # Handle Immediate Risk Lockouts (NEWS_VOLATILITY or UNCERTAIN)
        if regime == V6MarketRegime.NEWS_VOLATILITY:
            news_strat = STRATEGY_REGISTRY["NEWS_WAIT"]
            candidate = StrategySelectionCandidate(
                strategy_id=news_strat.strategy_id,
                name=news_strat.name,
                fit_score=95,
                regime_match=True,
                matched_concepts_count=0,
                matched_concepts=[],
                missing_concepts=[],
                rationale="Macroeconomic event risk or severe volatility spike active. Standby enforced to protect capital.",
                strategy_definition=news_strat.dict()
            )
            return AutoStrategySelectorResult(
                active_regime=regime,
                top_strategy=candidate,
                ranked_candidates=[candidate],
                selection_status="NEWS_STANDBY",
                rationale="High-impact news event window active. Capital protection standing by."
            )

        if regime == V6MarketRegime.UNCERTAIN:
            standby_strat = STRATEGY_REGISTRY["NEWS_WAIT"]
            candidate = StrategySelectionCandidate(
                strategy_id=standby_strat.strategy_id,
                name=standby_strat.name,
                fit_score=60,
                regime_match=True,
                matched_concepts_count=0,
                matched_concepts=[],
                missing_concepts=[],
                rationale="Market regime is statistically uncertain with conflicting indicators. No strategy qualified.",
                strategy_definition=standby_strat.dict()
            )
            return AutoStrategySelectorResult(
                active_regime=regime,
                top_strategy=None,
                ranked_candidates=[candidate],
                selection_status="UNCERTAIN_STANDBY",
                rationale="Insufficient technical conviction to qualify a trade strategy."
            )

        # Priority ranking weights based on market regime
        priority_order: Dict[V6MarketRegime, List[str]] = {
            V6MarketRegime.TREND_BULLISH_STRONG: ["TREND_PULLBACK", "STRUCTURE_CONTINUATION", "BREAKOUT_RETEST", "EMA_PULLBACK"],
            V6MarketRegime.TREND_BULLISH_WEAK: ["TREND_PULLBACK", "EMA_PULLBACK", "STRUCTURE_CONTINUATION"],
            V6MarketRegime.TREND_BEARISH_STRONG: ["TREND_PULLBACK", "STRUCTURE_CONTINUATION", "BREAKOUT_RETEST", "EMA_PULLBACK"],
            V6MarketRegime.TREND_BEARISH_WEAK: ["TREND_PULLBACK", "EMA_PULLBACK", "STRUCTURE_CONTINUATION"],
            V6MarketRegime.RANGE: ["RANGE_SUPPORT_RESISTANCE", "LIQUIDITY_SWEEP_REVERSAL", "FALSE_BREAKOUT", "MOMENTUM_DIVERGENCE"],
            V6MarketRegime.BREAKOUT: ["BREAKOUT_CONFIRMATION", "BREAKOUT_RETEST", "VOLATILITY_EXPANSION"],
            V6MarketRegime.REVERSAL_TRANSITION: ["LIQUIDITY_SWEEP_REVERSAL", "CHOCH_REVERSAL", "MOMENTUM_DIVERGENCE", "FALSE_BREAKOUT"],
            V6MarketRegime.HIGH_VOLATILITY: ["VOLATILITY_ADJUSTED_SETUP", "LIQUIDITY_SWEEP_REVERSAL"],
            V6MarketRegime.LOW_VOLATILITY: ["COMPRESSION_BREAKOUT", "RANGE_SUPPORT_RESISTANCE"],
        }

        priorities = priority_order.get(regime, [])
        candidates: List[StrategySelectionCandidate] = []

        for strat_id, strat in STRATEGY_REGISTRY.items():
            if strat_id == "NEWS_WAIT":
                continue

            # 1. Regime compatibility check
            regime_match = regime in strat.supported_regimes
            if not regime_match:
                continue

            # 2. Concept confluence scoring
            req_concepts = strat.required_concepts
            matched = [cid for cid in req_concepts if cid in detected_ids]
            missing = [cid for cid in req_concepts if cid not in detected_ids]

            # Base fit score starts at 50 for regime match
            fit = 50

            # Priority boost (up to +25)
            if strat_id in priorities:
                idx = priorities.index(strat_id)
                fit += max(0, 25 - (idx * 5))

            # Concept confluence boost (up to +25)
            if req_concepts:
                match_ratio = len(matched) / len(req_concepts)
                fit += int(match_ratio * 25)
            else:
                fit += 10

            # Cap fit score between 0 and 100
            fit = max(0, min(100, fit))

            rationale_parts = []
            if strat_id in priorities:
                rationale_parts.append(f"High-priority setup for {regime.value}.")
            if matched:
                rationale_parts.append(f"Supported by {len(matched)} live concepts: {', '.join(matched[:3])}.")
            if missing and len(missing) <= 2:
                rationale_parts.append(f"Awaiting final trigger confirmation on: {', '.join(missing)}.")

            candidates.append(StrategySelectionCandidate(
                strategy_id=strat_id,
                name=strat.name,
                fit_score=fit,
                regime_match=True,
                matched_concepts_count=len(matched),
                matched_concepts=matched,
                missing_concepts=missing,
                rationale=" ".join(rationale_parts) or f"Matches {regime.value} conditions.",
                strategy_definition=strat.model_dump()
            ))

        # Sort candidates descending by fit score and matched concepts
        candidates.sort(key=lambda c: (c.fit_score, c.matched_concepts_count), reverse=True)

        if not candidates or candidates[0].fit_score < 60:
            return AutoStrategySelectorResult(
                active_regime=regime,
                top_strategy=None,
                ranked_candidates=candidates,
                selection_status="NO_QUALIFIED_STRATEGY",
                rationale=f"No strategy in the registry met the minimum confluence threshold (60%) for {regime.value}."
            )

        top = candidates[0]
        return AutoStrategySelectorResult(
            active_regime=regime,
            top_strategy=top,
            ranked_candidates=candidates,
            selection_status="STRATEGY_SELECTED",
            rationale=f"Selected {top.name} with {top.fit_score}% regime and concept fitness."
        )


v6_strategy_selector = AutoStrategySelector()
