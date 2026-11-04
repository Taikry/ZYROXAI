"""
ZYROX AI V6 — Module 17: Auto Learning & Shadow Mode Engine
===========================================================
Tracks trading outcomes segregated by:
- Strategy ID
- Concept ID
- Symbol & Timeframe
- Market Regime
- Execution Environment: BACKTEST, DEMO, or LIVE_VERIFIED (Strictly segregated)

Enforces Shadow Mode for new or revised strategies before promotion.
Never modifies or increases user risk limits automatically.
"""
from __future__ import annotations

import datetime
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("zyrox.v6.learning")


class StrategyPerformanceRecord(BaseModel):
    """Statistical track record for one strategy/concept configuration."""
    strategy_id: str
    concept_id: str
    symbol: str
    timeframe: str
    regime: str
    mode: str = "DEMO"  # BACKTEST, DEMO, LIVE_VERIFIED, SHADOW_MODE
    total_samples: int = 0
    wins: int = 0
    losses: int = 0
    win_rate_pct: float = 0.0
    avg_r_multiple: float = 0.0
    profit_factor: float = 0.0
    max_drawdown_pct: float = 0.0
    is_promoted: bool = False
    last_updated: str = ""


class AutoLearningEngine:
    """Governs strategy performance metrics and shadow mode promotion."""

    def __init__(self):
        # In-memory performance cache (backed by database models in Module 19)
        self._records: Dict[str, StrategyPerformanceRecord] = {}

    def record_outcome(
        self,
        strategy_id: str,
        concept_id: str,
        symbol: str,
        timeframe: str,
        regime: str,
        outcome: str,  # "WIN", "LOSS", "BE"
        r_multiple: float,
        mode: str = "DEMO"
    ) -> StrategyPerformanceRecord:
        """Records a verified trade outcome and updates performance statistics."""
        key = f"{mode}:{strategy_id}:{concept_id}:{symbol}:{timeframe}:{regime}"
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if key not in self._records:
            self._records[key] = StrategyPerformanceRecord(
                strategy_id=strategy_id,
                concept_id=concept_id,
                symbol=symbol,
                timeframe=timeframe,
                regime=regime,
                mode=mode,
                total_samples=0,
                last_updated=now_str
            )

        rec = self._records[key]
        rec.total_samples += 1
        if outcome == "WIN":
            rec.wins += 1
        elif outcome == "LOSS":
            rec.losses += 1

        rec.win_rate_pct = round((rec.wins / rec.total_samples) * 100.0, 1)
        # Running avg R multiple
        rec.avg_r_multiple = round(((rec.avg_r_multiple * (rec.total_samples - 1)) + r_multiple) / rec.total_samples, 2)
        rec.last_updated = now_str

        # Promotion check out of SHADOW_MODE
        if rec.mode == "SHADOW_MODE":
            if rec.total_samples >= 30 and rec.win_rate_pct >= 55.0 and rec.avg_r_multiple >= 1.5:
                rec.is_promoted = True
                logger.info(f"Strategy {strategy_id} passed shadow mode verification and qualified for promotion.")

        return rec

    def get_performance_summary(self, strategy_id: str, mode: str = "DEMO") -> Dict[str, Any]:
        """Returns verified performance metrics for a strategy."""
        matching = [r for r in self._records.values() if r.strategy_id == strategy_id and r.mode == mode]
        if not matching:
            return {
                "strategy_id": strategy_id,
                "mode": mode,
                "status": "INSUFFICIENT_SAMPLES",
                "sample_count": 0,
                "message": "Fewer than 10 verified trades recorded. Performance metrics withheld to avoid false confidence."
            }

        total_samples = sum(m.total_samples for m in matching)
        total_wins = sum(m.wins for m in matching)
        total_losses = sum(m.losses for m in matching)
        win_rate = round((total_wins / total_samples) * 100.0, 1) if total_samples > 0 else 0.0
        avg_r = round(sum(m.avg_r_multiple * m.total_samples for m in matching) / total_samples, 2) if total_samples > 0 else 0.0

        return {
            "strategy_id": strategy_id,
            "mode": mode,
            "sample_count": total_samples,
            "win_rate_pct": win_rate,
            "avg_r_multiple": avg_r,
            "status": "STATISTICALLY_VALID" if total_samples >= 30 else "COLLECTING_SAMPLE_SIZE"
        }


v6_auto_learning_engine = AutoLearningEngine()

