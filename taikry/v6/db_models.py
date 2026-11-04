"""
ZYROX AI V6 — Module 19: Database Persistence Models
====================================================
SQLAlchemy 2.0 models for V6 Technical Intelligence persistence:
- v6_regime_results: Immutable log of regime classifications.
- v6_concept_detections: Detected technical concepts with level coordinates and evidence.
- v6_strategy_runs: Strategy selection records and confluence criteria.
- v6_best_setups: Best setup audit records with full entry, SL, TP1-3, and AI reviews.
"""
from __future__ import annotations

import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, JSON, ForeignKey, Index
)
from taikry.database.session import Base


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


class V6RegimeResultModel(Base):
    """Audit ledger for V6 market regime classifications."""
    __tablename__ = "v6_regime_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), index=True, nullable=False)
    timeframe = Column(String(16), index=True, nullable=False)
    regime = Column(String(40), index=True, nullable=False)
    strength = Column(Integer, nullable=False, default=50)
    evidence = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    data_quality = Column(String(32), default="SUFFICIENT")
    created_at = Column(DateTime, default=_utc_now, index=True, nullable=False)


class V6ConceptDetectionModel(Base):
    """Audit ledger for detected technical concepts across Categories A through J."""
    __tablename__ = "v6_concept_detections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(64), index=True, nullable=False)
    symbol = Column(String(32), index=True, nullable=False)
    timeframe = Column(String(16), nullable=False)
    category = Column(String(40), index=True, nullable=False)
    concept_id = Column(String(64), index=True, nullable=False)
    name = Column(String(128), nullable=False)
    confidence = Column(Integer, nullable=False, default=50)
    bias = Column(String(20), nullable=False, default="NEUTRAL")
    levels = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
    chart_overlay = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utc_now, index=True, nullable=False)


class V6BestSetupModel(Base):
    """Persistent ledger for ZYROX AI V6 Best Setup calculations."""
    __tablename__ = "v6_best_setups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    setup_id = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    symbol = Column(String(32), index=True, nullable=False)
    timeframe = Column(String(16), nullable=False)
    direction = Column(String(24), index=True, nullable=False)
    regime = Column(String(40), index=True, nullable=False)
    strategy_id = Column(String(64), index=True, nullable=True)
    strategy_name = Column(String(128), nullable=True)
    quality_score = Column(Integer, nullable=False, default=50)
    quality_classification = Column(String(32), nullable=False, default="WATCHLIST")
    entry_type = Column(String(24), default="MARKET")
    entry_price = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    stop_distance = Column(Float, nullable=True)
    invalidation_reason = Column(Text, nullable=True)
    tp1 = Column(Float, nullable=True)
    tp1_r = Column(Float, nullable=True)
    tp2 = Column(Float, nullable=True)
    tp2_r = Column(Float, nullable=True)
    tp3 = Column(Float, nullable=True)
    tp3_r = Column(Float, nullable=True)
    risk_reward_ratio = Column(String(20), nullable=True)
    trade_plan_json = Column(JSON, nullable=True)
    quality_score_json = Column(JSON, nullable=True)
    mtf_status_json = Column(JSON, nullable=True)
    ai_review_json = Column(JSON, nullable=True)
    risk_manager_json = Column(JSON, nullable=True)
    why_this_setup = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utc_now, index=True, nullable=False)

