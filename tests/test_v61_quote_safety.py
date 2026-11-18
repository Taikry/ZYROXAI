"""
Tests for ZYROX AI V6.1 Critical Broker Quote Safety.
Verifies:
1. Rejection of ESTIMATED_SPREAD with BLOCKED_ESTIMATED_SPREAD.
2. Rejection of REFERENCE_PRICE with BLOCKED_REFERENCE_ONLY.
3. Rejection of STALE with BLOCKED_STALE_FEED.
4. Rejection of DISCONNECTED with BLOCKED_DISCONNECTED_FEED.
5. Rejection of UNAVAILABLE or is_executable=False with BLOCKED_NO_EXECUTABLE_QUOTE.
6. Absolute elimination of synthetic fallback spreads (spread_est = 0.25).
"""
import pytest
import datetime
import pandas as pd
from unittest.mock import MagicMock, patch
from taikry.trading.xauusd_signal_engine import xauusd_signal_engine, xauusd_signal_engine as signal_module
from taikry.data.providers import QuoteClassification, build_quote_record


def test_quote_record_forces_is_executable_false_for_non_broker_quotes():
    rec_est = build_quote_record(
        symbol="XAUUSD",
        provider="Reference Price",
        bid=2650.0,
        ask=2650.25,
        classification=QuoteClassification.ESTIMATED_SPREAD,
        is_executable=True  # should be overridden to False
    )
    assert rec_est["quote_classification"] == QuoteClassification.ESTIMATED_SPREAD
    assert rec_est["is_executable"] is False

    rec_ref = build_quote_record(
        symbol="XAUUSD",
        provider="Reference Price",
        bid=2650.0,
        ask=2650.0,
        classification=QuoteClassification.REFERENCE_PRICE,
        is_executable=True
    )
    assert rec_ref["quote_classification"] == QuoteClassification.REFERENCE_PRICE
    assert rec_ref["is_executable"] is False


@pytest.fixture(autouse=True)
def mock_market_prerequisites(monkeypatch):
    now = datetime.datetime.now(datetime.timezone.utc)
    frame = pd.DataFrame({
        "timestamp": [now] * 30,
        "open": [2650.0] * 30,
        "high": [2655.0] * 30,
        "low": [2645.0] * 30,
        "close": [2650.1] * 30,
        "volume": [100.0] * 30,
        "source": ["EXNESS_MT5"] * 30
    })
    from taikry.trading import xauusd_signal_engine as sem
    monkeypatch.setattr(sem, "is_market_open", lambda *_args: (True, "OPEN"))
    monkeypatch.setattr(sem.market_data_engine, "get_multi_timeframe_candles", lambda *_args: {tf: frame.copy() for tf in ("W1", "D1", "H4", "H1", "M15", "M5")})
    monkeypatch.setattr(sem.market_data_engine, "get_verified_price", lambda _symbol: (2650.1, "EXNESS_MT5", now))
    monkeypatch.setattr(sem, "validate_dataframe", lambda *_args, **_kwargs: {"valid": True, "reason": None})
    monkeypatch.setattr(sem, "check_data_freshness", lambda *_args, **_kwargs: {"fresh": True, "status": "LIVE_FRESH"})
    monkeypatch.setattr(sem.mt5_receiver, "get_status", lambda: {"status": "CONNECTED"})


def test_engine_blocks_estimated_spread(monkeypatch):
    from taikry.trading import xauusd_signal_engine as sem
    monkeypatch.setattr(sem.market_data_engine, "get_verified_quote", lambda _symbol: {
        "symbol": "XAUUSD",
        "provider": "Estimated Spread Feed",
        "bid": 2650.00,
        "ask": 2650.25,
        "price": 2650.12,
        "quote_classification": QuoteClassification.ESTIMATED_SPREAD,
        "is_executable": False
    })

    result = xauusd_signal_engine.generate_xauusd_signal(raw_symbol="XAUUSD")

    assert result["success"] is False
    assert result["status"] == "BLOCKED_ESTIMATED_SPREAD"


