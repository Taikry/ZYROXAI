import React, { useState } from 'react';
import { TECHNICAL_CONCEPTS } from '../data/concepts';
import { TechnicalConcept } from '../types';
import { useLanguage } from '../hooks/useLanguage';
import {
  Layers,
  Sparkles,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  Cpu,
  Bookmark,
  Shield,
} from 'lucide-react';

export const TechnicalSection: React.FC = () => {
  const { isKhmer, t } = useLanguage();
  const [activeCategory, setActiveCategory] = useState<'ALL' | 'SMC' | 'ICT' | 'CLASSIC' | 'STRUCTURE'>('ALL');
  const [selectedConcept, setSelectedConcept] = useState<TechnicalConcept>(TECHNICAL_CONCEPTS[2]); // Order Blocks by default

  const filteredConcepts = TECHNICAL_CONCEPTS.filter(
    (c) => activeCategory === 'ALL' || c.category === activeCategory
  );

  const getActionColor = (action: TechnicalConcept['action']) => {
    switch (action) {
      case 'ENTRY':
        return 'text-[#00E59B] bg-[#00E59B]/10 border-[#00E59B]/30';
      case 'TARGET':
        return 'text-[#39FFC0] bg-[#39FFC0]/10 border-[#39FFC0]/30';
      case 'INVALIDATION':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      case 'FILTER':
        return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
      default:
        return 'text-[#87938D] bg-white/5 border-white/10';
    }
  };

  return (
    <section id="analysis" className="py-20 relative bg-[#050807] overflow-hidden">
      {/* Background Dots */}
      <div className="absolute inset-0 bg-dots-cyber opacity-25 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#00E59B]/10 border border-[#00E59B]/30 text-[#00E59B] text-xs font-mono font-semibold uppercase tracking-wider mb-3">
            <Layers className="w-3.5 h-3.5 text-[#39FFC0]" />
            <span>{t.technical.badge}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#F5F8F6] tracking-tight">
            {t.technical.title}
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#87938D] leading-relaxed">
            {t.technical.subtitle}
          </p>
        </div>

        {/* Category Navigation Pills */}
        <div className="flex items-center justify-center gap-2 mb-10 flex-wrap">
          {[
            { id: 'ALL', label: t.technical.tabsAll },
            { id: 'SMC', label: t.technical.tabsSmc },
            { id: 'ICT', label: t.technical.tabsIct },
            { id: 'STRUCTURE', label: isKhmer ? 'រចនាសម្ព័ន្ធទីផ្សារ' : 'Market Structure' },
            { id: 'CLASSIC', label: t.technical.tabsClassic },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveCategory(tab.id as any)}
              className={`px-4 py-2 rounded-xl text-xs font-mono font-semibold transition-all cursor-pointer ${
                activeCategory === tab.id
                  ? 'bg-[#00E59B] text-[#050807] shadow-[0_0_15px_rgba(0,229,155,0.35)]'
                  : 'bg-[#090F0C] text-[#87938D] hover:text-[#F5F8F6] border border-[#00E59B]/15'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Layout: Interactive Concept Explorer Grid + Active Inspector Pane */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Grid: Clickable Concepts */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            {filteredConcepts.map((concept) => {
              const isSelected = selectedConcept.id === concept.id;
              return (
                <div
                  key={concept.id}
                  onClick={() => setSelectedConcept(concept)}
                  className={`p-4 rounded-2xl border transition-all duration-300 cursor-pointer flex flex-col justify-between ${
                    isSelected
                      ? 'bg-[#090F0C] border-[#00E59B] shadow-[0_0_20px_rgba(0,229,155,0.25)]'
                      : 'bg-[#090F0C]/60 border-[#00E59B]/15 hover:border-[#00E59B]/35 hover:bg-[#090F0C]'
                  }`}
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-[#00E59B]/15 text-[#39FFC0] border border-[#00E59B]/30">
                        {concept.abbr}
                      </span>
                      <span
                        className={`text-[9px] font-mono uppercase px-2 py-0.5 rounded-full border ${getActionColor(
                          concept.action
                        )}`}
                      >
                        {concept.action}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-[#F5F8F6] group-hover:text-[#39FFC0] transition-colors">
                      {isKhmer ? concept.titleKh : concept.titleEn}
                    </h4>

                    <p className="text-xs text-[#87938D] mt-1.5 line-clamp-2 leading-relaxed">
                      {isKhmer ? concept.descKh : concept.descEn}
                    </p>
                  </div>

                  <div className="mt-3 pt-2 border-t border-[#00E59B]/10 flex items-center justify-between text-[10px] font-mono text-[#00E59B]">
                    <span>{concept.badge}</span>
                    <span>Inspect →</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Inspector: Deep Technical Breakdown */}
          <div className="lg:col-span-5 p-6 rounded-3xl bg-[#090F0C] border border-[#00E59B]/30 shadow-2xl space-y-6">
            {/* Inspector Header */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono font-bold px-3 py-1 rounded-xl bg-[#00E59B] text-[#050807]">
                  {selectedConcept.abbr} CONCEPT
                </span>
                <span
                  className={`text-[10px] font-mono uppercase px-2.5 py-1 rounded-full border ${getActionColor(
                    selectedConcept.action
                  )}`}
                >
                  {selectedConcept.action} ROLE
                </span>
              </div>

              <h3 className="text-xl sm:text-2xl font-bold text-[#F5F8F6]">
                {isKhmer ? selectedConcept.titleKh : selectedConcept.titleEn}
              </h3>
              <p className="text-xs sm:text-sm text-[#87938D] mt-2 leading-relaxed">
                {isKhmer ? selectedConcept.descKh : selectedConcept.descEn}
              </p>
            </div>

            {/* Algorithmic Core Rule Box */}
            <div className="p-4 rounded-2xl bg-[#050807] border border-[#00E59B]/25">
              <span className="text-[10px] font-mono uppercase tracking-wider text-[#39FFC0] block mb-1">
                {t.technical.coreRule}
              </span>
              <p className="text-xs sm:text-sm font-mono text-[#F5F8F6] leading-relaxed">
                {isKhmer ? selectedConcept.ruleKh : selectedConcept.ruleEn}
              </p>
            </div>

            {/* Interactive Confluence Checklist */}
            <div>
              <span className="text-xs font-mono uppercase tracking-wider text-[#87938D] block mb-3">
                {isKhmer ? 'លក្ខខណ្ឌផ្ទៀងផ្ទាត់ស្វ័យប្រវត្ត' : 'Automated Confluence Criteria'}
              </span>
              <div className="space-y-2 text-xs font-mono">
                {[
                  isKhmer ? 'ការបញ្ជាក់ទម្រង់ទៀន (Solid Candle Body Close)' : 'Solid Candle Body Close Confirmation',
                  isKhmer ? 'ការតម្រឹមជាមួយ Timeframe ធំ (Higher TF Bias)' : 'Higher Timeframe Directional Alignment',
                  isKhmer ? 'ការច្រោះព័ត៌មានម៉ាក្រូសេដ្ឋកិច្ច (News Blackout Filter)' : 'High-Impact Economic News Gate Passed',
                  isKhmer ? 'សមាមាត្រហានិភ័យ R:R លើសពី 1:2.0' : 'Mathematical R:R Ratio >= 1:2.0 Enforced',
                ].map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2.5 p-2 rounded-xl bg-white/5 border border-white/5 text-[#F5F8F6]"
                  >
                    <CheckCircle2 className="w-4 h-4 text-[#00E59B] shrink-0" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Live Visual Detection Simulation Card */}
            <div className="p-4 rounded-2xl bg-gradient-to-tr from-[#00E59B]/10 to-transparent border border-[#00E59B]/30 flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono text-[#00E59B] uppercase block">
                  AI Algorithmic Scanner
                </span>
                <span className="text-xs font-bold text-[#F5F8F6] mt-0.5 block">
                  Active in ZYROX Multi-Agent Loop
                </span>
              </div>
              <span className="px-2.5 py-1 rounded-lg bg-[#00E59B]/20 text-[#39FFC0] text-xs font-mono font-bold">
                Live Gated
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

