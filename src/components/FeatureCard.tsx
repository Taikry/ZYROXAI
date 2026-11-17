import React from 'react';
import { PlatformFeature } from '../types';
import { useLanguage } from '../hooks/useLanguage';
import {
  Bot,
  Users,
  Activity,
  Sparkles,
  Globe2,
  Grid,
  BookOpen,
  History,
  Newspaper,
  Send,
  ShieldCheck,
  Maximize2,
  CheckCircle,
} from 'lucide-react';

interface FeatureCardProps {
  feature: PlatformFeature;
}

export const FeatureCard: React.FC<FeatureCardProps> = ({ feature }) => {
  const { isKhmer } = useLanguage();

  const renderIcon = () => {
    const props = { className: "w-5 h-5 text-[#00E59B]" };
    switch (feature.icon) {
      case 'Bot': return <Bot {...props} />;
      case 'Users': return <Users {...props} />;
      case 'Activity': return <Activity {...props} />;
      case 'Sparkles': return <Sparkles {...props} />;
      case 'Globe2': return <Globe2 {...props} />;
      case 'Grid': return <Grid {...props} />;
      case 'BookOpen': return <BookOpen {...props} />;
      case 'History': return <History {...props} />;
      case 'Newspaper': return <Newspaper {...props} />;
      case 'Send': return <Send {...props} />;
      case 'ShieldCheck': return <ShieldCheck {...props} />;
      case 'Maximize2': return <Maximize2 {...props} />;
      default: return <CheckCircle {...props} />;
    }
  };

  return (
    <div className="glass-card group relative p-6 rounded-2xl flex flex-col justify-between hover:border-[#00E59B]/40 transition-all duration-300">
      {/* Top Header */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="w-11 h-11 rounded-xl bg-[#050807] border border-[#00E59B]/25 flex items-center justify-center p-2 group-hover:border-[#00E59B] group-hover:shadow-[0_0_15px_rgba(0,229,155,0.3)] transition-all">
            {renderIcon()}
          </div>

          {feature.metrics && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#00E59B]/10 text-[#39FFC0] border border-[#00E59B]/20">
              {feature.metrics}
            </span>
          )}
        </div>

        {/* Feature Title */}
        <h4 className="text-base md:text-lg font-bold text-[#F5F8F6] group-hover:text-[#39FFC0] transition-colors">
          {isKhmer ? feature.titleKh : feature.titleEn}
        </h4>

        {/* Description */}
        <p className="text-xs text-[#87938D] mt-2 leading-relaxed">
          {isKhmer ? feature.descKh : feature.descEn}
        </p>
      </div>

      {/* Bottom badge */}
      <div className="mt-4 pt-3 border-t border-[#00E59B]/10 flex items-center justify-between">
        <span className="text-[10px] font-mono uppercase tracking-wider text-[#87938D]">
          {isKhmer ? (feature.badgeKh || 'លក្ខណៈពិសេស') : (feature.badgeEn || 'CAPABILITY')}
        </span>
        <span className="text-[10px] font-mono text-[#00E59B] group-hover:translate-x-0.5 transition-transform">
          ZYROX AI →
        </span>
      </div>
    </div>
  );
};

