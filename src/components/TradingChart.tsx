import React, { useState, useMemo } from 'react';
import { TIMEFRAMES } from '../data/markets';
import { MarketAsset } from '../types';
import { Activity, RefreshCw, BarChart2, Eye, ShieldAlert, Sparkles } from 'lucide-react';

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

  // Generate synthetic yet deterministic realistic candlestick data based on asset and timeframe
  const candles: CandleData[] = useMemo(() => {
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

    // Anchor last candle close to current asset price
    list[list.length - 1].close = asset.price;
    list[list.length - 1].high = Math.max(list[list.length - 1].high, asset.price);
    list[list.length - 1].low = Math.min(list[list.length - 1].low, asset.price);

    return list;
  }, [asset.symbol, asset.price, activeTimeframe, tickCounter]);

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
    let ema = candles[0].close;
    return candles.map((c, i) => {
      ema = c.close * k + ema * (1 - k);
      return {
        x: paddingX + i * candleSpacing + candleSpacing / 2,
        y: getY(ema),
      };
    });
  }, [candles, minPrice, maxPrice, showVolume]);

  const emaPath = useMemo(() => {
    if (!emaPoints.length) return '';
    return emaPoints.reduce((acc, pt, i) => {
      return i === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
    }, '');
  }, [emaPoints]);

  // Order block coordinates (arbitrary structural zone near the lowest third)
  const obZone = useMemo(() => {
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

  const handleSimulateTick = () => {
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
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/25">
                ILLUSTRATIVE DEMO
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-[#87938D] mt-0.5 font-mono">
              <span>{asset.name}</span>
              <span>•</span>
              <span className="text-[#00E59B]">Spread: {asset.spread} pips</span>
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
            onClick={handleSimulateTick}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#00E59B]/15 hover:bg-[#00E59B]/25 text-[#39FFC0] border border-[#00E59B]/35 text-xs font-mono font-bold transition-all cursor-pointer shadow-sm active:scale-95"
            title="Simulate Real-Time Price Update"
          >
            <RefreshCw className="w-3.5 h-3.5 animate-spin" style={{ animationDuration: '4s' }} />
            <span>Tick</span>
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
            <pattern id="chartGridLines" width="60" height="40" patternUnits="userSpaceOnUse">
              <path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgba(0, 229, 155, 0.05)" strokeWidth="1" />
            </pattern>
          </defs>

          <rect width={chartWidth} height={chartHeight} fill="url(#chartGridLines)" />

          {/* Price Gridlines */}
          {[0.2, 0.4, 0.6, 0.8].map((pct, i) => {
            const priceLevel = minPrice + priceRange * pct;
            const yPos = getY(priceLevel);
            return (
              <g key={i}>
                <line
                  x1={paddingX}
                  y1={yPos}
                  x2={chartWidth - paddingX}
                  y2={yPos}
                  stroke="rgba(0, 229, 155, 0.08)"
                  strokeDasharray="3 3"
                />
                <text
                  x={chartWidth - 4}
                  y={yPos + 4}
                  textAnchor="end"
                  fill="#87938D"
                  fontSize="10"
                  fontFamily="JetBrains Mono"
                >
                  {priceLevel.toFixed(asset.category === 'forex' ? 4 : 2)}
                </text>
              </g>
            );
          })}

          {/* SMC Order Block (OB) Overlay */}
          {showOB && (
            <g>
              <rect
                x={paddingX + candleSpacing * 4}
                y={obZone.top}
                width={chartWidth - paddingX * 2 - candleSpacing * 4}
                height={obZone.height}
                fill="rgba(0, 229, 155, 0.08)"
                stroke="rgba(0, 229, 155, 0.4)"
                strokeWidth="1"
                rx="4"
              />
              <text
                x={paddingX + candleSpacing * 4 + 8}
                y={obZone.top + 13}
                fill="#39FFC0"
                fontSize="9"
                fontFamily="JetBrains Mono"
                fontWeight="bold"
              >
                +OB (Bullish Order Block Mitigation)
              </text>
            </g>
          )}

          {/* ICT Fair Value Gap (FVG) Overlay */}
          {showFVG && (
            <g>
              <rect
                x={paddingX + candleSpacing * 12}
                y={fvgZone.top}
                width={chartWidth - paddingX * 2 - candleSpacing * 12}
                height={fvgZone.height}
                fill="rgba(57, 255, 192, 0.06)"
                stroke="rgba(57, 255, 192, 0.35)"
                strokeDasharray="2 2"
                strokeWidth="1"
                rx="4"
              />
              <text
                x={paddingX + candleSpacing * 12 + 8}
                y={fvgZone.top + 12}
                fill="#39FFC0"
                fontSize="9"
                fontFamily="JetBrains Mono"
              >
                FVG Imbalance Zone (50% C.E.)
              </text>
            </g>
          )}

          {/* Break of Structure (BOS) Horizon */}
          <g>
            <line
              x1={paddingX + candleSpacing * 17}
              y1={getY(maxPrice * 0.998)}
              x2={chartWidth - paddingX}
              y2={getY(maxPrice * 0.998)}
              stroke="#00E59B"
              strokeWidth="1.2"
              strokeDasharray="4 3"
            />
            <text
              x={chartWidth - paddingX - 60}
              y={getY(maxPrice * 0.998) - 5}
              fill="#00E59B"
              fontSize="9"
              fontFamily="JetBrains Mono"
              fontWeight="bold"
            >
              BOS (Structure Break)
            </text>
          </g>

          {/* EMA Trend Curve */}
          {showEMA && emaPath && (
            <path
              d={emaPath}
              fill="none"
              stroke="#F59E0B"
              strokeWidth="1.6"
              strokeLinecap="round"
              opacity="0.85"
            />
          )}

          {/* Volume Histogram Bars */}
          {showVolume &&
            candles.map((c, i) => {
              const x = paddingX + i * candleSpacing + candleSpacing / 2;
              const isGreen = c.close >= c.open;
              const barHeight = (c.volume / maxVolume) * (volumeHeight - 8);
              const barY = chartHeight - paddingY - barHeight;
              const barWidth = Math.max(2, candleSpacing * 0.55);

              return (
                <rect
                  key={`vol-${i}`}
                  x={x - barWidth / 2}
                  y={barY}
                  width={barWidth}
                  height={barHeight}
                  fill={isGreen ? 'rgba(0, 229, 155, 0.35)' : 'rgba(244, 63, 94, 0.35)'}
                  rx="1"
                />
              );
            })}

          {/* Candlesticks */}
          {candles.map((c, i) => {
            const x = paddingX + i * candleSpacing + candleSpacing / 2;
            const isGreen = c.close >= c.open;
            const openY = getY(c.open);
            const closeY = getY(c.close);
            const highY = getY(c.high);
            const lowY = getY(c.low);
            const candleTop = Math.min(openY, closeY);
            const candleHeight = Math.max(2, Math.abs(closeY - openY));
            const candleWidth = Math.max(3, candleSpacing * 0.65);

            return (
              <g
                key={i}
                className="cursor-pointer group"
                onMouseEnter={() => {
                  setHoveredCandle(c);
                  setHoverCoords({ x, y: closeY });
                }}
              >
                {/* Wick */}
                <line
                  x1={x}
                  y1={highY}
                  x2={x}
                  y2={lowY}
                  stroke={isGreen ? '#00E59B' : '#F43F5E'}
                  strokeWidth="1.2"
                />

                {/* Body */}
                <rect
                  x={x - candleWidth / 2}
                  y={candleTop}
                  width={candleWidth}
                  height={candleHeight}
                  fill={isGreen ? '#00E59B' : '#F43F5E'}
                  stroke={isGreen ? '#39FFC0' : '#FB7185'}
                  strokeWidth="0.8"
                  rx="1"
                />

                {/* Interactive hover column highlight */}
                <rect
                  x={x - candleSpacing / 2}
                  y={0}
                  width={candleSpacing}
                  height={chartHeight}
                  fill="transparent"
                  className="hover:fill-white/5 transition-colors"
                />
              </g>
            );
          })}

          {/* Crosshair on hover */}
          {hoverCoords && (
            <g pointerEvents="none">
              <line
                x1={hoverCoords.x}
                y1={paddingY}
                x2={hoverCoords.x}
                y2={chartHeight - paddingY}
                stroke="rgba(57, 255, 192, 0.5)"
                strokeDasharray="3 3"
                strokeWidth="1"
              />
              <line
                x1={paddingX}
                y1={hoverCoords.y}
                x2={chartWidth - paddingX}
                y2={hoverCoords.y}
                stroke="rgba(57, 255, 192, 0.5)"
                strokeDasharray="3 3"
                strokeWidth="1"
              />
            </g>
          )}

          {/* Current Live Price Line */}
          <line
            x1={paddingX}
            y1={getY(asset.price)}
            x2={chartWidth - paddingX}
            y2={getY(asset.price)}
            stroke="#00E59B"
            strokeWidth="1.2"
            strokeDasharray="2 2"
          />

          <circle
            cx={chartWidth - paddingX}
            cy={getY(asset.price)}
            r="4"
            fill="#00E59B"
            className="animate-ping"
          />
          <circle cx={chartWidth - paddingX} cy={getY(asset.price)} r="3" fill="#39FFC0" />
        </svg>

        {/* Floating Tooltip HUD when hovering over a candle */}
        {hoveredCandle && (
          <div className="absolute top-2 left-4 px-3.5 py-1.5 rounded-xl bg-[#050807]/95 border border-[#00E59B]/50 backdrop-blur-md text-[11px] font-mono text-[#F5F8F6] shadow-2xl flex items-center gap-3">
            <span className="text-[#87938D]">{hoveredCandle.time}</span>
            <span>O: {hoveredCandle.open.toFixed(asset.category === 'forex' ? 4 : 2)}</span>
            <span>H: {hoveredCandle.high.toFixed(asset.category === 'forex' ? 4 : 2)}</span>
            <span>L: {hoveredCandle.low.toFixed(asset.category === 'forex' ? 4 : 2)}</span>
            <span className={hoveredCandle.close >= hoveredCandle.open ? 'text-[#00E59B]' : 'text-rose-400'}>
              C: {hoveredCandle.close.toFixed(asset.category === 'forex' ? 4 : 2)}
            </span>
            <span className="text-[#39FFC0]">Vol: {hoveredCandle.volume}</span>
          </div>
        )}
      </div>

      {/* Bottom Footer Info */}
      <div className="relative z-10 flex items-center justify-between pt-3 mt-2 border-t border-[#00E59B]/10 text-xs font-mono text-[#87938D]">
        <div className="flex items-center gap-4">
          <span>24h High: <strong className="text-[#F5F8F6]">{asset.high24h}</strong></span>
          <span>24h Low: <strong className="text-[#F5F8F6]">{asset.low24h}</strong></span>
          <span className="hidden sm:inline">Sentiment: <strong className="text-[#00E59B]">{asset.sentiment}% Bullish</strong></span>
        </div>
        <div className="flex items-center gap-2 text-[#00E59B]">
          <span className="w-2 h-2 rounded-full bg-[#00E59B] animate-pulse" />
          <span className="text-[11px]">AI Consensus Gated</span>
        </div>
      </div>
    </div>
  );
};
