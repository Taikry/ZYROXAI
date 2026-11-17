import React from 'react';
import { AnimatedLogo } from './AnimatedLogo';
import { useLanguage } from '../hooks/useLanguage';
import { ExternalLink, ShieldAlert, Heart } from 'lucide-react';

export const Footer: React.FC = () => {
  const { isKhmer, t } = useLanguage();

  const socialLinks = [
    {
      name: 'Facebook',
      url: 'https://www.facebook.com/share/1Eya5WXJXB/?mibextid=wwXIfr',
    },
    {
      name: 'TikTok',
      url: 'https://www.tiktok.com/@hengtaikry',
    },
    {
      name: 'GitHub',
      url: 'https://github.com/Taikry/Taikry-AI-Trading',
    },
  ];

  const quickLinks = [
    { label: t.nav.home, href: '#hero' },
    { label: t.nav.markets, href: '#markets' },
    { label: t.nav.agents, href: '#agents' },
    { label: t.nav.analysis, href: '#analysis' },
    { label: t.nav.features, href: '#features' },
    { label: t.nav.technology, href: '#technology' },
    { label: t.nav.developer, href: '#developer' },
  ];

  return (
    <footer className="relative bg-[#050807] border-t border-[#00E59B]/20 pt-16 pb-12 overflow-hidden z-20">
      {/* Background ambient lighting */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-3/4 h-64 bg-[#00E59B]/5 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-[#00E59B]/15">
          {/* Col 1 & 2: Brand & Tagline */}
          <div className="lg:col-span-2 flex flex-col">
            <AnimatedLogo size="lg" />
            <p className="text-xs sm:text-sm text-[#87938D] mt-4 max-w-sm leading-relaxed">
              {t.footer.description}
            </p>
            <div className="mt-4 flex items-center gap-2 text-xs font-mono text-[#00E59B]">
              <span className="w-2 h-2 rounded-full bg-[#00E59B] animate-pulse" />
              <span>{t.footer.tagline}</span>
            </div>
          </div>

          {/* Col 3: Navigation */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-[#F5F8F6] font-bold mb-4">
              {t.footer.quickLinks}
            </h4>
            <ul className="space-y-2 text-xs text-[#87938D]">
              {quickLinks.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="hover:text-[#39FFC0] transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Col 4: Creator & Channels */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-[#F5F8F6] font-bold mb-4">
              {t.footer.social}
            </h4>
            <ul className="space-y-2 text-xs text-[#87938D]">
              {socialLinks.map((s) => (
                <li key={s.name}>
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 hover:text-[#00E59B] transition-colors"
                  >
                    <span>{s.name}</span>
                    <ExternalLink className="w-3 h-3 opacity-60" />
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Col 5: Founder Verification */}
          <div>
            <h4 className="text-xs font-mono uppercase tracking-wider text-[#F5F8F6] font-bold mb-4">
              {t.developer.badge}
            </h4>
            <div className="p-4 rounded-xl bg-[#090F0C] border border-[#00E59B]/20">
              <span className="text-xs font-bold text-[#F5F8F6] block">
                HENG TAIKRY
              </span>
              <span className="text-[11px] font-mono text-[#00E59B] block mt-0.5">
                Founder & Full Stack AI Engineer
              </span>
              <p className="text-[10px] text-[#87938D] mt-2">
                Phnom Penh, Cambodia
              </p>
            </div>
          </div>
        </div>

        {/* Regulatory Risk Disclaimer */}
        <div className="py-6 border-b border-[#00E59B]/10 flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <p className="text-[11px] text-[#87938D] leading-relaxed">
            <strong className="text-amber-300 font-semibold uppercase tracking-wider">
              Risk Disclosure:
            </strong>{' '}
            {t.footer.disclaimer}
          </p>
        </div>

        {/* Bottom Credits */}
        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-[#87938D]">
          <div>
            © {new Date().getFullYear()} ZYROX AI. {t.footer.rights}
          </div>
          <div className="flex items-center gap-1">
            <span>{t.footer.developerCredit}</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
