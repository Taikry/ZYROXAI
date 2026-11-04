"""
ZYROX AI V6 — All Concepts Library Coordinator
==============================================
Orchestrates deterministic concept detectors across all 10 categories (A through J).
"""
from __future__ import annotations

from typing import List, Dict, Any, Optional
import pandas as pd

from taikry.v6.models import ConceptCategory, ConceptDetectionResult
from taikry.v6.concepts.structure import MarketStructureDetector
from taikry.v6.concepts.liquidity import LiquidityDetector
from taikry.v6.concepts.imbalance import ImbalanceDetector
from taikry.v6.concepts.orderflow import OrderFlowZonesDetector
from taikry.v6.concepts.levels import SupportResistanceDetector
from taikry.v6.concepts.price_action import PriceActionDetector
from taikry.v6.concepts.trend import TrendToolsDetector
from taikry.v6.concepts.momentum import MomentumDetector
from taikry.v6.concepts.volatility import VolatilityDetector
from taikry.v6.concepts.sessions import SessionConceptsDetector


class V6ConceptsCoordinator:
    """Coordinates detection across all 10 modular concept categories."""

    def __init__(self):
        self.detectors = [
            MarketStructureDetector(),      # Category A
            LiquidityDetector(),            # Category B
            ImbalanceDetector(),            # Category C
            OrderFlowZonesDetector(),       # Category D
            SupportResistanceDetector(),    # Category E
            PriceActionDetector(),          # Category F
            TrendToolsDetector(),           # Category G
            MomentumDetector(),             # Category H
            VolatilityDetector(),           # Category I
            SessionConceptsDetector(),      # Category J
        ]

    def detect_all(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        """Runs all 10 modular concept detectors against candle data."""
        all_concepts: List[ConceptDetectionResult] = []
        if df is None or len(df) < 5:
            return all_concepts

        for det in self.detectors:
            try:
                res = det.detect(df, timeframe=timeframe)
                all_concepts.extend(res)
            except Exception as exc:
                # Individual detector failure must never crash the entire analysis
                continue

        return all_concepts

    def group_by_category(self, concepts: List[ConceptDetectionResult]) -> Dict[str, List[Dict[str, Any]]]:
        """Groups concepts into Categories A through J for UI Concept Explorer."""
        grouped: Dict[str, List[Dict[str, Any]]] = {
            cat.value: [] for cat in ConceptCategory
        }
        for c in concepts:
            cat_key = c.category.value
            if cat_key in grouped:
                grouped[cat_key].append(c.model_dump())
        return grouped


v6_concepts_engine = V6ConceptsCoordinator()
