import React, { useState } from 'react';
import { DEMO_SIGNALS } from '../data/signals';
import { useLanguage } from '../hooks/useLanguage';
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  ShieldCheck,
  CheckCircle2,
  Clock,
  Target,
  Sparkles,
  Layers,
  Zap,
} from 'lucide-react';

export const SignalsSection: React.FC = () => {
  const { isKhmer, t } = useLanguage();
  const [direction, setDirection] = useState<'buy' | 'sell'>('buy');
  const signal = DEMO_SIGNALS[direction];

  return (
    <section id="signals" className="py-20 relative bg-[#090F0C]/90 overflow-hidden">
      {/* Background Lighting */}
      <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-[#00E59B]/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#00E59B]/10 border border-[#00E59B]/30 text-[#00E59B] text-xs font-mono font-semibold uppercase tracking-wider mb-3">
            <Sparkles className="w-3.5 h-3.5 text-[#39FFC0]" />
            <span>{t.signals.badge}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#F5F8F6] tracking-tight">
            {t.signals.title}
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#87938D] leading-relaxed">
            {t.signals.subtitle}
          </p>
        </div>

        {/* Clear Regulatory Disclaimer Card */}
        <div className="max-w-3xl mx-auto mb-10 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-start gap-3 text-xs text-amber-200">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold block uppercase tracking-wide text-amber-300">
              {t.signals.demoBadge}
            </strong>
            <p className="mt-0.5 leading-relaxed text-amber-200/90">
              {t.signals.demoWarning}
            </p>
          </div>
        </div>

        {/* Toggle Long / Short Preview */}
        <div className="flex items-center justify-center gap-3 mb-10">
          <button
            onClick={() => setDirection('buy')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer ${
              direction === 'buy'
                ? 'bg-[#00E59B] text-[#050807] shadow-[0_0_20px_rgba(0,229,155,0.4)]'
                : 'bg-[#050807] text-[#87938D] hover:text-[#F5F8F6] border border-[#00E59B]/20'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            <span>{t.signals.toggleBuy}</span>
          </button>

          <button
            onClick={() => setDirection('sell')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer ${
              direction === 'sell'
                ? 'bg-rose-500 text-white shadow-[0_0_20px_rgba(244,63,94,0.4)]'
                : 'bg-[#050807] text-[#87938D] hover:text-[#F5F8F6] border border-rose-500/20'
            }`}
          >
            <TrendingDown className="w-4 h-4" />
            <span>{t.signals.toggleSell}</span>
          </button>
        </div>

        {/* Institutional Signal Preview Card */}
        <div className="max-w-4xl mx-auto p-6 sm:p-10 rounded-3xl bg-[#050807] border-2 border-[#00E59B]/30 shadow-2xl relative overflow-hidden">
          {/* Ambient Corner Banner */}
          <div className="absolute top-0 right-0 bg-[#00E59B]/10 border-b border-l border-[#00E59B]/30 px-4 py-1.5 rounded-bl-2xl font-mono text-[11px] font-bold text-[#39FFC0] uppercase tracking-wider">
            {t.signals.demoBadge}
          </div>

          {/* Top Row: Symbol, Direction, Confidence */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-[#00E59B]/20">
            <div>
              <div className="flex items-center gap-3">
                <h3 className="text-2xl sm:text-3xl font-mono font-black text-[#F5F8F6] tracking-tight">
                  {signal.symbol}
                </h3>
                <span
                  className={`px-3 py-1 rounded-xl text-xs font-mono font-black uppercase tracking-wider ${
                    signal.direction === 'BUY'
                      ? 'bg-[#00E59B] text-[#050807]'
                      : 'bg-rose-500 text-white'
                  }`}
                >
                  {signal.direction}
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-white/5 text-[#87938D]">
                  {signal.marketName}
                </span>
              </div>
              <span className="text-xs text-[#87938D] mt-1 block">
                {t.signals.direction}: <strong>{signal.direction === 'BUY' ? 'BULLISH CONTINUATION' : 'BEARISH DISPLACEMENT'}</strong>
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-right">
                <span className="text-[10px] font-mono uppercase text-[#87938D] block">
                  {t.signals.confidence}
                </span>
                <span className="text-xl sm:text-2xl font-mono font-bold text-[#39FFC0]">
                  {signal.confidence}%
                </span>
              </div>
              <div className="text-right">
                <span className="text-[10px] font-mono uppercase text-[#87938D] block">
                  {t.signals.riskReward}
                </span>
                <span className="text-xl sm:text-2xl font-mono font-bold text-[#00E59B]">
                  {signal.riskReward}
                </span>
              </div>
            </div>
          </div>

          {/* Price Execution Architecture Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 sm:gap-4 my-8">
            {/* Entry */}
            <div className="p-4 rounded-2xl bg-[#090F0C] border border-[#00E59B]/30 flex flex-col justify-between">
              <span className="text-[10px] font-mono uppercase text-[#87938D]">
                {t.signals.entry}
              </span>
              <span className="text-lg sm:text-xl font-mono font-bold text-[#F5F8F6] mt-1">
                {signal.entry.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              <span className="text-[9px] font-mono text-[#00E59B] mt-0.5">
                DEMO LIMIT
              </span>
            </div>

            {/* Stop Loss */}
            <div className="p-4 rounded-2xl bg-[#090F0C] border border-rose-500/30 flex flex-col justify-between">
              <span className="text-[10px] font-mono uppercase text-rose-300">
                {t.signals.stopLoss}
              </span>
              <span className="text-lg sm:text-xl font-mono font-bold text-rose-400 mt-1">
                {signal.sl.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              <span className="text-[9px] font-mono text-rose-400/80 mt-0.5">
                RISK: {signal.riskPercent}
              </span>
            </div>

            {/* TP1 */}
            <div className="p-4 rounded-2xl bg-[#090F0C] border border-[#00E59B]/20 flex flex-col justify-between">
              <span className="text-[10px] font-mono uppercase text-[#87938D]">
                {t.signals.takeProfit1}
              </span>
              <span className="text-lg sm:text-xl font-mono font-bold text-[#00E59B] mt-1">
                {signal.tp1.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              <span className="text-[9px] font-mono text-[#87938D] mt-0.5">
                Target 1
              </span>
            </div>

            {/* TP2 */}
            <div className="p-4 rounded-2xl bg-[#090F0C] border border-[#00E59B]/20 flex flex-col justify-between">
              <span className="text-[10px] font-mono uppercase text-[#87938D]">
                {t.signals.takeProfit2}
              </span>
              <span className="text-lg sm:text-xl font-mono font-bold text-[#39FFC0] mt-1">
                {signal.tp2.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              <span className="text-[9px] font-mono text-[#87938D] mt-0.5">
                Target 2
              </span>
            </div>

            {/* TP3 */}
            <div className="p-4 rounded-2xl bg-[#090F0C] border border-[#00E59B]/20 flex flex-col justify-between col-span-2 sm:col-span-1">
              <span className="text-[10px] font-mono uppercase text-[#87938D]">
                {t.signals.takeProfit3}
              </span>
              <span className="text-lg sm:text-xl font-mono font-bold text-emerald-300 mt-1">
                {signal.tp3.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
              <span className="text-[9px] font-mono text-emerald-400 mt-0.5">
                Full Runner
              </span>
            </div>
          </div>

          {/* Risk-Reward Visual Progression Bar */}
          <div className="my-6">
            <div className="flex items-center justify-between text-xs font-mono text-[#87938D] mb-2">
              <span>Risk: 1.0R (Stop-Loss)</span>
              <span className="text-[#00E59B]">Reward: 3.5R (Target 2)</span>
            </div>
            <div className="w-full h-3 rounded-full bg-white/10 overflow-hidden flex">
              <div className="w-[22%] bg-rose-500/80 h-full" title="Risk (1.0R)" />
              <div className="w-[78%] bg-gradient-to-r from-[#00E59B] to-[#39FFC0] h-full" title="Reward (3.5R)" />
            </div>
          </div>

          {/* Confluence Signatures Checklist */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-[#87938D] mb-3 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#00E59B]" />
              <span>{t.signals.confluenceFactors} ({signal.confluenceCount} Verified Confluences)</span>
            </h4>
            <div className="space-y-2">
              {(isKhmer ? signal.reasonsKh : signal.reasonsEn).map((reason, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-[#090F0C] border border-[#00E59B]/15 text-xs text-[#F5F8F6] flex items-center gap-2.5"
                >
                  <CheckCircle2 className="w-4 h-4 text-[#00E59B] shrink-0" />
                  <span>{reason}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

