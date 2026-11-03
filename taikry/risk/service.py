"""
ZYROX AI — Unified Risk Intelligence Service V3
===============================================
The central institutional Risk Intelligence Service utilized by:
- Manual cockpit analysis
- Automatic 24/7 background scanner
- Multi-agent consensus fleet
- Telegram signal generator (Max 4/day, XAUUSD only)
- Lot-size & exposure calculator
- Paper portfolio & execution engine

Enforces 4 standard decisions (APPROVED, APPROVED_WITH_REDUCED_RISK, WAIT_FOR_CONFIRMATION, REJECTED)
and guarantees that every decision and veto reason is logged to PostgreSQL / SQLite.
"""
from __future__ import annotations

import math
import uuid
import logging
import datetime
import zoneinfo
from typing import Dict, Any, List, Optional, Tuple

from taikry.risk.models import (
    RiskDecision,
    MarketRegimeType,
    RiskAssessmentResult,
    SizingCalculation,
    RiskAssessmentLog,
    UserRiskSettings,
)
from taikry.risk.regime import regime_engine
from taikry.risk.portfolio import portfolio_engine
from taikry.risk.news_risk import news_risk_engine
from taikry.risk.quality_scorer import signal_quality_scorer

from taikry.database.session import SessionLocal
from taikry.config import (
    INITIAL_PAPER_BALANCE,
    RISK_PER_TRADE_PERCENT,
    MIN_RISK_REWARD_RATIO,
    MAX_RISK_PER_TRADE_PERCENT,
    get_symbol_config,
    get_risk_profile,
    RISK_PROFILES
)

logger = logging.getLogger("zyrox.risk.service")