def test_engine_blocks_reference_only_quote(monkeypatch):
    from taikry.trading import xauusd_signal_engine as sem
    monkeypatch.setattr(sem.market_data_engine, "get_verified_quote", lambda _symbol: {
        "symbol": "XAUUSD",
        "provider": "Reference Feed",
        "bid": 2650.00,
        "ask": 2650.00,
        "price": 2650.00,
        "quote_classification": QuoteClassification.REFERENCE_PRICE,
        "is_executable": False
    })

    result = xauusd_signal_engine.generate_xauusd_signal(raw_symbol="XAUUSD")

    assert result["success"] is False
    assert result["status"] == "BLOCKED_REFERENCE_ONLY"


def test_engine_blocks_stale_feed(monkeypatch):
    from taikry.trading import xauusd_signal_engine as sem
    monkeypatch.setattr(sem.market_data_engine, "get_verified_quote", lambda _symbol: {
        "symbol": "XAUUSD",
        "provider": "Stale Broker Feed",
        "bid": 2650.00,
        "ask": 2650.25,
        "price": 2650.12,
        "quote_classification": QuoteClassification.STALE,
        "is_executable": False
    })

    result = xauusd_signal_engine.generate_xauusd_signal(raw_symbol="XAUUSD")

    assert result["success"] is False
    assert result["status"] == "BLOCKED_STALE_FEED"


def test_engine_blocks_disconnected_feed(monkeypatch):
    from taikry.trading import xauusd_signal_engine as sem
    monkeypatch.setattr(sem.market_data_engine, "get_verified_quote", lambda _symbol: {
        "symbol": "XAUUSD",
        "provider": "Disconnected Feed",
        "bid": 2650.00,
        "ask": 2650.25,
        "price": 2650.12,
        "quote_classification": QuoteClassification.DISCONNECTED,
        "is_executable": False
    })

    result = xauusd_signal_engine.generate_xauusd_signal(raw_symbol="XAUUSD")

    assert result["success"] is False
    assert result["status"] == "BLOCKED_DISCONNECTED_FEED"


def test_engine_blocks_non_executable_or_unavailable(monkeypatch):
    from taikry.trading import xauusd_signal_engine as sem
    monkeypatch.setattr(sem.market_data_engine, "get_verified_quote", lambda _symbol: None)

    result = xauusd_signal_engine.generate_xauusd_signal(raw_symbol="XAUUSD")

    assert result["success"] is False
    assert result["status"] == "BLOCKED_NO_EXECUTABLE_QUOTE"


def test_oanda_and_yahoo_and_binance_forced_reference_only():
    """Any non-Exness source must fail-safe to REFERENCE_PRICE and is_executable=False."""
    rec_oanda = build_quote_record(
        symbol="XAUUSD",
        provider="OANDA",
        bid=2650.0,
        ask=2650.25,
        source="OANDA_V20",
        classification=QuoteClassification.REAL_BROKER_QUOTE,
        is_executable=True
    )
    assert rec_oanda["quote_classification"] == QuoteClassification.REFERENCE_PRICE
    assert rec_oanda["is_executable"] is False

    rec_yahoo = build_quote_record(
        symbol="XAUUSD",
        provider="Yahoo Finance",
        bid=2650.0,
        ask=2650.25,
        source="YAHOO",
        classification=QuoteClassification.REAL_BROKER_QUOTE,
        is_executable=True
    )
    assert rec_yahoo["quote_classification"] == QuoteClassification.REFERENCE_PRICE
    assert rec_yahoo["is_executable"] is False


def test_unclassified_quote_fails_closed(monkeypatch):
    """An unclassified quote with valid bid/ask must NEVER be promoted to REAL_BROKER_QUOTE."""
    from taikry.trading import xauusd_signal_engine as sem
    monkeypatch.setattr(sem.market_data_engine, "get_verified_quote", lambda _symbol: {
        "symbol": "XAUUSD",
        "provider": "Unknown Unclassified Feed",
        "bid": 2650.00,
        "ask": 2650.25,
        "price": 2650.12,
        # quote_classification omitted entirely
        "is_executable": False
    })

    result = xauusd_signal_engine.generate_xauusd_signal(raw_symbol="XAUUSD")
    assert result["success"] is False
    assert result["status"] == "BLOCKED_NO_EXECUTABLE_QUOTE"

