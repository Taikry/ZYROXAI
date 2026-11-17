"""
Continuous Market Monitoring Engine for TAIKRY AI MARKET INTELLIGENCE PRO
Orchestrates:
- 15-minute analysis cycles for primary assets
- Real-time paper trade position tracking & TP/SL execution
- Weekend closure awareness (Commodities & Forex vs 24/7 Crypto)
- Deduplication and cooldown management
- Error recovery with exponential backoff
"""
import logging
import time
import datetime
import threading
import math
from typing import Dict, Any, List

from taikry.config import (
    WATCHLIST,
    PRIMARY_SYMBOL,
    MONITORING_INTERVAL_MINUTES,
    COOLDOWN_MINUTES,
    MIN_RISK_REWARD_RATIO,
    TELEGRAM_CHAT_ID
)
from taikry.data.validator import is_market_open
from taikry.agents.consensus_engine import ai_consensus_engine
from taikry.agents.registry import agent_registry
from taikry.trading.paper_trading import paper_trading_engine
from taikry.trading.lifecycle import signal_lifecycle_manager, SignalState
from taikry.notifications.telegram_service import telegram_service
from taikry.notifications.make_webhook_dispatcher import dispatch_to_make
from taikry.trading.xauusd_signal_engine import xauusd_signal_engine, normalize_xauusd_symbol
from taikry.trading.xauusd_tracker import xauusd_performance_tracker

logger = logging.getLogger("taikry.monitoring.engine")


def _expire_trial_subscriptions(now_utc=None) -> int:
    """Mark expired SaaS trials on their subscription records."""
    from taikry.database.models import UserSubscription
    from taikry.database.session import SessionLocal

    if now_utc is None:
        # Subscription timestamps use timezone-naive UTC database columns.
        now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    elif now_utc.tzinfo is not None:
        now_utc = now_utc.astimezone(datetime.timezone.utc).replace(tzinfo=None)

    db = SessionLocal()
    try:
        expired_subscriptions = db.query(UserSubscription).filter(
            UserSubscription.status == "trial_active",
            UserSubscription.trial_expires_at.isnot(None),
            UserSubscription.trial_expires_at <= now_utc,
        ).all()
        for subscription in expired_subscriptions:
            subscription.status = "trial_expired"
        if expired_subscriptions:
            db.commit()
        return len(expired_subscriptions)
    finally:
        db.close()


