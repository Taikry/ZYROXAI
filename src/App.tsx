import React, { useState } from 'react';
import { LanguageProvider, useLanguage } from './hooks/useLanguage';
import { ParticleBackground } from './components/ParticleBackground';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import { TerminalModal } from './components/TerminalModal';
import { ScrollToTop } from './components/ScrollToTop';
import { HeroSection } from './sections/HeroSection';
import { MarketSection } from './sections/MarketSection';
import { AgentsSection } from './sections/AgentsSection';
import { TechnicalSection } from './sections/TechnicalSection';
import { SignalsSection } from './sections/SignalsSection';
import { FeaturesSection } from './sections/FeaturesSection';
import { TechnologySection } from './sections/TechnologySection';
import { DeveloperSection } from './sections/DeveloperSection';

const MainApp: React.FC = () => {
  const { isKhmer } = useLanguage();
  const [terminalOpen, setTerminalOpen] = useState<boolean>(false);

  return (
    <div className={`min-h-screen bg-[#050807] text-[#F5F8F6] relative selection:bg-[#00E59B]/20 selection:text-[#39FFC0] ${isKhmer ? 'font-khmer' : ''}`}>
      {/* Interactive Background Particle Canvas */}
      <ParticleBackground />

      {/* Navigation Header */}
      <Navbar onLaunchTerminal={() => setTerminalOpen(true)} />

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

      {/* Interactive Terminal Demo Modal */}
      <TerminalModal
        isOpen={terminalOpen}
        onClose={() => setTerminalOpen(false)}
      />

      {/* Floating Scroll to Top */}
      <ScrollToTop />
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

