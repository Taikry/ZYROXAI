import React, { useState, useEffect } from 'react';
import { AnimatedLogo } from './AnimatedLogo';
import { LanguageSwitcher } from './LanguageSwitcher';
import { MagneticButton } from './MagneticButton';
import { useLanguage } from '../hooks/useLanguage';
import { Menu, X, Terminal, Bot, ChevronRight, Send, LogIn } from 'lucide-react';

interface NavbarProps {
  onLaunchTerminal: () => void;
  onOpenAuth?: (mode?: 'signin' | 'signup') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onLaunchTerminal, onOpenAuth }) => {
  const { isKhmer, t } = useLanguage();
  const [isScrolled, setIsScrolled] = useState<boolean>(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { label: t.nav.home, href: '#hero' },
    { label: t.nav.markets, href: '#markets' },
    { label: t.nav.agents, href: '#agents' },
    { label: t.nav.analysis, href: '#analysis' },
    { label: t.nav.features, href: '#features' },
    { label: t.nav.technology, href: '#technology' },
    { label: t.nav.developer, href: '#developer' },
  ];

  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    setMobileMenuOpen(false);
    const target = document.querySelector(href);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 ${
        isScrolled
          ? 'py-3 bg-[#050807]/90 backdrop-blur-xl border-b border-[#00E59B]/20 shadow-lg shadow-black/50'
          : 'py-5 bg-transparent border-b border-white/5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Brand Logo */}
          <a
            href="#hero"
            onClick={(e) => handleLinkClick(e, '#hero')}
            className="cursor-pointer"
          >
            <AnimatedLogo size="md" />
          </a>

          {/* Desktop Navigation Links */}
          <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => handleLinkClick(e, link.href)}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-[#87938D] hover:text-[#39FFC0] hover:bg-white/5 transition-all cursor-pointer"
              >
                {link.label}
              </a>
            ))}
          </nav>

          {/* Right Controls: Language Switcher, System AI Button, & Terminal */}
          <div className="hidden sm:flex items-center gap-2.5">
            <LanguageSwitcher />

            {/* Dedicated System AI Highlight Button */}
            <MagneticButton
              variant="primary"
              size="sm"
              onClick={onLaunchTerminal}
              className="bg-gradient-to-r from-[#00E59B] to-[#39FFC0] text-[#050807] font-bold shadow-[0_0_20px_rgba(0,229,155,0.45)] border-0"
            >
              <Bot className="w-3.5 h-3.5 animate-pulse text-[#050807]" />
              <span>{isKhmer ? 'ប្រព័ន្ធ AI' : 'System AI'}</span>
            </MagneticButton>

            {/* Telegram Login Button */}
            <button
              onClick={() => onOpenAuth ? onOpenAuth('signin') : (window.location.href = '/api/v1/auth/telegram/login')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#229ED9]/15 hover:bg-[#229ED9]/25 text-xs font-mono font-medium text-[#229ED9] hover:text-[#52c1f7] border border-[#229ED9]/30 hover:border-[#229ED9]/60 transition-all cursor-pointer"
              title={isKhmer ? 'ចូលប្រើប្រាស់តាម Telegram' : 'Continue with Telegram'}
            >
              <Send className="w-3.5 h-3.5" />
              <span>{isKhmer ? 'ចូល Telegram' : 'Telegram Login'}</span>
            </button>

            {/* General Sign In / Free Trial */}
            <button
              onClick={() => onOpenAuth && onOpenAuth('signin')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-mono font-medium text-[#F5F8F6] border border-white/10 hover:border-white/20 transition-all cursor-pointer"
              title={isKhmer ? 'ចូលគណនី' : 'Sign In'}
            >
              <LogIn className="w-3.5 h-3.5 text-[#00E59B]" />
              <span>{isKhmer ? 'ចូលគណនី' : 'Sign In'}</span>
            </button>

            {/* Direct Link to Live Web Terminal Dashboard */}
            <a
              href="/dashboard/"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-[#00E59B]/10 text-xs font-mono font-medium text-[#87938D] hover:text-[#39FFC0] border border-white/10 hover:border-[#00E59B]/30 transition-all cursor-pointer"
            >
              <Terminal className="w-3.5 h-3.5 text-[#00E59B]" />
              <span>{isKhmer ? 'ផ្ទាំង Trade' : 'Terminal'}</span>
            </a>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-2 lg:hidden">
            <LanguageSwitcher compact />
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-xl bg-[#090F0C] border border-[#00E59B]/20 text-[#F5F8F6] hover:text-[#00E59B] transition-colors cursor-pointer"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-x-0 top-[65px] bg-[#090F0C]/95 backdrop-blur-2xl border-b border-[#00E59B]/25 p-6 shadow-2xl animate-fade-in">
          <nav className="flex flex-col gap-2">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => handleLinkClick(e, link.href)}
                className="flex items-center justify-between px-4 py-3 rounded-xl text-sm font-semibold text-[#F5F8F6] hover:bg-[#00E59B]/10 hover:text-[#00E59B] transition-colors"
              >
                <span>{link.label}</span>
                <ChevronRight className="w-4 h-4 text-[#87938D]" />
              </a>
            ))}

            <div className="pt-4 mt-2 border-t border-[#00E59B]/15 flex flex-col gap-2">
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  onLaunchTerminal();
                }}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-mono text-sm font-bold bg-gradient-to-r from-[#00E59B] to-[#39FFC0] text-[#050807] shadow-[0_0_20px_rgba(0,229,155,0.4)] cursor-pointer"
              >
                <Bot className="w-4 h-4 animate-pulse" />
                <span>{isKhmer ? 'ប្រព័ន្ធ AI (System AI)' : 'System AI Engine'}</span>
              </button>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onOpenAuth) onOpenAuth('signin');
                  else window.location.href = '/api/v1/auth/telegram/login';
                }}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-mono text-sm font-bold bg-[#229ED9] hover:bg-[#28a8e6] text-white shadow-[0_4px_15px_rgba(34,158,217,0.35)] cursor-pointer"
              >
                <Send className="w-4 h-4" />
                <span>{isKhmer ? 'បន្តជាមួយ Telegram (OIDC)' : 'Continue with Telegram'}</span>
              </button>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  if (onOpenAuth) onOpenAuth('signin');
                }}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl font-mono text-xs font-semibold bg-white/5 hover:bg-[#00E59B]/10 text-[#F5F8F6] border border-white/10 cursor-pointer"
              >
                <LogIn className="w-4 h-4 text-[#00E59B]" />
                <span>{isKhmer ? 'ចូលគណនី / ចុះឈ្មោះ (Email/Password)' : 'Sign In / Register'}</span>
              </button>
              <a
                href="/dashboard/"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl font-mono text-xs font-semibold bg-[#050807] text-[#87938D] hover:text-[#39FFC0] border border-white/10"
              >
                <Terminal className="w-4 h-4 text-[#00E59B]" />
                <span>{isKhmer ? 'បើកផ្ទាំង Web Terminal (/dashboard/)' : 'Launch Web Terminal'}</span>
              </a>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
};
