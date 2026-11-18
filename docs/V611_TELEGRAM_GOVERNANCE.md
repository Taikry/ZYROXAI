# ZYROX AI V6.1.1 — TELEGRAM SIGNAL GOVERNANCE & QUOTA MANAGEMENT

**Product:** ZYROX AI — Intelligence Beyond The Market  
**Version:** V6.1.1 Production Hardening  
**Target Channel:** Official ZYROX AI VIP Telegram  
**Daily Signal Limit:** Maximum 4 Signals per Calendar Day  
**Business Day Timezone:** Cambodia Time (`Asia/Phnom_Penh`, UTC+7)  
**Status:** IMPLEMENTED & VERIFIED  

---

## 1. Executive Summary

To preserve signal quality and prevent overtrading, ZYROX AI enforces a strict hard cap of **4 institutional signals per Cambodia calendar day**. In high-frequency, multi-worker environments, quota tracking cannot rely on in-memory counters.

Under ZYROX AI V6.1.1:
1. Daily quota is tied strictly to the Phnom Penh calendar date (`Asia/Phnom_Penh`, UTC+7).
2. Quota reservations are managed via atomic SQL conditional updates (`UPDATE ... WHERE reserved_count < daily_limit`), eliminating race conditions.
3. Deduplication suppresses repeat signals for the same directional setup within a 4-hour window.
4. Idempotency keys prevent double-counting across network retries.

---

## 2. Cambodia Business Date Calculation

Phnom Penh operates at UTC+7 without daylight saving shifts. The date boundary rolls over at exactly 00:00 ICT (17:00 UTC previous day):
```python
def get_cambodia_date_str(utc_dt: Optional[datetime.datetime] = None) -> str:
    current = utc_dt or datetime.datetime.now(datetime.timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=datetime.timezone.utc)
    return current.astimezone(CAMBODIA_TZ).strftime("%Y-%m-%d")
```

---

## 3. Atomic Database Quota Reservation

Before an approved signal is dispatched or inserted into the database, an atomic slot reservation is committed:
```python
def _reserve_daily_quota_slot(self, db, date_str: str) -> bool:
    # Inserts initial record if not present, then executes atomic conditional increment
    reserved = db.query(XAUUSDDailyQuotaReservation).filter(
        XAUUSDDailyQuotaReservation.cambodia_date == date_str,
        XAUUSDDailyQuotaReservation.reserved_count < self.daily_limit,
    ).update({
        "reserved_count": XAUUSDDailyQuotaReservation.reserved_count + 1,
        "updated_at": now,
    }, synchronize_session=False)
    return reserved == 1
```

If `reserved == 1`, the slot is secured. If `reserved == 0`, the daily quota has been reached, and signal delivery is blocked with `BLOCKED_DAILY_QUOTA_REACHED`.

---

## 4. Deduplication & Idempotency

1. **4-Hour Time Window Deduplication (`check_duplicate_signal`):**  
   If an active signal exists in the same direction (`BUY`/`SELL`) with an entry level within 2.0 points and SL within 2.5 points, subsequent signals are suppressed.
2. **Deterministic Idempotency Hash:**  
   `idempotency_raw = f"{cambodia_date}_{decision}_{entry:.2f}_{sl:.2f}_{tp1:.2f}"`  
   `idempotency_key = hashlib.sha256(idempotency_raw.encode("utf-8")).hexdigest()`  
   Retrying a webhook or scheduler trigger with an identical key returns `ALREADY_RESERVED` without incrementing the quota counter.

---

## 5. Verification Suite

Tested and verified in `tests/test_v61_telegram_governance.py`:
- `test_cambodia_date_calculation`: Verifies UTC+7 date rollover.
- `test_daily_quota_max_4_enforced`: Proves slots 1-4 succeed, slot 5 fails closed.
- `test_concurrent_quota_reservation_no_overcommit`: 10 parallel threads competing for 2 remaining slots result in **exactly 2 successes and 8 failures**.
- `test_saas_signal_quota_idempotency`: Verifies re-submission with the same idempotency key returns `ALREADY_RESERVED` without counter increment.
- `test_deduplication_suppresses_duplicate`: Verifies duplicate setup within 4 hours is suppressed.
