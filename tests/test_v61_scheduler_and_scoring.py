"""
Tests for ZYROX AI V6.1 Durable M15 Scheduler & Confluence Scoring:
- Unified 75/100 Minimum Actionable Confluence Score across all subsystems
- Elimination of conflicting 80 <= score <= 95 filters
- Distributed database locking via SystemSetting
- Scheduler heartbeat tracking
"""
import pytest
import datetime
from unittest.mock import MagicMock, patch

from taikry.monitoring.engine import acquire_scheduler_lock, update_scheduler_heartbeat, MarketMonitor247
from taikry.notifications.telegram_service import telegram_service
from taikry.database.session import SessionLocal
from taikry.database.models import SystemSetting


def test_distributed_scheduler_locking():
    key = "test_sched_lock_candle_123"
    owner_a = "worker_node_alpha"
    owner_b = "worker_node_beta"

    # 1. First owner acquires lock
    acquired = acquire_scheduler_lock(key, owner_id=owner_a, ttl_seconds=60)
    assert acquired is True

    # 2. Second owner is blocked while lock is active
    blocked = acquire_scheduler_lock(key, owner_id=owner_b, ttl_seconds=60)
    assert blocked is False

    # 3. Same owner can refresh/reacquire lock
    refreshed = acquire_scheduler_lock(key, owner_id=owner_a, ttl_seconds=60)
    assert refreshed is True


def test_scheduler_heartbeat():
    instance_id = "test_instance_99"
    candle = "2026-11-17 17:00:00 UTC"

    update_scheduler_heartbeat(instance_id, candle, status="HEALTHY")

    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "scheduler_heartbeat_m15").first()
        assert setting is not None
        assert instance_id in setting.value
        assert "HEALTHY" in setting.value
        assert candle in setting.value
    finally:
        db.close()


def test_confluence_score_75_is_accepted_by_telegram(monkeypatch):
    signal_payload = {
        "success": True,
        "status": "VALIDATED",
        "signal_id": "test_sig_75",
        "idempotency_key": "idem_key_75",
        "action": "BUY",
        "direction": "BUY",
        "symbol": "XAUUSD",
        "entry_price": 2650.00,
        "stop_loss": 2640.00,
        "take_profit_1": 2670.00,
        "take_profit_2": 2680.00,
        "take_profit_3": 2690.00,
        "ai_confluence_score": 75,
        "timeframes_analyzed": ["D1", "H4", "M15"],
        "supporting_evidence": ["Bullish Order Block", "ICT Fair Value Gap fill"]
    }

    # Mock DB query for persisted signal
    from taikry.database.session import SessionLocal
    from taikry.database.models import XAUUSDTelegramSignalModel

    db = SessionLocal()
    try:
        db.query(XAUUSDTelegramSignalModel).filter(XAUUSDTelegramSignalModel.signal_id == "test_sig_75").delete()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        sig_record = XAUUSDTelegramSignalModel(
            signal_id="test_sig_75",
            canonical_symbol="XAUUSD",
            direction="BUY",
            timeframes_analyzed=["D1", "H4", "M15"],
            entry_price=2650.0,
            stop_loss=2640.0,
            take_profit_1=2670.0,
            take_profit_2=2680.0,
            take_profit_3=2690.0,
            ai_confluence_score=75,
            consensus_summary="Bullish trend confluence at key order block",
            cambodia_date="2026-11-17",
            audit_history=[],
            signal_status="VALIDATED",
            telegram_delivery_status="PENDING",
            idempotency_key="idem_key_75",
            expires_at=now_utc + datetime.timedelta(minutes=30)
        )
        db.add(sig_record)
        db.commit()

        monkeypatch.setattr(telegram_service, "_dispatch_persistent_message", lambda *_args, **_kwargs: (True, "99999", None, "SENT"))

        success, msg_id, err = telegram_service.send_xauusd_signal_alert(signal_payload)
        # Score 75 must be accepted and not rejected
        assert "score" not in str(err or "").lower()
    finally:
        db.query(XAUUSDTelegramSignalModel).filter(XAUUSDTelegramSignalModel.signal_id == "test_sig_75").delete()
        db.commit()
        db.close()


def test_confluence_score_below_75_is_rejected_by_telegram(monkeypatch):
    signal_payload = {
        "success": True,
        "status": "VALIDATED",
        "signal_id": "test_sig_74",
        "idempotency_key": "idem_key_74",
        "action": "BUY",
        "direction": "BUY",
        "symbol": "XAUUSD",
        "entry_price": 2650.00,
        "stop_loss": 2640.00,
        "take_profit_1": 2670.00,
        "take_profit_2": 2680.00,
        "take_profit_3": 2690.00,
        "ai_confluence_score": 74,  # Sub-threshold
        "timeframes_analyzed": ["D1", "H4", "M15"]
    }

    from taikry.database.session import SessionLocal
    from taikry.database.models import XAUUSDTelegramSignalModel

    db = SessionLocal()
    try:
        db.query(XAUUSDTelegramSignalModel).filter(XAUUSDTelegramSignalModel.signal_id == "test_sig_74").delete()
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        sig_record = XAUUSDTelegramSignalModel(
            signal_id="test_sig_74",
            canonical_symbol="XAUUSD",
            direction="BUY",
            timeframes_analyzed=["D1", "H4", "M15"],
            entry_price=2650.0,
            stop_loss=2640.0,
            take_profit_1=2670.0,
            take_profit_2=2680.0,
            take_profit_3=2690.0,
            ai_confluence_score=74,
            consensus_summary="Sub-threshold confluence",
            cambodia_date="2026-11-17",
            audit_history=[],
            signal_status="VALIDATED",
            telegram_delivery_status="PENDING",
            idempotency_key="idem_key_74",
            expires_at=now_utc + datetime.timedelta(minutes=30)
        )
        db.add(sig_record)
        db.commit()

        success, msg_id, err = telegram_service.send_xauusd_signal_alert(signal_payload)
        assert success is False
        assert "score" in str(err or "").lower()
    finally:
        db.query(XAUUSDTelegramSignalModel).filter(XAUUSDTelegramSignalModel.signal_id == "test_sig_74").delete()
        db.commit()
        db.close()
