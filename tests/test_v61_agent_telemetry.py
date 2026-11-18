"""
Tests for Phase E: AI Agent Telemetry Audit & Integrity.
Verifies:
- Agent status belongs strictly to: IDLE, RUNNING, COMPLETED, FAILED, DISABLED, DEMO_MODE, STANDBY.
- No fake LIVE status or fabricated metrics.
- Required fields per agent: agent_name, status, last_execution_utc, result_summary, error, is_demo, model_provider.
- Disabled agents report status 'DISABLED'.
- Explicitly labeled demo agents report status 'DEMO_MODE'.
- Telemetry endpoint returns valid structure.
"""
import pytest
from taikry.agents.registry import agent_registry, AgentMetadata, AgentAdapter

ALLOWED_STATUSES = {"IDLE", "RUNNING", "COMPLETED", "FAILED", "DISABLED", "DEMO_MODE", "STANDBY"}
REQUIRED_FIELDS = {"agent_name", "status", "last_execution_utc", "result_summary", "error", "is_demo", "model_provider"}


def test_agent_telemetry_snapshot_schema_and_status():
    telemetry = agent_registry.get_telemetry_snapshot()
    assert len(telemetry) > 0

    for record in telemetry:
        # Check required fields
        for field in REQUIRED_FIELDS:
            assert field in record, f"Missing required field '{field}' in telemetry record {record}"

        # Status must be one of the permitted V6.1.1 statuses
        assert record["status"] in ALLOWED_STATUSES, f"Invalid status '{record['status']}' in {record['agent_name']}"
        # Ensure fake LIVE is not used
        assert record["status"] != "LIVE", "Fake 'LIVE' status detected; must use RUNNING, IDLE, etc."


def test_agent_disabled_status():
    adapter = agent_registry.get_adapter("technical_analyst")
    assert adapter is not None
    original_enabled = adapter.metadata.enabled
    try:
        adapter.metadata.enabled = False
        snapshot = agent_registry.get_telemetry_snapshot()
        tech = next(a for a in snapshot if a["agent_id"] == "technical_analyst")
        assert tech["status"] == "DISABLED"
    finally:
        adapter.metadata.enabled = original_enabled


def test_agent_demo_mode_status():
    adapter = agent_registry.get_adapter("ict_smc_analyst")
    assert adapter is not None
    original_demo = getattr(adapter.metadata, "is_demo", False)
    try:
        adapter.metadata.is_demo = True
        snapshot = agent_registry.get_telemetry_snapshot()
        ict = next(a for a in snapshot if a["agent_id"] == "ict_smc_analyst")
        assert ict["status"] == "DEMO_MODE"
        assert ict["is_demo"] is True
    finally:
        adapter.metadata.is_demo = original_demo


def test_agent_completed_and_failed_status():
    adapter = agent_registry.get_adapter("macro_analyst")
    assert adapter is not None
    orig_state = adapter.metadata.execution_state
    orig_health = adapter.metadata.health_status
    try:
        adapter.metadata.execution_state = "COMPLETED"
        adapter.metadata.health_status = "HEALTHY"
        snapshot = agent_registry.get_telemetry_snapshot()
        macro = next(a for a in snapshot if a["agent_id"] == "macro_analyst")
        assert macro["status"] == "COMPLETED"

        adapter.metadata.execution_state = "FAILED"
        snapshot = agent_registry.get_telemetry_snapshot()
        macro = next(a for a in snapshot if a["agent_id"] == "macro_analyst")
        assert macro["status"] == "FAILED"
    finally:
        adapter.metadata.execution_state = orig_state
        adapter.metadata.health_status = orig_health


def test_telemetry_api_endpoint():
    from fastapi.testclient import TestClient
    from taikry.api.app import app
    client = TestClient(app)

    response = client.get("/api/v1/agents/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "telemetry" in data
    assert len(data["telemetry"]) > 0
    for item in data["telemetry"]:
        assert item["status"] in ALLOWED_STATUSES
