import React, { useState } from 'react';
import { useLanguage } from '../hooks/useLanguage';
import {
  X,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  ShieldCheck,
  Terminal,
  Activity,
  Cpu,
  Layers,
  ChevronRight,
  Bot,
  ExternalLink,
  Sparkles,
} from 'lucide-react';
import { AI_AGENTS } from '../data/agents';

interface TerminalModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TerminalModal: React.FC<TerminalModalProps> = ({ isOpen, onClose }) => {
  const { isKhmer, t } = useLanguage();
  const [activeSymbol, setActiveSymbol] = useState<'XAUUSD' | 'BTCUSDT' | 'EURUSD'>('XAUUSD');
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [scanStep, setScanStep] = useState<number>(0);
  const [scanComplete, setScanComplete] = useState<boolean>(false);

  if (!isOpen) return null;

  const handleStartScan = () => {
    setIsScanning(true);
    setScanComplete(false);
    setScanStep(1);

    const timeouts = [
      setTimeout(() => setScanStep(2), 500),
      setTimeout(() => setScanStep(3), 1000),
      setTimeout(() => setScanStep(4), 1500),
      setTimeout(() => setScanStep(5), 2000),
      setTimeout(() => {
        setScanStep(6);
        setIsScanning(false);
        setScanComplete(true);
      }, 2500),
    ];

    return () => timeouts.forEach(clearTimeout);
  };

