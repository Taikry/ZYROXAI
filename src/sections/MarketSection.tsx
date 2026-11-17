import React, { useState } from 'react';
import { MARKETS_DATA } from '../data/markets';
import { MarketAsset } from '../types';
import { TradingChart } from '../components/TradingChart';
import { useLanguage } from '../hooks/useLanguage';
import {
  TrendingUp,
  TrendingDown,
  Activity,
  AlertTriangle,
  Globe2,
  Gauge,
  Sparkles,
  Zap,
} from 'lucide-react';

export const MarketSection: React.FC = () => {
  const { isKhmer, t } = useLanguage();
  const [selectedAsset, setSelectedAsset] = useState<MarketAsset>(MARKETS_DATA[0]);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'commodities' | 'crypto' | 'forex'>('all');

  const filteredAssets = MARKETS_DATA.filter(
    (a) => selectedFilter === 'all' || a.category === selectedFilter
  );

  return (
    <section id="markets" className="py-20 relative bg-[#050807] overflow-hidden">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-grid-cyber opacity-20 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#00E59B]/10 border border-[#00E59B]/30 text-[#00E59B] text-xs font-mono font-semibold uppercase tracking-wider mb-3">
            <Globe2 className="w-3.5 h-3.5 text-[#39FFC0]" />
            <span>{t.markets.badge}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#F5F8F6] tracking-tight">
            {t.markets.title}
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#87938D] leading-relaxed">
            {t.markets.subtitle}
          </p>
        </div>

        {/* Clear Illustrative Demonstration Banner */}
        <div className="mb-8 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-xs text-amber-200">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold block uppercase tracking-wide text-amber-300">
              {t.markets.disclaimerTitle}
            </strong>
            <p className="mt-0.5 leading-relaxed text-amber-200/90">
              {t.markets.disclaimerText}
            </p>
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center justify-center gap-2 mb-8 flex-wrap">
          {[
            { id: 'all', label: isKhmer ? 'ទាំងអស់' : 'All Markets' },
            { id: 'commodities', label: t.markets.commodities },
            { id: 'crypto', label: t.markets.crypto },
            { id: 'forex', label: t.markets.forex },
          ].map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedFilter(cat.id as any)}
              className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all cursor-pointer ${
                selectedFilter === cat.id
                  ? 'bg-[#00E59B] text-[#050807] shadow-[0_0_15px_rgba(0,229,155,0.35)]'
                  : 'bg-[#090F0C] text-[#87938D] hover:text-[#F5F8F6] border border-[#00E59B]/15'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Layout: Market Cards Grid + Dedicated Chart Focus */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Asset Selection Cards */}
          <div className="lg:col-span-5 space-y-3">
            {filteredAssets.map((asset) => {
              const isSelected = selectedAsset.symbol === asset.symbol;
              const isUp = asset.change24h >= 0;

              return (
                <div
                  key={asset.symbol}
                  onClick={() => setSelectedAsset(asset)}
                  className={`p-4 rounded-2xl border transition-all duration-300 cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? 'bg-[#090F0C] border-[#00E59B] shadow-[0_0_20px_rgba(0,229,155,0.2)]'
                      : 'bg-[#090F0C]/60 border-[#00E59B]/15 hover:border-[#00E59B]/35 hover:bg-[#090F0C]'
                  }`}
                >
                  {/* Asset Info */}
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[#050807] border border-[#00E59B]/25 p-2 flex items-center justify-center">
                      {asset.logo ? (
                        <img
                          src={asset.logo}
                          alt={asset.symbol}
                          className="w-full h-full object-contain"
                          onError={(e) => {
                            (e.currentTarget as HTMLElement).style.display = 'none';
                          }}
                        />
                      ) : (
                        <Activity className="w-5 h-5 text-[#00E59B]" />
                      )}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-[#F5F8F6]">
                          {asset.symbol}
                        </span>
                        <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-white/5 text-[#87938D]">
                          {asset.category}
                        </span>
                      </div>
                      <span className="text-xs text-[#87938D] block">
                        {asset.name}
                      </span>
                    </div>
                  </div>

                  {/* Price & Trend */}
                  <div className="text-right">
                    <span className="font-mono text-sm font-bold text-[#F5F8F6] block">
                      {asset.category === 'forex'
                        ? asset.price.toFixed(4)
                        : `$${asset.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 font-mono text-xs font-semibold ${
                        isUp ? 'text-[#00E59B]' : 'text-rose-400'
                      }`}
                    >
                      {isUp ? (
                        <TrendingUp className="w-3 h-3" />
                      ) : (
                        <TrendingDown className="w-3 h-3" />
                      )}
                      {isUp ? '+' : ''}
                      {asset.change24h}%
                    </span>
                  </div>
                </div>
              );
            })}

            {/* Backend Integration Hint */}
            <div className="p-4 rounded-xl bg-[#050807] border border-[#00E59B]/20 text-xs font-mono text-[#87938D] flex items-center justify-between">
              <span>{t.markets.connectBackend}</span>
              <span className="text-[#00E59B]">FastAPI / MT5 Bridge</span>
            </div>
          </div>

          {/* Right Column: Detailed Interactive Chart & Telemetry Dashboard */}
          <div className="lg:col-span-7 space-y-4">
            <TradingChart asset={selectedAsset} />

            {/* Real-time Indicator Gauge Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Bias */}
              <div className="p-4 rounded-xl bg-[#090F0C] border border-[#00E59B]/20 flex flex-col justify-between">
                <span className="text-[10px] font-mono uppercase text-[#87938D] flex items-center gap-1">
                  <Activity className="w-3.5 h-3.5 text-[#00E59B]" />
                  {t.markets.bias}
                </span>
                <span className="text-base font-mono font-bold text-[#39FFC0] mt-1">
                  {selectedAsset.bias.replace('_', ' ')}
                </span>
                <span className="text-[10px] text-[#87938D] mt-0.5">
                  Confluence Gated
                </span>
              </div>

              {/* Sentiment */}
              <div className="p-4 rounded-xl bg-[#090F0C] border border-[#00E59B]/20 flex flex-col justify-between">
                <span className="text-[10px] font-mono uppercase text-[#87938D] flex items-center gap-1">
                  <Gauge className="w-3.5 h-3.5 text-[#39FFC0]" />
                  {t.markets.sentiment}
                </span>
                <span className="text-base font-mono font-bold text-[#00E59B] mt-1">
                  {selectedAsset.sentiment}% Bullish
                </span>
                <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden mt-1">
                  <div
                    className="bg-[#00E59B] h-full rounded-full transition-all duration-500"
                    style={{ width: `${selectedAsset.sentiment}%` }}
                  />
                </div>
              </div>

              {/* Volatility */}
              <div className="p-4 rounded-xl bg-[#090F0C] border border-[#00E59B]/20 flex flex-col justify-between">
                <span className="text-[10px] font-mono uppercase text-[#87938D] flex items-center gap-1">
                  <Zap className="w-3.5 h-3.5 text-amber-400" />
                  {t.markets.volatility}
                </span>
                <span className="text-base font-mono font-bold text-amber-300 mt-1">
                  {selectedAsset.volatility} (ATR Exp.)
                </span>
                <span className="text-[10px] text-[#87938D] mt-0.5">
                  Dynamic Spread Gated
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

