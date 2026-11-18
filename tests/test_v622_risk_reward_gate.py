"""
ZYROX AI V6.2.2 — MINIMUM RISK/REWARD APPROVAL GATE TEST SUITE
==============================================================
Verifies the mandatory Risk/Reward confirmation gate across:
1. RR == 1.1 passes the gate.
2. RR > 1.1 passes the gate.
3. RR < 1.1 fails with exact message: "Signal rejected: Risk/Reward ratio is below the minimum required 1:1.1."
4. BUY calculation is correct (geometry, distances, ratios).
5. SELL calculation is correct (geometry, distances, ratios).
6. Zero risk distance is rejected (INVALID).
7. Invalid SL/TP direction is rejected (INVALID).
8. Missing quote is rejected (WAIT).
9. Stale quote is rejected (WAIT).
10. Telegram cannot bypass approval (rejects RR < 1.1 or invalid status).
11. AI agents cannot bypass approval (engine blocks unapproved RR).
12. Frontend cannot override backend validation (admin config persistence & validation).
13. TP1 is the conservative approval target (never hides behind TP3).
14. Execution cost disclosure (net vs gross estimated).
"""

import math
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from taikry.api.app import app
from taikry.trading.risk_reward_gate import (
    validate_signal_risk_reward,
    get_system_min_rr,
    set_system_min_rr,
    STATUS_APPROVED,
    STATUS_REJECTED,
    STATUS_INVALID,
    STATUS_WAIT,
)
from taikry.trading.xauusd_signal_engine import xauusd_signal_engine, calculate_trade_levels
from taikry.notifications.telegram_service import telegram_service
from taikry.database.session import SessionLocal
from taikry.database.models import SystemSetting, AuditLog, XAUUSDTelegramSignalModel

client = TestClient(app)


# -----------------------------------------------------------------------------
# 1. CORE RR RATIO EVALUATION TESTS
# -----------------------------------------------------------------------------

def test_rr_exactly_1_1_passes_gate():
    """RR exactly 1.1 (Risk 10.0, Reward 11.0) must pass the gate as APPROVED."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=4000.0,
        stop_loss=3990.0,
        take_profit_1=4011.0,
        min_rr_threshold=1.1,
    )
    assert res.status == STATUS_APPROVED
    assert res.is_approved is True
    assert res.risk_distance == pytest.approx(10.0)
    assert res.reward_distance_1 == pytest.approx(11.0)
    assert res.rr_tp1 == pytest.approx(1.1)
    assert res.difference == pytest.approx(0.0)
    assert res.rejection_reason is None


def test_rr_greater_than_1_1_passes_gate():
    """RR greater than 1.1 (e.g. 1:1.5, 1:2.0) must pass the gate as APPROVED."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2700.0,
        stop_loss=2690.0,
        take_profit_1=2715.0,  # Risk = 10, Reward = 15 -> RR = 1.5
        take_profit_2=2725.0,
        take_profit_3=2740.0,
        min_rr_threshold=1.1,
    )
    assert res.status == STATUS_APPROVED
    assert res.is_approved is True
    assert res.rr_tp1 == pytest.approx(1.5)
    assert res.rr_tp2 == pytest.approx(2.5)
    assert res.rr_tp3 == pytest.approx(4.0)
    assert res.difference == pytest.approx(0.4)


def test_rr_below_1_1_fails_with_exact_message():
    """RR below 1.1 must fail with status REJECTED and exact required message."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=4000.0,
        stop_loss=3990.0,
        take_profit_1=4010.0,  # Risk = 10, Reward = 10 -> RR = 1.0 < 1.1
        min_rr_threshold=1.1,
    )
    assert res.status == STATUS_REJECTED
    assert res.is_approved is False
    assert res.rr_tp1 == pytest.approx(1.0)
    assert res.min_required_rr == pytest.approx(1.1)
    assert res.difference == pytest.approx(-0.1)
    # Exact required rejection explanation string:
    assert res.rejection_reason == "Signal rejected: Risk/Reward ratio is below the minimum required 1:1.1."
    assert "below the minimum required 1:1.1" in res.explanation


# -----------------------------------------------------------------------------
# 2. DIRECTIONAL CALCULATION & GEOMETRIC CHECKS
# -----------------------------------------------------------------------------

def test_buy_calculation_is_correct():
    """For BUY: Stop Loss must be below Entry; Take Profit must be above Entry."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2650.0,
        stop_loss=2640.0,
        take_profit_1=2663.20,  # Risk = 10.0, Reward = 13.20 -> RR = 1.32
    )
    assert res.direction == "BUY"
    assert res.risk_distance == pytest.approx(10.0)
    assert res.reward_distance_1 == pytest.approx(13.20)
    assert res.rr_tp1 == pytest.approx(1.32)
    assert res.status == STATUS_APPROVED