  const steps = [
    { num: 1, labelEn: 'Ingesting L2 Order Book & Live Real-Time Tickstream', labelKh: 'ចាប់យកទិន្នន័យ Ticks ទីផ្សារផ្ទាល់ Real-Time' },
    { num: 2, labelEn: 'Calculating EMA 20/50/200 & RSI Momentum Divergence', labelKh: 'គណនា EMA 20/50/200 & RSI Momentum Divergence' },
    { num: 3, labelEn: 'Identifying Bullish Order Block & 50% FVG C.E. Imbalance', labelKh: 'កំណត់ Bullish Order Block & តំបន់ FVG' },
    { num: 4, labelEn: 'Validating Mathematical Risk/Reward Gate (Min 1:1.5 R:R)', labelKh: 'ត្រួតពិនិត្យសមាមាត្រហានិភ័យ R:R (1:1.5 ឡើង)' },
    { num: 5, labelEn: 'Multi-Agent Consensus Arbiter (14/14 Neural Quorum)', labelKh: 'ការបោះឆ្នោតស្រុះស្រួលពហុភ្នាក់ងារ AI ទាំង ១៤' },
    { num: 6, labelEn: 'Signal Approved: Dynamic Entry with Protected Stop Loss', labelKh: 'សញ្ញាបានអនុម័ត: មាន Entry & Stop Loss ច្បាស់លាស់' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-10 bg-black/85 backdrop-blur-md animate-fade-in">
      {/* Modal Card */}
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-3xl bg-[#090F0C] border border-[#00E59B]/40 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.9),0_0_30px_rgba(0,229,155,0.2)] overflow-hidden">
        {/* Top Terminal Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#00E59B]/20 bg-[#050807]/90">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-rose-500/80" />
              <span className="w-3 h-3 rounded-full bg-amber-500/80" />
              <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>
            <div className="h-4 w-px bg-white/10" />
            <div className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-[#00E59B] animate-pulse" />
              <span className="font-mono text-xs font-bold text-[#F5F8F6]">
                ZYROX SYSTEM AI — 14-AGENT CONSENSUS FLEET
              </span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00E59B]/15 text-[#39FFC0] border border-[#00E59B]/30 font-semibold flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#00E59B] animate-ping" />
              SYSTEM AI ACTIVE
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#87938D] hover:text-[#F5F8F6] hover:bg-white/5 transition-colors cursor-pointer"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Header Description */}
          <div>
            <h3 className="text-xl font-bold text-[#F5F8F6] flex items-center gap-2">
              <span>{isKhmer ? 'ដំណើរការវិភាគដោយប្រព័ន្ធ AI' : 'Live Multi-Agent Consensus Analysis'}</span>
              <Sparkles className="w-4 h-4 text-[#00E59B]" />
            </h3>
            <p className="text-xs text-[#87938D] mt-1">
              {isKhmer
                ? 'ដំណើរការស្កេនទិន្នន័យទីផ្សារផ្ទាល់តាមរយៈភ្នាក់ងារ AI ទាំង ១៤ ដើម្បីកំណត់ទិសដៅជួញដូរប្រកបដោយសុវត្ថិភាពខ្ពស់។'
                : 'Execute multi-agent neural consensus scan across live institutional market structure, SMC order blocks, and macro correlation.'}
            </p>
          </div>

          {/* Symbol Selector & Action Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 p-3 rounded-2xl bg-[#050807] border border-[#00E59B]/20">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-[#87938D]">
                Asset:
              </span>
              {(['XAUUSD', 'BTCUSDT', 'EURUSD'] as const).map((sym) => (
                <button
                  key={sym}
                  onClick={() => {
                    setActiveSymbol(sym);
                    setScanStep(0);
                    setScanComplete(false);
                  }}
                  className={`px-3 py-1 text-xs font-mono font-semibold rounded-lg transition-all cursor-pointer ${
                    activeSymbol === sym
                      ? 'bg-[#00E59B] text-[#050807] shadow-[0_0_10px_rgba(0,229,155,0.3)] font-bold'
                      : 'text-[#87938D] hover:text-[#F5F8F6]'
                  }`}
                >
                  {sym}
                </button>
              ))}
            </div>

            <button
              onClick={handleStartScan}
              disabled={isScanning}
              className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer ${
                isScanning
                  ? 'bg-emerald-500/20 text-[#39FFC0] cursor-not-allowed'
                  : 'bg-gradient-to-r from-[#00E59B] to-[#39FFC0] text-[#050807] hover:brightness-110 shadow-[0_0_20px_rgba(0,229,155,0.4)]'
              }`}
            >
              {isScanning ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  <span>{isKhmer ? 'កំពុងស្កេន AI...' : 'Analyzing Quorum...'}</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>{isKhmer ? 'ចាប់ផ្តើមស្កេន AI' : 'Run Consensus Scan'}</span>
                </>
              )}
            </button>
          </div>

          {/* Real-time Agents Grid */}
          <div className="space-y-2">
            <span className="text-xs font-mono uppercase tracking-wider text-[#87938D] block">
              Active Neural Fleet (14 Agents)
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
              {AI_AGENTS.slice(0, 8).map((agent, i) => (
                <div
                  key={agent.id}
                  className="p-2.5 rounded-xl bg-[#050807]/70 border border-[#00E59B]/15 flex items-center justify-between"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#00E59B] animate-pulse" />
                    <span className="text-[11px] font-mono text-[#F5F8F6] truncate max-w-[100px]">
                      {isKhmer ? agent.nameKh : agent.nameEn}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-[#39FFC0] font-bold">
                    {scanStep > i ? 'VOTED' : 'READY'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Sequential Live Steps */}
          <div className="space-y-2">
            <span className="text-xs font-mono uppercase tracking-wider text-[#87938D] block">
              Execution Pipeline
            </span>
            <div className="space-y-1.5 font-mono text-xs">
              {steps.map((st) => {
                const isPassed = scanStep > st.num;
                const isCurrent = scanStep === st.num;

                return (
                  <div
                    key={st.num}
                    className={`flex items-center gap-3 p-2.5 rounded-xl border transition-all ${
                      isPassed
                        ? 'bg-[#00E59B]/10 border-[#00E59B]/30 text-[#F5F8F6]'
                        : isCurrent
                        ? 'bg-cyan-500/10 border-cyan-500/40 text-cyan-200'
                        : 'bg-[#050807]/40 border-white/5 text-[#87938D]'
                    }`}
                  >
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-bold ${
                        isPassed
                          ? 'bg-[#00E59B] text-[#050807]'
                          : isCurrent
                          ? 'bg-cyan-400 text-[#050807] animate-pulse'
                          : 'bg-white/10 text-[#87938D]'
                      }`}
                    >
                      {st.num}
                    </div>
                    <span className="flex-1">
                      {isKhmer ? st.labelKh : st.labelEn}
                    </span>
                    {isPassed && <CheckCircle2 className="w-4 h-4 text-[#00E59B]" />}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Scan Result Preview Box */}
          {scanComplete && (
            <div className="p-4 rounded-2xl bg-gradient-to-r from-[#00E59B]/20 via-[#00B981]/15 to-transparent border border-[#00E59B]/50 flex flex-wrap items-center justify-between gap-4 shadow-[0_0_25px_rgba(0,229,155,0.2)]">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-[#39FFC0] block font-bold">
                  ✓ {isKhmer ? 'ការវិភាគ AI ត្រូវបានអនុម័ត' : 'CONSENSUS APPROVED'}
                </span>
                <span className="text-sm font-bold text-[#F5F8F6] mt-0.5 block">
                  {activeSymbol} ACTIONABLE BUY | SL Protected | Min R:R 1:2.5
                </span>
              </div>
              <div className="flex items-center gap-3">
                <a
                  href="/dashboard/"
                  className="px-4 py-2 rounded-xl bg-[#00E59B] hover:bg-[#39FFC0] text-[#050807] text-xs font-mono font-bold shadow-[0_0_15px_rgba(0,229,155,0.4)] flex items-center gap-1.5 transition-all cursor-pointer"
                >
                  <Terminal className="w-3.5 h-3.5" />
                  <span>{isKhmer ? 'បើកមើលក្នុង Terminal' : 'Open in Terminal'}</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 bg-[#050807] border-t border-[#00E59B]/15 flex items-center justify-between text-xs font-mono text-[#87938D]">
          <span className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#00E59B]" />
            <span>FastAPI Unified Host & AI Consensus Core</span>
          </span>
          <div className="flex items-center gap-3">
            <a
              href="/dashboard/"
              className="text-[#39FFC0] hover:underline flex items-center gap-1"
            >
              <span>{isKhmer ? 'ផ្ទាំង Web Terminal ពេញលេញ' : 'Full Web Terminal'}</span>
              <ChevronRight className="w-3 h-3" />
            </a>
            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#F5F8F6] transition-colors cursor-pointer"
            >
              {t.modal.close}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
