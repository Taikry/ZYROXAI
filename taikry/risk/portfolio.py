"""
ZYROX AI — Multi-Market Portfolio Intelligence Engine V3
========================================================
Governs portfolio-level exposure, currency concentration, cross-asset correlation,
aggregate stop-loss exposure, and drawdown protection across Forex, Metals, and Crypto.
"""
from __future__ import annotations

import logging
import datetime
import zoneinfo
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from taikry.database.session import SessionLocal
from taikry.database.models import PaperTrade
from taikry.risk.models import PortfolioExposureSummary
from taikry.config import (
    INITIAL_PAPER_BALANCE,
    RISK_PER_TRADE_PERCENT,
    MAX_SIMULTANEOUS_POSITIONS,
    get_symbol_config,
    WATCHLIST
)

logger = logging.getLogger("zyrox.risk.portfolio")

# Predefined institutional correlation table for asset universe
CROSS_ASSET_CORRELATION: Dict[Tuple[str, str], float] = {
    # Crypto cluster
    ("BTCUSDT", "ETHUSDT"): 0.88,
    ("BTCUSDT", "SOLUSDT"): 0.82,
    ("ETHUSDT", "SOLUSDT"): 0.84,
    ("BTCUSDT", "BNBUSDT"): 0.75,
    ("BTCUSDT", "XRPUSDT"): 0.65,
    # Forex USD cluster
    ("EURUSD", "GBPUSD"): 0.78,
    ("EURUSD", "USDCHF"): -0.92,
    ("EURUSD", "USDJPY"): -0.42,
    ("GBPUSD", "USDJPY"): -0.38,
    ("AUDUSD", "NZDUSD"): 0.86,
    ("USDCAD", "XAUUSD"): -0.55,
    # Metals vs Currency
    ("XAUUSD", "XAGUSD"): 0.85,
    ("XAUUSD", "EURUSD"): 0.62,
    ("XAUUSD", "USDJPY"): -0.48,
    ("XAUUSD", "BTCUSDT"): 0.32,
}

ASSET_CLASS_MAP: Dict[str, str] = {
    "XAUUSD": "METALS",
    "XAGUSD": "METALS",
    "EURUSD": "FOREX",
    "GBPUSD": "FOREX",
    "USDJPY": "FOREX",
    "AUDUSD": "FOREX",
    "NZDUSD": "FOREX",
    "USDCAD": "FOREX",
    "USDCHF": "FOREX",
    "EURJPY": "FOREX",
    "GBPJPY": "FOREX",
    "BTCUSDT": "CRYPTO",
    "ETHUSDT": "CRYPTO",
    "BNBUSDT": "CRYPTO",
    "SOLUSDT": "CRYPTO",
    "XRPUSDT": "CRYPTO",
    "DOGEUSDT": "CRYPTO",
    "ADAUSDT": "CRYPTO",
    "AVAXUSDT": "CRYPTO",
    "LINKUSDT": "CRYPTO",
    "SUIUSDT": "CRYPTO",
}


