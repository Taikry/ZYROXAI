"""
Tests for Conversational / General Chat and Intent Classification in ZYROX AI.
Ensures greetings, identity inquiries, general question inquiries ('ចុះបើសួរទូទៅ'),
and educational concepts (SMC, FVG) return conversational responses without forcing
a trading signal card (HOLD XAUUSD, entry/sl/tp, 14-agent consensus list).
"""
import pytest
from taikry.ai.llm_client import classify_chat_intent, chat_with_real_ai


def test_intent_classification_greetings():
    greetings = ["HELLO", "hello", "Hi", "hey there", "សួស្តី", "ជំរាបសួរ", "សុខសប្បាយជាទេ?"]
    for g in greetings:
        intent, cat = classify_chat_intent(g)
        assert intent == "CONVERSATIONAL", f"Expected CONVERSATIONAL for '{g}', got {intent}"
        assert cat == "GREETING", f"Expected GREETING for '{g}', got {cat}"


def test_intent_classification_general_inquiries():
    inquiries = [
        "ចុះបើសួរទូទៅ",
        "ចុះប់ើសួរទូទៅ",
        "តើសួរទូទៅបានទេ?",
        "Can I ask general questions?",
        "general question",
    ]
    for q in inquiries:
        intent, cat = classify_chat_intent(q)
        assert intent == "CONVERSATIONAL", f"Expected CONVERSATIONAL for '{q}', got {intent}"
        assert cat == "GENERAL_INQUIRY", f"Expected GENERAL_INQUIRY for '{q}', got {cat}"


def test_intent_classification_identity_and_help():
    identity_queries = [
        "who are you",
        "what can you do",
        "help",
        "តើអ្នកជានរណា",
        "តើអ្នកអាចធ្វើអ្វីបានខ្លះ?",
    ]
    for q in identity_queries:
        intent, cat = classify_chat_intent(q)
        assert intent == "CONVERSATIONAL", f"Expected CONVERSATIONAL for '{q}', got {intent}"
        assert cat == "IDENTITY_HELP", f"Expected IDENTITY_HELP for '{q}', got {cat}"


def test_intent_classification_educational_concepts():
    concepts = [
        "what is FVG?",
        "what is SMC?",
        "what is order block?",
        "what is risk management?",
        "តើ FVG ជាអ្វី?",
    ]
    for c in concepts:
        intent, cat = classify_chat_intent(c)
        assert intent == "CONVERSATIONAL", f"Expected CONVERSATIONAL for '{c}', got {intent}"
        assert cat == "CONCEPT_EDUCATION", f"Expected CONCEPT_EDUCATION for '{c}', got {cat}"


def test_intent_classification_market_analysis():
    market_queries = [
        "Analyze XAUUSD market structure",
        "Review consensus of all 14 AI agents for XAUUSD",
        "Institutional ICT / SMC zones, FVG, liquidity sweeps and order blocks",
        "Best institutional setups now",
        "Macro news & FOMC impact",
        "Risk check against configured server limits",
        "Pre-news deep research report for XAUUSD",
        "វិភាគមើលក្រាហ្វិកនេះ និងរក Entry, SL, TP",
        "Should I buy or sell gold?",
        "What is the trend for XAUUSD?",
        "BTCUSDT analysis",
    ]
    for m in market_queries:
        intent, _ = classify_chat_intent(m)
        assert intent == "MARKET_ANALYSIS", f"Expected MARKET_ANALYSIS for '{m}', got {intent}"


def test_chat_with_real_ai_hello():
    res = chat_with_real_ai("HELLO", symbol="XAUUSD", timeframe="15m")
    assert res.get("status") == "SUCCESS"
    assert res.get("is_conversational") is True
    assert res.get("query_type") == "CONVERSATIONAL"
    assert res.get("conversational_category") == "GREETING"
    assert res.get("trade_execution", {}).get("action") == "NONE"
    assert len(res.get("agents", [])) == 0
    assert "synthesis_summary_kh" in res.get("smart_analysis", {})
    assert "synthesis_summary_en" in res.get("smart_analysis", {})
    assert len(res.get("suggested_chips", [])) > 0


def test_chat_with_real_ai_general_inquiry():
    res = chat_with_real_ai("ចុះប់ើសួរទូទៅ", symbol="XAUUSD", timeframe="15m")
    assert res.get("status") == "SUCCESS"
    assert res.get("is_conversational") is True
    assert res.get("query_type") == "CONVERSATIONAL"
    assert res.get("conversational_category") == "GENERAL_INQUIRY"
    assert res.get("trade_execution", {}).get("action") == "NONE"
    assert len(res.get("agents", [])) == 0
    assert "synthesis_summary_kh" in res.get("smart_analysis", {})
    assert "synthesis_summary_en" in res.get("smart_analysis", {})
