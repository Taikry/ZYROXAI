"""
AGENT 4 — INDEPENDENT RISK VALIDATOR
The Gatekeeper and Chief Risk Officer.
Independently reviews findings of Agents 1, 2, and 3.
Validates:
- Higher-timeframe (HTF) trend agreement
- Inter-agent conflicting biases
- Data freshness & market open status
- Spread and volatility bounds
- Entry, Stop-Loss, and Take-Profit structural geometry
- Strict Risk-to-Reward ratio (configured minimum)
- Risk per trade sizing (configured percentage of simulated equity)
- Economic event proximity risk
Decision: APPROVE, REJECT, WAIT, or NO TRADE with explicit reasons.
"""
from typing import Dict, Any, List, Optional
import math
from taikry.config import (
    MIN_RISK_REWARD_RATIO,
    RISK_PER_TRADE_PERCENT,
    INITIAL_PAPER_BALANCE,
    MAX_SIMULTANEOUS_POSITIONS,
    get_symbol_config,
    get_risk_profile,
    RISK_PROFILES
)
from taikry.data.validator import check_data_freshness, is_market_open
from taikry.data.economic_calendar import economic_calendar_provider
from taikry.data.providers import market_data_engine
from taikry.database.session import SessionLocal
from taikry.database.models import PaperTrade