def test_sell_calculation_is_correct():
    """For SELL: Stop Loss must be above Entry; Take Profit must be below Entry."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="SELL",
        entry=2650.0,
        stop_loss=2660.0,
        take_profit_1=2636.80,  # Risk = 10.0, Reward = 13.20 -> RR = 1.32
    )
    assert res.direction == "SELL"
    assert res.risk_distance == pytest.approx(10.0)
    assert res.reward_distance_1 == pytest.approx(13.20)
    assert res.rr_tp1 == pytest.approx(1.32)
    assert res.status == STATUS_APPROVED


def test_zero_risk_distance_is_rejected():
    """Zero risk distance (Entry == Stop Loss) must be rejected with status INVALID."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2650.0,
        stop_loss=2650.0,
        take_profit_1=2665.0,
    )
    assert res.status == STATUS_INVALID
    assert res.is_approved is False
    assert "Invalid BUY geometry" in res.rejection_reason or "zero" in res.rejection_reason.lower()


def test_invalid_sl_tp_direction_is_rejected():
    """Invalid direction geometry must be rejected as INVALID."""
    # BUY with SL above Entry
    buy_bad_sl = validate_signal_risk_reward(
        symbol="XAUUSD", direction="BUY", entry=2650.0, stop_loss=2655.0, take_profit_1=2670.0
    )
    assert buy_bad_sl.status == STATUS_INVALID
    assert "Stop Loss" in buy_bad_sl.rejection_reason

    # BUY with TP below Entry
    buy_bad_tp = validate_signal_risk_reward(
        symbol="XAUUSD", direction="BUY", entry=2650.0, stop_loss=2640.0, take_profit_1=2645.0
    )
    assert buy_bad_tp.status == STATUS_INVALID
    assert "Take Profit" in buy_bad_tp.rejection_reason

    # SELL with SL below Entry
    sell_bad_sl = validate_signal_risk_reward(
        symbol="XAUUSD", direction="SELL", entry=2650.0, stop_loss=2645.0, take_profit_1=2635.0
    )
    assert sell_bad_sl.status == STATUS_INVALID
    assert "Stop Loss" in sell_bad_sl.rejection_reason

    # SELL with TP above Entry
    sell_bad_tp = validate_signal_risk_reward(
        symbol="XAUUSD", direction="SELL", entry=2650.0, stop_loss=2660.0, take_profit_1=2665.0
    )
    assert sell_bad_tp.status == STATUS_INVALID
    assert "Take Profit" in sell_bad_tp.rejection_reason


# -----------------------------------------------------------------------------
# 3. QUOTE FRESHNESS & SCORE PREREQUISITE GATES
# -----------------------------------------------------------------------------

def test_missing_quote_is_rejected():
    """Unverified or missing broker quote must place setup in WAIT status."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2700.0,
        stop_loss=2690.0,
        take_profit_1=2720.0,
        quote_verified=False,
    )
    assert res.status == STATUS_WAIT
    assert res.is_approved is False
    assert "quote is missing" in res.rejection_reason.lower()


def test_stale_quote_is_rejected():
    """Stale market quote must place setup in WAIT status."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2700.0,
        stop_loss=2690.0,
        take_profit_1=2720.0,
        quote_fresh=False,
    )
    assert res.status == STATUS_WAIT
    assert res.is_approved is False


def test_confluence_score_below_75_is_rejected():
    """Confluence score < 75 must place setup in WAIT status."""
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2700.0,
        stop_loss=2690.0,
        take_profit_1=2720.0,
        confluence_score=70,  # Below 75
    )
    assert res.status == STATUS_WAIT
    assert res.is_approved is False
    assert "70/100" in res.rejection_reason


# -----------------------------------------------------------------------------
# 4. TP1 CONSERVATIVE GATE (NEVER HIDE BEHIND TP3)
# -----------------------------------------------------------------------------

def test_tp1_is_default_conservative_gate_never_hidden_by_tp3():
    """
    Even if TP2 and TP3 have huge reward ratios (e.g. 1:3.0, 1:5.0),
    if TP1 has RR < 1.1, the signal MUST be REJECTED!
    """
    res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2700.0,
        stop_loss=2690.0,        # Risk = 10.0
        take_profit_1=2709.0,    # Reward 1 = 9.0 -> RR1 = 0.90 (< 1.1)
        take_profit_2=2730.0,    # Reward 2 = 30.0 -> RR2 = 3.00
        take_profit_3=2750.0,    # Reward 3 = 50.0 -> RR3 = 5.00
        min_rr_threshold=1.1,
    )
    assert res.status == STATUS_REJECTED
    assert res.is_approved is False
    assert res.rr_tp1 == 0.90
    assert res.rr_tp2 == 3.00
    assert res.rr_tp3 == 5.00
    assert "Risk/Reward ratio is below the minimum required 1:1.1" in res.rejection_reason


