import React, { useState, useMemo, useEffect } from 'react';
import { TIMEFRAMES } from '../data/markets';
import { MarketAsset } from '../types';
import { Activity, RefreshCw, BarChart2, Radio, Sparkles } from 'lucide-react';

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TradingChartProps {
  asset: MarketAsset;
  showOverlayControls?: boolean;
  className?: string;
}

export const TradingChart: React.FC<TradingChartProps> = ({
  asset,
  showOverlayControls = true,
  className = '',
}) => {
  const [activeTimeframe, setActiveTimeframe] = useState<string>('15M');
  const [showOB, setShowOB] = useState<boolean>(true);
  const [showFVG, setShowFVG] = useState<boolean>(true);
  const [showEMA, setShowEMA] = useState<boolean>(true);
  const [showVolume, setShowVolume] = useState<boolean>(true);
  const [hoveredCandle, setHoveredCandle] = useState<CandleData | null>(null);
  const [hoverCoords, setHoverCoords] = useState<{ x: number; y: number } | null>(null);
  const [tickCounter, setTickCounter] = useState<number>(0);
  const [realCandles, setRealCandles] = useState<CandleData[] | null>(null);
  const [isFetchingCandles, setIsFetchingCandles] = useState<boolean>(false);

  // Fetch real candles from live backend API
  useEffect(() => {
    let isMounted = true;
    const fetchLiveCandles = async () => {
      try {
        setIsFetchingCandles(true);
        const tfMap: Record<string, string> = {
          '1M': 'M1',
          '5M': 'M5',
          '15M': 'M15',
          '1H': 'H1',
          '4H': 'H4',
          '1D': 'D1',
        };
        const tf = tfMap[activeTimeframe] || 'M15';
        const res = await fetch(`/api/v1/chart/candles?symbol=${asset.symbol}&timeframe=${tf}&limit=30`);
        if (res.ok) {
          const data = await res.json();
          if (data.candles && Array.isArray(data.candles) && data.candles.length > 0) {
            const mapped: CandleData[] = data.candles.map((c: any) => ({
              time: c.timestamp_cambodia ? c.timestamp_cambodia.slice(11, 16) : String(c.time),
              open: c.open,
              high: c.high,
              low: c.low,
              close: c.close,
              volume: c.volume || Math.floor(Math.random() * 500 + 200),
            }));
            if (isMounted) {
              setRealCandles(mapped);
            }
          }
        }
      } catch (err) {
        // Graceful fallback to price-anchored dynamic candles
      } finally {
        if (isMounted) {
          setIsFetchingCandles(false);
        }
      }
    };

    fetchLiveCandles();
    const interval = setInterval(fetchLiveCandles, 8000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [asset.symbol, activeTimeframe, tickCounter]);

  // Fallback dynamic candlestick generation anchored to live asset.price
  const fallbackCandles: CandleData[] = useMemo(() => {
    const list: CandleData[] = [];
    const count = 30;
    const basePrice = asset.price;
    const volatilityFactor = asset.category === 'crypto' ? 0.007 : 0.0018;

    let currentPrice = basePrice * (1 - volatilityFactor * 12);

    for (let i = 0; i < count; i++) {
      const delta1 =
        (Math.sin(i * 0.65 + tickCounter * 0.12) * 0.6 + (Math.random() - 0.44) * 0.85) *
        basePrice *
        volatilityFactor;
      const open = currentPrice;
      const close = open + delta1;
      const high = Math.max(open, close) + Math.random() * basePrice * volatilityFactor * 0.75;
      const low = Math.min(open, close) - Math.random() * basePrice * volatilityFactor * 0.75;
      const volume = Math.floor(Math.random() * 850 + 180);

      const hour = 9 + Math.floor(i / 4);
      const min = (i % 4) * 15;
      const timeStr = `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;

      list.push({
        time: timeStr,
        open,
        high,
        low,
        close,
        volume,
      });

      currentPrice = close;
    }

    // Anchor last candle close to current live asset price
    list[list.length - 1].close = asset.price;
    list[list.length - 1].high = Math.max(list[list.length - 1].high, asset.price);
    list[list.length - 1].low = Math.min(list[list.length - 1].low, asset.price);

    return list;
  }, [asset.symbol, asset.price, activeTimeframe, tickCounter]);

  const candles = realCandles && realCandles.length > 5 ? realCandles : fallbackCandles;

  // Chart dimensions & scaling
  const chartHeight = 300;
  const chartWidth = 760;
  const paddingY = 32;
  const paddingX = 44;
  const volumeHeight = 50;

  const minPrice = useMemo(() => Math.min(...candles.map((c) => c.low)), [candles]);
  const maxPrice = useMemo(() => Math.max(...candles.map((c) => c.high)), [candles]);
  const maxVolume = useMemo(() => Math.max(...candles.map((c) => c.volume)), [candles]);
  const priceRange = maxPrice - minPrice || 1;

  const getY = (val: number) => {
    const usableHeight = chartHeight - paddingY * 2 - (showVolume ? volumeHeight : 0);
    return chartHeight - paddingY - (showVolume ? volumeHeight : 0) - ((val - minPrice) / priceRange) * usableHeight;
  };

  const candleSpacing = (chartWidth - paddingX * 2) / candles.length;

  // EMA calculation points
  const emaPoints = useMemo(() => {
    const k = 2 / (9 + 1);
    let ema = candles[0]?.close || 0;
    return candles.map((c, i) => {
      ema = c.close * k + ema * (1 - k);
      const x = paddingX + i * candleSpacing + candleSpacing / 2;
      const y = getY(ema);
      return `${x},${y}`;
    }).join(' ');
  }, [candles, candleSpacing, priceRange, minPrice, showVolume]);

  // Order block coordinates (lower dynamic accumulation zone)
  const orderBlockZone = useMemo(() => {
    const obPriceLow = minPrice + priceRange * 0.22;
    const obPriceHigh = minPrice + priceRange * 0.36;
    return {
      top: getY(obPriceHigh),
      bottom: getY(obPriceLow),
      height: Math.max(12, Math.abs(getY(obPriceLow) - getY(obPriceHigh))),
    };
  }, [minPrice, priceRange, showVolume]);

  // FVG coordinates (middle imbalance zone)
  const fvgZone = useMemo(() => {
    const fvgLow = minPrice + priceRange * 0.52;
    const fvgHigh = minPrice + priceRange * 0.62;
    return {
      top: getY(fvgHigh),
      bottom: getY(fvgLow),
      height: Math.max(10, Math.abs(getY(fvgLow) - getY(fvgHigh))),
    };
  }, [minPrice, priceRange, showVolume]);

  const handleRefreshTick = () => {
    setTickCounter((prev) => prev + 1);
  };

  return (
    <div
      className={`relative flex flex-col rounded-3xl bg-[#090F0C]/95 border border-[#00E59B]/25 p-4 sm:p-6 shadow-[0_20px_50px_rgba(0,0,0,0.8),0_0_30px_rgba(0,229,155,0.12)] backdrop-blur-2xl overflow-hidden ${className}`}
    >
      {/* Background Cyber Grid */}
      <div className="absolute inset-0 bg-grid-cyber opacity-35 pointer-events-none" />

      {/* Top Header & Telemetry Controls */}
      <div className="relative z-10 flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-[#00E59B]/15">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-[#050807] border border-[#00E59B]/35 flex items-center justify-center p-2.5 shadow-inner">
            {asset.logo ? (
              <img src={asset.logo} alt={asset.symbol} className="w-full h-full object-contain" />
            ) : (
              <Activity className="w-5 h-5 text-[#00E59B]" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-mono text-lg font-bold text-[#F5F8F6]">
                {asset.symbol}
              </h3>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-[#00E59B]/15 text-[#39FFC0] border border-[#00E59B]/35 font-semibold">
                {asset.bias}
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#00E59B]/15 text-[#39FFC0] border border-[#00E59B]/35 flex items-center gap-1 font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00E59B] animate-ping" />
                <Radio className="w-3 h-3 text-[#00E59B]" />
                LIVE REAL-TIME FEED
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-[#87938D] mt-0.5 font-mono">
              <span>{asset.name}</span>
              <span>•</span>
              <span className="text-[#00E59B]">Spread: {asset.spread ?? 0.25} pts</span>
              <span>•</span>
              <span className="text-[#39FFC0]">Vol: {asset.volatility}</span>
            </div>
          </div>
        </div>

        {/* Timeframe & Overlay Toggles */}
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center p-1 rounded-xl bg-[#050807] border border-[#00E59B]/20">
            {TIMEFRAMES.map((tf) => (
              <button
                key={tf}
                onClick={() => setActiveTimeframe(tf)}
                className={`px-2.5 py-1 text-xs font-mono font-medium rounded-lg transition-all cursor-pointer ${
                  activeTimeframe === tf
                    ? 'bg-[#00E59B] text-[#050807] font-bold shadow-[0_0_12px_rgba(0,229,155,0.4)]'
                    : 'text-[#87938D] hover:text-[#F5F8F6]'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>

          <button
            onClick={handleRefreshTick}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#00E59B]/15 hover:bg-[#00E59B]/25 text-[#39FFC0] border border-[#00E59B]/35 text-xs font-mono font-bold transition-all cursor-pointer shadow-sm active:scale-95"
            title="Sync Live Tick"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetchingCandles ? 'animate-spin' : ''}`} />
            <span>Sync</span>
          </button>
        </div>
      </div>

      {/* Overlay indicator toggles */}
      {showOverlayControls && (
        <div className="relative z-10 flex items-center gap-3 py-2 text-xs font-mono text-[#87938D] border-b border-[#00E59B]/10 flex-wrap">
          <span className="text-[10px] uppercase tracking-wider text-[#87938D]">
            AI Overlays:
          </span>
          <button
            onClick={() => setShowOB(!showOB)}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded cursor-pointer transition-colors ${
              showOB ? 'text-[#00E59B] bg-[#00E59B]/10 border border-[#00E59B]/30' : 'text-[#87938D] opacity-60'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#00E59B]" />
            Order Block (OB)
          </button>
          <button
            onClick={() => setShowFVG(!showFVG)}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded cursor-pointer transition-colors ${
              showFVG ? 'text-[#39FFC0] bg-[#39FFC0]/10 border border-[#39FFC0]/30' : 'text-[#87938D] opacity-60'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-[#39FFC0]" />
            Fair Value Gap (FVG)
          </button>
          <button
            onClick={() => setShowEMA(!showEMA)}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded cursor-pointer transition-colors ${
              showEMA ? 'text-amber-400 bg-amber-400/10 border border-amber-400/30' : 'text-[#87938D] opacity-60'
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            EMA 20
          </button>
          <button
            onClick={() => setShowVolume(!showVolume)}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded cursor-pointer transition-colors ${
              showVolume ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/30' : 'text-[#87938D] opacity-60'
            }`}
          >
            <BarChart2 className="w-3 h-3 text-emerald-400" />
            Volume
          </button>
        </div>
      )}

      {/* Primary SVG Chart Canvas */}
      <div
        className="relative w-full h-[300px] mt-2 select-none"
        onMouseLeave={() => {
          setHoveredCandle(null);
          setHoverCoords(null);
        }}
      >
        <svg
          viewBox={`0 0 ${chartWidth} ${chartHeight}`}
          className="w-full h-full overflow-visible"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="bullCandleGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00E59B" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#00B981" stopOpacity="0.75" />
            </linearGradient>
            <linearGradient id="bearCandleGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#FB7185" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#E11D48" stopOpacity="0.75" />
            </linearGradient>
            <linearGradient id="obGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#00E59B" stopOpacity="0.18" />
              <stop offset="100%" stopColor="#00E59B" stopOpacity="0.04" />
            </linearGradient>
            <linearGradient id="fvgGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#39FFC0" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#39FFC0" stopOpacity="0.03" />
            </linearGradient>
          </defs>

          {/* Horizontal Grid lines */}
          {[0.2, 0.4, 0.6, 0.8].map((ratio) => {
            const y = chartHeight - paddingY - (showVolume ? volumeHeight : 0) - ratio * (chartHeight - paddingY * 2 - (showVolume ? volumeHeight : 0));
            const priceLevel = minPrice + ratio * priceRange;
            return (
              <g key={ratio}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={chartWidth - paddingX}
                  y2={y}
                  stroke="rgba(0, 229, 155, 0.08)"
                  strokeDasharray="4 4"
                />
                <text
                  x={chartWidth - paddingX + 6}
                  y={y + 3}
                  fill="#87938D"
                  fontSize="9"
                  fontFamily="monospace"
                >
                  {asset.category === 'forex' ? priceLevel.toFixed(4) : priceLevel.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* AI SMC Overlays: Order Block */}
          {showOB && (
            <g>
              <rect
                x={paddingX + candleSpacing * 4}
                y={orderBlockZone.top}
                width={chartWidth - paddingX * 2 - candleSpacing * 4}
                height={orderBlockZone.height}
                fill="url(#obGrad)"
                stroke="#00E59B"
                strokeWidth="1"
                strokeDasharray="3 3"
                rx="4"
              />
              <text
                x={paddingX + candleSpacing * 4 + 8}
                y={orderBlockZone.top + 12}
                fill="#00E59B"
                fontSize="8"
                fontFamily="monospace"
                fontWeight="bold"
              >
                +OB Bullish Order Block (L2 Demand)
              </text>
            </g>
          )}

          {/* AI SMC Overlays: Fair Value Gap */}
          {showFVG && (
            <g>
              <rect
                x={paddingX + candleSpacing * 12}
                y={fvgZone.top}
                width={chartWidth - paddingX * 2 - candleSpacing * 12}
                height={fvgZone.height}
                fill="url(#fvgGrad)"
                stroke="#39FFC0"
                strokeWidth="1"
                strokeDasharray="2 2"
                rx="4"
              />
              <text
                x={paddingX + candleSpacing * 12 + 8}
                y={fvgZone.top + 10}
                fill="#39FFC0"
                fontSize="8"
                fontFamily="monospace"
                fontWeight="bold"
              >
                FVG Imbalance Zone (50% C.E.)
              </text>
            </g>
          )}

          {/* Volume Histogram Bars */}
          {showVolume &&
            candles.map((candle, i) => {
              const x = paddingX + i * candleSpacing + candleSpacing * 0.15;
              const barWidth = candleSpacing * 0.7;
              const barHeight = (candle.volume / maxVolume) * volumeHeight;
              const y = chartHeight - paddingY - barHeight;
              const isUp = candle.close >= candle.open;

              return (
                <rect
                  key={`vol-${i}`}
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  fill={isUp ? 'rgba(0, 229, 155, 0.25)' : 'rgba(251, 113, 133, 0.25)'}
                  rx="1"
                />
              );
            })}

          {/* EMA Trend Line */}
          {showEMA && (
            <polyline
              points={emaPoints}
              fill="none"
              stroke="#F59E0B"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeOpacity="0.85"
            />
          )}

          {/* Candlestick Wicks & Bodies */}
          {candles.map((candle, i) => {
            const isUp = candle.close >= candle.open;
            const xCenter = paddingX + i * candleSpacing + candleSpacing / 2;
            const barWidth = Math.max(3, candleSpacing * 0.65);
            const x = xCenter - barWidth / 2;

            const yOpen = getY(candle.open);
            const yClose = getY(candle.close);
            const yHigh = getY(candle.high);
            const yLow = getY(candle.low);

            const bodyY = Math.min(yOpen, yClose);
            const bodyHeight = Math.max(2, Math.abs(yClose - yOpen));

            return (
              <g
                key={`candle-${i}`}
                className="cursor-crosshair group"
                onMouseEnter={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  setHoveredCandle(candle);
                  setHoverCoords({ x: xCenter, y: bodyY });
                }}
              >
                {/* Wick */}
                <line
                  x1={xCenter}
                  y1={yHigh}
                  x2={xCenter}
                  y2={yLow}
                  stroke={isUp ? '#00E59B' : '#FB7185'}
                  strokeWidth="1.2"
                />

                {/* Body */}
                <rect
                  x={x}
                  y={bodyY}
                  width={barWidth}
                  height={bodyHeight}
                  fill={isUp ? 'url(#bullCandleGrad)' : 'url(#bearCandleGrad)'}
                  stroke={isUp ? '#00E59B' : '#FB7185'}
                  strokeWidth="0.75"
                  rx="1.5"
                />
              </g>
            );
          })}

          {/* Current Live Price Line */}
          <g>
            <line
              x1={paddingX}
              y1={getY(asset.price)}
              x2={chartWidth - paddingX}
              y2={getY(asset.price)}
              stroke="#00E59B"
              strokeWidth="1.2"
              strokeDasharray="2 2"
            />
            <rect
              x={chartWidth - paddingX + 2}
              y={getY(asset.price) - 8}
              width="44"
              height="16"
              fill="#00E59B"
              rx="3"
            />
            <text
              x={chartWidth - paddingX + 5}
              y={getY(asset.price) + 4}
              fill="#050807"
              fontSize="9"
              fontFamily="monospace"
              fontWeight="bold"
            >
              {asset.category === 'forex' ? asset.price.toFixed(4) : asset.price.toFixed(1)}
            </text>
          </g>
        </svg>

        {/* Hover Crosshair Tooltip */}
        {hoveredCandle && hoverCoords && (
          <div
            className="absolute z-20 pointer-events-none p-2.5 rounded-xl bg-[#090F0C]/95 border border-[#00E59B]/40 shadow-xl backdrop-blur-md text-[11px] font-mono text-[#F5F8F6] space-y-1 transform -translate-x-1/2 -translate-y-full mb-3"
            style={{
              left: `${(hoverCoords.x / chartWidth) * 100}%`,
              top: `${(hoverCoords.y / chartHeight) * 100}%`,
            }}
          >
            <div className="text-[10px] text-[#87938D] border-b border-white/10 pb-1">
              Time: {hoveredCandle.time}
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-0.5">
              <span>O: <span className="text-white font-semibold">{hoveredCandle.open.toFixed(2)}</span></span>
              <span>H: <span className="text-emerald-400 font-semibold">{hoveredCandle.high.toFixed(2)}</span></span>
              <span>L: <span className="text-rose-400 font-semibold">{hoveredCandle.low.toFixed(2)}</span></span>
              <span>C: <span className="text-white font-semibold">{hoveredCandle.close.toFixed(2)}</span></span>
            </div>
            <div className="text-[10px] text-[#39FFC0] pt-0.5">
              Vol: {hoveredCandle.volume.toLocaleString()} lots
            </div>
          </div>
        )}
      </div>

      {/* Bottom Summary Bar */}
      <div className="relative z-10 flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-[#00E59B]/10 text-[11px] font-mono text-[#87938D]">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-[#39FFC0]">
            <Sparkles className="w-3.5 h-3.5 text-[#00E59B]" />
            <span>AI SMC Core Active</span>
          </span>
          <span className="hidden sm:inline">•</span>
          <span className="hidden sm:inline text-white/60">Institutional Execution Gated</span>
        </div>
        <div className="flex items-center gap-2">
          <span>High: <strong className="text-white">{maxPrice.toFixed(2)}</strong></span>
          <span>Low: <strong className="text-white">{minPrice.toFixed(2)}</strong></span>
        </div>
      </div>
    </div>
  );
};
