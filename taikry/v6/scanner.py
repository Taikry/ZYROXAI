"""
ZYROX AI V6 — Module 11: Multi-Market Auto Scanner
==================================================
Scans provider-supported markets across:
- FOREX
- XAUUSD & METALS
- CRYPTO
- ALL SUPPORTED MARKETS
- CUSTOM WATCHLIST

Executes high-efficiency deterministic screening before involving AI reviews:
1. Load provider-supported symbols from MarketSymbolRegistry / Config.
2. Fetch candles and validate data integrity.
3. Classify market regime.
4. Detect technical concepts.
5. Calculate setup quality scores.
6. Rank candidates by score and expected R:R.
7. Return sorted institutional candidates.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from taikry.config import WATCHLIST
from taikry.data.providers import market_data_engine
from taikry.v6.models import V6MarketRegime, BestSetupResult
from taikry.v6.service import v6_intelligence_service

logger = logging.getLogger("zyrox.v6.scanner")


class MarketScanItem(BaseModel):
    """Ranked item in the multi-market scanner result."""
    symbol: str
    asset_class: str
    regime: str
    direction: str
    quality_score: int
    classification: str
    strategy_name: str
    entry_price: Optional[float]
    stop_loss: Optional[float]
    tp1: Optional[float]
    risk_reward: Optional[str]
    setup_id: str


class MarketScanResult(BaseModel):
    """Complete output of a multi-market scan."""
    market_filter: str
    timeframe: str
    total_symbols_scanned: int
    qualified_setups_count: int
    candidates: List[MarketScanItem] = Field(default_factory=list)
    timestamp: str


class V6MarketScanner:
    """Autonomous Multi-Market Scanner for ZYROX AI V6."""

    def __init__(self):
        self.service = v6_intelligence_service

    def get_symbols_for_filter(self, market_filter: str) -> List[Dict[str, str]]:
        """Maps market filter category to supported symbols."""
        m_filt = market_filter.strip().upper()

        if m_filt in ("XAUUSD", "GOLD", "METALS"):
            return [w for w in WATCHLIST if w.get("symbol") in ("XAUUSD", "XAGUSD")]
        elif m_filt == "FOREX":
            return [w for w in WATCHLIST if w.get("type") == "FOREX"]
        elif m_filt == "CRYPTO":
            return [w for w in WATCHLIST if w.get("type") == "CRYPTO"]
        else:  # "ALL" or custom
            return WATCHLIST

    def scan_markets(
        self,
        market_filter: str = "ALL",
        timeframe: str = "M15",
        min_quality_score: int = 55,
        max_symbols: int = 15
    ) -> MarketScanResult:
        """
        Executes fast deterministic screening across symbols and ranks qualified opportunities.
        """
        import datetime
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        targets = self.get_symbols_for_filter(market_filter)[:max_symbols]
        candidates: List[MarketScanItem] = []

        for item in targets:
            sym = item.get("symbol")
            if not sym:
                continue
            try:
                # Fast pipeline execution
                setup = self.service.analyze_best_setup(symbol=sym, timeframe=timeframe)
                score = setup.quality_score.total_score

                if score >= min_quality_score:
                    candidates.append(MarketScanItem(
                        symbol=setup.symbol,
                        asset_class=item.get("type", "FOREX"),
                        regime=setup.regime.value,
                        direction=setup.direction,
                        quality_score=score,
                        classification=setup.quality_score.classification,
                        strategy_name=setup.strategy.get("name", "N/A"),
                        entry_price=setup.trade_plan.entry_price,
                        stop_loss=setup.trade_plan.stop_loss,
                        tp1=setup.trade_plan.tp1,
                        risk_reward=setup.trade_plan.risk_reward_ratio,
                        setup_id=setup.setup_id
                    ))
            except Exception as exc:
                logger.debug(f"Scan failed for {sym}: {exc}")
                continue

        # Sort descending by quality score
        candidates.sort(key=lambda c: c.quality_score, reverse=True)

        return MarketScanResult(
            market_filter=market_filter,
            timeframe=timeframe,
            total_symbols_scanned=len(targets),
            qualified_setups_count=len(candidates),
            candidates=candidates,
            timestamp=now_str
        )


v6_scanner = V6MarketScanner()

