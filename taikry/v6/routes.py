"""
ZYROX AI V6 — Module 18: RESTful API Endpoints
==============================================
Mounted under `/api/v6/*`:
- POST /api/v6/regime/analyze
- POST /api/v6/concepts/detect
- POST /api/v6/strategy/select
- POST /api/v6/best-setup
- POST /api/v6/scan
- GET  /api/v6/concepts/{analysis_id}
- GET  /api/v6/setups/{setup_id}
- GET  /api/v6/chart-overlays/{analysis_id}
- GET  /api/v6/strategies
- GET  /api/v6/learning/stats
"""
from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request
from pydantic import BaseModel, Field

from taikry.data.providers import market_data_engine
from taikry.database.session import SessionLocal
from taikry.v6.models import V6MarketRegime, RegimeAnalysisResult, BestSetupResult
from taikry.v6.regime import v6_regime_engine
from taikry.v6.concepts.detector import v6_concepts_engine
from taikry.v6.strategies.registry import STRATEGY_REGISTRY
from taikry.v6.strategies.selector import v6_strategy_selector
from taikry.v6.service import v6_intelligence_service
from taikry.v6.scanner import v6_scanner, MarketScanResult
from taikry.v6.auto_learning import v6_auto_learning_engine
from taikry.v6.db_models import V6RegimeResultModel, V6ConceptDetectionModel, V6BestSetupModel

router = APIRouter(prefix="/api/v6", tags=["ZYROX AI V6 Intelligence"])

# In-memory fast cache for analysis sessions & chart overlays
_ANALYSIS_SESSIONS: Dict[str, Dict[str, Any]] = {}


class AnalyzeRegimeRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M15"


class DetectConceptsRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M15"


class SelectStrategyRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M15"


class BestSetupRequest(BaseModel):
    symbol: str = "XAUUSD"
    timeframe: str = "M15"
    custom_weights: Optional[Dict[str, int]] = None


class MarketScanRequest(BaseModel):
    market_filter: str = "ALL"  # FOREX, XAUUSD, CRYPTO, ALL
    timeframe: str = "M15"
    min_quality_score: int = 55
    max_symbols: int = 15


@router.post("/regime/analyze", response_model=RegimeAnalysisResult)
def analyze_market_regime(req: AnalyzeRegimeRequest):
    """Classifies live market into one of the 11 canonical regimes."""
    df = market_data_engine.get_candles(req.symbol, req.timeframe, limit=100)
    res = v6_regime_engine.analyze_regime(req.symbol, df, timeframe=req.timeframe)

    # Persist log asynchronously / safe DB write
    try:
        db = SessionLocal()
        try:
            db.add(V6RegimeResultModel(
                symbol=req.symbol.upper(),
                timeframe=req.timeframe.upper(),
                regime=res.regime.value,
                strength=res.strength,
                evidence=res.evidence,
                metrics=res.metrics,
                data_quality=res.data_quality
            ))
            db.commit()
        finally:
            db.close()
    except Exception:
        pass

    return res


@router.post("/concepts/detect")
def detect_technical_concepts(req: DetectConceptsRequest):
    """Detects concepts across all 10 categories (A through J)."""
    df = market_data_engine.get_candles(req.symbol, req.timeframe, limit=100)
    concepts = v6_concepts_engine.detect_all(df, timeframe=req.timeframe)
    by_category = v6_concepts_engine.group_by_category(concepts)

    analysis_id = f"AN-{uuid.uuid4().hex[:10].upper()}"
    _ANALYSIS_SESSIONS[analysis_id] = {
        "analysis_id": analysis_id,
        "symbol": req.symbol.upper(),
        "timeframe": req.timeframe,
        "concepts": [c.model_dump() for c in concepts],
        "by_category": by_category,
        "chart_overlays": [c.chart_overlay for c in concepts if c.chart_overlay]
    }

    # Save to database
    try:
        db = SessionLocal()
        try:
            for c in concepts:
                if c.detected:
                    db.add(V6ConceptDetectionModel(
                        analysis_id=analysis_id,
                        symbol=req.symbol.upper(),
                        timeframe=req.timeframe.upper(),
                        category=c.category.value,
                        concept_id=c.concept_id,
                        name=c.name,
                        confidence=c.confidence,
                        bias=c.bias,
                        levels=c.levels,
                        evidence=c.evidence,
                        chart_overlay=c.chart_overlay
                    ))
            db.commit()
        finally:
            db.close()
    except Exception:
        pass

    return {
        "analysis_id": analysis_id,
        "symbol": req.symbol.upper(),
        "timeframe": req.timeframe,
        "concepts_count": len(concepts),
        "detected_count": len([c for c in concepts if c.detected]),
        "concepts": [c.model_dump() for c in concepts],
        "by_category": by_category
    }


@router.post("/strategy/select")
def select_strategy(req: SelectStrategyRequest):
    """Selects high-probability strategy matching live regime and concepts."""
    df = market_data_engine.get_candles(req.symbol, req.timeframe, limit=100)
    regime_res = v6_regime_engine.analyze_regime(req.symbol, df, timeframe=req.timeframe)
    concepts = v6_concepts_engine.detect_all(df, timeframe=req.timeframe)

    selection = v6_strategy_selector.select_strategy(
        symbol=req.symbol.upper(),
        regime_result=regime_res,
        detected_concepts=concepts,
        timeframe=req.timeframe
    )
    return selection.model_dump()