class MarketMonitor247:
    """Continuous market surveillance while the host process is running."""

    def __init__(self):
        self.is_running = False
        self._thread = None
        self.interval_seconds = max(1, int(MONITORING_INTERVAL_MINUTES)) * 60
        self.cooldown_tracker = {}
        self.last_scan_time = None
        self.last_vip_check_time = 0
        self.last_error = None
        self._state_lock = threading.Lock()
        self._scan_lock = threading.Lock()
        self._stop_event = threading.Event()
        self.stats = {
            "cycles_completed": 0,
            "reports_generated": 0,
            "alerts_dispatched": 0,
            "errors_handled": 0
        }

    def start_background(self):
        """Starts monitoring in a dedicated daemon thread."""
        with self._state_lock:
            if self.is_running and self._thread and self._thread.is_alive():
                return
            self._stop_event.clear()
            self.is_running = True
            self._thread = threading.Thread(target=self._run_loop, name="taikry-market-monitor", daemon=True)
            self._thread.start()

    def stop(self):
        """Signals monitoring loop to gracefully terminate."""
        with self._state_lock:
            self.is_running = False
            self._stop_event.set()

    def scan_once(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Run one serialized scan so background and manual requests cannot double-dispatch."""
        with self._scan_lock:
            return self._scan_once(symbols)

    def _scan_once(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """
        Executes a single end-to-end market scan across watchlist.
        Prioritizes XAUUSD (Gold) as #1 asset in the universe.
        Dispatches the #1 validated setup with AI Confluence Score 80%-95%.
        Evaluates active and waiting signal lifecycle state transitions on every tick.
        """
        errors_before = self.stats["errors_handled"]
        raw_symbols = symbols or [w["symbol"] for w in WATCHLIST]
        # Institutional Priority Queue: XAUUSD scanned first
        target_symbols = sorted(raw_symbols, key=lambda s: 0 if s == PRIMARY_SYMBOL else 1)

        results = []
        current_prices = {}
        qualifying_candidates = []

        for raw_sym in target_symbols:
            sym = str(raw_sym).strip().upper()
            if not sym:
                continue
            open_ok, reason = is_market_open(sym)
            if not open_ok:
                # Weekend / Closed hours for Forex & Gold: Skip gracefully without raising errors
                continue

            try:
                consensus_adapter = agent_registry.get_adapter("consensus_engine")
                if consensus_adapter:
                    res = consensus_adapter.execute(symbol=sym, force_refresh=True)
                else:
                    res = ai_consensus_engine.analyze_symbol(sym, force_refresh=True)
                results.append(res)
                self.stats["reports_generated"] += 1

                try:
                    verified_p = float(res.get("verified_price") or 0.0)
                except (TypeError, ValueError):
                    verified_p = 0.0
                data_quality = res.get("data_quality") or {}
                freshness = data_quality.get("freshness") or {}
                price_source = str(res.get("price_source") or "").upper()
                price_is_verified = (
                    freshness.get("fresh") is True
                    and not data_quality.get("synthetic_timeframes")
                    and not any(marker in price_source for marker in ("SYNTHETIC", "DEMO", "UNAVAILABLE"))
                )
                if price_is_verified and math.isfinite(verified_p) and verified_p > 0:
                    current_prices[sym] = verified_p

                setup_status = res.get("setup_status")
                prop_dir = res.get("proposed_direction")
                try:
                    score = float(res.get("ai_score") or res.get("confidence_score") or 0)
                except (TypeError, ValueError):
                    score = 0.0

                # Only complete, directionally valid setups in the approved alert band can be dispatched.
                if (
                    setup_status == "APPROVE"
                    and prop_dir in ["LONG", "SHORT", "BUY", "SELL"]
                    and math.isfinite(score)
                    and 80 <= score <= 95
                    and price_is_verified
                    and self._has_valid_plan(res)
                ):
                    qualifying_candidates.append(res)

            except Exception:
                self.stats["errors_handled"] += 1
                self.last_error = f"{sym}: analysis failed"
                logger.exception("Market analysis failed for %s", sym)

        # Institutional Selection: Dispatch ONLY the single #1 BEST SETUP from the universe
        if qualifying_candidates:
            # Sort by ai_score descending, with gold (XAUUSD) preference on score ties
            qualifying_candidates.sort(
                key=lambda x: (
                    float(x.get("ai_score") or x.get("confidence_score") or 0),
                    1 if str(x.get("symbol", "")).upper() == "XAUUSD" else 0
                ),
                reverse=True
            )
            best_setup = qualifying_candidates[0]
            try:
                self._handle_approved_setup(best_setup)
            except Exception:
                self.stats["errors_handled"] += 1
                self.last_error = f"{best_setup.get('symbol', 'unknown')}: signal dispatch failed"
                logger.exception("Approved signal dispatch failed for %s", best_setup.get("symbol"))

        # 1. Evaluate persistent signal lifecycle states against latest prices
        if current_prices:
            signal_lifecycle_manager.evaluate_signals(current_prices)
            # Evaluate dedicated XAUUSD Telegram signal outcomes
            xau_price = current_prices.get("XAUUSD")
            if xau_price and xau_price > 0:
                xauusd_performance_tracker.evaluate_signals_against_market(xau_price)

        # 2. Check and update open paper trades against latest prices
        if current_prices:
            closed_events = paper_trading_engine.update_open_trades(current_prices)
            for ev in closed_events:
                self._notify_trade_closure(ev)

        # 3. Periodic VIP Subscription & SaaS Trial Expiration Sweep (Every 15 mins)
        now_ts = time.time()
        if now_ts - self.last_vip_check_time >= 900:
            self.last_vip_check_time = now_ts
            try:
                from taikry.subscriptions.vip_manager import vip_subscription_manager
                vip_subscription_manager.check_and_process_expirations()
            except Exception:
                self.stats["errors_handled"] += 1
                self.last_error = "VIP subscription expiration sweep failed"
                logger.exception("VIP subscription expiration sweep failed")
            # SaaS 14-Day Free Trial expiration sweep
            try:
                _expire_trial_subscriptions()
            except Exception:
                self.stats["errors_handled"] += 1
                self.last_error = "trial expiration sweep failed"
                logger.exception("SaaS trial expiration sweep failed")

        self.last_scan_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if self.stats["errors_handled"] == errors_before:
            self.last_error = None
        self.stats["cycles_completed"] += 1
        return results

    @staticmethod
    def _has_valid_plan(consensus_res: Dict[str, Any]) -> bool:
        """Reject incomplete or directionally inconsistent plans before choosing a dispatch candidate."""
        direction = str(consensus_res.get("proposed_direction") or "").upper()
        is_buy = direction in ("LONG", "BUY")
        if not is_buy and direction not in ("SHORT", "SELL"):
            return False
        try:
            entry = float(consensus_res.get("entry_price"))
            stop = float(consensus_res.get("stop_loss"))
            tp1 = float(consensus_res.get("take_profit_1"))
        except (TypeError, ValueError):
            return False
        if not all(math.isfinite(value) and value > 0 for value in (entry, stop, tp1)):
            return False
        if (is_buy and not stop < entry < tp1) or (not is_buy and not stop > entry > tp1):
            return False
        if abs(tp1 - entry) / abs(entry - stop) < float(MIN_RISK_REWARD_RATIO):
            return False

        tp2_raw = consensus_res.get("take_profit_2")
        if tp2_raw is not None:
            try:
                tp2 = float(tp2_raw)
            except (TypeError, ValueError):
                return False
            if not math.isfinite(tp2) or tp2 <= 0:
                return False
            if (is_buy and tp2 <= tp1) or (not is_buy and tp2 >= tp1):
                return False
        return True

    def _handle_approved_setup(self, consensus_res: Dict[str, Any]):
        """
        Dispatches high-conviction approved setup.
        XAUUSD uses the broker-validated signal engine and atomic daily quota.
        Other supported symbols use the same verified consensus plan that passed this scan.
        """
        sym = consensus_res["symbol"]
        try:
            score = float(consensus_res.get("ai_score") or consensus_res.get("confidence_score") or 0)
        except (TypeError, ValueError):
            return

        if consensus_res.get("setup_status") != "APPROVE" or consensus_res.get("proposed_direction") not in ["LONG", "SHORT", "BUY", "SELL"]:
            return

        # Strict Guard: Score MUST be strictly within 80% - 95%
        if score < 80 or score > 95:
            return

        is_buy = consensus_res.get("proposed_direction") in ["LONG", "BUY"]
        direction = "BUY" if is_buy else "SELL"

        # Respect the configured cooldown to prevent repeated alerts for the same symbol.
        cooldown_limit = max(0.0, float(COOLDOWN_MINUTES))
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        last_time = self.cooldown_tracker.get(sym)
        if last_time:
            if last_time.tzinfo is None:
                last_time = last_time.replace(tzinfo=datetime.timezone.utc)
            elapsed_min = (now_utc - last_time).total_seconds() / 60.0
            if elapsed_min < cooldown_limit:
                return

        if not self._has_valid_plan(consensus_res):
            logger.info("Approved setup for %s skipped: price levels are incomplete or conflict with direction.", sym)
            return
        entry = float(consensus_res["entry_price"])
        sl = float(consensus_res["stop_loss"])
        tp1 = float(consensus_res["take_profit_1"])
        tp2_raw = consensus_res.get("take_profit_2")
        tp2 = float(tp2_raw) if tp2_raw is not None else None

        # 1. Register persistent stateful signal in Signal Lifecycle Manager (General Dashboard)
        created_signal = signal_lifecycle_manager.create_signal(
            symbol=sym,
            direction=direction,
            entry_price=entry,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2,
            risk_reward=consensus_res.get("risk_reward_ratio", "N/A"),
            ai_score=score,
            timeframe=consensus_res.get("timeframe", "M15"),
            initial_state=SignalState.WAITING_CONFIRMATION,
            trigger_cause=f"AI Consensus score {score}% approved for {direction} {sym}"
        )

        # 2. Execute simulated paper trade (Internal dashboard simulation)
        paper_res = paper_trading_engine.open_trade(
            symbol=sym,
            direction=direction,
            entry_price=entry,
            stop_loss=sl,
            take_profit_1=tp1,
            take_profit_2=tp2
        )

        # 3. Send the approved plan to Telegram. Gold remains subject to its
        # dedicated fresh-MT5 checks and persisted daily delivery quota.
        telegram_ok = False
        canonical_gold = normalize_xauusd_symbol(sym)
        if canonical_gold == "XAUUSD":
            xau_signal = xauusd_signal_engine.generate_xauusd_signal("XAUUSD")
            if xau_signal.get("success"):
                telegram_ok, msg_id, tg_err = telegram_service.send_xauusd_signal_alert(xau_signal)
                if not telegram_ok:
                    logger.warning("Telegram delivery failed for %s: %s", sym, tg_err)
                elif msg_id and created_signal.get("signal_id"):
                    signal_lifecycle_manager.attach_telegram_message(
                        created_signal["signal_id"], msg_id, take_profit_3=xau_signal.get("take_profit_3")
                    )
            else:
                logger.info("XAUUSD signal suppressed: %s", xau_signal.get("error") or xau_signal.get("rejection_reason"))
        else:
            report_payload = dict(consensus_res)
            report_payload["signal_id"] = created_signal.get("signal_id")
            telegram_ok = telegram_service.send_validated_signal_report(report_payload)
            if not telegram_ok:
                logger.info("Telegram did not deliver the validated %s plan (check bot configuration and plan freshness).", sym)

        # 4. Dispatch to Make Webhook (for automation / dashboard logging)
        payload = {
            "event": "VALIDATED_SIGNAL",
            "signal_id": created_signal.get("signal_id"),
            "symbol": sym,
            "direction": direction,
            "ai_score": score,
            "entry_price": consensus_res["entry_price"],
            "stop_loss": consensus_res["stop_loss"],
            "take_profit_1": consensus_res["take_profit_1"],
            "take_profit_2": tp2,
            "risk_reward": consensus_res.get("risk_reward_ratio"),
            "signal_plan": {
                "action": direction,
                "symbol": sym,
                "timeframe": consensus_res.get("timeframe", "M15"),
                "entry_price": entry,
                "stop_loss": sl,
                "take_profit_1": tp1,
                "take_profit_2": tp2,
                "risk_reward": consensus_res.get("risk_reward_ratio"),
                "ai_score": score,
                "score_explanation": consensus_res.get("score_explanation"),
                "price_source": consensus_res.get("price_source"),
                "timestamp_utc": consensus_res.get("timestamp_utc"),
            },
            "timeframe": consensus_res.get("timeframe", "M15"),
            "price_source": consensus_res.get("price_source"),
            "setup_status": consensus_res.get("setup_status"),
            "paper_trade": paper_res,
            "report_english": consensus_res.get("report_english"),
            "report_khmer": consensus_res.get("report_khmer"),
            **({"chat_id": TELEGRAM_CHAT_ID, "telegram_chat_id": TELEGRAM_CHAT_ID} if TELEGRAM_CHAT_ID else {}),
            "timestamp": now_utc.isoformat()
        }
        make_result = dispatch_to_make(payload, event_type="critical_market_alert")
        if not make_result.get("success"):
            logger.warning("Make webhook delivery failed for %s: %s", sym, make_result.get("error"))

        self.cooldown_tracker[sym] = now_utc
        if telegram_ok or make_result.get("success"):
            self.stats["alerts_dispatched"] += 1

    def _notify_trade_closure(self, trade_event: Dict[str, Any]):
        """Dispatches trade completion notification."""
        if trade_event.get("user_id") is not None:
            from taikry.trading.paper_trade_alerts import dispatch_paper_trade_alert
            dispatch_paper_trade_alert(trade_event)
            return

        msg = f"""🔔 <b>PAPER TRADE CLOSED: {trade_event['direction']} {trade_event['symbol']}</b>

Reason: <b>{trade_event['exit_reason']}</b>
Exit Price: <code>{trade_event['exit_price']}</code>
Net PnL: <b>${trade_event['net_pnl']:+,.2f}</b>
R-Multiple: <b>{trade_event['r_multiple']:+.2f}R</b>
"""
        if not telegram_service.send_message(msg):
            logger.info("Trade closure notification was not delivered for %s", trade_event.get("symbol", "unknown"))

    def _run_loop(self):
        """
        Durable background scheduler aligned to M15 candle closes.
        - Continuous intrabar position and price tracking every 5 seconds.
        - Triggers full multi-agent analysis exactly at :00, :15, :30, :45 UTC.
        - Persists every 15-minute report into fifteen_minute_market_reports.
        """
        logger.info("ZYROX AI V3.1 M15 Candle Close Scheduler started.")

        while self.is_running and not self._stop_event.is_set():
            try:
                wait_sec, candle_label = get_seconds_to_next_m15_close()
                target_utc = time.time() + wait_sec

                # Sub-loop: run continuous intrabar surveillance until the M15 close
                while time.time() < target_utc and not self._stop_event.is_set():
                    # 1. Update open paper trades against latest prices
                    try:
                        from taikry.data.mt5_receiver import mt5_tick_receiver
                        current_quote = mt5_tick_receiver.get_latest_tick("XAUUSD")
                        if current_quote and current_quote.get("bid"):
                            xau_price = float(current_quote["bid"])
                            closed = paper_trading_engine.update_open_trades({"XAUUSD": xau_price})
                            for ev in closed:
                                self._notify_trade_closure(ev)
                    except Exception as tick_err:
                        logger.debug("Intrabar trade check note: %s", tick_err)

                    # Sleep in small slices (5s) to allow responsive cancellation and timely triggers
                    time_remaining = target_utc - time.time()
                    sleep_time = min(5.0, max(0.5, time_remaining))
                    if time_remaining > 0.5:
                        self._stop_event.wait(sleep_time)

                if self._stop_event.is_set():
                    break

                # M15 Candle Close reached! Execute full 15-minute cycle
                cycle_start = time.monotonic()
                logger.info("Executing scheduled M15 analysis cycle for %s...", candle_label)

                # Execute full analysis for XAUUSD Gold
                consensus_adapter = agent_registry.get_adapter("consensus_engine")
                if consensus_adapter:
                    res = consensus_adapter.execute(symbol="XAUUSD", force_refresh=True)
                else:
                    res = ai_consensus_engine.analyze_symbol("XAUUSD", force_refresh=True)

                # Persist to database
                _save_fifteen_minute_report(res, candle_label)
                self.stats["reports_generated"] += 1
                self.stats["cycles_completed"] += 1

                # Check if setup is actionable (Score >= 75 and all gates pass)
                confluence_info = res.get("confluence_score") or {}
                selected_score = int(confluence_info.get("selected_score") or res.get("ai_score") or 0)
                is_actionable = bool(
                    confluence_info.get("is_actionable")
                    or (res.get("setup_status") == "APPROVE" and selected_score >= 75)
                )

                if is_actionable and res.get("setup_status") == "APPROVE":
                    self._handle_approved_setup(res)

                elapsed = time.monotonic() - cycle_start
                logger.info(
                    "Completed M15 cycle for %s in %.2fs (Decision: %s, Score: %d/100)",
                    candle_label, elapsed, res.get("setup_status", "WAIT"), selected_score
                )

            except Exception:
                self.stats["errors_handled"] += 1
                self.last_error = "M15 scheduler cycle failure"
                logger.exception("Unhandled M15 scheduler cycle failure")
                self._stop_event.wait(10.0)

        with self._state_lock:
            self.is_running = False
        logger.info("ZYROX AI V3.1 M15 Candle Close Scheduler stopped.")


def get_seconds_to_next_m15_close():
    """
    Returns (seconds_to_wait, candle_close_label_utc).
    Next M15 mark is at minute 00, 15, 30, or 45:00 UTC.
    Adds a 2-second grace period for broker bar completion.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    minute = now.minute
    next_m = ((minute // 15) + 1) * 15
    if next_m == 60:
        target_close = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    else:
        target_close = now.replace(minute=next_m, second=0, microsecond=0)

    execution_time = target_close + datetime.timedelta(seconds=2)
    wait_seconds = (execution_time - now).total_seconds()
    candle_label = target_close.strftime("%Y-%m-%d %H:%M:00 UTC")
    return max(1.0, wait_seconds), candle_label


def _save_fifteen_minute_report(report_res: Dict[str, Any], candle_close_label: str) -> bool:
    """Persists a scheduled 15-minute M15 report for XAUUSD into fifteen_minute_market_reports."""
    from taikry.database.session import SessionLocal
    from taikry.database.models import FifteenMinuteMarketReport

    db = SessionLocal()
    try:
        confluence_data = report_res.get("confluence_score") or {}
        cat_scores = confluence_data.get("category_breakdown") or {}

        existing = db.query(FifteenMinuteMarketReport).filter(
            FifteenMinuteMarketReport.candle_close_utc == candle_close_label
        ).first()

        decision = str(report_res.get("setup_status") or "WAIT").upper()
        if decision not in {"WAIT", "HOLD", "BUY", "SELL"}:
            decision = "WAIT"

        buy_sc = int(report_res.get("confluence_buy_score") or confluence_data.get("buy_score") or 0)
        sell_sc = int(report_res.get("confluence_sell_score") or confluence_data.get("sell_score") or 0)
        sel_sc = int(confluence_data.get("selected_score") or report_res.get("ai_score") or 0)
        grade = str(confluence_data.get("grade") or "WEAK")
        is_act = bool(confluence_data.get("is_actionable", False))

        entry_p = report_res.get("entry_price")
        sl_p = report_res.get("stop_loss")
        tp1_p = report_res.get("take_profit_1")
        tp2_p = report_res.get("take_profit_2")
        tp3_p = report_res.get("take_profit_3")
        rr_str = str(report_res.get("risk_reward_ratio") or "")

        if not existing:
            record = FifteenMinuteMarketReport(
                candle_close_utc=candle_close_label,
                cycle_timestamp=datetime.datetime.now(datetime.timezone.utc),
                symbol="XAUUSD",
                timeframe="M15",
                decision_status=decision,
                market_bias=str(report_res.get("market_bias") or "NEUTRAL"),
                confluence_buy_score=buy_sc,
                confluence_sell_score=sell_sc,
                selected_score=sel_sc,
                score_grade=grade,
                is_actionable=is_act,
                market_price=float(report_res.get("verified_price") or 0.0),
                spread=float(report_res.get("data_quality", {}).get("spread") or 0.0) if isinstance(report_res.get("data_quality"), dict) else None,
                entry_price=float(entry_p) if entry_p is not None and str(entry_p) != "N/A" else None,
                stop_loss=float(sl_p) if sl_p is not None and str(sl_p) != "N/A" else None,
                take_profit_1=float(tp1_p) if tp1_p is not None and str(tp1_p) != "N/A" else None,
                take_profit_2=float(tp2_p) if tp2_p is not None and str(tp2_p) != "N/A" else None,
                take_profit_3=float(tp3_p) if tp3_p is not None and str(tp3_p) != "N/A" else None,
                risk_reward=rr_str,
                category_scores=cat_scores,
                supporting_reasons=confluence_data.get("supporting_reasons"),
                contradicting_reasons=confluence_data.get("contradicting_reasons"),
                missing_confirmations=confluence_data.get("missing_confirmations"),
                report_en=report_res.get("report_english"),
                report_kh=report_res.get("report_khmer"),
                telegram_dispatched=False
            )
            db.add(record)
        else:
            existing.decision_status = decision
            existing.market_bias = str(report_res.get("market_bias") or "NEUTRAL")
            existing.confluence_buy_score = buy_sc
            existing.confluence_sell_score = sell_sc
            existing.selected_score = sel_sc
            existing.score_grade = grade
            existing.is_actionable = is_act
            existing.category_scores = cat_scores
            existing.report_en = report_res.get("report_english")
            existing.report_kh = report_res.get("report_khmer")

        db.commit()
        return True
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to persist FifteenMinuteMarketReport: %s", exc)
        return False
    finally:
        db.close()

market_monitor_247 = MarketMonitor247()
