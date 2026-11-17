import React from 'react';
import { ARCHITECTURE_LAYERS } from '../data/architecture';
import { useLanguage } from '../hooks/useLanguage';
import {
  Server,
  Layout,
  Cpu,
  BrainCircuit,
  Radio,
  Database,
  Shield,
  Cloud,
  Send,
  Lock,
  ArrowDown,
  Sparkles,
} from 'lucide-react';

export const TechnologySection: React.FC = () => {
  const { isKhmer, t } = useLanguage();

  const renderIcon = (iconName: string) => {
    const props = { className: "w-5 h-5 text-[#00E59B]" };
    switch (iconName) {
      case 'Layout': return <Layout {...props} />;
      case 'Server': return <Server {...props} />;
      case 'Cpu': return <Cpu {...props} />;
      case 'BrainCircuit': return <BrainCircuit {...props} />;
      case 'RadioReceiver': return <Radio {...props} />;
      case 'Database': return <Database {...props} />;
      default: return <Server {...props} />;
    }
  };

  return (
    <section id="technology" className="py-20 relative bg-[#090F0C]/80 overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-grid-cyber opacity-20 pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#00E59B]/10 border border-[#00E59B]/30 text-[#00E59B] text-xs font-mono font-semibold uppercase tracking-wider mb-3">
            <Cpu className="w-3.5 h-3.5 text-[#39FFC0]" />
            <span>{t.architecture.badge}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#F5F8F6] tracking-tight">
            {t.architecture.title}
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#87938D] leading-relaxed">
            {t.architecture.subtitle}
          </p>
        </div>

        {/* 6-Tier Pipeline Flow */}
        <div className="max-w-4xl mx-auto space-y-4">
          {ARCHITECTURE_LAYERS.map((layer, idx) => (
            <React.Fragment key={layer.step}>
              <div className="p-6 rounded-2xl bg-[#050807] border border-[#00E59B]/20 hover:border-[#00E59B]/50 transition-all duration-300 flex flex-col md:flex-row md:items-center justify-between gap-6 group shadow-lg">
                <div className="flex items-start md:items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-[#090F0C] border border-[#00E59B]/30 flex items-center justify-center p-3 group-hover:border-[#00E59B] group-hover:shadow-[0_0_15px_rgba(0,229,155,0.3)] transition-all">
                    {renderIcon(layer.icon)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-[#00E59B]">
                        LAYER 0{layer.step}
                      </span>
                      <span className="text-white/20">•</span>
                      <h3 className="text-base sm:text-lg font-bold text-[#F5F8F6] group-hover:text-[#39FFC0] transition-colors">
                        {isKhmer ? layer.titleKh : layer.titleEn}
                      </h3>
                    </div>
                    <p className="text-xs text-[#87938D] mt-1">
                      {isKhmer ? layer.roleKh : layer.roleEn}
                    </p>
                    <p className="text-[11px] font-mono text-[#39FFC0]/90 mt-1">
                      {isKhmer ? layer.detailKh : layer.detailEn}
                    </p>
                  </div>
                </div>

                <div className="shrink-0 text-left md:text-right">
                  <span className="inline-block px-3 py-1 rounded-lg bg-[#090F0C] border border-[#00E59B]/25 text-xs font-mono font-semibold text-[#00E59B]">
                    {layer.tech}
                  </span>
                </div>
              </div>

              {idx < ARCHITECTURE_LAYERS.length - 1 && (
                <div className="flex justify-center py-0.5">
                  <div className="w-8 h-8 rounded-full bg-[#050807] border border-[#00E59B]/25 flex items-center justify-center text-[#00E59B]">
                    <ArrowDown className="w-4 h-4 animate-bounce" style={{ animationDuration: '3s' }} />
                  </div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Security & Deployment Cards */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {/* Cloud Ready */}
          <div className="p-5 rounded-2xl bg-[#050807] border border-[#00E59B]/20 flex flex-col justify-between">
            <div className="flex items-center gap-2 mb-2 text-[#00E59B]">
              <Cloud className="w-4 h-4" />
              <span className="text-xs font-mono font-bold uppercase">Cloud Deployment</span>
            </div>
            <p className="text-xs text-[#87938D] leading-relaxed">
              Configured for Docker containerization on Render with auto-scaling, Singapore region low latency, and 24/7 background worker health checks.
            </p>
          </div>

          {/* Telegram Dispatch */}
          <div className="p-5 rounded-2xl bg-[#050807] border border-[#00E59B]/20 flex flex-col justify-between">
            <div className="flex items-center gap-2 mb-2 text-[#39FFC0]">
              <Send className="w-4 h-4" />
              <span className="text-xs font-mono font-bold uppercase">Telegram Gateway</span>
            </div>
            <p className="text-xs text-[#87938D] leading-relaxed">
              Automated asynchronous webhook notifications with chart snapshots and bilingual trade setups delivered in milliseconds.
            </p>
          </div>

          {/* Zero Credential Exposure */}
          <div className="p-5 rounded-2xl bg-[#050807] border border-[#00E59B]/20 flex flex-col justify-between">
            <div className="flex items-center gap-2 mb-2 text-emerald-400">
              <Lock className="w-4 h-4" />
              <span className="text-xs font-mono font-bold uppercase">Enterprise Security</span>
            </div>
            <p className="text-xs text-[#87938D] leading-relaxed">
              Strict environment variable isolation. Zero private API tokens or broker credentials exposed to client-side bundles.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