@router.post("/best-setup", response_model=BestSetupResult)
def get_best_setup(req: BestSetupRequest, request: Request):
    """
    Executes master V6 pipeline:
    Regime -> Concepts -> Strategy Selection -> Quality Scoring -> Trade Levels -> AI Review -> Risk Arbiter.
    """
    user_id = getattr(request.state, "user_id", None) if hasattr(request, "state") else None
    setup = v6_intelligence_service.analyze_best_setup(
        symbol=req.symbol.upper(),
        timeframe=req.timeframe,
        user_id=user_id,
        custom_weights=req.custom_weights
    )

    # Persist Best Setup to database
    try:
        db = SessionLocal()
        try:
            db.add(V6BestSetupModel(
                setup_id=setup.setup_id,
                user_id=user_id,
                symbol=setup.symbol,
                timeframe=setup.timeframe,
                direction=setup.direction,
                regime=setup.regime.value,
                strategy_id=setup.strategy.get("strategy_id"),
                strategy_name=setup.strategy.get("name"),
                quality_score=setup.quality_score.total_score,
                quality_classification=setup.quality_score.classification,
                entry_type=setup.trade_plan.entry_type,
                entry_price=setup.trade_plan.entry_price,
                stop_loss=setup.trade_plan.stop_loss,
                stop_distance=setup.trade_plan.stop_distance,
                invalidation_reason=setup.trade_plan.invalidation_reason,
                tp1=setup.trade_plan.tp1,
                tp1_r=setup.trade_plan.tp1_r,
                tp2=setup.trade_plan.tp2,
                tp2_r=setup.trade_plan.tp2_r,
                tp3=setup.trade_plan.tp3,
                tp3_r=setup.trade_plan.tp3_r,
                risk_reward_ratio=setup.trade_plan.risk_reward_ratio,
                trade_plan_json=setup.trade_plan.model_dump(),
                quality_score_json=setup.quality_score.model_dump(),
                mtf_status_json=setup.multi_timeframe_status,
                ai_review_json=setup.ai_review,
                risk_manager_json=setup.risk_manager,
                why_this_setup=setup.why_this_setup
            ))
            db.commit()
        finally:
            db.close()
    except Exception:
        pass

    return setup


@router.post("/scan", response_model=MarketScanResult)
def scan_markets(req: MarketScanRequest):
    """Performs multi-market screening across Forex, Metals, Crypto, or All."""
    res = v6_scanner.scan_markets(
        market_filter=req.market_filter,
        timeframe=req.timeframe,
        min_quality_score=req.min_quality_score,
        max_symbols=req.max_symbols
    )
    return res


@router.get("/concepts/{analysis_id}")
def get_concepts_by_id(analysis_id: str):
    """Retrieves concepts associated with an analysis ID."""
    if analysis_id in _ANALYSIS_SESSIONS:
        return _ANALYSIS_SESSIONS[analysis_id]

    # Query DB fallback
    db = SessionLocal()
    try:
        rows = db.query(V6ConceptDetectionModel).filter_by(analysis_id=analysis_id).all()
        if not rows:
            raise HTTPException(status_code=404, detail=f"Analysis session {analysis_id} not found.")
        return {
            "analysis_id": analysis_id,
            "symbol": rows[0].symbol,
            "timeframe": rows[0].timeframe,
            "detected_count": len(rows),
            "concepts": [
                {
                    "concept_id": r.concept_id,
                    "name": r.name,
                    "category": r.category,
                    "confidence": r.confidence,
                    "bias": r.bias,
                    "levels": r.levels,
                    "evidence": r.evidence,
                    "chart_overlay": r.chart_overlay
                }
                for r in rows
            ]
        }
    finally:
        db.close()


@router.get("/setups/{setup_id}")
def get_setup_by_id(setup_id: str):
    """Retrieves a specific setup record by ID."""
    db = SessionLocal()
    try:
        row = db.query(V6BestSetupModel).filter_by(setup_id=setup_id).first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Setup {setup_id} not found.")
        return {
            "setup_id": row.setup_id,
            "symbol": row.symbol,
            "timeframe": row.timeframe,
            "direction": row.direction,
            "regime": row.regime,
            "strategy": {"strategy_id": row.strategy_id, "name": row.strategy_name},
            "quality_score": row.quality_score_json,
            "trade_plan": row.trade_plan_json,
            "mtf_status": row.mtf_status_json,
            "ai_review": row.ai_review_json,
            "risk_manager": row.risk_manager_json,
            "why_this_setup": row.why_this_setup,
            "created_at": row.created_at.isoformat()
        }
    finally:
        db.close()


@router.get("/chart-overlays/{analysis_id}")
def get_chart_overlays(analysis_id: str):
    """Returns visual chart overlay elements for Lightweight Charts."""
    if analysis_id in _ANALYSIS_SESSIONS:
        return {"analysis_id": analysis_id, "overlays": _ANALYSIS_SESSIONS[analysis_id].get("chart_overlays", [])}
    return {"analysis_id": analysis_id, "overlays": []}


@router.get("/strategies")
def list_strategy_registry():
    """Returns the full 14-strategy catalog and execution contracts."""
    return {
        "total_strategies": len(STRATEGY_REGISTRY),
        "strategies": [s.model_dump() for s in STRATEGY_REGISTRY.values()]
    }


@router.get("/best-concept")
def get_best_concept(symbol: str = "XAUUSD", timeframe: str = "M15"):
    """Module 5: Returns the single top qualified concept for the given symbol."""
    return v6_intelligence_service.get_best_concept_now(symbol=symbol.upper(), timeframe=timeframe)


@router.get("/learning/stats")
def get_learning_stats(strategy_id: str = "TREND_PULLBACK", mode: str = "DEMO"):
    """Returns Shadow Mode & performance accounting stats for a strategy."""
    return v6_auto_learning_engine.get_performance_summary(strategy_id=strategy_id, mode=mode)
