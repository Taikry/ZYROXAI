"""
Tests for AI Chat Multi-Agent Fleet Integration
Verifies that POST /api/v1/ai/chat works with all specialized AI agents:
- Technical Analyst
- ICT / SMC Analyst
- Fractal MTF Analyst
- Market Regime Agent
- Quantitative Research Agent
- ML Forecast Model
- Macro & Global News
- Order Flow & CVD
- Concept Recommender
- Risk Guardian
- Critic & Adversary
- Slippage & Execution Simulator
- Data Integrity Agent
- Capital Exposure & Portfolio Guardian
"""
import pytest
from fastapi.testclient import TestClient
from taikry.api.app import app
from taikry.ai.llm_client import chat_with_real_ai, _extract_and_standardize_agents
from taikry.database.session import SessionLocal
from taikry.database.models import User
from taikry.saas.auth_service import sign_up_user, login_user


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_header():
    db = SessionLocal()
    email = "test_chat_agent_user@zyrox.ai"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        sign_up_user(db, email, "Password123!", "Chat Test User")
    ok, _, data = login_user(db, email, "Password123!")
    db.close()
    assert ok
    return {"Authorization": f"Bearer {data['session_token']}"}


def test_ai_chat_multi_agent_fleet_xauusd(client, auth_header):
    """Verifies that chat with XAUUSD incorporates all registered AI agents."""
    resp = client.post(
        "/api/v1/ai/chat",
        headers=auth_header,
        json={
            "query": "Analyze XAUUSD with all AI agents",
            "symbol": "XAUUSD",
            "timeframe": "15m",
            "provider": "auto",
            "history": []
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") in {"SUCCESS", "DEGRADED"}
    assert "agents" in data
    agents = data["agents"]
    assert len(agents) >= 12, f"Expected at least 12 agents, got {len(agents)}"

    # Check that required core agents are present
    agent_ids = {a.get("id") for a in agents}
    required_agents = {
        "technical_analyst",
        "ict_smc_analyst",
        "regime_detection_agent",
        "ml_forecast_agent",
        "macro_analyst",
        "risk_validator"
    }
    for req in required_agents:
        assert req in agent_ids, f"Required agent {req} missing from chat agents"

    # Verify agent properties
    for ag in agents:
        assert ag.get("id")
        assert ag.get("name")
        assert ag.get("bias") in {"BULLISH", "BEARISH", "NEUTRAL"}
        assert isinstance(ag.get("confidence"), (int, float))
        assert ag.get("status")

    # Verify summary
    summary = data.get("agent_run_summary", {})
    assert summary.get("total_agents") == len(agents)
    assert "bullish_count" in summary
    assert "bearish_count" in summary
    assert "neutral_count" in summary

    # Verify bilingual synthesis
    smart = data.get("smart_analysis", {})
    assert smart.get("synthesis_summary_en")
    assert smart.get("synthesis_summary_kh")


def test_ai_chat_multi_agent_khmer_query(client, auth_header):
    """Verifies that natural Khmer queries are correctly processed with agent telemetry."""
    resp = client.post(
        "/api/v1/ai/chat",
        headers=auth_header,
        json={
            "query": "វិភាគមើលទីផ្សារមាស XAUUSD និងប្រាប់ពីទិសដៅ AI ទាំងអស់",
            "symbol": "XAUUSD",
            "timeframe": "15m",
            "provider": "auto",
            "history": []
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "SUCCESS"
    smart = data.get("smart_analysis", {})
    assert len(smart.get("synthesis_summary_kh", "")) > 10
    assert len(data.get("agents", [])) >= 12


def test_ai_chat_deterministic_fallback():
    """Verifies deterministic synthesis fallback when cloud LLMs are unavailable."""
    from taikry.ai.llm_client import _build_multi_agent_deterministic_synthesis

    mock_agents = [
        {"id": "technical_analyst", "name": "Technical Analyst", "icon": "📈", "bias": "BULLISH", "confidence": 75.0, "status": "SUCCESS", "rationale": "EMA structure bullish"},
        {"id": "ict_smc_analyst", "name": "ICT / SMC Analyst", "icon": "🏛️", "bias": "BEARISH", "confidence": 80.0, "status": "SUCCESS", "rationale": "Inside Premium OTE zone"},
        {"id": "regime_detection_agent", "name": "Market Regime", "icon": "🧭", "bias": "BULLISH", "confidence": 65.0, "status": "SUCCESS", "rationale": "Trending Bullish"},
        {"id": "risk_validator", "name": "Risk Guardian", "icon": "🛡️", "bias": "NEUTRAL", "confidence": 90.0, "status": "SUCCESS", "rationale": "Holding for safety"},
    ]

    en_syn, kh_syn = _build_multi_agent_deterministic_synthesis(
        symbol="XAUUSD",
        timeframe="15m",
        price_val=2750.50,
        all_agents=mock_agents,
        live_dir="HOLD",
        live_entry=None,
        live_sl=None,
        live_tp1=None,
        live_tp2=None,
        live_rr="N/A",
        live_conf=None,
        approved_setup=None,
        query="Explain market structure"
    )

    assert "Multi-Agent" in en_syn
    assert "Technical Analyst" in en_syn
    assert "ICT / SMC Analyst" in en_syn
    assert "ក្រុមភ្នាក់ងារ AI" in kh_syn
    assert "ហានិភ័យ" in kh_syn