# -----------------------------------------------------------------------------
# 5. EXECUTION COST & GROSS VS NET DISCLOSURE
# -----------------------------------------------------------------------------

def test_execution_cost_validation_gross_vs_net():
    """
    When bid, ask and spread are provided, net RR is calculated and cost_basis is NET.
    When execution cost data is missing, cost_basis discloses GROSS_ESTIMATED.
    """
    # With complete execution costs:
    net_res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2700.25,
        stop_loss=2690.0,
        take_profit_1=2715.0,
        bid=2700.0,
        ask=2700.25,
        spread=0.25,
        commission_per_lot=7.0,
        lot_size=100.0,
    )
    assert net_res.cost_basis == "NET"
    assert net_res.is_net is True
    assert net_res.commission_per_unit == pytest.approx(0.07)
    assert net_res.estimated_total_costs == pytest.approx(0.32)
    assert net_res.net_rr_tp1 is not None

    # Without execution costs:
    gross_res = validate_signal_risk_reward(
        symbol="XAUUSD",
        direction="BUY",
        entry=2700.0,
        stop_loss=2690.0,
        take_profit_1=2715.0,
        bid=None,
        ask=None,
        spread=None,
    )
    assert gross_res.cost_basis == "GROSS_ESTIMATED"
    assert gross_res.is_net is False
    assert gross_res.net_rr_tp1 is None


# -----------------------------------------------------------------------------
# 6. TELEGRAM BYPASS PREVENTION
# -----------------------------------------------------------------------------

def test_telegram_cannot_bypass_rr_approval():
    """Telegram alert dispatcher MUST fail closed if RR < 1.1 or signal is unapproved."""
    # 1. Reject signal with insufficient RR
    bad_rr_signal = {
        "success": True,
        "status": "VALIDATED",
        "signal_id": f"TEST-SIG-BAD-RR-{uuid.uuid4().hex[:6]}",
        "canonical_symbol": "XAUUSD",
        "direction": "BUY",
        "entry_price": 2700.0,
        "stop_loss": 2690.0,
        "take_profit_1": 2709.0,  # RR = 0.90 < 1.1
        "take_profit_2": 2720.0,
        "take_profit_3": 2730.0,
        "ai_score": 88,
        "idempotency_key": "dummy_key",
    }
    sent, msg_id, err = telegram_service.send_xauusd_signal_alert(bad_rr_signal)
    assert sent is False
    assert "below the minimum required" in err or "below the required" in err or "XAUUSD signal is not persisted" in err

    # 2. Persisted signal with RR < 1.1 must be rejected by Telegram dispatcher
    db = SessionLocal()
    sig_id = f"SIG-TEST-RR-FAIL-{uuid.uuid4().hex[:6]}"
    try:
        model = XAUUSDTelegramSignalModel(
            signal_id=sig_id,
            canonical_symbol="XAUUSD",
            direction="BUY",
            timeframes_analyzed=["M15", "H1"],
            entry_price=2700.0,
            stop_loss=2690.0,
            take_profit_1=2709.0,  # RR = 0.90 < 1.1
            take_profit_2=2720.0,
            take_profit_3=2730.0,
            risk_reward_1=0.90,
            risk_reward_2=2.00,
            risk_reward_3=3.00,
            ai_confluence_score=85,
            consensus_summary="Quorum test",
            signal_status="VALIDATED",
            telegram_delivery_status="PENDING",
            idempotency_key=f"idemp_{sig_id}",
            cambodia_date="2026-11-18",
            audit_history=[],
        )
        db.add(model)
        db.commit()

        persisted_bad_signal = {
            "success": True,
            "status": "VALIDATED",
            "signal_id": sig_id,
            "canonical_symbol": "XAUUSD",
            "direction": "BUY",
            "entry_price": 2700.0,
            "stop_loss": 2690.0,
            "take_profit_1": 2709.0,
            "take_profit_2": 2720.0,
            "take_profit_3": 2730.0,
            "ai_score": 85,
            "idempotency_key": f"idemp_{sig_id}",
        }
        sent, msg_id, err = telegram_service.send_xauusd_signal_alert(persisted_bad_signal)
        assert sent is False
        assert "below the minimum required 1:1.1" in err or "reward/risk is below" in err
    finally:
        db.query(XAUUSDTelegramSignalModel).filter(XAUUSDTelegramSignalModel.signal_id == sig_id).delete()
        db.commit()
        db.close()


# -----------------------------------------------------------------------------
# 7. AI AGENTS CANNOT BYPASS RR APPROVAL
# -----------------------------------------------------------------------------

