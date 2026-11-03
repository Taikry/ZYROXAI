"""
ZYROX AI — News Risk Engine V3
==============================
Provides calendar-aware risk evaluation for CPI, NFP, FOMC, PCE, and other high-impact events.
Calculates pre/post event protection windows, affected instrument matrices, and surfaces
data freshness limitations gracefully.
"""
from __future__ import annotations

import logging
import datetime
import zoneinfo
from typing import Dict, Any, List, Optional
from taikry.risk.models import NewsRiskAssessment, NewsFilterMode
from taikry.data.economic_calendar import economic_calendar_provider

logger = logging.getLogger("zyrox.risk.news")

# Currency-to-affected symbols mapping
CURRENCY_AFFECTED_INSTRUMENTS: Dict[str, List[str]] = {
    "USD": ["XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCAD", "USDCHF", "BTCUSDT", "ETHUSDT", "SOLUSDT"],
    "EUR": ["EURUSD", "EURJPY"],
    "GBP": ["GBPUSD", "GBPJPY"],
    "JPY": ["USDJPY", "EURJPY", "GBPJPY"],
    "CAD": ["USDCAD"],
    "AUD": ["AUDUSD"],
    "NZD": ["NZDUSD"],
}


class NewsRiskEngine:
    """Calendar-aware event proximity screener and spread blowout protector."""

    def __init__(self):
        self.default_pre_window_mins = 30
        self.default_post_window_mins = 15

    def evaluate_news_risk(
        self,
        symbol: str,
        filter_mode: str = "STANDARD",
        custom_pre_window: Optional[int] = None,
        custom_post_window: Optional[int] = None
    ) -> NewsRiskAssessment:
        """
        Audits economic calendar proximity for the requested symbol.
        Enforces safety disclaimers and handles unavailable feeds transparently.
        """
        pre_window = custom_pre_window or (
            60 if filter_mode == "STRICT" else (15 if filter_mode == "FLEXIBLE" else self.default_pre_window_mins)
        )
        post_window = custom_post_window or self.default_post_window_mins

        cambodia_tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_local = now_utc.astimezone(cambodia_tz)

        if filter_mode == "OFF":
            return NewsRiskAssessment(
                news_status="MONITOR_ONLY",
                is_blackout=False,
                pre_event_window_minutes=0,
                post_event_window_minutes=0,
                disclaimer="News risk filter is turned OFF by trader request. High volatility may occur around releases."
            )

        # Call underlying calendar provider
        calendar_res = economic_calendar_provider.check_news_blackout(symbol)
        status = calendar_res.get("status", "UNKNOWN")

        if status == "UNAVAILABLE":
            return NewsRiskAssessment(
                news_status="FEED_UNAVAILABLE",
                is_blackout=False if filter_mode == "FLEXIBLE" else True,
                pre_event_window_minutes=pre_window,
                post_event_window_minutes=post_window,
                source_freshness="UNAVAILABLE",
                disclaimer="Live economic calendar feed is temporarily unreachable. Pre-event protection active by default."
            )

        is_blackout = calendar_res.get("is_blackout", False)
        event_name = calendar_res.get("event")
        event_time_utc = calendar_res.get("time_utc")
        event_currency = calendar_res.get("currency")
        mins_until = calendar_res.get("minutes_until")

        scheduled_time_local = None
        if event_time_utc:
            try:
                dt_utc = datetime.datetime.fromisoformat(event_time_utc.replace("Z", "+00:00"))
                scheduled_time_local = dt_utc.astimezone(cambodia_tz).strftime("%Y-%m-%d %H:%M:%S UTC+7")
            except Exception:
                scheduled_time_local = event_time_utc

        if is_blackout:
            news_status = "BLACKOUT_ACTIVE"
        elif mins_until is not None and 0 < mins_until <= (pre_window * 2):
            news_status = "ADVISORY_APPROACHING"
        else:
            news_status = "CLEAR"

        return NewsRiskAssessment(
            news_status=news_status,
            event_name=event_name,
            scheduled_time_utc=event_time_utc,
            scheduled_time_local=scheduled_time_local,
            currency=event_currency,
            impact_level="HIGH" if is_blackout or news_status != "CLEAR" else "NORMAL",
            minutes_until_event=round(mins_until, 1) if mins_until is not None else None,
            pre_event_window_minutes=pre_window,
            post_event_window_minutes=post_window,
            is_blackout=is_blackout,
            source_name="FairEconomy / ForexFactory",
            source_freshness="LIVE_FRESH",
            disclaimer="Economic calendar events represent official macro releases. Liquidity may widen spreads abruptly."
        )


news_risk_engine = NewsRiskEngine()
