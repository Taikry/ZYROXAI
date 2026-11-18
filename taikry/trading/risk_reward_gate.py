"""
ZYROX AI — CENTRALIZED RISK/REWARD CONFIRMATION GATE
====================================================
Mandatory Risk/Reward confirmation gate enforcing:
1. Minimum required Risk/Reward ratio: 1.1 (1:1.1 floor).
2. Conservative validation on TP1 (never hide behind TP3).
3. Geometric direction checks:
   - BUY: SL < Entry < TP1 (< TP2 < TP3)
   - SELL: SL > Entry > TP1 (> TP2 > TP3)
4. Execution cost validation (Bid, Ask, Spread, Commission) with Gross vs Net disclosure.
5. Standardized approval statuses: APPROVED, REJECTED, INVALID, WAIT.
6. Standardized rejection message: "Signal rejected: Risk/Reward ratio is below the minimum required 1:1.1."
7. Global configurable Admin setting stored in SystemSetting and logged in AuditLog.
"""

import math
import logging
from typing import Dict, Any, Optional, Tuple, NamedTuple
from dataclasses import dataclass, field

from taikry.config import COMMISSION_PER_LOT
from taikry.database.session import SessionLocal

logger = logging.getLogger("taikry.trading.risk_reward_gate")

DEFAULT_MIN_RISK_REWARD: float = 1.1
SETTING_KEY_MIN_RR = "min_risk_reward_ratio"

STATUS_APPROVED = "APPROVED"
STATUS_REJECTED = "REJECTED"
STATUS_INVALID = "INVALID"
STATUS_WAIT = "WAIT"


@dataclass
class RiskRewardValidationResult:
    """Structured result of the centralized Risk/Reward gate evaluation."""
    status: str                         # APPROVED | REJECTED | INVALID | WAIT
    is_approved: bool                   # True only if APPROVED
    symbol: str                         # Canonical symbol (e.g. XAUUSD)
    direction: str                      # BUY | SELL
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: Optional[float] = None
    take_profit_3: Optional[float] = None
    risk_distance: float = 0.0
    reward_distance_1: float = 0.0
    reward_distance_2: Optional[float] = None
    reward_distance_3: Optional[float] = None
    rr_tp1: float = 0.0
    rr_tp2: Optional[float] = None
    rr_tp3: Optional[float] = None
    min_required_rr: float = DEFAULT_MIN_RISK_REWARD
    difference: float = 0.0             # rr_tp1 - min_required_rr
    rejection_reason: Optional[str] = None
    explanation: str = ""
    cost_basis: str = "GROSS_ESTIMATED"  # NET | GROSS_ESTIMATED
    is_net: bool = False
    net_rr_tp1: Optional[float] = None
    spread: Optional[float] = None
    commission_per_unit: Optional[float] = None
    estimated_total_costs: Optional[float] = None
    gate_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "is_approved": self.is_approved,
            "symbol": self.symbol,
            "direction": self.direction,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit_1": self.take_profit_1,
            "take_profit_2": self.take_profit_2,
            "take_profit_3": self.take_profit_3,
            "risk_distance": round(self.risk_distance, 2),
            "reward_distance_1": round(self.reward_distance_1, 2),
            "reward_distance_2": round(self.reward_distance_2, 2) if self.reward_distance_2 is not None else None,
            "reward_distance_3": round(self.reward_distance_3, 2) if self.reward_distance_3 is not None else None,
            "risk_reward_ratio": round(self.rr_tp1, 2),
            "rr_tp1": round(self.rr_tp1, 2),
            "rr_tp2": round(self.rr_tp2, 2) if self.rr_tp2 is not None else None,
            "rr_tp3": round(self.rr_tp3, 2) if self.rr_tp3 is not None else None,
            "min_required_rr": round(self.min_required_rr, 2),
            "difference": round(self.difference, 2),
            "rejection_reason": self.rejection_reason,
            "explanation": self.explanation,
            "cost_basis": self.cost_basis,
            "is_net": self.is_net,
            "net_rr_tp1": round(self.net_rr_tp1, 2) if self.net_rr_tp1 is not None else None,
            "spread": round(self.spread, 4) if self.spread is not None else None,
            "commission_per_unit": round(self.commission_per_unit, 4) if self.commission_per_unit is not None else None,
            "estimated_total_costs": round(self.estimated_total_costs, 4) if self.estimated_total_costs is not None else None,
            "gate_details": self.gate_details,
        }


