"""
ZYROX AI — Advanced Risk Intelligence V3 Models & Data Contracts
================================================================
Defines database persistence models, enumerations, and Pydantic schemas
for unified multi-market risk governance, regime detection, and capital protection.
"""
from __future__ import annotations

import datetime
import enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON, Enum as SAEnum
)

from taikry.database.session import Base
from taikry.config import (
    INITIAL_PAPER_BALANCE,
    RISK_PER_TRADE_PERCENT,
    MIN_RISK_REWARD_RATIO,
    MAX_DAILY_LOSS_PERCENT,
    MAX_SIMULTANEOUS_POSITIONS,
)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class RiskDecision(str, enum.Enum):
    """The four canonical V3 institutional risk decisions."""
    APPROVED = "APPROVED"
    APPROVED_WITH_REDUCED_RISK = "APPROVED_WITH_REDUCED_RISK"
    WAIT_FOR_CONFIRMATION = "WAIT_FOR_CONFIRMATION"
    REJECTED = "REJECTED"


class MarketRegimeType(str, enum.Enum):
    """The eight canonical V3 market regimes."""
    STRONG_TREND = "STRONG_TREND"
    WEAK_TREND = "WEAK_TREND"
    RANGE = "RANGE"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    BREAKOUT = "BREAKOUT"
    REVERSAL = "REVERSAL"
    UNCERTAIN = "UNCERTAIN"


class NewsFilterMode(str, enum.Enum):
    """News protection window mode."""
    STRICT = "STRICT"      # 60m pre/post blackout + medium events
    STANDARD = "STANDARD"  # 30m pre/post high-impact blackout
    FLEXIBLE = "FLEXIBLE"  # 15m buffer, scalp mode active
    OFF = "OFF"            # Advisory warning only, zero lockout


# =============================================================================
# SQLALCHEMY ORM PERSISTENCE MODELS
# =============================================================================

class UserRiskSettings(Base):
    """
    User-configurable capital protection and risk management preferences.
    Can be per-user or default system-wide profile.
    """
    __tablename__ = "user_risk_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    risk_mode = Column(String(32), default="BALANCED", nullable=False)  # CONSERVATIVE, BALANCED, AGGRESSIVE, CUSTOM
    risk_per_trade_percent = Column(Float, default=RISK_PER_TRADE_PERCENT, nullable=False)
    min_risk_reward_ratio = Column(Float, default=MIN_RISK_REWARD_RATIO, nullable=False)
    max_daily_loss_percent = Column(Float, default=MAX_DAILY_LOSS_PERCENT, nullable=False)
    max_weekly_loss_percent = Column(Float, default=5.0, nullable=False)
    max_monthly_loss_percent = Column(Float, default=10.0, nullable=False)
    max_drawdown_percent = Column(Float, default=8.0, nullable=False)
    max_simultaneous_positions = Column(Integer, default=MAX_SIMULTANEOUS_POSITIONS, nullable=False)
    max_portfolio_risk_percent = Column(Float, default=5.0, nullable=False)
    max_correlated_positions = Column(Integer, default=2, nullable=False)
    news_filter_mode = Column(String(32), default="STANDARD", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)


class RiskAssessmentLog(Base):
    """
    Immutable institutional audit log for every risk assessment evaluated by
    manual analysis, 24/7 background scanner, Telegram dispatch, or paper trader.
    """
    __tablename__ = "risk_assessment_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=True, index=True)
    symbol = Column(String(32), nullable=False, index=True)
    direction = Column(String(16), nullable=False)  # BUY, SELL, NONE
    entry_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit_1 = Column(Float, nullable=True)
    take_profit_2 = Column(Float, nullable=True)
    calculated_rr = Column(String(16), nullable=True)
    decision = Column(String(32), nullable=False, index=True)  # RiskDecision
    risk_mode = Column(String(32), default="BALANCED", nullable=False)
    risk_percentage = Column(Float, nullable=False)
    account_equity = Column(Float, nullable=False)
    risk_amount_usd = Column(Float, nullable=False)
    recommended_lots = Column(Float, default=0.01, nullable=False)
    quality_score = Column(Integer, default=0, nullable=False)  # 0 to 100
    market_regime = Column(String(32), default="UNCERTAIN", nullable=False)
    news_status = Column(String(32), default="CLEAR", nullable=False)
    portfolio_risk_pct = Column(Float, default=0.0, nullable=False)
    veto_reasons = Column(JSON, default=list, nullable=False)
    advisory_notes = Column(JSON, default=list, nullable=False)
    validation_details = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)