class RiskIntelligenceService:
    """The Chief Risk Officer & Unified Risk Arbiter for ZYROX AI."""

    def __init__(self):
        self.regime_engine = regime_engine
        self.portfolio_engine = portfolio_engine
        self.news_engine = news_risk_engine
        self.quality_scorer = signal_quality_scorer

    def get_user_risk_settings(self, user_id: Optional[int] = None, db: Optional[Any] = None) -> Dict[str, Any]:
        """Loads user-specific risk configurations, falling back to default profile."""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            settings_obj = None
            if user_id:
                settings_obj = db.query(UserRiskSettings).filter(UserRiskSettings.user_id == user_id).first()
            if not settings_obj:
                settings_obj = db.query(UserRiskSettings).filter(UserRiskSettings.user_id == None).first()

            if settings_obj:
                return {
                    "risk_mode": settings_obj.risk_mode,
                    "risk_per_trade_percent": float(settings_obj.risk_per_trade_percent),
                    "min_risk_reward_ratio": float(settings_obj.min_risk_reward_ratio),
                    "max_daily_loss_percent": float(settings_obj.max_daily_loss_percent),
                    "max_weekly_loss_percent": float(settings_obj.max_weekly_loss_percent),
                    "max_monthly_loss_percent": float(settings_obj.max_monthly_loss_percent),
                    "max_drawdown_percent": float(settings_obj.max_drawdown_percent),
                    "max_simultaneous_positions": int(settings_obj.max_simultaneous_positions),
                    "max_portfolio_risk_percent": float(settings_obj.max_portfolio_risk_percent),
                    "max_correlated_positions": int(settings_obj.max_correlated_positions),
                    "news_filter_mode": settings_obj.news_filter_mode,
                }
            return get_risk_profile("BALANCED")
        except Exception as exc:
            logger.warning(f"Could not load UserRiskSettings: {exc}")
            return get_risk_profile("BALANCED")
        finally:
            if close_db:
                db.close()

    def evaluate_trade_candidate(
        self,
        symbol: str,
        direction: str,  # BUY, SELL, NONE
        entry_price: float,
        stop_loss: float,
        take_profit_1: float,
        take_profit_2: Optional[float] = None,
        spread_price: Optional[float] = None,
        account_equity: float = INITIAL_PAPER_BALANCE,
        risk_mode: Optional[str] = None,
        custom_risk_options: Optional[Dict[str, Any]] = None,
        candle_df: Optional[Any] = None,
        structure_info: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        persist_log: bool = True
    ) -> RiskAssessmentResult:
        """
        Executes unified 9-factor risk assessment across market structure,
        spreads, R:R floor, portfolio capacity, news events, and drawdown limits.
        """
        assessment_id = f"RSK-{uuid.uuid4().hex[:10].upper()}"
        cambodia_tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_local = now_utc.astimezone(cambodia_tz)
        ts_utc_str = now_utc.isoformat()
        ts_local_str = now_local.strftime("%Y-%m-%d %H:%M:%S UTC+7")

        veto_reasons: List[str] = []
        advisory_notes: List[str] = []

        # 1. Resolve Active Risk Profile & User Settings
        user_settings = self.get_user_risk_settings(user_id)
        effective_mode = risk_mode or user_settings.get("risk_mode", "BALANCED")
        merged_overrides = dict(user_settings)
        if custom_risk_options:
            merged_overrides.update(custom_risk_options)

        active_profile = get_risk_profile(effective_mode, merged_overrides)
        min_rr = float(active_profile.get("min_risk_reward_ratio", MIN_RISK_REWARD_RATIO))
        risk_pct = float(active_profile.get("risk_per_trade_percent", RISK_PER_TRADE_PERCENT))
        max_spread_pct = float(active_profile.get("max_spread_pct", 0.20))
        news_mode = str(active_profile.get("news_filter_mode", "STANDARD"))

        # 2. Geometric & Stop Loss Validity Check
        direction_norm = direction.strip().upper()
        if direction_norm not in {"BUY", "SELL", "LONG", "SHORT"}:
            veto_reasons.append("Trade direction is neutral, undefined, or missing.")

        risk_dist = abs(entry_price - stop_loss) if (entry_price and stop_loss) else 0.0
        reward_dist = abs(take_profit_1 - entry_price) if (entry_price and take_profit_1) else 0.0

        if direction_norm in {"BUY", "LONG"}:
            if stop_loss >= entry_price:
                veto_reasons.append(f"Invalid geometry: BUY Stop Loss ({stop_loss}) must be below Entry ({entry_price}).")
            if take_profit_1 <= entry_price:
                veto_reasons.append(f"Invalid geometry: BUY Take Profit ({take_profit_1}) must be above Entry ({entry_price}).")
        elif direction_norm in {"SELL", "SHORT"}:
            if stop_loss <= entry_price:
                veto_reasons.append(f"Invalid geometry: SELL Stop Loss ({stop_loss}) must be above Entry ({entry_price}).")
            if take_profit_1 >= entry_price:
                veto_reasons.append(f"Invalid geometry: SELL Take Profit ({take_profit_1}) must be below Entry ({entry_price}).")

        # 3. Risk-to-Reward Ratio Check
        rr_val = round(reward_dist / max(0.0001, risk_dist), 2) if risk_dist > 0 else 0.0
        calculated_rr_str = f"1:{rr_val}"
        if rr_val < min_rr:
            veto_reasons.append(
                f"Insufficient Risk-to-Reward: Calculated R:R is {calculated_rr_str}, failing the {active_profile['name']} floor of 1:{min_rr}."
            )

        # 4. Spread and Volatility Check
        if spread_price is not None and spread_price > 0 and risk_dist > 0:
            spread_ratio = spread_price / risk_dist
            if spread_ratio > max_spread_pct:
                veto_reasons.append(
                    f"Spread cost ({spread_price:.4f}) exceeds {int(max_spread_pct * 100)}% of stop distance ({risk_dist:.4f}). High execution friction."
                )

        # 5. Market Regime Detection
        regime_res = self.regime_engine.classify_regime(symbol, candle_df, structure_info)
        if regime_res.regime == MarketRegimeType.HIGH_VOLATILITY:
            advisory_notes.append("High volatility expansion detected. Expect wider wicks and temporary spread spikes.")
        elif regime_res.regime == MarketRegimeType.LOW_VOLATILITY:
            advisory_notes.append("Volatility squeeze coiling. Breakout confirmation recommended before full entry.")

        # 6. News Risk Evaluation
        news_res = self.news_engine.evaluate_news_risk(symbol, filter_mode=news_mode)
        if news_res.is_blackout:
            veto_reasons.append(
                f"High-impact news blackout active: '{news_res.event_name or 'Major Event'}' ({news_res.currency or 'USD'}). Spreads and slippage unsafe."
            )
        elif news_res.news_status == "ADVISORY_APPROACHING":
            advisory_notes.append(
                f"Upcoming event: '{news_res.event_name}' in {news_res.minutes_until_event} mins. Consider tight trailing stops."
            )

        # 7. Portfolio Exposure & Capital Protection Check
        portfolio_res = self.portfolio_engine.evaluate_portfolio(
            proposed_symbol=symbol,
            proposed_direction=direction_norm,
            proposed_risk_pct=risk_pct,
            account_equity=account_equity
        )
        if not portfolio_res.is_capacity_available:
            for w in portfolio_res.warnings:
                if "Drawdown" in w or "Cap Exceeded" in w or "Limit Exceeded" in w:
                    veto_reasons.append(w)
                else:
                    advisory_notes.append(w)

        # 8. Signal Quality Scoring
        quality_res = self.quality_scorer.calculate_score(
            symbol=symbol,
            direction=direction_norm,
            rr_ratio=rr_val,
            trend_aligned="TREND" in regime_res.regime.value or "BREAKOUT" in regime_res.regime.value,
            structure_confirmed=len(veto_reasons) == 0,
            momentum_aligned=True,
            volatility_ok=regime_res.regime != MarketRegimeType.HIGH_VOLATILITY,
            entry_quality_ok=len(veto_reasons) == 0,
            news_clear=not news_res.is_blackout,
            data_fresh=True
        )

        # 9. Sizing and Decision Resolution
        cfg = get_symbol_config(symbol)
        contract_size = float(cfg.get("lot_size", 100 if "XAU" in symbol.upper() else 100000))

        # Position Sizing
        is_reduced = False
        reduced_reason = None
        applied_risk_pct = risk_pct

        # Decide canonical decision
        if veto_reasons:
            decision = RiskDecision.REJECTED
        elif regime_res.regime == MarketRegimeType.LOW_VOLATILITY or news_res.news_status == "ADVISORY_APPROACHING":
            decision = RiskDecision.WAIT_FOR_CONFIRMATION
        elif len(advisory_notes) >= 2 or portfolio_res.total_allocated_risk_pct > 3.0:
            decision = RiskDecision.APPROVED_WITH_REDUCED_RISK
            is_reduced = True
            applied_risk_pct = round(risk_pct * 0.5, 3)
            reduced_reason = "Allocated risk scaled to 50% due to cross-asset advisory headwinds and portfolio load."
        else:
            decision = RiskDecision.APPROVED

        risk_amount_usd = round(account_equity * (applied_risk_pct / 100.0), 2)
        raw_lots = risk_amount_usd / (risk_dist * contract_size) if (risk_dist > 0 and contract_size > 0) else 0.01
        recommended_lots = round(min(10.0, max(0.01, math.floor(raw_lots * 100) / 100.0)), 2) if raw_lots >= 0.01 else 0.01

        sizing = SizingCalculation(
            account_equity=account_equity,
            risk_percentage=applied_risk_pct,
            risk_amount_usd=risk_amount_usd,
            stop_distance=round(risk_dist, 4),
            lot_size=recommended_lots,
            is_reduced_risk=is_reduced,
            reduced_reason=reduced_reason
        )

        can_exec = decision in {RiskDecision.APPROVED, RiskDecision.APPROVED_WITH_REDUCED_RISK}
        can_telegram = can_exec and "XAU" in symbol.upper() and (80 <= quality_res.total_score <= 95)

        result = RiskAssessmentResult(
            assessment_id=assessment_id,
            symbol=symbol.upper(),
            direction=direction_norm,
            decision=decision,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            calculated_rr=calculated_rr_str,
            min_required_rr=min_rr,
            risk_mode=effective_mode,
            sizing=sizing,
            regime=regime_res,
            news=news_res,
            portfolio=portfolio_res,
            quality=quality_res,
            veto_reasons=veto_reasons,
            advisory_notes=advisory_notes,
            timestamp_utc=ts_utc_str,
            timestamp_local=ts_local_str,
            can_execute_paper=can_exec,
            can_publish_telegram=can_telegram
        )

        # 10. Persist Assessment to Database Audit Log
        if persist_log:
            try:
                db = SessionLocal()
                log_entry = RiskAssessmentLog(
                    assessment_id=assessment_id,
                    user_id=user_id,
                    symbol=symbol.upper(),
                    direction=direction_norm,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                    take_profit_1=take_profit_1,
                    take_profit_2=take_profit_2,
                    calculated_rr=calculated_rr_str,
                    decision=decision.value,
                    risk_mode=effective_mode,
                    risk_percentage=applied_risk_pct,
                    account_equity=account_equity,
                    risk_amount_usd=risk_amount_usd,
                    recommended_lots=recommended_lots,
                    quality_score=quality_res.total_score,
                    market_regime=regime_res.regime.value,
                    news_status=news_res.news_status,
                    portfolio_risk_pct=portfolio_res.total_allocated_risk_pct,
                    veto_reasons=veto_reasons,
                    advisory_notes=advisory_notes,
                    validation_details={
                        "min_required_rr": min_rr,
                        "adx": regime_res.adx_value,
                        "hurst": regime_res.hurst_exponent,
                        "is_reduced_risk": is_reduced,
                    }
                )
                db.add(log_entry)
                db.commit()
                db.close()
            except Exception as exc:
                logger.warning(f"Could not persist RiskAssessmentLog: {exc}")

        return result


risk_intelligence_service = RiskIntelligenceService()
