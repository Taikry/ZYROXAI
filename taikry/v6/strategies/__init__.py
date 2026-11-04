"""
ZYROX AI V6 — Strategy Engine Package
=====================================
Formal Strategy Registry and Auto Strategy Selector.
"""
from taikry.v6.strategies.registry import STRATEGY_REGISTRY, StrategyDefinition
from taikry.v6.strategies.selector import v6_strategy_selector, AutoStrategySelector, StrategySelectionCandidate, AutoStrategySelectorResult

__all__ = [
    "STRATEGY_REGISTRY",
    "StrategyDefinition",
    "v6_strategy_selector",
    "AutoStrategySelector",
    "StrategySelectionCandidate",
    "AutoStrategySelectorResult"
]