# =============================================================================
# PYDANTIC DATA TRANSFER OBJECTS (SCHEMAS)
# =============================================================================

class SizingCalculation(BaseModel):
    account_equity: float
    risk_percentage: float
    risk_amount_usd: float
    stop_distance: float
    lot_size: float
    is_reduced_risk: bool = False
    reduced_reason: Optional[str] = None


class SignalQualityBreakdown(BaseModel):
    total_score: int = Field(ge=0, le=100)
    grade: str  # STANDARD, HIGH, ELITE
    trend_score: int = Field(ge=0, le=15)
    structure_score: int = Field(ge=0, le=15)
    momentum_score: int = Field(ge=0, le=15)
    volatility_score: int = Field(ge=0, le=10)
    entry_score: int = Field(ge=0, le=15)
    risk_reward_score: int = Field(ge=0, le=15)
    news_score: int = Field(ge=0, le=10)
    data_quality_score: int = Field(ge=0, le=5)
    explanation: str
    disclaimer: str = (
        "Internal setup confluence metric derived from 8 validated structural and quantitative factors. "
        "Not a probability of profit or guarantee of financial return."
    )


class RegimeClassificationResult(BaseModel):
    regime: MarketRegimeType
    volatility_state: str  # LOW_VOLATILITY, NORMAL, HIGH_VOLATILITY
    hurst_exponent: float
    adx_value: float
    atr_14: float
    bb_width_pct: float
    evidence: List[str]
    is_confirmed: bool
    rationale: str


class NewsRiskAssessment(BaseModel):
    news_status: str  # CLEAR, BLACKOUT_ACTIVE, ADVISORY_APPROACHING, FEED_UNAVAILABLE
    event_name: Optional[str] = None
    scheduled_time_utc: Optional[str] = None
    scheduled_time_local: Optional[str] = None
    currency: Optional[str] = None
    impact_level: Optional[str] = None
    minutes_until_event: Optional[float] = None
    pre_event_window_minutes: int = 30
    post_event_window_minutes: int = 15
    is_blackout: bool = False
    source_name: str = "FairEconomy / ForexFactory"
    source_freshness: str = "LIVE_FRESH"
    disclaimer: str = "Economic calendar feeds are third-party indicative. Real releases may experience spread blowouts."


class PortfolioExposureSummary(BaseModel):
    total_open_positions: int
    total_allocated_risk_pct: float
    max_portfolio_risk_pct: float
    is_capacity_available: bool
    net_usd_exposure: float
    net_crypto_exposure: float
    net_metal_exposure: float
    active_symbols: List[str]
    correlated_group_counts: Dict[str, int]
    drawdown_pct: float
    is_drawdown_limit_breached: bool
    warnings: List[str]


class RiskAssessmentResult(BaseModel):
    """The canonical V3 risk assessment output returned to all system consumers."""
    assessment_id: str
    symbol: str
    direction: str
    decision: RiskDecision
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit_1: Optional[float] = None
    take_profit_2: Optional[float] = None
    calculated_rr: Optional[str] = None
    min_required_rr: float
    risk_mode: str
    sizing: SizingCalculation
    regime: RegimeClassificationResult
    news: NewsRiskAssessment
    portfolio: PortfolioExposureSummary
    quality: SignalQualityBreakdown
    veto_reasons: List[str]
    advisory_notes: List[str]
    timestamp_utc: str
    timestamp_local: str
    can_execute_paper: bool
    can_publish_telegram: bool
