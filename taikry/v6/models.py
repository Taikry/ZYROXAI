"""
ZYROX AI V6 — Core Data Models & Type Contracts
================================================
Defines strict Pydantic schemas and enums for:
- 11-State Market Regimes
- 10-Category Concepts Library (Categories A through J)
- Strategy Registry & Auto Selector
- Explainable Setup Quality Scoring (0–100 scale)
- Trade Levels (Entry, Invalidation Smart SL, Multi-Target TP1/TP2/TP3)
"""
from __future__ import annotations

import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class V6MarketRegime(str, enum.Enum):
    """The 11 canonical V6 market regimes."""
    TREND_BULLISH_STRONG = "TREND_BULLISH_STRONG"
    TREND_BULLISH_WEAK = "TREND_BULLISH_WEAK"
    TREND_BEARISH_STRONG = "TREND_BEARISH_STRONG"
    TREND_BEARISH_WEAK = "TREND_BEARISH_WEAK"
    RANGE = "RANGE"
    BREAKOUT = "BREAKOUT"
    REVERSAL_TRANSITION = "REVERSAL_TRANSITION"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    NEWS_VOLATILITY = "NEWS_VOLATILITY"
    UNCERTAIN = "UNCERTAIN"


class RegimeAnalysisResult(BaseModel):
    """Result of deterministic market regime detection."""
    regime: V6MarketRegime
    strength: int = Field(ge=0, le=100, description="Confidence/strength score 0-100")
    evidence: List[str] = Field(default_factory=list)
    timeframe: str = "M15"
    timestamp: str = ""
    data_quality: str = "SUFFICIENT"
    metrics: Dict[str, Any] = Field(default_factory=dict)


class ConceptCategory(str, enum.Enum):
    """The 10 modular concept categories (Categories A through J)."""
    MARKET_STRUCTURE = "MARKET_STRUCTURE"       # Cat A
    SMART_MONEY_LIQUIDITY = "SMART_MONEY_LIQUIDITY" # Cat B
    IMBALANCE = "IMBALANCE"                     # Cat C
    ORDER_FLOW_ZONES = "ORDER_FLOW_ZONES"       # Cat D
    SUPPORT_RESISTANCE = "SUPPORT_RESISTANCE"   # Cat E
    PRICE_ACTION = "PRICE_ACTION"               # Cat F
    TREND_TOOLS = "TREND_TOOLS"                 # Cat G
    MOMENTUM = "MOMENTUM"                       # Cat H
    VOLATILITY = "VOLATILITY"                   # Cat I
    SESSION_CONCEPTS = "SESSION_CONCEPTS"       # Cat J


class ConceptDetectionResult(BaseModel):
    """Standardized representation of any detected technical concept."""
    concept_id: str
    name: str
    category: ConceptCategory
    detected: bool = False
    confidence: int = Field(default=0, ge=0, le=100)
    bias: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
    timeframe: str = "M15"
    levels: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[str] = Field(default_factory=list)
    chart_overlay: Optional[Dict[str, Any]] = None


class SetupQualityScore(BaseModel):
    """
    Granular 0-100 setup quality score rubric:
    - Market Regime Fit (0–20)
    - Higher Timeframe Alignment (0–20)
    - Structure Confirmation (0–20)
    - Concept Quality (0–15)
    - Volatility Suitability (0–10)
    - Risk/Reward (0–10)
    - News Risk (0–5)
    """
    total_score: int = Field(ge=0, le=100)
    classification: str = "WATCHLIST"  # HIGH_QUALITY (85-100), VALID_SETUP (70-84), WATCHLIST (55-69), REJECTED (<55)
    regime_fit_score: int = 0
    htf_alignment_score: int = 0
    structure_confirmation_score: int = 0
    concept_quality_score: int = 0
    volatility_suitability_score: int = 0
    risk_reward_score: int = 0
    news_risk_score: int = 0
    explanation: str = ""
    disclaimer: str = "Internal confluence metric, not a probability of profit or guarantee."


class TradePlanLevels(BaseModel):
    """Calculated, technically justified trade entry, invalidation SL, and multi-target TPs."""
    direction: str = "WAIT"  # BUY, SELL, WAIT, NO_TRADE
    entry_type: str = "MARKET"  # MARKET, LIMIT, ENTRY_ZONE
    entry_price: Optional[float] = None
    entry_zone_low: Optional[float] = None
    entry_zone_high: Optional[float] = None
    entry_trigger: str = ""
    stop_loss: Optional[float] = None
    stop_distance: Optional[float] = None
    invalidation_reason: str = ""
    tp1: Optional[float] = None
    tp1_reason: Optional[str] = None
    tp1_r: Optional[float] = None
    tp2: Optional[float] = None
    tp2_reason: Optional[str] = None
    tp2_r: Optional[float] = None
    tp3: Optional[float] = None
    tp3_reason: Optional[str] = None
    tp3_r: Optional[float] = None
    risk_reward_ratio: Optional[str] = None


class BestSetupResult(BaseModel):
    """Final unified output for ZYROX AI V6 Best Setup & Analysis Center."""
    setup_id: str
    symbol: str
    timeframe: str
    direction: str  # STRONG_BUY, BUY, WAIT, SELL, STRONG_SELL, NO_TRADE
    regime: V6MarketRegime
    strategy: Dict[str, Any]
    concept: Dict[str, Any]
    trade_plan: TradePlanLevels
    quality_score: SetupQualityScore
    multi_timeframe_status: Dict[str, Any]
    ai_review: Dict[str, Any]
    risk_manager: Dict[str, Any]
    why_this_setup: List[str]
    timestamp: str

