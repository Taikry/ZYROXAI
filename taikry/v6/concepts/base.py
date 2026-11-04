"""
ZYROX AI V6 — Base Concept Detector Contract
============================================
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd

from taikry.v6.models import ConceptDetectionResult, ConceptCategory


class BaseConceptDetector(ABC):
    """Abstract base class for all V6 technical concept detectors."""

    @property
    @abstractmethod
    def category(self) -> ConceptCategory:
        """The concept category (Categories A through J)."""
        pass

    @abstractmethod
    def detect(self, df: pd.DataFrame, timeframe: str = "M15") -> List[ConceptDetectionResult]:
        """Runs deterministic detection on candle dataset and returns qualified concept results."""
        pass

