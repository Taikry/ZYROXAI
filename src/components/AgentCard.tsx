import React from 'react';
import { AIAgent } from '../types';
import { useLanguage } from '../hooks/useLanguage';
import {
  TrendingUp,
  BarChart3,
  Layers,
  ShieldAlert,
  CheckCheck,
  Radio,
  Zap,
  Activity,
} from 'lucide-react';

interface AgentCardProps {
  agent: AIAgent;
  onSelect?: () => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({ agent, onSelect }) => {
  const { isKhmer } = useLanguage();

  // Dynamic Lucide icon mapper
  const renderIcon = () => {
    switch (agent.icon) {
      case 'TrendingUp':
        return <TrendingUp className="w-5 h-5 text-[#00E59B]" />;
      case 'BarChart3':
        return <BarChart3 className="w-5 h-5 text-[#39FFC0]" />;
      case 'Layers':
        return <Layers className="w-5 h-5 text-[#00E59B]" />;
      case 'ShieldAlert':
        return <ShieldAlert className="w-5 h-5 text-emerald-400" />;
      case 'CheckCheck':
        return <CheckCheck className="w-5 h-5 text-[#39FFC0]" />;
      case 'Radio':
        return <Radio className="w-5 h-5 text-teal-400" />;
      default:
        return <Activity className="w-5 h-5 text-[#00E59B]" />;
    }
  };

  const getStatusStyles = () => {
    switch (agent.status) {
      case 'ACTIVE':
        return {
          pill: 'bg-emerald-500/10 text-[#00E59B] border-emerald-500/30',
          dot: 'bg-[#00E59B]',
          labelEn: 'ONLINE & MONITORING',
          labelKh: 'ដំណើរការ & តាមដាន',
        };
      case 'PROCESSING':
        return {
          pill: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
          dot: 'bg-cyan-400',
          labelEn: 'ORDER FLOW SCANNING',
          labelKh: 'កំពុងស្កេន ORDER FLOW',
        };
      case 'CONSENSUS':
        return {
          pill: 'bg-emerald-400/15 text-[#39FFC0] border-emerald-400/40',
          dot: 'bg-[#39FFC0]',
          labelEn: 'VOTING CONFLUENCE',
          labelKh: 'កំពុងបោះឆ្នោតស្រុះស្រួល',
        };
      default:
        return {
          pill: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
          dot: 'bg-slate-400',
          labelEn: 'CALIBRATING',
          labelKh: 'ត្រៀមលក្ខណៈ',
        };
    }
  };

  const statusStyle = getStatusStyles();
  const capabilities = isKhmer ? agent.capabilitiesKh : agent.capabilitiesEn;

  return (
    <div
      onClick={onSelect}
      className="glass-card group relative flex flex-col justify-between p-6 rounded-2xl cursor-pointer hover:border-[#00E59B]/40 hover:shadow-[0_10px_35px_-10px_rgba(0,229,155,0.2)] transition-all duration-300"
    >
      {/* Top Bar: Icon + Status Pill */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="w-12 h-12 rounded-xl bg-[#050807] border border-[#00E59B]/30 flex items-center justify-center p-2.5 shadow-inner group-hover:border-[#00E59B] group-hover:shadow-[0_0_15px_rgba(0,229,155,0.3)] transition-all">
            {renderIcon()}
          </div>

          <div
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold uppercase border ${statusStyle.pill}`}
          >
            <span className={`w-2 h-2 rounded-full ${statusStyle.dot} animate-pulse`} />
            <span>{isKhmer ? statusStyle.labelKh : statusStyle.labelEn}</span>
          </div>
        </div>

        {/* Agent Name & Title */}
        <h4 className="text-lg font-bold text-[#F5F8F6] group-hover:text-[#39FFC0] transition-colors leading-snug">
          {isKhmer ? agent.nameKh : agent.nameEn}
        </h4>
        <p className="text-xs font-mono text-[#00E59B] mt-1 tracking-wider uppercase">
          {isKhmer ? agent.roleKh : agent.roleEn}
        </p>

        {/* Description */}
        <p className="text-xs text-[#87938D] mt-3 leading-relaxed">
          {isKhmer ? agent.descriptionKh : agent.descriptionEn}
        </p>
      </div>

      {/* Middle: Capability Tags */}
      <div className="my-5">
        <span className="text-[10px] uppercase font-mono tracking-wider text-[#87938D] block mb-2">
          {isKhmer ? 'សមត្ថភាពស្នូល' : 'Core Capabilities'}
        </span>
        <div className="flex flex-wrap gap-1.5">
          {capabilities.map((tag, idx) => (
            <span
              key={idx}
              className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-[#050807]/70 border border-[#00E59B]/15 text-[#F5F8F6] group-hover:border-[#00E59B]/30 transition-colors"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Bottom Bar: Telemetry Stats */}
      <div className="pt-3 border-t border-[#00E59B]/15 flex items-center justify-between text-[11px] font-mono text-[#87938D]">
        <div className="flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-[#00E59B]" />
          <span>Latency: <strong className="text-[#F5F8F6]">{agent.latencyMs}ms</strong></span>
        </div>
        <div>
          <span>Confidence: <strong className="text-[#39FFC0]">{agent.confidence}%</strong></span>
        </div>
      </div>
    </div>
  );
};

