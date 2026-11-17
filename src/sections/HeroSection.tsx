import React from 'react';
import { TradingChart } from '../components/TradingChart';
import { MarketTicker } from '../components/MarketTicker';
import { NeuralOrb3D } from '../components/NeuralOrb3D';
import { MagneticButton } from '../components/MagneticButton';
import { useRealtimeMarkets } from '../hooks/useRealtimeMarkets';
import { useLanguage } from '../hooks/useLanguage';
import {
  Terminal,
  Compass,
  Bot,
  Shield,
  Activity,
  Layers,
  Zap,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

interface HeroSectionProps {
  onLaunchTerminal: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onLaunchTerminal }) => {
  const { isKhmer, t } = useLanguage();
  const { markets } = useRealtimeMarkets();
  const primaryAsset = markets.find((m) => m.symbol === 'XAUUSD') || markets[0];

  const scrollTo = (id: string) => {
    const el = document.querySelector(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section id="hero" className="relative pt-24 pb-16 md:pt-36 md:pb-24 overflow-hidden">
      {/* 3D Interactive Neural Orb - Ambient Center Position */}
      <div className="absolute top-28 md:top-20 left-1/2 -translate-x-1/2 -z-0 opacity-40 md:opacity-70 pointer-events-none filter blur-[0.5px]">
        <NeuralOrb3D size={440} />
      </div>

      {/* Radiant Glowing Background Core */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] md:w-[900px] md:h-[450px] bg-gradient-to-b from-[#00E59B]/20 via-[#00B981]/5 to-transparent rounded-full blur-[130px] pointer-events-none -z-10" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Top Announcement Badge with Animated Soundwave Spectrum */}
        <div className="flex justify-center mb-6">
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#090F0C]/90 border border-[#00E59B]/30 shadow-[0_0_20px_rgba(0,229,155,0.2)] text-xs font-mono text-[#F5F8F6] backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-[#00E59B] animate-ping" />
            <span className="text-[#39FFC0] font-bold tracking-wide">
              {isKhmer ? 'ប្រព័ន្ធ AI ដំណើរការ' : 'SYSTEM AI ONLINE'}
            </span>
            <span className="text-white/20">|</span>
            <div className="hidden sm:flex items-center gap-0.5 h-3">
              <span className="w-0.5 bg-[#00E59B] h-2 animate-pulse" />
              <span className="w-0.5 bg-[#39FFC0] h-3 animate-pulse" style={{ animationDelay: '0.2s' }} />
              <span className="w-0.5 bg-[#00E59B] h-1.5 animate-pulse" style={{ animationDelay: '0.4s' }} />
              <span className="w-0.5 bg-[#39FFC0] h-2.5 animate-pulse" style={{ animationDelay: '0.1s' }} />
            </div>
            <span className="text-[#87938D] hidden sm:inline">14-Agent Consensus Fleet Active</span>
          </div>
        </div>

        {/* Cinematic Main Headline */}
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-[#F5F8F6] leading-[1.08]">
            <span>{t.hero.titlePart1}</span>{' '}
            <span className="text-gradient-emerald block mt-1 drop-shadow-[0_0_35px_rgba(0,229,155,0.35)]">
              {t.hero.titlePart2}
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-lg md:text-xl text-[#87938D] max-w-2xl mx-auto leading-relaxed">
            {t.hero.subtitle}
          </p>

          {/* High-Performance CTA Buttons with Dedicated SYSTEM AI Button */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            {/* CTA 1: System AI (Primary Highlight) */}
            <MagneticButton
              variant="primary"
              size="lg"
              onClick={onLaunchTerminal}
              className="bg-gradient-to-r from-[#00E59B] to-[#39FFC0] text-[#050807] font-extrabold shadow-[0_0_30px_rgba(0,229,155,0.45)] border-0 cursor-pointer"
            >
              <Bot className="w-5 h-5 text-[#050807] animate-pulse" />
              <span className="tracking-wide">{isKhmer ? 'ប្រព័ន្ធ AI (System AI)' : 'System AI Engine'}</span>
              <Sparkles className="w-4 h-4 text-[#050807]" />
            </MagneticButton>

            {/* CTA 2: Launch Full Web Terminal */}
            <a
              href="/dashboard/"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-[#090F0C] hover:bg-[#00E59B]/10 text-sm font-mono font-bold text-[#F5F8F6] hover:text-[#39FFC0] border border-[#00E59B]/30 hover:border-[#00E59B] shadow-lg transition-all group cursor-pointer"
            >
              <Terminal className="w-4 h-4 text-[#00E59B] group-hover:rotate-12 transition-transform" />
              <span>{isKhmer ? 'ផ្ទាំង Web Terminal' : 'Live Terminal'}</span>
              <ArrowRight className="w-4 h-4 text-[#87938D] group-hover:translate-x-1 group-hover:text-[#39FFC0] transition-all" />
            </a>

            {/* CTA 3: 14 AI Agents Fleet */}
            <MagneticButton
              variant="secondary"
              size="lg"
              onClick={() => scrollTo('#agents')}
            >
              <Compass className="w-4 h-4 text-[#00E59B]" />
              <span>{isKhmer ? 'ភ្នាក់ងារ AI ទាំង ១៤' : '14 AI Agents'}</span>
            </MagneticButton>
          </div>

          {/* Live Data Assurance Note */}
          <p className="text-[11px] font-mono text-[#87938D] mt-4 opacity-80">
            {isKhmer
              ? '● ទិន្នន័យទីផ្សារផ្ទាល់ Real-Time ពី OANDA v20, Binance Spot & MT5 Bridge'
              : '● Live Institutional Feeds from OANDA v20, Binance Spot & Windows MT5 Bridge'}
          </p>
        </div>

        {/* Visual Hero Dashboard Centerpiece with Floating Glass Cards */}
        <div className="relative mt-12 md:mt-16 max-w-5xl mx-auto">
          {/* Subtle Ambient Backing Glow */}
          <div className="absolute -inset-2 rounded-3xl bg-gradient-to-r from-[#00E59B]/25 via-[#39FFC0]/20 to-[#00B981]/25 blur-2xl opacity-70" />

          {/* Main Chart Component with Live Real-Time Data */}
          <TradingChart asset={primaryAsset} className="relative z-10" />

          {/* Floating AI Intelligence Card 1 (Top Left) */}
          <div className="hidden lg:flex absolute -top-8 -left-12 z-20 items-center gap-3 p-3.5 rounded-2xl bg-[#090F0C]/90 border border-[#00E59B]/35 backdrop-blur-xl shadow-[0_15px_35px_rgba(0,0,0,0.8),0_0_20px_rgba(0,229,155,0.15)] animate-float-slow">
            <div className="w-10 h-10 rounded-xl bg-[#00E59B]/15 border border-[#00E59B]/40 flex items-center justify-center">
              <Layers className="w-5 h-5 text-[#00E59B]" />
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase text-[#39FFC0] block font-semibold">
                ICT Detection Active
              </span>
              <span className="text-xs font-bold text-[#F5F8F6]">
                15M Bullish Order Block + FVG
              </span>
            </div>
          </div>

          {/* Floating AI Intelligence Card 2 (Bottom Right) */}
          <div
            className="hidden lg:flex absolute -bottom-8 -right-10 z-20 items-center gap-3 p-3.5 rounded-2xl bg-[#090F0C]/90 border border-[#00E59B]/35 backdrop-blur-xl shadow-[0_15px_35px_rgba(0,0,0,0.8),0_0_20px_rgba(0,229,155,0.15)] animate-float-slow"
            style={{ animationDelay: '2.5s' }}
          >
            <div className="w-10 h-10 rounded-xl bg-[#39FFC0]/15 border border-[#39FFC0]/40 flex items-center justify-center">
              <Shield className="w-5 h-5 text-[#39FFC0]" />
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase text-[#00E59B] block font-semibold">
                Risk Gatekeeper Verified
              </span>
              <span className="text-xs font-bold text-[#F5F8F6]">
                R:R 1:3.5 • Stop Loss Protected
              </span>
            </div>
          </div>

          {/* Mobile/Tablet Compact Intelligence Badges */}
          <div className="flex lg:hidden flex-wrap items-center justify-center gap-2.5 mt-3 relative z-20">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#090F0C]/90 border border-[#00E59B]/30 text-[11px] text-[#F5F8F6] shadow-sm">
              <Layers className="w-3.5 h-3.5 text-[#00E59B]" />
              <span>ICT 15M Bullish OB + FVG</span>
            </div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#090F0C]/90 border border-[#39FFC0]/30 text-[11px] text-[#F5F8F6] shadow-sm">
              <Shield className="w-3.5 h-3.5 text-[#39FFC0]" />
              <span>Risk Verified: R:R 1:3.5</span>
            </div>
          </div>
        </div>

        {/* Quick Institutional Telemetry Stats Grid */}
        <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {[
            { val: '14 Neural Agents', label: isKhmer ? 'ភ្នាក់ងារ AI ឯកទេស' : '14 Specialized Agents', icon: <Bot className="w-4 h-4 text-[#00E59B]" /> },
            { val: '21+ Liquid Assets', label: t.hero.statsMarkets, icon: <Activity className="w-4 h-4 text-[#39FFC0]" /> },
            { val: '< 50ms Processing', label: t.hero.statsLatency, icon: <Zap className="w-4 h-4 text-emerald-400" /> },
            { val: '80% Gate Consensus', label: t.hero.statsConsensus, icon: <Shield className="w-4 h-4 text-teal-400" /> },
          ].map((item, idx) => (
            <div
              key={idx}
              className="p-4 rounded-2xl bg-[#090F0C]/80 border border-[#00E59B]/20 text-center flex flex-col items-center justify-center backdrop-blur-md shadow-lg hover:border-[#00E59B]/40 transition-colors"
            >
              <div className="mb-1.5">{item.icon}</div>
              <span className="font-mono text-base md:text-lg font-bold text-[#F5F8F6]">
                {item.val}
              </span>
              <span className="text-[11px] text-[#87938D] mt-0.5">
                {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Animated Continuous Live Market Ticker */}
      <div className="mt-16">
        <MarketTicker />
      </div>
    </section>
  );
};