def get_system_min_rr() -> float:
    """
    Retrieves the global minimum Risk/Reward ratio from SystemSetting table.
    Defaults to 1.1 if unconfigured, invalid, or database unavailable.
    """
    try:
        from taikry.database.models import SystemSetting
        db = SessionLocal()
        try:
            row = db.query(SystemSetting).filter(SystemSetting.key == SETTING_KEY_MIN_RR).first()
            if row and row.value:
                val = float(row.value)
                if math.isfinite(val) and val >= 1.0:
                    return round(val, 2)
        finally:
            db.close()
    except Exception as exc:
        logger.debug(f"Unable to read {SETTING_KEY_MIN_RR} from DB: {exc}")
    return DEFAULT_MIN_RISK_REWARD


def set_system_min_rr(
    new_value: float,
    actor_user_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> float:
    """
    Persists an updated global minimum Risk/Reward ratio to SystemSetting
    and records an audit log entry.
    Requires new_value >= 1.0.
    """
    val = float(new_value)
    if not math.isfinite(val) or val < 1.0 or val > 20.0:
        raise ValueError("Minimum Risk/Reward ratio must be a positive numeric value between 1.0 and 20.0.")

    target_val = round(val, 2)
    from taikry.database.models import SystemSetting, AuditLog
    import datetime
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == SETTING_KEY_MIN_RR).first()
        old_val = setting.value if setting else str(DEFAULT_MIN_RISK_REWARD)
        now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        if setting:
            setting.value = str(target_val)
            setting.updated_by = actor_user_id
            setting.updated_at = now_utc
        else:
            setting = SystemSetting(
                key=SETTING_KEY_MIN_RR,
                value=str(target_val),
                is_secret=False,
                description="Global minimum Risk/Reward approval gate floor for trade signals",
                updated_by=actor_user_id,
                updated_at=now_utc
            )
            db.add(setting)

        audit = AuditLog(
            actor_user_id=actor_user_id,
            action="UPDATE_MIN_RISK_REWARD_RATIO",
            target_type="system_setting",
            target_id=SETTING_KEY_MIN_RR,
            details={
                "previous_value": old_val,
                "new_value": str(target_val),
                "timestamp": now_utc.isoformat(),
            },
            ip_address=ip_address,
            created_at=now_utc,
        )
        db.add(audit)
        db.commit()
        return target_val
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def validate_signal_risk_reward(
    symbol: str,
    direction: str,
    entry: float,
    stop_loss: float,
    take_profit_1: float,
    take_profit_2: Optional[float] = None,
    take_profit_3: Optional[float] = None,
    bid: Optional[float] = None,
    ask: Optional[float] = None,
    spread: Optional[float] = None,
    commission_per_lot: float = COMMISSION_PER_LOT,
    min_rr_threshold: Optional[float] = None,
    confluence_score: Optional[int] = None,
    quote_verified: bool = True,
    quote_fresh: bool = True,
    technical_confirmed: bool = True,
    other_checks_passed: bool = True,
    lot_size: float = 100.0,  # XAUUSD 100 oz per standard lot
) -> RiskRewardValidationResult:
    """
    Centralized validation gate for trade signals.
    Evaluates:
      1. Inputs & geometric validity (SL / Entry / TP ordering).
      2. Risk distance and TP1, TP2, TP3 reward distances.
      3. Conservative TP1 Risk/Reward ratio >= min_rr (default 1.1).
      4. Execution cost basis (Gross vs Net).
      5. Auxiliary gates: Confluence Score (>= 75), Quote verified & fresh, Technical confirmed.
    """
    effective_min_rr = float(min_rr_threshold) if min_rr_threshold is not None else get_system_min_rr()
    effective_min_rr = round(max(1.0, effective_min_rr), 2)

    # Normalize inputs
    norm_symbol = str(symbol or "").strip().upper()
    norm_dir = str(direction or "").strip().upper()
    if norm_dir in ("LONG", "BUY"):
        clean_dir = "BUY"
    elif norm_dir in ("SHORT", "SELL"):
        clean_dir = "SELL"
    else:
        clean_dir = "UNKNOWN"

    gate_details = {
        "score_passed": (confluence_score is None or confluence_score >= 75),
        "quote_verified": bool(quote_verified),
        "quote_fresh": bool(quote_fresh),
        "technical_confirmed": bool(technical_confirmed),
        "other_checks_passed": bool(other_checks_passed),
        "min_required_rr": effective_min_rr,
    }

    # 1. Direction check
    if clean_dir not in ("BUY", "SELL"):
        return RiskRewardValidationResult(
            status=STATUS_INVALID,
            is_approved=False,
            symbol=norm_symbol,
            direction=norm_dir,
            entry_price=0.0,
            stop_loss=0.0,
            take_profit_1=0.0,
            min_required_rr=effective_min_rr,
            rejection_reason="Invalid signal direction. Must be BUY or SELL.",
            explanation="Direction must be either BUY or SELL for trade level validation.",
            gate_details=gate_details
        )

    # 2. Number validation
    try:
        e = float(entry)
        sl = float(stop_loss)
        tp1 = float(take_profit_1)
        tp2 = float(take_profit_2) if take_profit_2 is not None else None
        tp3 = float(take_profit_3) if take_profit_3 is not None else None
    except (TypeError, ValueError):
        return RiskRewardValidationResult(
            status=STATUS_INVALID,
            is_approved=False,
            symbol=norm_symbol,
            direction=clean_dir,
            entry_price=0.0,
            stop_loss=0.0,
            take_profit_1=0.0,
            min_required_rr=effective_min_rr,
            rejection_reason="Invalid price level data: entry, stop_loss, or take_profit_1 is not a valid number.",
            explanation="Numeric prices must be finite, non-zero positive numbers.",
            gate_details=gate_details
        )

    levels_finite = math.isfinite(e) and math.isfinite(sl) and math.isfinite(tp1) and e > 0 and sl > 0 and tp1 > 0
    if not levels_finite:
        return RiskRewardValidationResult(
            status=STATUS_INVALID,
            is_approved=False,
            symbol=norm_symbol,
            direction=clean_dir,
            entry_price=e if math.isfinite(e) else 0.0,
            stop_loss=sl if math.isfinite(sl) else 0.0,
            take_profit_1=tp1 if math.isfinite(tp1) else 0.0,
            min_required_rr=effective_min_rr,
            rejection_reason="Price levels must be positive finite numbers.",
            explanation="Prices must be greater than zero.",
            gate_details=gate_details
        )

    # 3. Geometric ordering & distance check
    if clean_dir == "BUY":
        if sl >= e:
            return RiskRewardValidationResult(
                status=STATUS_INVALID,
                is_approved=False,
                symbol=norm_symbol,
                direction=clean_dir,
                entry_price=e,
                stop_loss=sl,
                take_profit_1=tp1,
                min_required_rr=effective_min_rr,
                rejection_reason=f"Invalid BUY geometry: Stop Loss ({sl:.2f}) must be strictly below Entry ({e:.2f}).",
                explanation=f"For a BUY signal, Stop Loss must be placed below the entry price (SL: {sl:.2f} >= Entry: {e:.2f}).",
                gate_details=gate_details
            )
        if tp1 <= e:
            return RiskRewardValidationResult(
                status=STATUS_INVALID,
                is_approved=False,
                symbol=norm_symbol,
                direction=clean_dir,
                entry_price=e,
                stop_loss=sl,
                take_profit_1=tp1,
                min_required_rr=effective_min_rr,
                rejection_reason=f"Invalid BUY geometry: Take Profit ({tp1:.2f}) must be strictly above Entry ({e:.2f}).",
                explanation=f"For a BUY signal, Take Profit must be placed above the entry price (TP1: {tp1:.2f} <= Entry: {e:.2f}).",
                gate_details=gate_details
            )
        if tp2 is not None and tp2 <= tp1:
            return RiskRewardValidationResult(
                status=STATUS_INVALID,
                is_approved=False,
                symbol=norm_symbol,
                direction=clean_dir,
                entry_price=e,
                stop_loss=sl,
                take_profit_1=tp1,
                take_profit_2=tp2,
                min_required_rr=effective_min_rr,
                rejection_reason=f"Invalid BUY TP progression: TP2 ({tp2:.2f}) must be higher than TP1 ({tp1:.2f}).",
                explanation="Take Profit targets must expand sequentially away from entry.",
                gate_details=gate_details
            )
        if tp3 is not None and tp2 is not None and tp3 <= tp2:
            return RiskRewardValidationResult(
                status=STATUS_INVALID,
                is_approved=False,
                symbol=norm_symbol,
                direction=clean_dir,
                entry_price=e,
                stop_loss=sl,
                take_profit_1=tp1,
                take_profit_2=tp2,
                take_profit_3=tp3,
                min_required_rr=effective_min_rr,
                rejection_reason=f"Invalid BUY TP progression: TP3 ({tp3:.2f}) must be higher than TP2 ({tp2:.2f}).",
                explanation="Take Profit targets must expand sequentially away from entry.",
                gate_details=gate_details
            )
    else:  # SELL
        if sl <= e:
            return RiskRewardValidationResult(
                status=STATUS_INVALID,
                is_approved=False,
                symbol=norm_symbol,
                direction=clean_dir,
                entry_price=e,
                stop_loss=sl,
                take_profit_1=tp1,
                min_required_rr=effective_min_rr,
                rejection_reason=f"Invalid SELL geometry: Stop Loss ({sl:.2f}) must be strictly above Entry ({e:.2f}).",
                explanation=f"For a SELL signal, Stop Loss must be placed above the entry price (SL: {sl:.2f} <= Entry: {e:.2f}).",
                gate_details=gate_details
            )
        if tp1 >= e:
            return RiskRewardValidationResult(
                status=STATUS_INVALID,
                is_approved=False,
                symbol=norm_symbol,
                direction=clean_dir,
                entry_price=e,
                stop_loss=sl,
                take_profit_1=tp1,
                min_required_rr=effective_min_rr,
                rejection_reason=f"Invalid SELL geometry: Take Profit ({tp1:.2f}) must be strictly below Entry ({e:.2f}).",
                explanation=f"For a SELL signal, Take Profit must be placed below the entry price (TP1: {tp1:.2f} >= Entry: {e:.2f}).",
                gate_details=gate_details
            )
        if tp2 is not None and tp2 >= tp1:
            return RiskRewardValidationResult(
                status=STATUS_INVALID,
                is_approved=False,
                symbol=norm_symbol,
                direction=clean_dir,
                entry_price=e,
                stop_loss=sl,
                take_profit_1=tp1,
                take_profit_2=tp2,
                min_required_rr=effective_min_rr,
                rejection_reason=f"Invalid SELL TP progression: TP2 ({tp2:.2f}) must be lower than TP1 ({tp1:.2f}).",
                explanation="Take Profit targets must expand sequentially away from entry.",
                gate_details=gate_details
            )
        if tp3 is not None and tp2 is not None and tp3 >= tp2:
            return RiskRewardValidationResult(
                status=STATUS_INVALID,
                is_approved=False,
                symbol=norm_symbol,
                direction=clean_dir,
                entry_price=e,
                stop_loss=sl,
                take_profit_1=tp1,
                take_profit_2=tp2,
                take_profit_3=tp3,
                min_required_rr=effective_min_rr,
                rejection_reason=f"Invalid SELL TP progression: TP3 ({tp3:.2f}) must be lower than TP2 ({tp2:.2f}).",
                explanation="Take Profit targets must expand sequentially away from entry.",
                gate_details=gate_details
            )

    risk_dist = abs(e - sl)
    if risk_dist <= 0:
        return RiskRewardValidationResult(
            status=STATUS_INVALID,
            is_approved=False,
            symbol=norm_symbol,
            direction=clean_dir,
            entry_price=e,
            stop_loss=sl,
            take_profit_1=tp1,
            min_required_rr=effective_min_rr,
            rejection_reason="Zero risk distance: Entry equals Stop Loss.",
            explanation="Trade has zero risk distance which is mathematically undefined.",
            gate_details=gate_details
        )

    reward_dist_1 = abs(tp1 - e)
    reward_dist_2 = abs(tp2 - e) if tp2 is not None else None
    reward_dist_3 = abs(tp3 - e) if tp3 is not None else None

    rr_tp1 = round(reward_dist_1 / risk_dist, 2)
    rr_tp2 = round(reward_dist_2 / risk_dist, 2) if reward_dist_2 is not None else None
    rr_tp3 = round(reward_dist_3 / risk_dist, 2) if reward_dist_3 is not None else None

    # 4. Execution Cost Computation
    effective_spread = spread
    if effective_spread is None and bid is not None and ask is not None and math.isfinite(bid) and math.isfinite(ask):
        if ask > bid:
            effective_spread = ask - bid

    comm_per_unit = commission_per_lot / lot_size if (lot_size and lot_size > 0) else 0.07
    cost_basis = "GROSS_ESTIMATED"
    is_net = False
    net_rr_tp1 = None
    estimated_total_costs = None

    if effective_spread is not None and math.isfinite(effective_spread) and effective_spread > 0:
        cost_basis = "NET"
        is_net = True
        estimated_total_costs = effective_spread + comm_per_unit
        net_risk = risk_dist + estimated_total_costs
        net_reward = max(0.0, reward_dist_1 - estimated_total_costs)
        net_rr_tp1 = round(net_reward / net_risk, 2) if net_risk > 0 else 0.0
    else:
        # Disclose that ratio is gross
        cost_basis = "GROSS_ESTIMATED"
        is_net = False

    diff = round(rr_tp1 - effective_min_rr, 2)

    # 5. Risk/Reward evaluation
    # Standard rejection message required:
    # "Signal rejected: Risk/Reward ratio is below the minimum required 1:1.1."
    if rr_tp1 < effective_min_rr:
        rejection_msg = f"Signal rejected: Risk/Reward ratio is below the minimum required 1:{effective_min_rr:.1f}."
        explanation = (
            f"Actual RR is 1:{rr_tp1:.2f}, which is below the minimum required 1:{effective_min_rr:.1f} "
            f"(short by {abs(diff):.2f}). TP1 is the conservative approval target and cannot be bypassed."
        )
        return RiskRewardValidationResult(
            status=STATUS_REJECTED,
            is_approved=False,
            symbol=norm_symbol,
            direction=clean_dir,
            entry_price=e,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            risk_distance=risk_dist,
            reward_distance_1=reward_dist_1,
            reward_distance_2=reward_dist_2,
            reward_distance_3=reward_dist_3,
            rr_tp1=rr_tp1,
            rr_tp2=rr_tp2,
            rr_tp3=rr_tp3,
            min_required_rr=effective_min_rr,
            difference=diff,
            rejection_reason=rejection_msg,
            explanation=explanation,
            cost_basis=cost_basis,
            is_net=is_net,
            net_rr_tp1=net_rr_tp1,
            spread=effective_spread,
            commission_per_unit=comm_per_unit,
            estimated_total_costs=estimated_total_costs,
            gate_details=gate_details
        )

    # 6. Check prerequisite gates (Quote fresh/verified, Score >= 75, Technical confirmation)
    if not quote_verified or not quote_fresh:
        reason = "Exness MT5 quote is missing, stale, or unverified; setup placed in WAIT."
        return RiskRewardValidationResult(
            status=STATUS_WAIT,
            is_approved=False,
            symbol=norm_symbol,
            direction=clean_dir,
            entry_price=e,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            risk_distance=risk_dist,
            reward_distance_1=reward_dist_1,
            reward_distance_2=reward_dist_2,
            reward_distance_3=reward_dist_3,
            rr_tp1=rr_tp1,
            rr_tp2=rr_tp2,
            rr_tp3=rr_tp3,
            min_required_rr=effective_min_rr,
            difference=diff,
            rejection_reason=reason,
            explanation=reason,
            cost_basis=cost_basis,
            is_net=is_net,
            net_rr_tp1=net_rr_tp1,
            spread=effective_spread,
            commission_per_unit=comm_per_unit,
            estimated_total_costs=estimated_total_costs,
            gate_details=gate_details
        )

    if confluence_score is not None and confluence_score < 75:
        reason = f"Confluence score {confluence_score}/100 is below the 75/100 approval threshold; setup placed in WAIT."
        return RiskRewardValidationResult(
            status=STATUS_WAIT,
            is_approved=False,
            symbol=norm_symbol,
            direction=clean_dir,
            entry_price=e,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            risk_distance=risk_dist,
            reward_distance_1=reward_dist_1,
            reward_distance_2=reward_dist_2,
            reward_distance_3=reward_dist_3,
            rr_tp1=rr_tp1,
            rr_tp2=rr_tp2,
            rr_tp3=rr_tp3,
            min_required_rr=effective_min_rr,
            difference=diff,
            rejection_reason=reason,
            explanation=reason,
            cost_basis=cost_basis,
            is_net=is_net,
            net_rr_tp1=net_rr_tp1,
            spread=effective_spread,
            commission_per_unit=comm_per_unit,
            estimated_total_costs=estimated_total_costs,
            gate_details=gate_details
        )

    if not technical_confirmed:
        reason = "Technical confirmation gate did not pass; setup placed in WAIT."
        return RiskRewardValidationResult(
            status=STATUS_WAIT,
            is_approved=False,
            symbol=norm_symbol,
            direction=clean_dir,
            entry_price=e,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            risk_distance=risk_dist,
            reward_distance_1=reward_dist_1,
            reward_distance_2=reward_dist_2,
            reward_distance_3=reward_dist_3,
            rr_tp1=rr_tp1,
            rr_tp2=rr_tp2,
            rr_tp3=rr_tp3,
            min_required_rr=effective_min_rr,
            difference=diff,
            rejection_reason=reason,
            explanation=reason,
            cost_basis=cost_basis,
            is_net=is_net,
            net_rr_tp1=net_rr_tp1,
            spread=effective_spread,
            commission_per_unit=comm_per_unit,
            estimated_total_costs=estimated_total_costs,
            gate_details=gate_details
        )

    if not other_checks_passed:
        reason = "Risk and safety checks failed; setup placed in WAIT."
        return RiskRewardValidationResult(
            status=STATUS_WAIT,
            is_approved=False,
            symbol=norm_symbol,
            direction=clean_dir,
            entry_price=e,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            risk_distance=risk_dist,
            reward_distance_1=reward_dist_1,
            reward_distance_2=reward_dist_2,
            reward_distance_3=reward_dist_3,
            rr_tp1=rr_tp1,
            rr_tp2=rr_tp2,
            rr_tp3=rr_tp3,
            min_required_rr=effective_min_rr,
            difference=diff,
            rejection_reason=reason,
            explanation=reason,
            cost_basis=cost_basis,
            is_net=is_net,
            net_rr_tp1=net_rr_tp1,
            spread=effective_spread,
            commission_per_unit=comm_per_unit,
            estimated_total_costs=estimated_total_costs,
            gate_details=gate_details
        )

    # All gates passed: APPROVED!
    explanation = (
        f"Signal APPROVED: TP1 Risk/Reward 1:{rr_tp1:.2f} satisfies minimum 1:{effective_min_rr:.1f} floor. "
        f"All price levels, quote safety, technical confirmation, and risk gates verified."
    )
    return RiskRewardValidationResult(
        status=STATUS_APPROVED,
        is_approved=True,
        symbol=norm_symbol,
        direction=clean_dir,
        entry_price=e,
        stop_loss=sl,
        take_profit_1=tp1,
        take_profit_2=tp2,
        take_profit_3=tp3,
        risk_distance=risk_dist,
        reward_distance_1=reward_dist_1,
        reward_distance_2=reward_dist_2,
        reward_distance_3=reward_dist_3,
        rr_tp1=rr_tp1,
        rr_tp2=rr_tp2,
        rr_tp3=rr_tp3,
        min_required_rr=effective_min_rr,
        difference=diff,
        rejection_reason=None,
        explanation=explanation,
        cost_basis=cost_basis,
        is_net=is_net,
        net_rr_tp1=net_rr_tp1,
        spread=effective_spread,
        commission_per_unit=comm_per_unit,
        estimated_total_costs=estimated_total_costs,
        gate_details=gate_details
    )
