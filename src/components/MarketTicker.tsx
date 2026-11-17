import React from 'react';
import { MARKETS_DATA } from '../data/markets';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

export const MarketTicker: React.FC = () => {
  // Duplicate array to enable seamless looping marquee
  const tickerItems = [...MARKETS_DATA, ...MARKETS_DATA, ...MARKETS_DATA];

  return (
    <div className="relative w-full overflow-hidden border-y border-[#00E59B]/15 bg-[#090F0C]/80 backdrop-blur-md py-2.5 z-20">
      {/* Left and right vignette gradients */}
      <div className="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-[#050807] to-transparent z-10 pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-[#050807] to-transparent z-10 pointer-events-none" />

      <div className="animate-marquee flex items-center gap-8">
        {tickerItems.map((item, idx) => {
          const isUp = item.change24h >= 0;
          return (
            <div
              key={`${item.symbol}-${idx}`}
              className="inline-flex items-center gap-3.5 px-3 py-1 rounded-lg bg-[#050807]/50 border border-white/5 hover:border-[#00E59B]/30 transition-colors cursor-pointer group"
            >
              {/* Asset Symbol & Category */}
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

              {/* Price */}
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

              {/* Bias Pill */}
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