def test_ai_agents_cannot_bypass_rr_approval():
    """Even with unanimous 100% agent quorum, RR < 1.1 must return WAIT."""
    from taikry.trading.xauusd_signal_engine import SIGNAL_VOTER_IDS
    from types import SimpleNamespace

    agent_outputs = {}
    for aid in SIGNAL_VOTER_IDS:
        agent_outputs[aid] = {
            "agent_id": aid,
            "name": aid,
            "bias": "BULLISH",
            "confidence": 95,
            "status": "SUCCESS",
            "contributes_to_consensus": True,
            "evidence": ["Unanimous bullish flow"],
        }
    # Technical analyst gives levels that produce RR < 1.1
    agent_outputs["technical_analyst"]["key_levels"] = {
        "atr": 5.0,
        "swing_low": 2695.0,
        "take_profit_1": 2702.0,  # Entry 2700, SL ~2694.25 (risk 5.75), TP1 2702 (reward 2) -> RR < 1.1
    }

    # Force candidate reviews to approve
    candidate_review = {
        "risk_validator": {"decision": "APPROVE", "reasons": []},
        "counter_analysis_agent": {"critique_stance": "CHALLENGE_CLEARED", "fragility_score": 10},
        "portfolio_analysis_agent": {"is_approved": True},
        "execution_simulation_agent": {"is_execution_viable": True, "net_risk_reward": 0.5},
    }
    adapters = {
        k: SimpleNamespace(execute=lambda _r=v, **kwargs: dict(_r))
        for k, v in candidate_review.items()
    }

    with patch("taikry.agents.registry.agent_registry.get_adapter", side_effect=lambda a: adapters.get(a)):
        with patch.object(xauusd_signal_engine, "_load_agent_weights", return_value={}):
            with patch("taikry.trading.xauusd_signal_engine.calculate_confluence_scores", return_value=SimpleNamespace(selected_score=90, to_dict=lambda: {"score": 90})):
                # If calculate_trade_levels yields RR < 1.1, consensus must be WAIT
                with patch("taikry.trading.xauusd_signal_engine.calculate_trade_levels", return_value={
                    "stop_loss": 2690.0,
                    "take_profit_1": 2705.0,  # Risk = 10, Reward = 5 -> RR = 0.5 < 1.1
                    "take_profit_2": 2720.0,
                    "take_profit_3": 2740.0,
                    "risk_distance": 10.0,
                    "risk_reward_1": 0.5,
                    "risk_reward_2": 2.0,
                    "risk_reward_3": 4.0,
                }):
                    consensus = xauusd_signal_engine.synthesize_consensus("XAUUSD", 2700.0, agent_outputs, {})
                    assert consensus["decision"] == "WAIT"
                    assert "below the minimum required 1:1.1" in consensus["rejection_reason"]


# -----------------------------------------------------------------------------
# 8. ADMIN SETTINGS PERSISTENCE & AUDIT LOGGING
# -----------------------------------------------------------------------------

def test_admin_settings_persistence_and_audit_logging():
    """
    Admin endpoint /api/v1/xauusd/signals/admin/config must:
    1. Validate positive numeric values (>= 1.0).
    2. Reject negative, zero, or non-numeric values.
    3. Persist to SystemSetting table.
    4. Record an AuditLog entry.
    5. Be readable via GET /api/v1/xauusd/signals/admin/config.
    """
    # 1. Update min_rr to 1.2
    resp = client.post("/api/v1/xauusd/signals/admin/config", json={"min_rr": 1.2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["current_config"]["min_rr"] == 1.2

    # Verify persisted in database
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter(SystemSetting.key == "min_risk_reward_ratio").first()
        assert setting is not None
        assert float(setting.value) == 1.2

        audit = db.query(AuditLog).filter(
            AuditLog.action == "UPDATE_MIN_RISK_REWARD_RATIO"
        ).order_by(AuditLog.id.desc()).first()
        assert audit is not None
        assert audit.target_id == "min_risk_reward_ratio"
        assert audit.details["new_value"] == "1.2"
    finally:
        db.close()

    # 2. Verify GET endpoint
    get_resp = client.get("/api/v1/xauusd/signals/admin/config")
    assert get_resp.status_code == 200
    assert get_resp.json()["current_config"]["min_rr"] == 1.2

    # 3. Reject invalid values (< 1.0, 0, negative)
    bad_resp = client.post("/api/v1/xauusd/signals/admin/config", json={"min_rr": 0.5})
    assert bad_resp.status_code == 400
    assert "between 1.0 and 20.0" in bad_resp.json()["detail"]

    bad_resp2 = client.post("/api/v1/xauusd/signals/admin/config", json={"min_rr": -1.0})
    assert bad_resp2.status_code == 400

    # Reset back to default 1.1
    reset_resp = client.post("/api/v1/xauusd/signals/admin/config", json={"min_rr": 1.1})
    assert reset_resp.status_code == 200
    assert reset_resp.json()["current_config"]["min_rr"] == 1.1
    assert get_system_min_rr() == 1.1
