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
      setTimeout(() => setScanStep(2), 600),
      setTimeout(() => setScanStep(3), 1200),
      setTimeout(() => setScanStep(4), 1800),
      setTimeout(() => setScanStep(5), 2400),
      setTimeout(() => {
        setScanStep(6);
        setIsScanning(false);
        setScanComplete(true);
      }, 3000),
    ];

    return () => timeouts.forEach(clearTimeout);
  };

  const steps = [
    { num: 1, labelEn: 'Ingesting L2 Order Book & Tick Stream', labelKh: 'ចាប់យកទិន្នន័យ Ticks & Order Book' },
    { num: 2, labelEn: 'Calculating EMA 20/50/200 & RSI Momentum Divergence', labelKh: 'គណនា EMA 20/50/200 & RSI Momentum' },
    { num: 3, labelEn: 'Identifying Bullish Order Block & 50% FVG C.E. Retest', labelKh: 'កំណត់ Order Block & ការបំពេញ FVG' },
    { num: 4, labelEn: 'Validating Mathematical Risk/Reward Gate (1:3.5)', labelKh: 'ត្រួតពិនិត្យសមាមាត្រហានិភ័យ R:R (1:3.5)' },
    { num: 5, labelEn: 'Multi-Agent Consensus Arbiter (6/6 Neural Votes)', labelKh: 'ការបោះឆ្នោតស្រុះស្រួលពហុភ្នាក់ងារ AI' },
    { num: 6, labelEn: 'Validated Signal Ready: BUY XAUUSD @ 2,724.50', labelKh: 'សញ្ញាបានអនុម័ត: BUY XAUUSD @ 2,724.50' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-10 bg-black/80 backdrop-blur-md animate-fade-in">
      {/* Modal Card */}
      <div className="relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-3xl bg-[#090F0C] border border-[#00E59B]/30 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.9),0_0_30px_rgba(0,229,155,0.15)] overflow-hidden">
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
              <Terminal className="w-4 h-4 text-[#00E59B]" />
              <span className="font-mono text-xs font-bold text-[#F5F8F6]">
                ZYROX AI TERMINAL ENGINE v4.0
              </span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#00E59B]/10 text-[#39FFC0] border border-[#00E59B]/20">
              {t.modal.demoTag}
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
            <h3 className="text-xl font-bold text-[#F5F8F6]">
              {t.modal.title}
            </h3>
            <p className="text-xs text-[#87938D] mt-1">
              {t.modal.subtitle}
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
                      ? 'bg-[#00E59B] text-[#050807] shadow-[0_0_10px_rgba(0,229,155,0.3)]'
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
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all cursor-pointer ${
                isScanning
                  ? 'bg-emerald-500/20 text-[#39FFC0] cursor-not-allowed'
                  : 'bg-[#00E59B] text-[#050807] hover:bg-[#39FFC0] shadow-[0_0_15px_rgba(0,229,155,0.4)]'
              }`}
            >
              {isScanning ? (
                <>
                  <Activity className="w-4 h-4 animate-spin" />
                  <span>{t.modal.scanning}</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>{t.modal.runScan}</span>
                </>
              )}
            </button>
          </div>

          {/* Real-time Agent Consensus Grid */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-[#87938D] mb-3 flex items-center justify-between">
              <span>Agent Consensus Matrix</span>
              <span className="text-[#00E59B]">6 Agents Active</span>
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {AI_AGENTS.map((agent) => {
                const isApproved = scanStep >= 5;
                return (
                  <div
                    key={agent.id}
                    className="p-3 rounded-xl bg-[#050807] border border-[#00E59B]/15 flex items-center justify-between"
                  >
                    <div>
                      <span className="text-xs font-bold text-[#F5F8F6] block truncate">
                        {isKhmer ? agent.nameKh : agent.nameEn}
                      </span>
                      <span className="text-[10px] font-mono text-[#87938D]">
                        Weight: 1.0 • Latency: {agent.latencyMs}ms
                      </span>
                    </div>

                    <div className="flex items-center">
                      {isScanning ? (
                        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                      ) : isApproved ? (
                        <CheckCircle2 className="w-4 h-4 text-[#00E59B]" />
                      ) : (
                        <span className="w-2 h-2 rounded-full bg-emerald-500/40" />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Stepper Pipeline */}
          <div className="space-y-2">
            <h4 className="text-xs font-mono uppercase tracking-wider text-[#87938D] mb-2">
              Consensus Execution Pipeline
            </h4>
            <div className="space-y-2">
              {steps.map((st) => {
                const isPassed = scanStep >= st.num;
                const isCurrent = scanStep === st.num && isScanning;

                return (
                  <div
                    key={st.num}
                    className={`flex items-center gap-3 p-3 rounded-xl border text-xs font-mono transition-all ${
                      isPassed
                        ? 'bg-[#00E59B]/10 border-[#00E59B]/30 text-[#F5F8F6]'
                        : isCurrent
                        ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-300'
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
            <div className="p-4 rounded-2xl bg-gradient-to-r from-[#00E59B]/15 via-[#00B981]/10 to-transparent border border-[#00E59B]/40 flex flex-wrap items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-widest text-[#39FFC0] block">
                  {t.modal.scanComplete}
                </span>
                <span className="text-sm font-bold text-[#F5F8F6] mt-0.5 block">
                  {activeSymbol} BUY @ 2,724.50 | SL: 2,717.00 | TP1: 2,739.50 | R:R 1:3.5
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-xl bg-[#00E59B] text-[#050807] text-xs font-mono font-bold shadow-[0_0_12px_rgba(0,229,155,0.4)]">
                  {t.modal.consensusScore}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 bg-[#050807] border-t border-[#00E59B]/15 flex items-center justify-between text-xs font-mono text-[#87938D]">
          <span>Institutional Simulated Sandbox Environment</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-[#F5F8F6] transition-colors cursor-pointer"
          >
            {t.modal.close}
          </button>
        </div>
      </div>
    </div>
  );
};

