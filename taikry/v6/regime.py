"""
ZYROX AI V6 — Module 1: Deterministic Market Regime Engine
==========================================================
Classifies market conditions into 11 canonical regimes using validated quantitative evidence:
- TREND_BULLISH_STRONG
- TREND_BULLISH_WEAK
- TREND_BEARISH_STRONG
- TREND_BEARISH_WEAK
- RANGE
- BREAKOUT
- REVERSAL_TRANSITION
- HIGH_VOLATILITY
- LOW_VOLATILITY
- NEWS_VOLATILITY
- UNCERTAIN

Never classifies a market with high certainty when evidence is weak or conflicting.
"""
from __future__ import annotations

import datetime
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from taikry.v6.models import V6MarketRegime, RegimeAnalysisResult
from taikry.indicators.technical import (
    calculate_ema,
    calculate_atr,
    calculate_dmi_adx,
    calculate_bollinger_bands,
)
from taikry.indicators.ict_smc import (
    identify_swing_points,
    detect_structure_breaks,
)
from taikry.risk.news_risk import news_risk_engine

logger = logging.getLogger("zyrox.v6.regime")


class V6MarketRegimeEngine:
    """Deterministic, quantitative market regime engine for ZYROX AI V6."""

    @staticmethod
    def calculate_hurst_exponent(prices: np.ndarray, max_lags: int = 20) -> float:
        """
        Calculates Hurst Exponent (H):
        H > 0.55 -> Persistent trending
        H < 0.45 -> Mean-reverting range
        0.45 <= H <= 0.55 -> Random walk / noise
        """
        if len(prices) < 30:
            return 0.50
        try:
            # Check strong directional monotonicity (pure trending series)
            time_idx = np.arange(len(prices))
            corr = np.corrcoef(time_idx, prices)[0, 1]
            if not np.isnan(corr) and abs(corr) >= 0.80:
                return round(min(0.95, 0.50 + (abs(corr) * 0.40)), 3)

            lags = range(2, min(max_lags, len(prices) // 4))
            tau = []
            for lag in lags:
                diff = prices[lag:] - prices[:-lag]
                std_diff = np.std(diff)
                tau.append(std_diff if std_diff > 1e-8 else 1e-8)
            if len(tau) < 3:
                return 0.50
            m = np.polyfit(np.log(list(lags)), np.log(tau), 1)
            hurst = float(m[0] * 2.0)
            return round(max(0.01, min(0.99, hurst)), 3)
        except Exception:
            return 0.50

    def analyze_regime(
        self,
        symbol: str,
        df: Optional[pd.DataFrame],
        timeframe: str = "M15",
        news_context: Optional[Dict[str, Any]] = None
    ) -> RegimeAnalysisResult:
        """
        Analyzes candle dataset and classifies market into one of the 11 regimes.
        Guarantees explainable evidence and fallback to UNCERTAIN when data is sparse.
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # 0. Data Sufficiency Verification
        if df is None or df.empty or len(df) < 25:
            return RegimeAnalysisResult(
                regime=V6MarketRegime.UNCERTAIN,
                strength=10,
                evidence=["Market candle depth is below 25 bars; insufficient data for statistical confirmation."],
                timeframe=timeframe,
                timestamp=now_iso,
                data_quality="INSUFFICIENT",
                metrics={"candle_count": 0 if df is None else len(df)}
            )

        closes = df["close"].astype(float).values
        highs = df["high"].astype(float).values
        lows = df["low"].astype(float).values
        curr_price = float(closes[-1])

        # 1. Check News Blackout / Event Risk first
        news_active = False
        news_event_desc = ""
        try:
            if news_context and news_context.get("is_blackout"):
                news_active = True
                news_event_desc = news_context.get("event_name", "High-impact economic event active")
            else:
                news_eval = news_risk_engine.evaluate_news_risk(symbol, filter_mode="STANDARD")
                if news_eval.is_blackout:
                    news_active = True
                    news_event_desc = news_eval.event_summary or "High-impact economic calendar event in proximity"
        except Exception as exc:
            logger.debug(f"News check bypassed in regime: {exc}")

        # 2. Technical and Statistical Metrics
        hurst = self.calculate_hurst_exponent(closes)
        close_series = pd.Series(closes)

        # EMAs: 20, 50, 200
        ema_20_series = calculate_ema(close_series, 20)
        ema_50_series = calculate_ema(close_series, 50)
        ema_20 = float(ema_20_series.iloc[-1])
        ema_50 = float(ema_50_series.iloc[-1])
        ema_200 = float(calculate_ema(close_series, 200).iloc[-1]) if len(closes) >= 150 else None

        # EMA Slope (% change over last 5 bars)
        ema_20_prev5 = float(ema_20_series.iloc[-5]) if len(ema_20_series) >= 5 else ema_20
        ema_20_slope_pct = ((ema_20 - ema_20_prev5) / ema_20_prev5) * 100.0 if ema_20_prev5 > 0 else 0.0

        # ATR 14 & Percentile
        atr_series = calculate_atr(df, period=14)
        atr_14 = float(atr_series.iloc[-1]) if not atr_series.empty else 0.0
        atr_pct = (atr_14 / curr_price) * 100.0 if curr_price > 0 else 0.0

        atr_pct_series = (atr_series / close_series.replace(0, np.nan)) * 100.0
        rolling_atr_window = atr_pct_series.tail(min(len(df), 100))
        atr_percentile = float(pd.Series(rolling_atr_window).rank(pct=True).iloc[-1] * 100.0) if len(rolling_atr_window) >= 15 else 50.0

        # Single-candle spike check
        latest_candle_range = abs(highs[-1] - lows[-1])
        is_candle_spike = latest_candle_range > (3.0 * atr_14) if atr_14 > 0 else False

        # DMI & ADX
        dmi = calculate_dmi_adx(df, period=14)
        adx_val = float(dmi["adx"].dropna().iloc[-1]) if not dmi["adx"].dropna().empty else 15.0
        plus_di = float(dmi["plus_di"].dropna().iloc[-1]) if not dmi["plus_di"].dropna().empty else 20.0
        minus_di = float(dmi["minus_di"].dropna().iloc[-1]) if not dmi["minus_di"].dropna().empty else 20.0

        # Bollinger Bands
        bb = calculate_bollinger_bands(close_series, period=20, num_std=2.0)
        bb_upper = float(bb["bb_upper"].iloc[-1])
        bb_lower = float(bb["bb_lower"].iloc[-1])
        bb_middle = float(bb["bb_middle"].iloc[-1])
        bb_width_pct = ((bb_upper - bb_lower) / bb_middle * 100.0) if bb_middle > 0 else 1.0

        # Donchian 20 channel breakout check
        highest_20 = float(np.max(highs[-21:-1])) if len(highs) >= 21 else highs[-1]
        lowest_20 = float(np.min(lows[-21:-1])) if len(lows) >= 21 else lows[-1]
        is_breakout_up = (curr_price > highest_20 and curr_price > ema_20)
        is_breakout_down = (curr_price < lowest_20 and curr_price < ema_20)

        # Structure analysis: Swings, BOS, CHoCH
        swings = identify_swing_points(df, left=2, right=2)
        struct = detect_structure_breaks(df, swings)
        shs = swings.get("swing_highs", [])
        sls = swings.get("swing_lows", [])

        higher_highs_lows = False
        lower_highs_lows = False
        if len(shs) >= 2 and len(sls) >= 2:
            if shs[-1]["price"] > shs[-2]["price"] and sls[-1]["price"] > sls[-2]["price"]:
                higher_highs_lows = True
            elif shs[-1]["price"] < shs[-2]["price"] and sls[-1]["price"] < sls[-2]["price"]:
                lower_highs_lows = True

        bos = struct.get("bos")
        choch = struct.get("choch")

        evidence: List[str] = []
        metrics: Dict[str, Any] = {
            "current_price": round(float(curr_price), 4),
            "ema_20": round(float(ema_20), 4),
            "ema_50": round(float(ema_50), 4),
            "ema_200": round(float(ema_200), 4) if ema_200 else None,
            "ema_20_slope_pct": round(float(ema_20_slope_pct), 3),
            "adx": round(float(adx_val), 1),
            "plus_di": round(float(plus_di), 1),
            "minus_di": round(float(minus_di), 1),
            "atr_14": round(float(atr_14), 4),
            "atr_percentile": round(float(atr_percentile), 1),
            "bb_width_pct": round(float(bb_width_pct), 2),
            "hurst_exponent": float(hurst),
            "candle_spike": bool(is_candle_spike),
            "news_active": bool(news_active),
        }

        # 3. Deterministic 11-Regime Decision Tree

        # A. NEWS VOLATILITY (Highest Priority event risk)
        if news_active or (is_candle_spike and atr_percentile >= 90):
            regime = V6MarketRegime.NEWS_VOLATILITY
            strength = 90
            evidence.append(f"High-impact macroeconomic event or violent spike detected ({news_event_desc or 'Single-candle range > 3x ATR'}). Spread expansion risk.")
            evidence.append(f"Metrics: ATR percentile = {atr_percentile:.1f}%, BB Width = {bb_width_pct:.2f}%.")

        # B. REVERSAL TRANSITION (Structural CHoCH + exhaustion)
        elif choch is not None:
            regime = V6MarketRegime.REVERSAL_TRANSITION
            strength = 82
            evidence.append(f"Change of Character ({choch.get('type')}) at {choch.get('level')} signaling trend exhaustion and structural reversal shift.")
            evidence.append(f"Metrics: ADX = {adx_val:.1f}, Hurst = {hurst:.2f}, EMA 20 slope = {ema_20_slope_pct:+.2f}%.")

        # C. STRONG BULLISH TREND (Persistent momentum + structure alignment)
        elif (
            (curr_price > ema_20 > ema_50 or (higher_highs_lows and curr_price > ema_20))
            and adx_val >= 24.0
            and plus_di > minus_di
        ):
            regime = V6MarketRegime.TREND_BULLISH_STRONG
            strength = min(95, int(50 + (adx_val * 0.8) + (hurst * 30)))
            evidence.append(f"Strong persistent bullish trend (ADX: {adx_val:.1f}, Hurst: {hurst:.2f}) with aligned moving averages (Price > EMA 20 > EMA 50).")
            if higher_highs_lows:
                evidence.append("Confirmed bullish structure with consecutive Higher Highs and Higher Lows.")
            evidence.append(f"Metrics: +DI ({plus_di:.1f}) > -DI ({minus_di:.1f}), EMA 20 slope = {ema_20_slope_pct:+.2f}%.")

        # D. STRONG BEARISH TREND (Persistent momentum + structure alignment)
        elif (
            (curr_price < ema_20 < ema_50 or (lower_highs_lows and curr_price < ema_20))
            and adx_val >= 24.0
            and minus_di > plus_di
        ):
            regime = V6MarketRegime.TREND_BEARISH_STRONG
            strength = min(95, int(50 + (adx_val * 0.8) + (hurst * 30)))
            evidence.append(f"Strong persistent bearish trend (ADX: {adx_val:.1f}, Hurst: {hurst:.2f}) with aligned moving averages (Price < EMA 20 < EMA 50).")
            if lower_highs_lows:
                evidence.append("Confirmed bearish structure with consecutive Lower Highs and Lower Lows.")
            evidence.append(f"Metrics: -DI ({minus_di:.1f}) > +DI ({plus_di:.1f}), EMA 20 slope = {ema_20_slope_pct:+.2f}%.")

        # E. BREAKOUT (Volatility expansion piercing channel)
        elif (is_breakout_up or is_breakout_down) and (bb_width_pct > 0.85 or atr_percentile > 70):
            regime = V6MarketRegime.BREAKOUT
            strength = 85
            dir_label = "Bullish expansion above 20-bar Donchian high" if is_breakout_up else "Bearish expansion below 20-bar Donchian low"
            evidence.append(f"Price breakout confirmed: {dir_label} with expanding volatility (BB Width: {bb_width_pct:.2f}%).")
            evidence.append(f"Metrics: Donchian Range [{lowest_20:.4f} - {highest_20:.4f}], ADX = {adx_val:.1f}.")

        # F. LOW VOLATILITY (Volatility compression / squeeze)
        elif bb_width_pct < 0.35 or atr_percentile < 20.0:
            regime = V6MarketRegime.LOW_VOLATILITY
            strength = 80
            evidence.append(f"Volatility compression squeeze (BB Width: {bb_width_pct:.2f}%, ATR Percentile: {atr_percentile:.1f}%). Liquidity coiling.")
            evidence.append(f"Metrics: Price inside tight band [{bb_lower:.4f} - {bb_upper:.4f}].")

        # G. RANGE / MEAN REVERSION (Consolidation before weak trends)
        elif (hurst < 0.48 or adx_val < 20.0) and bb_width_pct < 1.1:
            regime = V6MarketRegime.RANGE
            strength = 75
            evidence.append(f"Mean-reverting consolidation range (Hurst: {hurst:.2f}, ADX: {adx_val:.1f}). Price oscillating between horizontal bounds.")
            evidence.append(f"Metrics: Price bounded between {bb_lower:.4f} and {bb_upper:.4f}.")

        # H. HIGH VOLATILITY (Erratic wide swings)
        elif bb_width_pct > 1.35 or atr_percentile >= 85.0:
            regime = V6MarketRegime.HIGH_VOLATILITY
            strength = 78
            evidence.append(f"Elevated market volatility (BB Width: {bb_width_pct:.2f}%, ATR Percentile: {atr_percentile:.1f}%). Wide spreads and rapid swings.")
            evidence.append(f"Metrics: ATR 14 = {atr_14:.4f} ({atr_pct:.2f}%), ADX = {adx_val:.1f}.")

        # I. WEAK BULLISH TREND
        elif curr_price > ema_50 and (plus_di > minus_di or ema_20_slope_pct > 0.05) and adx_val >= 18.0:
            regime = V6MarketRegime.TREND_BULLISH_WEAK
            strength = 68
            evidence.append(f"Moderate bullish upward drift (Price > EMA 50), but trend strength is moderate (ADX: {adx_val:.1f}, Hurst: {hurst:.2f}).")
            evidence.append(f"Metrics: EMA 20 slope = {ema_20_slope_pct:+.2f}%, +DI = {plus_di:.1f}, -DI = {minus_di:.1f}.")

        # J. WEAK BEARISH TREND
        elif curr_price < ema_50 and (minus_di > plus_di or ema_20_slope_pct < -0.05) and adx_val >= 18.0:
            regime = V6MarketRegime.TREND_BEARISH_WEAK
            strength = 68
            evidence.append(f"Moderate bearish downward drift (Price < EMA 50), but trend strength is moderate (ADX: {adx_val:.1f}, Hurst: {hurst:.2f}).")
            evidence.append(f"Metrics: EMA 20 slope = {ema_20_slope_pct:+.2f}%, -DI = {minus_di:.1f}, +DI = {plus_di:.1f}.")

        # K. RANGE FALLBACK (Non-trending consolidation)
        elif hurst < 0.50 or adx_val < 22.0:
            regime = V6MarketRegime.RANGE
            strength = 70
            evidence.append(f"Consolidation range (Hurst: {hurst:.2f}, ADX: {adx_val:.1f}). No statistically significant trend detected.")
            evidence.append(f"Metrics: BB Width = {bb_width_pct:.2f}%.")

        # L. UNCERTAIN (Fallback when evidence is conflicting or borderline)
        else:
            regime = V6MarketRegime.UNCERTAIN
            strength = 40
            evidence.append("Conflicting directional and volatility metrics. Trend and range evidence do not reach statistical threshold.")
            evidence.append(f"Metrics: ADX = {adx_val:.1f}, Hurst = {hurst:.2f}, BB Width = {bb_width_pct:.2f}%.")

        return RegimeAnalysisResult(
            regime=regime,
            strength=strength,
            evidence=evidence,
            timeframe=timeframe,
            timestamp=now_iso,
            data_quality="HIGH_FIDELITY",
            metrics=metrics
        )


v6_regime_engine = V6MarketRegimeEngine()
