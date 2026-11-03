"""
ZYROX AI — Market Regime Detection Engine V3
============================================
Classifies market conditions into 8 standard states:
- STRONG_TREND
- WEAK_TREND
- RANGE
- HIGH_VOLATILITY
- LOW_VOLATILITY
- BREAKOUT
- REVERSAL
- UNCERTAIN

Provides supporting quantitative evidence, indicator metrics, and strict data-sufficiency checks.
"""
from __future__ import annotations

import math
import logging
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from taikry.risk.models import MarketRegimeType, RegimeClassificationResult

logger = logging.getLogger("zyrox.risk.regime")


class MarketRegimeEngine:
    """Quantitative classifier for 8-state market regimes."""

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

    @staticmethod
    def calculate_adx(highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, period: int = 14) -> float:
        """Computes Wilder's Average Directional Index (ADX)."""
        if len(closes) < period + 5:
            return 15.0
        try:
            tr_list = []
            plus_dm = []
            minus_dm = []
            for i in range(1, len(closes)):
                h_diff = highs[i] - highs[i - 1]
                l_diff = lows[i - 1] - lows[i]
                plus_dm.append(h_diff if h_diff > l_diff and h_diff > 0 else 0.0)
                minus_dm.append(l_diff if l_diff > h_diff and l_diff > 0 else 0.0)
                tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
                tr_list.append(tr)

            if len(tr_list) < period:
                return 15.0

            tr_s = pd.Series(tr_list).rolling(period).mean()
            p_dm_s = pd.Series(plus_dm).rolling(period).mean()
            m_dm_s = pd.Series(minus_dm).rolling(period).mean()

            plus_di = 100.0 * (p_dm_s / tr_s.replace(0, 1e-8))
            minus_di = 100.0 * (m_dm_s / tr_s.replace(0, 1e-8))

            dx = 100.0 * (abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, 1e-8))
            adx_val = float(dx.rolling(period).mean().dropna().iloc[-1]) if not dx.dropna().empty else 18.0
            return round(max(0.0, min(100.0, adx_val)), 1)
        except Exception:
            return 18.0

    def classify_regime(
        self,
        symbol: str,
        df: Optional[pd.DataFrame],
        structure_info: Optional[Dict[str, Any]] = None
    ) -> RegimeClassificationResult:
        """
        Classifies candles and structure into one of the 8 canonical regimes.
        Safely returns UNCERTAIN if data depth is insufficient.
        """
        if df is None or df.empty or len(df) < 25:
            return RegimeClassificationResult(
                regime=MarketRegimeType.UNCERTAIN,
                volatility_state="UNKNOWN",
                hurst_exponent=0.50,
                adx_value=0.0,
                atr_14=0.0,
                bb_width_pct=0.0,
                evidence=["Market candle depth is below 25 bars; insufficient data for statistical confirmation."],
                is_confirmed=False,
                rationale="Insufficient data depth to confirm market regime with mathematical confidence."
            )

        closes = df["close"].astype(float).values
        highs = df["high"].astype(float).values
        lows = df["low"].astype(float).values

        # 1. Quantitative Metrics
        hurst = self.calculate_hurst_exponent(closes)
        adx = self.calculate_adx(highs, lows, closes)

        # ATR 14
        tr_list = [
            max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
            for i in range(1, len(closes))
        ]
        atr_14 = float(np.mean(tr_list[-14:])) if len(tr_list) >= 14 else float(np.mean(tr_list))
        atr_pct = (atr_14 / closes[-1]) * 100.0 if closes[-1] > 0 else 0.0

        # Moving Averages
        close_series = pd.Series(closes)
        ema_20 = float(close_series.ewm(span=20).mean().iloc[-1])
        ema_50 = float(close_series.ewm(span=50).mean().iloc[-1]) if len(closes) >= 50 else ema_20

        # Bollinger Band Width
        rolling_std = float(close_series.rolling(20).std().iloc[-1]) if len(closes) >= 20 else 0.0
        bb_width = (rolling_std * 4.0 / ema_20) * 100.0 if ema_20 > 0 else 1.0

        # Volatility State determination
        if bb_width < 0.35:
            vol_state = "LOW_VOLATILITY"
        elif bb_width > 1.25 or atr_pct > 1.2:
            vol_state = "HIGH_VOLATILITY"
        else:
            vol_state = "NORMAL"

        evidence: List[str] = []
        struct = structure_info or {}
        bos = struct.get("bos_detected", False)
        choch = struct.get("choch_detected", False)
        rsi_val = float(struct.get("rsi_14", 50.0))

        # Check Donchian 20 breakout
        highest_20 = float(np.max(highs[-21:-1])) if len(highs) >= 21 else highs[-1]
        lowest_20 = float(np.min(lows[-21:-1])) if len(lows) >= 21 else lows[-1]
        is_breakout = (closes[-1] > highest_20 and closes[-1] > ema_20) or (closes[-1] < lowest_20 and closes[-1] < ema_20)

        # 8-State Classification Logic
        diff_from_ema50 = abs((closes[-1] - ema_50) / ema_50) * 100.0 if ema_50 > 0 else 0.0

        if choch and (rsi_val > 70 or rsi_val < 30):
            regime = MarketRegimeType.REVERSAL
            evidence.append(f"Structural Change of Character (CHOCH) detected with extreme RSI momentum ({rsi_val:.1f}). Exhaustion reversal.")
        elif is_breakout and vol_state == "HIGH_VOLATILITY":
            regime = MarketRegimeType.BREAKOUT
            evidence.append(f"Price expansion piercing 20-bar Donchian channel with expanding volatility (BB Width: {bb_width:.2f}%). Breakout phase.")
        elif adx >= 28 and hurst >= 0.58 and (ema_20 > ema_50 or ema_20 < ema_50):
            regime = MarketRegimeType.STRONG_TREND
            trend_dir = "Bullish" if ema_20 > ema_50 else "Bearish"
            evidence.append(f"Strong persistent trend (ADX: {adx}, Hurst: {hurst:.2f}) with aligned moving averages ({trend_dir}).")
        elif adx >= 18 and hurst >= 0.52:
            regime = MarketRegimeType.WEAK_TREND
            evidence.append(f"Moderate directional drift (ADX: {adx}, Hurst: {hurst:.2f}) with moderate trend strength.")
        elif vol_state == "HIGH_VOLATILITY":
            regime = MarketRegimeType.HIGH_VOLATILITY
            evidence.append(f"Heightened market volatility (BB Width {bb_width:.2f}%, ATR {atr_14:.2f} pts). Spread blowout caution advised.")
        elif vol_state == "LOW_VOLATILITY" or (bb_width < 0.40 and diff_from_ema50 < 0.20):
            regime = MarketRegimeType.LOW_VOLATILITY
            evidence.append(f"Volatility compression squeeze (BB Width {bb_width:.2f}%). Liquidity coiling for directional release.")
        elif hurst < 0.46 and adx < 20:
            regime = MarketRegimeType.RANGE
            evidence.append(f"Mean-reverting consolidation range (Hurst: {hurst:.2f}, ADX: {adx}). Oscillating between horizontal bounds.")
        else:
            regime = MarketRegimeType.RANGE
            evidence.append(f"Rotational trading range with balanced supply and demand (Hurst: {hurst:.2f}, ADX: {adx}).")

        evidence.append(f"Metrics: ATR 14 = {atr_14:.2f} pts ({atr_pct:.2f}%), ADX = {adx}, Hurst = {hurst:.2f}, BB Width = {bb_width:.2f}%.")

        return RegimeClassificationResult(
            regime=regime,
            volatility_state=vol_state,
            hurst_exponent=hurst,
            adx_value=adx,
            atr_14=round(atr_14, 4),
            bb_width_pct=round(bb_width, 2),
            evidence=evidence,
            is_confirmed=True,
            rationale=f"Market operates in {regime.value} with {vol_state} conditions."
        )


regime_engine = MarketRegimeEngine()
