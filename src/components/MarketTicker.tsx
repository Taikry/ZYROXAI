import React from 'react';
import { useRealtimeMarkets } from '../hooks/useRealtimeMarkets';
import { TrendingUp, TrendingDown, Radio } from 'lucide-react';

export const MarketTicker: React.FC = () => {
  const { markets, isLive } = useRealtimeMarkets();
  // Duplicate array to enable seamless looping marquee
  const tickerItems = [...markets, ...markets, ...markets];

  return (
    <div className="relative w-full overflow-hidden border-y border-[#00E59B]/15 bg-[#090F0C]/90 backdrop-blur-md py-2.5 z-20 flex items-center">
      {/* Live Feed Status Pill (Fixed on Left) */}
      <div className="shrink-0 pl-4 pr-3 py-1 flex items-center gap-2 border-r border-[#00E59B]/20 bg-[#050807]/80 z-20 hidden md:flex">
        <span className="relative flex h-2 w-2">
          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${isLive ? 'bg-[#00E59B]' : 'bg-amber-400'} opacity-75`} />
          <span className={`relative inline-flex rounded-full h-2 w-2 ${isLive ? 'bg-[#00E59B]' : 'bg-amber-500'}`} />
        </span>
        <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-[#39FFC0] flex items-center gap-1">
          <Radio className="w-3 h-3 text-[#00E59B]" />
          <span>{isLive ? 'LIVE TICKSTREAM' : 'SYNCING FEED'}</span>
        </span>
      </div>

      {/* Left and right vignette gradients */}
      <div className="absolute left-0 md:left-40 top-0 bottom-0 w-16 bg-gradient-to-r from-[#050807] to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-[#050807] to-transparent z-10 pointer-events-none" />

      <div className="animate-marquee flex items-center gap-8 pl-4">
        {tickerItems.map((item, idx) => {
          const isUp = item.change24h >= 0;
          return (
            <div
              key={`${item.symbol}-${idx}`}
              className="inline-flex items-center gap-3 px-3 py-1 rounded-lg bg-[#050807]/60 border border-white/5 hover:border-[#00E59B]/40 hover:bg-[#00E59B]/5 transition-all cursor-pointer group shrink-0"
            >
              {/* Asset Symbol & Logo */}
              <div className="flex items-center gap-2">
                {item.logo && (
                  <img
                    src={item.logo}
                    alt={item.symbol}
                    className="w-4 h-4 object-contain rounded-full"
                    onError={(e) => {
                      (e.currentTarget as HTMLElement).style.display = 'none';
                    }}
                  />
                )}
                <span className="font-mono text-xs font-bold text-[#F5F8F6] tracking-wide group-hover:text-[#39FFC0] transition-colors">
                  {item.symbol}
                </span>
              </div>

              {/* Real-time Price */}
              <span className="font-mono text-xs font-semibold text-[#F5F8F6]">
                {item.category === 'forex'
                  ? item.price.toFixed(4)
                  : `$${item.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
              </span>

              {/* 24h Change */}
              <span
                className={`inline-flex items-center gap-0.5 font-mono text-[11px] font-semibold ${
                  isUp ? 'text-[#00E59B]' : 'text-rose-400'
                }`}
              >
                {isUp ? (
                  <TrendingUp className="w-3 h-3" />
                ) : (
                  <TrendingDown className="w-3 h-3" />
                )}
                {isUp ? '+' : ''}
                {item.change24h}%
              </span>

              {/* Spread Badge */}
              {item.spread !== undefined && (
                <span className="text-[9px] font-mono px-1 py-0.5 rounded bg-white/5 text-[#87938D] border border-white/10 hidden sm:inline">
                  SPR {item.spread}
                </span>
              )}

              {/* Live Bias Pill */}
              <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-[#00E59B]/10 text-[#00E59B] border border-[#00E59B]/20">
                {item.bias.replace('_', ' ')}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
