"""
Tests for Phase F: Telegram Daily Quota & Deduplication Governance.
Verifies:
- Daily signal limit (max 4/day Cambodia time).
- Atomic reservation in DB fails closed once limit reached.
- Concurrent workers respect the quota ceiling without race conditions.
- Deduplication prevents duplicate signals.
- Idempotency keys prevent double-counting.
"""
import concurrent.futures
import datetime
import pytest
from taikry.database.session import SessionLocal, init_db
from taikry.database.models import (
    XAUUSDDailyQuotaReservation,
    XAUUSDTelegramSignalModel,
    TelegramSignalDailyQuotaModel,
    TelegramSignalQuotaReservationModel,
)
from taikry.trading.xauusd_signal_engine import (
    XAUUSDSignalEngine,
    get_cambodia_date_str,
    CAMBODIA_TZ,
)
from taikry.saas.signal_quota_service import (
    reserve_signal_alert_slot,
    signal_quota_idempotency_key,
    cambodia_date_str,
)


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_cambodia_date_calculation():
    # Verify UTC+7 conversion
    utc_dt = datetime.datetime(2026, 11, 18, 16, 30, 0, tzinfo=datetime.timezone.utc)
    # 16:30 UTC + 7 hours is 23:30 on Nov 18
    assert get_cambodia_date_str(utc_dt) == "2026-11-18"

    utc_dt2 = datetime.datetime(2026, 11, 18, 17, 30, 0, tzinfo=datetime.timezone.utc)
    # 17:30 UTC + 7 hours is 00:30 on Nov 19
    assert get_cambodia_date_str(utc_dt2) == "2026-11-19"


def test_daily_quota_max_4_enforced():
    engine = XAUUSDSignalEngine()
    test_date = "2099-01-01"
    db = SessionLocal()
    try:
        # Clean test date
        db.query(XAUUSDDailyQuotaReservation).filter_by(cambodia_date=test_date).delete()
        db.commit()

        # Slots 1 through 4 must succeed
        for i in range(4):
            reserved = engine._reserve_daily_quota_slot(db, test_date)
            assert reserved is True, f"Slot {i+1} should have succeeded"

        # Slot 5 must fail (limit is 4)
        reserved_5 = engine._reserve_daily_quota_slot(db, test_date)
        assert reserved_5 is False, "Slot 5 must fail closed when quota reaches 4"
    finally:
        db.query(XAUUSDDailyQuotaReservation).filter_by(cambodia_date=test_date).delete()
        db.commit()
        db.close()


def test_concurrent_quota_reservation_no_overcommit():
    engine = XAUUSDSignalEngine()
    test_date = "2099-01-02"
    db = SessionLocal()
    try:
        db.query(XAUUSDDailyQuotaReservation).filter_by(cambodia_date=test_date).delete()
        db.commit()

        # Already reserve 2 slots, so only 2 remain
        engine._reserve_daily_quota_slot(db, test_date)
        engine._reserve_daily_quota_slot(db, test_date)
        db.commit()
    finally:
        db.close()

    def try_reserve():
        local_db = SessionLocal()
        try:
            res = engine._reserve_daily_quota_slot(local_db, test_date)
            if res:
                local_db.commit()
            return res
        finally:
            local_db.close()

    # Launch 10 concurrent threads fighting for the remaining 2 slots
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(try_reserve) for _ in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    successes = sum(1 for r in results if r is True)
    failures = sum(1 for r in results if r is False)

    assert successes == 2, f"Expected exactly 2 successes, got {successes}"
    assert failures == 8, f"Expected exactly 8 failures, got {failures}"

    # Verify DB final state
    db = SessionLocal()
    try:
        res = db.query(XAUUSDDailyQuotaReservation).filter_by(cambodia_date=test_date).first()
        assert res.reserved_count == 4
        db.query(XAUUSDDailyQuotaReservation).filter_by(cambodia_date=test_date).delete()
        db.commit()
    finally:
        db.close()


def test_saas_signal_quota_idempotency():
    test_date = "2099-01-03"
    user_id = 99999
    idempotency_key = signal_quota_idempotency_key(user_id, test_date, "SIG-TEST-001")
    db = SessionLocal()
    try:
        # Clean test state
        db.query(TelegramSignalQuotaReservationModel).filter_by(user_id=user_id).delete()
        db.query(TelegramSignalDailyQuotaModel).filter_by(user_id=user_id).delete()
        db.commit()

        # 1. First reservation
        success, code = reserve_signal_alert_slot(db, user_id, test_date, daily_limit=4, idempotency_key=idempotency_key)
        assert success is True
        assert code == "RESERVED"

        # 2. Duplicate reservation with SAME idempotency key must not increment count
        success2, code2 = reserve_signal_alert_slot(db, user_id, test_date, daily_limit=4, idempotency_key=idempotency_key)
        assert success2 is True
        assert code2 == "ALREADY_RESERVED"

        # Check reserved count is still 1
        record = db.query(TelegramSignalDailyQuotaModel).filter_by(user_id=user_id, cambodia_date=test_date).first()
        assert record.reserved_count == 1
    finally:
        db.query(TelegramSignalQuotaReservationModel).filter_by(user_id=user_id).delete()
        db.query(TelegramSignalDailyQuotaModel).filter_by(user_id=user_id).delete()
        db.commit()
        db.close()


def test_deduplication_suppresses_duplicate():
    engine = XAUUSDSignalEngine()
    db = SessionLocal()
    try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        sig = XAUUSDTelegramSignalModel(
            signal_id="SIG-TEST-DUP-01",
            canonical_symbol="XAUUSD",
            direction="BUY",
            timeframes_analyzed=["M15"],
            entry_price=2650.00,
            entry_zone_low=2649.25,
            entry_zone_high=2650.75,
            stop_loss=2645.00,
            take_profit_1=2660.00,
            take_profit_2=2670.00,
            take_profit_3=2680.00,
            risk_reward_1=2.0,
            risk_reward_2=4.0,
            risk_reward_3=6.0,
            ai_confluence_score=85,
            broker_source="EXNESS_MT5",
            consensus_summary="Buy signal test summary",
            idempotency_key="idemp_test_dup_001",
            cambodia_date="2026-11-18",
            audit_history=[{"from": None, "to": "GENERATED"}],
            signal_status="SENT",
            telegram_delivery_status="SENT",
            created_at=now_utc.replace(tzinfo=None),
        )
        db.add(sig)
        db.commit()

        # Check duplicate with similar entry (2650.50 vs 2650.00 is <= 1.5 pts)
        is_dup, msg = engine.check_duplicate_signal(direction="BUY", entry_price=2650.50, stop_loss=2645.00)
        assert is_dup is True
        assert "Duplicate" in msg

        # Opposite direction should not be duplicate
        is_dup_sell, _ = engine.check_duplicate_signal(direction="SELL", entry_price=2650.50, stop_loss=2655.00)
        assert is_dup_sell is False
    finally:
        db.query(XAUUSDTelegramSignalModel).filter_by(signal_id="SIG-TEST-DUP-01").delete()
        db.commit()
        db.close()
