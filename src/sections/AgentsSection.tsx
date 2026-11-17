import React, { useState } from 'react';
import { AI_AGENTS, AI_WORKFLOW_STEPS } from '../data/agents';
import { AgentCard } from '../components/AgentCard';
import { AIAgent } from '../types';
import { useLanguage } from '../hooks/useLanguage';
import {
  Bot,
  Play,
  RotateCcw,
  CheckCircle2,
  Cpu,
  Layers,
  Zap,
  Info,
  ShieldCheck,
  Activity,
} from 'lucide-react';

export const AgentsSection: React.FC = () => {
  const { isKhmer, t } = useLanguage();
  const [selectedAgent, setSelectedAgent] = useState<AIAgent>(AI_AGENTS[0]);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simProgress, setSimProgress] = useState<number>(0);

  const handleRunSimulation = () => {
    setIsSimulating(true);
    setSimProgress(1);

    const timer1 = setTimeout(() => setSimProgress(2), 500);
    const timer2 = setTimeout(() => setSimProgress(3), 1000);
    const timer3 = setTimeout(() => setSimProgress(4), 1500);
    const timer4 = setTimeout(() => setSimProgress(5), 2000);
    const timer5 = setTimeout(() => {
      setSimProgress(6);
      setIsSimulating(false);
    }, 2600);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      clearTimeout(timer5);
    };
  };

  return (
    <section id="agents" className="py-24 relative bg-[#090F0C]/85 overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/2 left-0 -translate-y-1/2 w-[500px] h-[500px] bg-[#00E59B]/5 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute top-1/3 right-0 w-[500px] h-[500px] bg-[#39FFC0]/5 rounded-full blur-[140px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#00E59B]/10 border border-[#00E59B]/30 text-[#00E59B] text-xs font-mono font-semibold uppercase tracking-wider mb-3">
            <Bot className="w-3.5 h-3.5 text-[#39FFC0]" />
            <span>{t.agents.badge}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#F5F8F6] tracking-tight">
            {t.agents.title}
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#87938D] leading-relaxed">
            {t.agents.subtitle}
          </p>
        </div>

        {/* 6 AI Agents Card Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {AI_AGENTS.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onSelect={() => setSelectedAgent(agent)}
            />
          ))}
        </div>

        {/* Interactive Neural Consensus Orchestrator Center */}
        <div className="mt-20 pt-16 border-t border-[#00E59B]/20">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-[#00E59B] font-bold block mb-1">
                Interactive Neural Pipeline
              </span>
              <h3 className="text-2xl sm:text-3xl font-bold text-[#F5F8F6]">
                {t.agents.workflowTitle}
              </h3>
              <p className="text-xs sm:text-sm text-[#87938D] mt-1.5 max-w-xl">
                {t.agents.workflowSubtitle}
              </p>
            </div>

            <button
              onClick={handleRunSimulation}
              disabled={isSimulating}
              className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-mono text-xs font-bold transition-all cursor-pointer shadow-lg ${
                isSimulating
                  ? 'bg-[#00E59B]/20 text-[#39FFC0] border border-[#00E59B]/40 cursor-not-allowed'
                  : 'bg-[#00E59B] text-[#050807] hover:bg-[#39FFC0] shadow-[0_0_20px_rgba(0,229,155,0.4)]'
              }`}
            >
              {isSimulating ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  <span>Streaming Synaptic Vectors...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Simulate Neural Consensus</span>
                </>
              )}
            </button>
          </div>

          {/* Stepper Pipeline Flow Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">
            {AI_WORKFLOW_STEPS.map((step) => {
              const isPassed = simProgress >= step.step;
              const isCurrent = simProgress === step.step && isSimulating;

              return (
                <div
                  key={step.step}
                  className={`relative p-4 rounded-2xl border flex flex-col justify-between transition-all duration-300 ${
                    isPassed
                      ? 'bg-[#00E59B]/10 border-[#00E59B]/50 shadow-[0_0_20px_rgba(0,229,155,0.2)]'
                      : isCurrent
                      ? 'bg-cyan-500/15 border-cyan-400 shadow-[0_0_20px_rgba(57,255,192,0.3)]'
                      : 'bg-[#050807] border-[#00E59B]/20'
                  }`}
                >
                  {/* Step Number & Time Badge */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span
                        className={`w-7 h-7 rounded-lg font-mono text-xs font-bold flex items-center justify-center border ${
                          isPassed
                            ? 'bg-[#00E59B] text-[#050807] border-[#00E59B]'
                            : isCurrent
                            ? 'bg-cyan-400 text-[#050807] border-cyan-400 animate-pulse'
                            : 'bg-[#00E59B]/15 text-[#39FFC0] border-[#00E59B]/30'
                        }`}
                      >
                        0{step.step}
                      </span>
                      <span className="text-[10px] font-mono text-[#87938D]">
                        {step.time}
                      </span>
                    </div>

                    {/* Title & Description */}
                    <h4 className="text-xs sm:text-sm font-bold text-[#F5F8F6] leading-tight">
                      {isKhmer ? step.titleKh : step.titleEn}
                    </h4>
                    <p className="text-[11px] text-[#87938D] mt-2 leading-relaxed">
                      {isKhmer ? step.descKh : step.descEn}
                    </p>
                  </div>

                  {/* Responsible Agent & Indicator */}
                  <div className="mt-4 pt-2.5 border-t border-[#00E59B]/15 flex items-center justify-between text-[10px] font-mono text-[#00E59B]">
                    <div className="flex items-center gap-1.5 truncate">
                      <Zap className="w-3 h-3 text-[#39FFC0] shrink-0" />
                      <span className="truncate">{step.agent}</span>
                    </div>
                    {isPassed && <CheckCircle2 className="w-3.5 h-3.5 text-[#00E59B] shrink-0" />}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Consensus Result Pill if simulation run */}
          {simProgress >= 6 && (
            <div className="mt-6 p-4 rounded-2xl bg-gradient-to-r from-[#00E59B]/20 via-[#39FFC0]/15 to-[#00B981]/20 border border-[#00E59B]/50 flex flex-wrap items-center justify-between gap-4 animate-fade-in shadow-xl">
              <div className="flex items-center gap-3">
                <ShieldCheck className="w-6 h-6 text-[#00E59B]" />
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-[#00E59B]/20 text-[#00E59B] border border-[#00E59B]/40">
                      DEMO ARCHITECTURE PREVIEW
                    </span>
                    <span className="text-xs font-mono font-bold text-[#F5F8F6]">
                      Multi-Agent 100-Point Confluence Scoring Gate
                    </span>
                  </div>
                  <span className="text-[11px] text-[#87938D]">
                    Institutional Gate: Score &ge; 75/100 required for actionable BUY/SELL &bull; Missing data scores 0 points &bull; Max 4 signals/day
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSimProgress(0)}
                className="px-3 py-1 rounded-lg bg-[#050807] border border-[#00E59B]/30 text-xs font-mono text-[#39FFC0] hover:bg-white/5 cursor-pointer flex items-center gap-1.5"
              >
                <RotateCcw className="w-3 h-3" />
                Reset
              </button>
            </div>
          )}

          {/* Backend Integration Architecture Note */}
          <div className="mt-8 p-4 rounded-2xl bg-[#050807] border border-[#00E59B]/20 flex items-center gap-3 text-xs text-[#87938D]">
            <Info className="w-4 h-4 text-[#00E59B] shrink-0" />
            <p className="leading-relaxed">
              <strong className="text-[#F5F8F6] font-semibold">Backend Integration Architecture:</strong>{' '}
              {t.agents.integrationNote} Real-time execution requires live streaming connectivity via Python FastAPI and MT5 broker bridge.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};
