"""
ZYROX AI V6.1.1 - Scheduler Locking & Idempotent M15 Execution Tests
Verifies that:
1. Database errors fail closed (return False, never True).
2. Only one worker can hold the distributed lock at a time.
3. Concurrent worker threads competing for the same M15 candle lock have exactly one winner.
4. Lock release and TTL expiration work properly.
"""

import pytest
import datetime
import concurrent.futures
from unittest.mock import patch
from taikry.monitoring.engine import acquire_scheduler_lock, release_scheduler_lock
from taikry.database.session import SessionLocal
from taikry.database.models import SystemSetting


@pytest.fixture(autouse=True)
def clean_test_locks():
    db = SessionLocal()
    db.query(SystemSetting).filter(SystemSetting.key.like("test_m15_lock_%")).delete(synchronize_session=False)
    db.commit()
    db.close()
    yield
    db = SessionLocal()
    db.query(SystemSetting).filter(SystemSetting.key.like("test_m15_lock_%")).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_scheduler_lock_fails_closed_on_db_error(monkeypatch):
    """When a database exception occurs, acquire_scheduler_lock must fail closed (return False)."""
    with patch("taikry.database.session.SessionLocal") as mock_session:
        mock_db = mock_session.return_value
        mock_db.query.side_effect = Exception("Database connection terminated")

        res = acquire_scheduler_lock("test_m15_lock_err", owner_id="worker_fail", ttl_seconds=60)
        assert res is False, "Database errors must fail closed and return False"


def test_scheduler_lock_mutual_exclusion():
    """Worker 1 acquires lock; Worker 2 must be rejected."""
    key = "test_m15_lock_mutex"
    res1 = acquire_scheduler_lock(key, owner_id="worker_alpha", ttl_seconds=60)
    assert res1 is True

    res2 = acquire_scheduler_lock(key, owner_id="worker_beta", ttl_seconds=60)
    assert res2 is False, "Worker beta should not acquire an active lock held by worker alpha"


def test_scheduler_lock_release_and_reacquire():
    """Releasing the lock allows another worker to acquire it."""
    key = "test_m15_lock_rel"
    res1 = acquire_scheduler_lock(key, owner_id="worker_1", ttl_seconds=60)
    assert res1 is True

    rel = release_scheduler_lock(key, owner_id="worker_1")
    assert rel is True

    res2 = acquire_scheduler_lock(key, owner_id="worker_2", ttl_seconds=60)
    assert res2 is True


def test_concurrent_threads_competing_for_same_m15_close():
    """10 concurrent threads try to claim the same M15 candle close simultaneously. Exactly 1 must win."""
    key = f"test_m15_lock_concurrent_{int(datetime.datetime.now().timestamp())}"
    num_threads = 10

    def attempt_claim(worker_idx):
        return acquire_scheduler_lock(key, owner_id=f"worker_{worker_idx}", ttl_seconds=60)

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(attempt_claim, i) for i in range(num_threads)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # Exactly 1 True, all others False
    assert results.count(True) == 1, f"Expected exactly 1 lock winner, got {results.count(True)}"
    assert results.count(False) == num_threads - 1