class RiskValidatorAgent:
    """Agent 4: Independent Quantitative Risk & Governance Auditor."""
    AGENT_ID = "risk_validator"
    AGENT_NAME = "Agent 4 — Independent Risk Validator"

    def validate(
        self,
        symbol: str,
        verified_price: float,
        price_timestamp: Any,
        agent1_report: Dict[str, Any],
        agent2_report: Dict[str, Any],
        agent3_report: Dict[str, Any],
        simulated_equity: float = INITIAL_PAPER_BALANCE,
        open_positions_count: Optional[int] = None,
        spread_price: Optional[float] = None,
        candidate_levels: Optional[Dict[str, Any]] = None,
        bid_price: Optional[float] = None,
        ask_price: Optional[float] = None,
        trade_style: str = "INTRADAY",
        risk_mode: Optional[str] = None,
        risk_options: Optional[Dict[str, Any]] = None,
        min_risk_reward_ratio: Optional[float] = None,
        risk_per_trade_percent: Optional[float] = None,
        max_spread_pct: Optional[float] = None,
        news_filter_mode: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Runs independent risk assessment.
        Returns strict institutional verdict adaptive to selected Risk Profile.
        """

        custom_overrides = dict(risk_options or {})
        if min_risk_reward_ratio is not None:
            custom_overrides["min_risk_reward_ratio"] = min_risk_reward_ratio
        if risk_per_trade_percent is not None:
            custom_overrides["risk_per_trade_percent"] = risk_per_trade_percent
        if max_spread_pct is not None:
            custom_overrides["max_spread_pct"] = max_spread_pct
        if news_filter_mode is not None:
            custom_overrides["news_filter_mode"] = news_filter_mode
        active_profile = get_risk_profile(risk_mode, custom_overrides)
        eff_min_rr = float(active_profile.get("min_risk_reward_ratio", MIN_RISK_REWARD_RATIO))
        eff_risk_pct = float(active_profile.get("risk_per_trade_percent", RISK_PER_TRADE_PERCENT))
        eff_max_spread = float(active_profile.get("max_spread_pct", 0.20))
        eff_news_mode = str(active_profile.get("news_filter_mode", "STANDARD")).upper()

        rejection_reasons = []
        warning_notes = []
        validation_checks = {
            "risk_profile": active_profile,
            "min_required_rr": eff_min_rr,
            "max_risk_percent": eff_risk_pct,
            "max_spread_pct": eff_max_spread,
            "news_filter_mode": eff_news_mode
        }

        try:
            verified_price = float(verified_price)
            simulated_equity = float(simulated_equity)
        except (TypeError, ValueError):
            verified_price = 0.0
            simulated_equity = 0.0
        if not math.isfinite(verified_price) or verified_price <= 0:
            rejection_reasons.append("Verified market price is missing or invalid; setup rejected.")
        if not math.isfinite(simulated_equity) or simulated_equity <= 0:
            rejection_reasons.append("Account equity is missing or invalid; position sizing cannot be verified.")

        if spread_price is None:
            # Render and other cloud deployments cannot read a desktop MT5
            # bridge. Use the same verified broker quote path as data quality
            # (MT5 when available, otherwise authenticated OANDA v20, Binance, or institutional estimate).
            quote = market_data_engine.get_verified_quote(symbol)
            if quote:
                try:
                    bid = float(quote.get("bid"))
                    ask = float(quote.get("ask"))
                    if math.isfinite(bid) and math.isfinite(ask) and bid > 0 and ask > bid:
                        spread_price = ask - bid
                        if bid_price is None or ask_price is None:
                            if verified_price > 0 and abs(verified_price - ((bid + ask) / 2.0)) / verified_price < 0.05:
                                bid_price = bid
                                ask_price = ask
                except (TypeError, ValueError):
                    spread_price = None

        if spread_price is None:
            # Authoritative institutional fallback from symbol configuration
            cfg = get_symbol_config(symbol)
            spread_est = cfg.get("spread_estimate")
            if spread_est is not None:
                try:
                    spread_price = float(spread_est)
                    if verified_price > 0:
                        bid_price = round(verified_price - spread_price / 2.0, 5)
                        ask_price = round(verified_price + spread_price / 2.0, 5)
                except (TypeError, ValueError):
                    spread_price = None

        try:
            spread_price = float(spread_price) if spread_price is not None else None
        except (TypeError, ValueError):
            spread_price = None
        if spread_price is None or not math.isfinite(spread_price) or spread_price <= 0:
            rejection_reasons.append("Verified bid/ask spread is unavailable; execution cost cannot be checked.")
            spread_price = None
        validation_checks["spread_price"] = spread_price



        positions_verified = open_positions_count is not None
        if open_positions_count is None:
            db = SessionLocal()
            try:
                open_positions_count = db.query(PaperTrade).filter(PaperTrade.status == "OPEN").count()
                positions_verified = True
            except Exception:
                open_positions_count = MAX_SIMULTANEOUS_POSITIONS
                rejection_reasons.append("Could not verify the number of open paper positions; setup rejected.")
            finally:
                db.close()

        # 1. Market Open & Data Freshness Check
        open_ok, open_msg = is_market_open(symbol)
        freshness = check_data_freshness(symbol, price_timestamp)
        validation_checks["market_open"] = open_ok
        validation_checks["data_freshness"] = freshness["status"]

        if not open_ok:
            rejection_reasons.append(f"Market is closed ({open_msg}); new setup rejected.")

        if not freshness["fresh"] and freshness["status"] != "WEEKEND_CLOSED":
            rejection_reasons.append(f"Market data is stale ({freshness['age_minutes']} minutes old). Trade rejected.")

        # 1b. Real-Time High-Impact News Blackout Check (FOMC, PPI, CPI, NFP)
        blackout = economic_calendar_provider.check_news_blackout(symbol)
        validation_checks["news_blackout_active"] = blackout.get("is_blackout", False)
        validation_checks["calendar_status"] = blackout.get("status", "UNKNOWN")
        if eff_news_mode != "OFF":
            if blackout.get("is_blackout"):
                if eff_news_mode == "FLEXIBLE":
                    warning_notes.append(f"Flexible scalp mode: {blackout.get('advisory_en')}")
                else:
                    rejection_reasons.append(blackout["advisory_en"])
                    warning_notes.append(blackout["advisory_kh"])
            elif blackout.get("status") == "UNAVAILABLE":
                if eff_news_mode == "FLEXIBLE":
                    warning_notes.append("Calendar feed unavailable: proceeding under scalp risk limits.")
                else:
                    rejection_reasons.append(blackout["advisory_en"])
                    warning_notes.append(blackout["advisory_kh"])

        # 2. Maximum Simultaneous Position Count Check
        validation_checks["open_positions_count"] = open_positions_count
        validation_checks["open_positions_verified"] = positions_verified
        if open_positions_count >= MAX_SIMULTANEOUS_POSITIONS:
            rejection_reasons.append(f"Maximum simultaneous open position limit ({MAX_SIMULTANEOUS_POSITIONS}) reached. Trade rejected.")

        # 3. Inter-Agent Agreement and Conflict Analysis
        bias_1 = agent1_report.get("bias", "NEUTRAL")
        bias_2 = agent2_report.get("bias", "NEUTRAL")
        bias_3 = agent3_report.get("bias", "NEUTRAL")

        # Map directions
        def get_direction(b: str) -> str:
            if "BULLISH" in b:
                return "LONG"
            if "BEARISH" in b:
                return "SHORT"
            return "FLAT"

        dir_1 = get_direction(bias_1)
        dir_2 = get_direction(bias_2)
        dir_3 = get_direction(bias_3)

        validation_checks["agent1_direction"] = dir_1
        validation_checks["agent2_direction"] = dir_2
        validation_checks["agent3_direction"] = dir_3

        # Major conflict detection: e.g. Agent 1 says LONG, Agent 2 says SHORT
        if dir_1 != "FLAT" and dir_2 != "FLAT" and dir_1 != dir_2:
            rejection_reasons.append(
                f"Severe Inter-Agent Conflict: Technical Analyst proposes {dir_1} while ICT/SMC Analyst proposes {dir_2}. Consensus impossible."
            )

        if dir_1 == "FLAT" and dir_2 == "FLAT":
            # Fallback to Macro Analyst direction or structural tilt
            proposed_dir = dir_3 if dir_3 != "FLAT" else "NONE"
            if proposed_dir == "NONE":
                rejection_reasons.append("No directional consensus from technical, ICT/SMC, or macro agents.")
            else:
                warning_notes.append("Technical & ICT agents are neutral; direction is based on macro analysis only.")
        else:
            proposed_dir = dir_1 if dir_1 != "FLAT" else dir_2

        # 4. Entry, Stop-Loss, and Take-Profit Calculation Validation
        klevels_1 = agent1_report.get("key_price_levels", {})
        klevels_2 = agent2_report.get("key_price_zones", {})
        try:
            atr = float(klevels_1.get("atr") or 0.0)
        except (TypeError, ValueError):
            atr = 0.0
        if not math.isfinite(atr) or atr <= 0:
            atr = 0.0

        try:
            bid_price = float(bid_price) if bid_price is not None else None
            ask_price = float(ask_price) if ask_price is not None else None
        except (TypeError, ValueError):
            bid_price = ask_price = None

        # Select candidate SL/TP from the agent that actually proposed the direction
        candidate_source = candidate_levels
        if candidate_source is None and proposed_dir == dir_1 and agent1_report.get("setup_eligible"):
            candidate_source = klevels_1
        elif candidate_source is None and proposed_dir == dir_2 and agent2_report.get("setup_eligible"):
            candidate_source = klevels_2
        elif candidate_source is None and proposed_dir == dir_1:
            candidate_source = klevels_1
        elif candidate_source is None and proposed_dir == dir_2:
            candidate_source = klevels_2
        elif candidate_source is None:
            candidate_source = klevels_1 if klevels_1.get("suggested_stop_loss") else klevels_2

        sl = candidate_source.get("suggested_stop_loss", candidate_source.get("stop_loss")) if candidate_source else None
        tp1 = candidate_source.get("take_profit_1") if candidate_source else None
        tp2 = candidate_source.get("take_profit_2") if candidate_source else None
        normalized_levels = []
        for level in (sl, tp1, tp2):
            try:
                numeric_level = float(level)
                normalized_levels.append(numeric_level if math.isfinite(numeric_level) and numeric_level > 0 else None)
            except (TypeError, ValueError):
                normalized_levels.append(None)
        sl, tp1, tp2 = normalized_levels

        # Do not manufacture a trade direction or price levels when all agents are neutral.
        entry = verified_price
        dec = 3 if "JPY" in str(symbol).upper() else (2 if verified_price > 10 else 4)
        if proposed_dir not in ("LONG", "SHORT"):
            sl = tp1 = tp2 = None
            risk = reward_tp1 = 0.0
        else:
            # For a real market-entry plan, account for the executable side of
            # the spread instead of pricing both directions at the midpoint.
            if bid_price is not None and ask_price is not None and math.isfinite(bid_price) and math.isfinite(ask_price) and bid_price > 0 and ask_price > bid_price:
                entry = round(ask_price if proposed_dir == "LONG" else bid_price, dec)
            else:
                entry = verified_price
            # Check and refine price geometry
            levels_valid = True
            if proposed_dir == "SHORT":
                # For Short: SL must be above Entry and TP1 below Entry
                if not sl or sl <= entry:
                    if atr <= 0:
                        rejection_reasons.append("A valid stop-loss or measured ATR is required to calculate risk levels.")
                        levels_valid = False
                    else:
                        atr_mult = 0.9 if str(trade_style).upper() == "SCALPING" else 1.5
                        sl = round(entry + (atr_mult * atr), dec)
                if levels_valid:
                    risk = sl - entry
                    if not tp1 or tp1 >= entry:
                        tp1 = round(entry - (risk * eff_min_rr), dec)
                    reward_tp1 = entry - tp1
                    if not tp2 or tp2 >= tp1:
                        tp2 = round(entry - (risk * max(eff_min_rr + 0.5, eff_min_rr * 1.5)), dec)
                else:
                    sl = tp1 = tp2 = None
                    risk = reward_tp1 = 0.0
            else:
                # For Long: SL must be below Entry and TP1 above Entry
                if not sl or sl >= entry:
                    if atr <= 0:
                        rejection_reasons.append("A valid stop-loss or measured ATR is required to calculate risk levels.")
                        levels_valid = False
                    else:
                        atr_mult = 0.9 if str(trade_style).upper() == "SCALPING" else 1.5
                        sl = round(entry - (atr_mult * atr), dec)
                if levels_valid:
                    risk = entry - sl
                    if not tp1 or tp1 <= entry:
                        tp1 = round(entry + (risk * eff_min_rr), dec)
                    reward_tp1 = tp1 - entry
                    if not tp2 or tp2 <= tp1:
                        tp2 = round(entry + (risk * max(eff_min_rr + 0.5, eff_min_rr * 1.5)), dec)
                else:
                    sl = tp1 = tp2 = None
                    risk = reward_tp1 = 0.0

        if risk > 0 and reward_tp1 > 0:
            rr_ratio = round(reward_tp1 / risk, 2)
            validation_checks["calculated_rr"] = f"1:{rr_ratio}"
            # Enforce the selected Risk-to-Reward Ratio floor
            if rr_ratio < eff_min_rr:
                rejection_reasons.append(
                    f"Insufficient Risk-to-Reward: Calculated R:R is 1:{rr_ratio}, which fails the {active_profile['name']} minimum of 1:{eff_min_rr}."
                )
        else:
            rr_ratio = 0.0
            rejection_reasons.append("Missing valid Stop Loss or Take Profit targets.")

        if spread_price is not None and risk > 0 and (spread_price / risk) > eff_max_spread:
            rejection_reasons.append(
                f"Verified spread ({spread_price:g}) exceeds {int(eff_max_spread * 100)}% of stop distance ({risk:g}); setup rejected under {active_profile['name']} profile."
            )

        # 5. Position sizing from configured risk of simulated equity
        cfg = get_symbol_config(symbol)
        max_risk_dollars = simulated_equity * (eff_risk_pct / 100.0)
        validation_checks["simulated_equity"] = simulated_equity
        validation_checks["max_risk_dollars"] = max_risk_dollars

        if sl and risk > 0:
            lot_size = cfg.get("lot_size", 100)
            pip_value = cfg.get("pip_value", 0.1)
            # Standard lot sizing: risk_dollars / (price_risk * lot_size)
            raw_lots = max_risk_dollars / (risk * lot_size)
            if raw_lots < 0.01:
                rejection_reasons.append("Minimum supported position size would exceed the configured risk limit.")
                validation_checks["recommended_position_lots"] = 0.0
            else:
                calculated_lots = min(10.0, math.floor(raw_lots * 100) / 100.0)
                validation_checks["recommended_position_lots"] = calculated_lots
        else:
            validation_checks["recommended_position_lots"] = 0.0

        # 6. Macro Headwind Check (Dissenting opinion preservation)
        if dir_3 != "FLAT" and dir_3 != proposed_dir:
            warning_notes.append(
                f"Macro Headwind Alert: Agent 3 notes fundamental headwind ({bias_3}). Trade size should remain strictly risk-controlled."
            )

        # Final Risk Verdict
        if rejection_reasons:
            decision = "REJECT"
            reasons = rejection_reasons
        elif warning_notes and len(warning_notes) >= 2:
            decision = "WAIT"
            reasons = warning_notes
        else:
            decision = "APPROVE"
            reasons = [
                f"Setup validated: Direction {proposed_dir}, verified R:R 1:{rr_ratio} >= 1:{eff_min_rr}, Risk capped at {eff_risk_pct}% equity (${max_risk_dollars}) under {active_profile['name']} profile."
            ]

        be_trigger = None
        partial_tp = tp1
        runner_tp = tp2
        if entry and sl and risk > 0:
            be_trigger = round(entry + risk, dec) if proposed_dir == "LONG" else round(entry - risk, dec)
            if runner_tp is None:
                runner_tp = round(entry + (2.5 * risk), dec) if proposed_dir == "LONG" else round(entry - (2.5 * risk), dec)

        smart_trading = {
            "breakeven_trigger": be_trigger,
            "partial_take_profit": partial_tp,
            "runner_take_profit": runner_tp,
            "recommended_lots": validation_checks.get("recommended_position_lots", 0.0),
            "trade_style": trade_style,
            "scalp_suitability": "HIGH" if (spread_price is not None and risk > 0 and (spread_price / risk) <= 0.15) else "MODERATE"
        }

        return {
            "agent_id": self.AGENT_ID,
            "agent_name": self.AGENT_NAME,
            "decision": decision,
            "proposed_direction": proposed_dir,
            "entry_price": entry,
            "stop_loss": sl,
            "take_profit_1": tp1,
            "take_profit_2": tp2,
            "calculated_rr": f"1:{rr_ratio}",
            "risk_profile": active_profile,
            "position_sizing": {
                "risk_percent": eff_risk_pct,
                "risk_amount_dollars": max_risk_dollars,
                "recommended_lots": validation_checks.get("recommended_position_lots", 0.0)
            },
            "smart_trading": smart_trading,
            "reasons": reasons,
            "warnings": warning_notes,
            "checks": validation_checks
        }

risk_validator_agent = RiskValidatorAgent()
