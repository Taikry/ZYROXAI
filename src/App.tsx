import React, { useState } from 'react';
import { LanguageProvider, useLanguage } from './hooks/useLanguage';
import { ParticleBackground } from './components/ParticleBackground';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { TerminalModal } from './components/TerminalModal';
import { AuthModal } from './components/AuthModal';
import { ScrollToTop } from './components/ScrollToTop';
import { HeroSection } from './sections/HeroSection';
import { MarketSection } from './sections/MarketSection';
import { AgentsSection } from './sections/AgentsSection';
import { TechnicalSection } from './sections/TechnicalSection';
import { SignalsSection } from './sections/SignalsSection';
import { FeaturesSection } from './sections/FeaturesSection';
import { TechnologySection } from './sections/TechnologySection';
import { DeveloperSection } from './sections/DeveloperSection';
import { Bot, Sparkles } from 'lucide-react';

const MainApp: React.FC = () => {
  const { isKhmer } = useLanguage();
  const [terminalOpen, setTerminalOpen] = useState<boolean>(false);
  const [authOpen, setAuthOpen] = useState<boolean>(false);
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');

  const handleOpenAuth = (mode?: 'signin' | 'signup') => {
    setAuthMode(mode || 'signin');
    setAuthOpen(true);
  };

  return (
    <div className={`min-h-screen bg-[#050807] text-[#F5F8F6] relative selection:bg-[#00E59B]/20 selection:text-[#39FFC0] ${isKhmer ? 'font-khmer' : ''}`}>
      {/* Interactive Background Particle Canvas */}
      <ParticleBackground />

      {/* Navigation Header */}
      <Navbar
        onLaunchTerminal={() => setTerminalOpen(true)}
        onOpenAuth={handleOpenAuth}
      />

      {/* Main Sections */}
      <main className="relative z-10">
        <HeroSection onLaunchTerminal={() => setTerminalOpen(true)} />
        <MarketSection />
        <AgentsSection />
        <TechnicalSection />
        <SignalsSection />
        <FeaturesSection />
        <TechnologySection />
        <DeveloperSection />
      </main>

      {/* Footer */}
      <Footer />

      {/* Interactive System AI Engine Modal */}
      <TerminalModal
        isOpen={terminalOpen}
        onClose={() => setTerminalOpen(false)}
      />

      {/* Authentication & Telegram Login Modal */}
      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        initialMode={authMode}
      />

      {/* Floating System AI Quick Action Button */}
      <div className="fixed bottom-6 right-6 z-40 flex items-center gap-2">
        <button
          onClick={() => setTerminalOpen(true)}
          className="px-4 py-2.5 rounded-full bg-[#090F0C]/95 hover:bg-[#00E59B] text-[#00E59B] hover:text-[#050807] border border-[#00E59B]/40 hover:border-[#00E59B] shadow-[0_0_25px_rgba(0,229,155,0.35)] backdrop-blur-xl flex items-center gap-2 transition-all duration-300 group cursor-pointer font-mono text-xs font-bold"
          title="Open System AI Intelligence"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00E59B] group-hover:bg-[#050807] opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00E59B] group-hover:bg-[#050807]" />
          </span>
          <Bot className="w-4 h-4 animate-pulse" />
          <span>{isKhmer ? 'ប្រព័ន្ធ AI' : 'System AI'}</span>
          <Sparkles className="w-3.5 h-3.5 opacity-80" />
        </button>

        {/* Scroll To Top */}
        <ScrollToTop />
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <LanguageProvider>
      <MainApp />
    </LanguageProvider>
  );
};

export default App;
