import React from 'react';
import { DeveloperProfile } from '../components/DeveloperProfile';
import { useLanguage } from '../hooks/useLanguage';
import { Sparkles, Terminal } from 'lucide-react';

export const DeveloperSection: React.FC = () => {
  const { isKhmer, t } = useLanguage();

  return (
    <section id="developer" className="py-24 relative bg-[#050807] overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-gradient-to-r from-[#00E59B]/10 via-[#39FFC0]/5 to-transparent rounded-full blur-[140px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#00E59B]/10 border border-[#00E59B]/30 text-[#00E59B] text-xs font-mono font-semibold uppercase tracking-wider mb-3">
            <Terminal className="w-3.5 h-3.5 text-[#39FFC0]" />
            <span>{t.developer.badge}</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#F5F8F6] tracking-tight">
            {t.developer.title}
          </h2>
          <p className="mt-4 text-sm sm:text-base text-[#87938D] leading-relaxed">
            {t.developer.subtitle}
          </p>
        </div>

        {/* Developer Profile Container */}
        <DeveloperProfile />
      </div>
    </section>
  );
};