class PortfolioIntelligenceEngine:
    """Multi-market portfolio auditor and capital risk governor."""

    def __init__(self):
        self.max_portfolio_risk_pct = 5.0
        self.max_correlated_positions = 2
        self.max_drawdown_limit_pct = 8.0

    @staticmethod
    def get_correlation(sym1: str, sym2: str) -> float:
        """Looks up or computes correlation between two instruments."""
        s1, s2 = sym1.upper(), sym2.upper()
        if s1 == s2:
            return 1.0
        if (s1, s2) in CROSS_ASSET_CORRELATION:
            return CROSS_ASSET_CORRELATION[(s1, s2)]
        if (s2, s1) in CROSS_ASSET_CORRELATION:
            return CROSS_ASSET_CORRELATION[(s2, s1)]
        # Default correlation based on asset classes
        cls1 = ASSET_CLASS_MAP.get(s1, "OTHER")
        cls2 = ASSET_CLASS_MAP.get(s2, "OTHER")
        if cls1 == cls2 and cls1 == "CRYPTO":
            return 0.70
        if cls1 == cls2 and cls1 == "FOREX":
            return 0.50
        return 0.10

    def evaluate_portfolio(
        self,
        proposed_symbol: Optional[str] = None,
        proposed_direction: Optional[str] = None,
        proposed_risk_pct: float = RISK_PER_TRADE_PERCENT,
        account_equity: float = INITIAL_PAPER_BALANCE,
        peak_equity: Optional[float] = None,
        db_session: Optional[Any] = None,
        user_id: Optional[int] = None,
        max_portfolio_risk_pct: Optional[float] = None,
        max_simultaneous_positions: Optional[int] = None,
        max_drawdown_limit_pct: Optional[float] = None,
        max_correlated_positions: Optional[int] = None,
        max_daily_loss_pct: float = 2.5,
        max_weekly_loss_pct: float = 5.0,
        max_monthly_loss_pct: float = 10.0
    ) -> PortfolioExposureSummary:
        """
        Audits active paper trades, calculates currency and asset exposures,
        evaluates correlation concentration, and checks drawdown limits.
        """
        db = db_session or SessionLocal()
        close_on_exit = db_session is None
        warnings: List[str] = []
        portfolio_cap = float(max_portfolio_risk_pct or self.max_portfolio_risk_pct)
        position_cap = int(max_simultaneous_positions or MAX_SIMULTANEOUS_POSITIONS)
        drawdown_cap = float(max_drawdown_limit_pct or self.max_drawdown_limit_pct)
        correlated_position_cap = int(max_correlated_positions or self.max_correlated_positions)

        try:
            # user_id=None means the system's unowned paper ledger; never mix user accounts.
            user_scope = PaperTrade.user_id.is_(None) if user_id is None else PaperTrade.user_id == user_id
            open_trades = db.query(PaperTrade).filter(
                PaperTrade.status == "OPEN",
                user_scope,
            ).all()
            open_count = len(open_trades)

            # 1. Total Allocated Portfolio Risk
            total_allocated_risk = sum(
                float(getattr(t, "risk_percentage", RISK_PER_TRADE_PERCENT) or RISK_PER_TRADE_PERCENT)
                for t in open_trades
            )
            projected_risk = total_allocated_risk + (proposed_risk_pct if proposed_symbol else 0.0)

            # 2. Currency Exposure Accounting
            currency_exposure: Dict[str, float] = defaultdict(float)
            asset_class_exposure: Dict[str, float] = defaultdict(float)
            active_symbols = [t.symbol for t in open_trades]

            for t in open_trades:
                sym = t.symbol.upper()
                pos_risk = float(getattr(t, "risk_percentage", RISK_PER_TRADE_PERCENT) or RISK_PER_TRADE_PERCENT)
                asset_cls = ASSET_CLASS_MAP.get(sym, "FOREX")
                asset_class_exposure[asset_cls] += pos_risk

                # Currency weighting
                dir_mult = 1.0 if str(t.direction).upper() in {"BUY", "LONG"} else -1.0
                if "USD" in sym:
                    if sym.startswith("USD"):
                        currency_exposure["USD"] += pos_risk * dir_mult
                    elif sym.endswith("USD") or "USDT" in sym:
                        currency_exposure["USD"] -= pos_risk * dir_mult

            # Include proposed setup in exposure audit
            if proposed_symbol and proposed_direction:
                p_sym = proposed_symbol.upper()
                p_cls = ASSET_CLASS_MAP.get(p_sym, "FOREX")
                asset_class_exposure[p_cls] += proposed_risk_pct
                p_dir_mult = 1.0 if proposed_direction.upper() in {"BUY", "LONG"} else -1.0
                if "USD" in p_sym:
                    if p_sym.startswith("USD"):
                        currency_exposure["USD"] += proposed_risk_pct * p_dir_mult
                    elif p_sym.endswith("USD") or "USDT" in p_sym:
                        currency_exposure["USD"] -= proposed_risk_pct * p_dir_mult

            # 3. Correlation Concentration Check
            correlated_group_counts: Dict[str, int] = defaultdict(int)
            for sym in active_symbols + ([proposed_symbol] if proposed_symbol else []):
                cls_name = ASSET_CLASS_MAP.get(sym.upper(), "FOREX")
                correlated_group_counts[cls_name] += 1

            # High pairwise correlation warnings and a configurable hard cap.
            correlated_open_count = 0
            if proposed_symbol:
                p_sym = proposed_symbol.upper()
                for open_t in open_trades:
                    corr = self.get_correlation(p_sym, open_t.symbol)
                    if abs(corr) >= 0.75:
                        correlated_open_count += 1
                        same_dir = (proposed_direction or "").upper() == str(open_t.direction).upper()
                        if corr > 0 and same_dir:
                            warnings.append(
                                f"High Positive Correlation ({corr:.2f}) with open {open_t.symbol} position. Risk is compounding."
                            )
                        elif corr < 0 and not same_dir:
                            warnings.append(
                                f"Negative Correlation ({corr:.2f}) with opposing {open_t.symbol} position creates synthetic double-risk."
                            )
                if correlated_open_count + 1 > correlated_position_cap:
                    warnings.append(
                        f"Correlated Position Limit Exceeded: {correlated_open_count + 1} highly correlated positions would exceed the configured limit of {correlated_position_cap}."
                    )

            # Concentration thresholds
            if correlated_group_counts.get("CRYPTO", 0) > 3:
                warnings.append("Crypto Concentration Warning: Over 3 simultaneous crypto positions open.")
            if correlated_group_counts.get("FOREX", 0) > 3:
                warnings.append("Forex Concentration Warning: Over 3 simultaneous currency positions open.")
            if abs(currency_exposure.get("USD", 0.0)) > 2.0:
                warnings.append(f"Heavy USD Directional Exposure ({currency_exposure['USD']:+.1f}% risk). Sensitive to DXY volatility.")

            # 4. Drawdown Monitoring
            peak = peak_equity or max(account_equity, INITIAL_PAPER_BALANCE)
            drawdown_pct = 0.0
            if peak > 0 and account_equity < peak:
                drawdown_pct = round(((peak - account_equity) / peak) * 100.0, 2)

            is_drawdown_limit_breached = drawdown_pct >= drawdown_cap
            if is_drawdown_limit_breached:
                warnings.append(
                    f"CRITICAL: Account drawdown ({drawdown_pct:.1f}%) has breached the maximum safety threshold ({drawdown_cap:.1f}%). New approvals blocked."
                )

            # Calculate loss circuit breakers from closed trades in the same user ledger.
            cambodia_tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
            now_local = datetime.datetime.now(cambodia_tz)
            day_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = day_start - datetime.timedelta(days=day_start.weekday())
            month_start = day_start.replace(day=1)

            def as_naive_utc(value: datetime.datetime) -> datetime.datetime:
                return value.astimezone(datetime.timezone.utc).replace(tzinfo=None)

            earliest_period_start = min(day_start, week_start, month_start)
            closed_trades = db.query(PaperTrade).filter(
                PaperTrade.status == "CLOSED",
                user_scope,
                PaperTrade.exit_time.is_not(None),
                PaperTrade.exit_time >= as_naive_utc(earliest_period_start),
            ).order_by(PaperTrade.exit_time.asc()).all()

            def loss_percent(period_start: datetime.datetime) -> float:
                cutoff = as_naive_utc(period_start)
                period_trades = [t for t in closed_trades if t.exit_time and t.exit_time >= cutoff]
                net_pnl = sum(float(t.pnl or 0.0) for t in period_trades)
                starting_equity = (
                    float(period_trades[0].balance_before or account_equity)
                    if period_trades else float(account_equity or INITIAL_PAPER_BALANCE)
                )
                if starting_equity <= 0:
                    return 0.0
                return round(max(0.0, -net_pnl) / starting_equity * 100.0, 2)

            daily_loss_pct = loss_percent(day_start)
            weekly_loss_pct = loss_percent(week_start)
            monthly_loss_pct = loss_percent(month_start)
            is_loss_limit_breached = (
                daily_loss_pct >= float(max_daily_loss_pct)
                or weekly_loss_pct >= float(max_weekly_loss_pct)
                or monthly_loss_pct >= float(max_monthly_loss_pct)
            )
            for label, used, limit in (
                ("Daily", daily_loss_pct, max_daily_loss_pct),
                ("Weekly", weekly_loss_pct, max_weekly_loss_pct),
                ("Monthly", monthly_loss_pct, max_monthly_loss_pct),
            ):
                if used >= float(limit):
                    warnings.append(f"{label} Loss Limit Exceeded: {used:.2f}% used against {float(limit):.2f}%.")

            is_capacity_available = (
                projected_risk <= portfolio_cap
                and (open_count + (1 if proposed_symbol else 0)) <= position_cap
                and not is_drawdown_limit_breached
                and not is_loss_limit_breached
                and not any("Correlated Position Limit Exceeded" in warning for warning in warnings)
            )

            if not is_capacity_available and projected_risk > portfolio_cap:
                warnings.append(
                    f"Portfolio Risk Cap Exceeded: Projected risk {projected_risk:.1f}% exceeds max {portfolio_cap:.1f}%."
                )
            if (open_count + (1 if proposed_symbol else 0)) > position_cap:
                warnings.append(
                    f"Position Count Limit Exceeded: Max {position_cap} simultaneous positions allowed."
                )

            return PortfolioExposureSummary(
                total_open_positions=open_count,
                total_allocated_risk_pct=round(total_allocated_risk, 2),
                max_portfolio_risk_pct=portfolio_cap,
                is_capacity_available=is_capacity_available,
                net_usd_exposure=round(currency_exposure["USD"], 2),
                net_crypto_exposure=round(asset_class_exposure["CRYPTO"], 2),
                net_metal_exposure=round(asset_class_exposure["METALS"], 2),
                active_symbols=active_symbols,
                correlated_group_counts=dict(correlated_group_counts),
                drawdown_pct=drawdown_pct,
                is_drawdown_limit_breached=is_drawdown_limit_breached,
                daily_loss_pct=daily_loss_pct,
                weekly_loss_pct=weekly_loss_pct,
                monthly_loss_pct=monthly_loss_pct,
                is_loss_limit_breached=is_loss_limit_breached,
                warnings=warnings
            )
        except Exception as exc:
            logger.warning(f"Portfolio exposure calculation fallback: {exc}")
            return PortfolioExposureSummary(
                total_open_positions=0,
                total_allocated_risk_pct=0.0,
                max_portfolio_risk_pct=portfolio_cap,
                is_capacity_available=False,
                net_usd_exposure=0.0,
                net_crypto_exposure=0.0,
                net_metal_exposure=0.0,
                active_symbols=[],
                correlated_group_counts={},
                drawdown_pct=0.0,
                is_drawdown_limit_breached=False,
                daily_loss_pct=0.0,
                weekly_loss_pct=0.0,
                monthly_loss_pct=0.0,
                is_loss_limit_breached=True,
                warnings=["Database portfolio query failed; capital safety lock active."]
            )
        finally:
            if close_on_exit:
                db.close()


portfolio_engine = PortfolioIntelligenceEngine()
