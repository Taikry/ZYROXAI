import React, { useState } from 'react';
import { useLanguage } from '../hooks/useLanguage';
import {
  CheckCircle2,
  ExternalLink,
  Code2,
  Terminal,
  Sparkles,
  MapPin,
  GraduationCap,
  Layers,
  Cpu,
  Shield,
  Activity,
  Copy,
  Check,
  Send,
  Bot,
  TrendingUp,
  Gamepad2,
  Server,
  Globe2,
  Briefcase,
  UserCheck,
  Flame,
} from 'lucide-react';

export const DeveloperProfile: React.FC = () => {
  const { isKhmer, t } = useLanguage();
  const [activePhoto, setActivePhoto] = useState<'cinematic' | 'fullcard' | 'waterfront' | 'campus'>('cinematic');
  const [activeTab, setActiveTab] = useState<'story' | 'skills' | 'projects' | 'terminal' | 'contact'>('story');
  const [copiedText, setCopiedText] = useState<string | null>(null);
  const [activeSkillCat, setActiveSkillCat] = useState<number>(0);

  const photos = {
    cinematic: {
      src: '/assets/developer/heng_taikry_cinematic_portrait.png',
      alt: 'Heng Taikry — Command Center Portrait',
      labelEn: 'Command Center',
      labelKh: 'រូបថតនៅតុធ្វើការ',
    },
    fullcard: {
      src: '/assets/developer/heng_taikry_cinematic_card.jpg',
      alt: 'Heng Taikry — Official Full Developer Profile Card',
      labelEn: 'Full Card',
      labelKh: 'កាតព័ត៌មានពេញលេញ',
    },
    waterfront: {
      src: '/assets/developer/heng_taikry_waterfront.jpg',
      alt: 'Heng Taikry — Waterfront Resort',
      labelEn: 'Waterfront',
      labelKh: 'រូបថតនៅមាត់ទឹក',
    },
    campus: {
      src: '/assets/developer/heng_taikry_outdoor.png',
      alt: 'Heng Taikry — Outdoor Campus Profile',
      labelEn: 'Campus View',
      labelKh: 'រូបថតក្រៅបន្ទប់',
    },
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 2200);
  };

  // Categorized authentic skills from Heng Taikry's official profile card
  const skillCategories = [
    {
      titleEn: 'AI Development',
      titleKh: 'ការអភិវឌ្ឍប្រព័ន្ធ AI',
      icon: <Cpu className="w-4 h-4 text-[#00E59B]" />,
      skillsEn: [
        'Machine Learning & Predictive Modeling',
        'Deep Learning & Neural Architectures',
        'NLP / LLM Integration & Orchestration',
        'AI Automation & Agent Consensus',
        'OpenAI API / GPT Fine-Tuning',
        'AI Multi-Market Trading & Prediction',
      ],
      skillsKh: [
        'Machine Learning & គំរូទស្សន៍ទាយ',
        'Deep Learning & បណ្តាញ Neural',
        'NLP / LLM Integration & ការសម្របសម្រួល',
        'AI Automation & ការស្រុះស្រួលភ្នាក់ងារ',
        'OpenAI API & GPT Models',
        'AI វិភាគទីផ្សារ & ព្យាករណ៍ទិសដៅ',
      ],
    },
    {
      titleEn: 'Trading Analysis',
      titleKh: 'ការវិភាគបច្ចេកទេសទីផ្សារ',
      icon: <TrendingUp className="w-4 h-4 text-[#39FFC0]" />,
      skillsEn: [
        'Technical Analysis & Smart Money Concepts',
        'Indicator Strategy (EMA, RSI, MACD, ATR)',
        'Market Prediction & Order Flow Imbalance',
        'Backtesting Systems & Statistical Rigor',
        'Risk Management & Drawdown Gating',
        'TradingView Pine Script & TV Integration',
      ],
      skillsKh: [
        'ការវិភាគបច្ចេកទេស & Smart Money Concepts',
        'យុទ្ធសាស្ត្រសូចនាករ (EMA, RSI, MACD, ATR)',
        'ការទស្សន៍ទាយទីផ្សារ & Order Flow Imbalance',
        'ប្រព័ន្ធ Backtesting & ស្ថិតិវិភាគ',
        'ការគ្រប់គ្រងហានិភ័យ & Drawdown Gating',
        'ការរួមបញ្ចូល TradingView & Pine Script',
      ],
    },
    {
      titleEn: 'EA Trading / Algorithmic',
      titleKh: 'ប្រព័ន្ធជួញដូរស្វ័យប្រវត្ត (EA)',
      icon: <Bot className="w-4 h-4 text-emerald-400" />,
      skillsEn: [
        'MQL4 / MQL5 Expert Advisors',
        'Automated 24/7 Trading Bots',
        'Strategy Development & Walk-Forward Testing',
        'Backtesting & Parameter Optimization',
        'Money Management & Dynamic Lot Sizing',
        'VPS Hosting & 24/7 Low-Latency Automation',
      ],
      skillsKh: [
        'MQL4 / MQL5 Expert Advisors (EA)',
        'Trading Bots ស្វ័យប្រវត្ត ២៤/៧',
        'ការបង្កើតយុទ្ធសាស្ត្រ & Walk-Forward Testing',
        'Backtesting & ការកំណត់ប៉ារ៉ាម៉ែត្រល្អបំផុត',
        'ការគ្រប់គ្រងដើមទុន & Dynamic Lot Sizing',
        'ការតម្លើងលើ Cloud VPS ២៤/៧',
      ],
    },
    {
      titleEn: 'Web & Software Development',
      titleKh: 'ការអភិវឌ្ឍ Web & Software',
      icon: <Code2 className="w-4 h-4 text-cyan-400" />,
      skillsEn: [
        'Full Stack Development (React, Next.js, Node.js)',
        'RESTful & WebSocket API Development',
        'Database Design (PostgreSQL, MongoDB, Redis)',
        'Real-time Application & Event Streaming',
        'DevOps, Docker & Cloud Deployment',
        'Clean Code, Design Patterns & Architecture',
      ],
      skillsKh: [
        'Full Stack Development (React, Next.js, Node.js)',
        'ការបង្កើត RESTful & WebSocket APIs',
        'រៀបចំ Database (PostgreSQL, MongoDB, Redis)',
        'កម្មវិធី Real-time & Event Streaming',
        'DevOps, Docker & ការដាក់ឱ្យដំណើរការលើ Cloud',
        'Clean Code & ស្ថាបត្យកម្មប្រព័ន្ធកម្រិតខ្ពស់',
      ],
    },
    {
      titleEn: 'MMO Game Development',
      titleKh: 'ការអភិវឌ្ឍហ្គេម MMORPG',
      icon: <Gamepad2 className="w-4 h-4 text-teal-400" />,
      skillsEn: [
        'MMORPG Game Server Architecture',
        'Real-time Gameplay Systems & Synch',
        'Database & High-Concurrency Networking',
        'Player, Inventory & Guild Systems',
        'Virtual Item & In-Game Economy Systems',
        'Unity 3D / C# / Node.js Distributed State',
      ],
      skillsKh: [
        'ស្ថាបត្យកម្ម Game Server MMORPG',
        'ប្រព័ន្ធ Gameplay ក្នុងពេលជាក់ស្តែង',
        'Database & បណ្តាញ Networking កម្រិតខ្ពស់',
        'ប្រព័ន្ធតួអង្គ, អីវ៉ាន់ & Guild System',
        'ប្រព័ន្ធសេដ្ឋកិច្ចក្នុងហ្គេម & Item Virtual',
        'Unity 3D / C# / Node.js State',
      ],
    },
  ];

  // Authentic proficiency ratings from Heng Taikry's official profile card
  const proficiencies = [
    { name: 'Next.js', pct: 95 },
    { name: 'Node.js', pct: 95 },
    { name: 'TypeScript', pct: 90 },
    { name: 'MQL4 / MQL5', pct: 90 },
    { name: 'Python', pct: 85 },
    { name: 'PostgreSQL', pct: 85 },
    { name: 'Docker', pct: 85 },
    { name: 'AWS / VPS', pct: 80 },
    { name: 'MongoDB', pct: 80 },
    { name: 'Redis', pct: 75 },
  ];

  // Featured flagship projects built by Heng Taikry
  const projects = [
    {
      title: 'ZYROX AI — Market Intelligence Platform',
      category: 'Flagship AI Fintech Platform',
      descEn: 'Full-stack multi-market trading analysis platform combining 6 autonomous neural agents, real-time ICT / Smart Money Concept detection, MT5 bridge streaming, and institutional risk management.',
      descKh: 'ប្រព័ន្ធ AI វិភាគទីផ្សារហិរញ្ញវត្ថុពហុទ្រព្យសកម្ម ដែលរួមបញ្ចូលភ្នាក់ងារស្វ័យប្រវត្តចំនួន ៦ ការគូសបង្ហាញ ICT / SMC ពេលជាក់ស្តែង និងការគ្រប់គ្រងហានិភ័យកម្រិតស្ថាប័ន។',
      stack: ['React 19', 'TypeScript', 'FastAPI', 'PostgreSQL', 'MT5 Bridge', 'Tailwind'],
      url: 'https://github.com/Taikry/Taikry-AI-Trading',
      featured: true,
    },
    {
      title: 'Autonomous Algorithmic Trading Bots (EA)',
      category: 'Algorithmic Fintech Automation',
      descEn: 'High-precision algorithmic trading systems authored in MQL4/MQL5, featuring mathematical risk-to-reward gating (>= 1:2.0), automated trailing stop logic, and 24/7 VPS execution.',
      descKh: 'ប្រព័ន្ធជួញដូរស្វ័យប្រវត្តកម្រិតខ្ពស់សរសេរជា MQL4/MQL5 ជាមួយការកំណត់សមាមាត្រហានិភ័យយ៉ាងតឹងរ៉ឹង (>= 1:2.0) និងដំណើរការលើ Cloud VPS ២៤/៧។',
      stack: ['MQL4', 'MQL5', 'MetaTrader', 'VPS', 'Python', 'Algorithmic Execution'],
      url: 'https://github.com/Taikry/Taikry-AI-Trading',
      featured: false,
    },
    {
      title: 'Quantitative Backtesting & Market Engine',
      category: 'Quantitative Research',
      descEn: 'Walk-forward historical backtesting engine with Monte Carlo simulations, multi-timeframe candle parsing, ATR volatility modeling, and automated Telegram reporting.',
      descKh: 'ម៉ាស៊ីនធ្វើតេស្តទិន្នន័យប្រវត្តិសាស្ត្រជាមួយ Monte Carlo Simulations ការគណនា ATR Volatility និងការបញ្ជូនរបាយការណ៍ស្វ័យប្រវត្តទៅ Telegram។',
      stack: ['Python', 'FastAPI', 'Pandas', 'WebSockets', 'Telegram API'],
      url: 'https://github.com/Taikry/Taikry-AI-Trading',
      featured: false,
    },
    {
      title: 'Scalable MMORPG Server Architecture',
      category: 'Distributed Systems',
      descEn: 'High-concurrency multiplayer game server handling real-time player synchronization, secure virtual economy transactions, and persistent world state.',
      descKh: 'ស្ថាបត្យកម្ម Game Server ដែលអាចផ្ទុកអ្នកលេងច្រើនក្នុងពេលតែមួយ ជាមួយប្រព័ន្ធ Sync ពេលជាក់ស្តែង និងការគ្រប់គ្រងសេដ្ឋកិច្ចក្នុងហ្គេម។',
      stack: ['Node.js', 'C#', 'Unity 3D', 'Socket.io', 'MongoDB', 'Redis'],
      url: 'https://github.com/Taikry/Taikry-AI-Trading',
      featured: false,
    },
  ];

  const socialChannels = [
    {
      name: 'Facebook',
      handle: 'Heng Taikry',
      meta: '2.5K Followers • Digital Creator',
      url: 'https://www.facebook.com/share/1Eya5WXJXB/?mibextid=wwXIfr',
      color: 'hover:border-blue-500/50 hover:bg-blue-500/10 text-blue-400',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
        </svg>
      ),
    },
    {
      name: 'TikTok',
      handle: '@hengtaikry',
      meta: '10.1K Followers • 91.1K Likes',
      url: 'https://www.tiktok.com/@hengtaikry',
      color: 'hover:border-pink-500/50 hover:bg-pink-500/10 text-pink-400',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.24 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z" />
        </svg>
      ),
    },
    {
      name: 'GitHub',
      handle: 'Taikry / Taikry-AI-Trading',
      meta: 'Open Source Repositories & Engine',
      url: 'https://github.com/Taikry/Taikry-AI-Trading',
      color: 'hover:border-[#00E59B]/50 hover:bg-[#00E59B]/10 text-[#00E59B]',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="relative w-full rounded-3xl bg-gradient-to-b from-[#090F0C] via-[#070C0A] to-[#050807] border border-[#00E59B]/30 p-6 md:p-12 overflow-hidden shadow-2xl">
      {/* Background Ambient Glows */}
      <div className="absolute -top-40 -right-40 w-[500px] h-[500px] bg-[#00E59B]/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] bg-[#39FFC0]/5 rounded-full blur-[140px] pointer-events-none" />

      {/* Top Banner Tagline from Official Profile Card */}
      <div className="relative z-10 flex flex-wrap items-center justify-between gap-4 pb-8 mb-8 border-b border-[#00E59B]/15">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#050807] border border-[#00E59B]/30 flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-[#39FFC0]" />
          </div>
          <div>
            <span className="text-[10px] font-mono uppercase tracking-[0.2em] text-[#00E59B] block font-bold">
              Founder & Full Stack Architect
            </span>
            <span className="text-sm font-mono text-[#F5F8F6] font-semibold">
              Building Powerful Solutions • Automating the Future • Creating Real Value
            </span>
          </div>
        </div>

        {/* Live Status Beacon */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#050807] border border-[#00E59B]/35 shadow-inner">
          <span className="w-2 h-2 rounded-full bg-[#00E59B] animate-ping" />
          <span className="text-xs font-mono text-[#39FFC0] font-semibold">
            Available for Remote Work & Fintech Systems
          </span>
        </div>
      </div>

      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
        {/* Left Column: Portrait Presentation with Multi-View Switcher */}
        <div className="lg:col-span-5 flex flex-col items-center">
          <div className="relative group w-full max-w-sm">
            {/* Animated Radiant Rim Light */}
            <div className="absolute -inset-1.5 rounded-3xl bg-gradient-to-tr from-[#00E59B] via-[#39FFC0] to-[#00B981] opacity-75 blur-md group-hover:opacity-100 group-hover:blur-lg transition-all duration-700 animate-pulse-glow" />

            {/* Photo Container */}
            <div className="relative w-full aspect-[4/5] rounded-2xl overflow-hidden bg-[#050807] border-2 border-[#00E59B]/40 shadow-2xl">
              <img
                src={photos[activePhoto].src}
                alt={photos[activePhoto].alt}
                className="w-full h-full object-cover transition-all duration-500 group-hover:scale-105"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src = '/assets/developer/heng_taikry_cinematic_card.jpg';
                }}
              />

              {/* Verified Badge Overlay */}
              <div className="absolute bottom-3 left-3 right-3 px-3.5 py-2 rounded-xl bg-[#050807]/90 border border-[#00E59B]/40 backdrop-blur-md flex items-center justify-between shadow-xl">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-[#00E59B]" />
                  <span className="text-xs font-mono font-bold text-[#F5F8F6]">
                    HENG TAIKRY
                  </span>
                </div>
                <span className="text-[10px] font-mono uppercase text-[#39FFC0] px-2 py-0.5 rounded bg-[#00E59B]/15 border border-[#00E59B]/30 font-semibold">
                  FOUNDER • VERIFIED
                </span>
              </div>
            </div>
          </div>

          {/* Photo Switcher Tabs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 w-full max-w-sm mt-4 p-1 rounded-xl bg-[#050807] border border-[#00E59B]/20">
            {(Object.keys(photos) as Array<keyof typeof photos>).map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => setActivePhoto(key)}
                className={`py-1.5 text-xs font-mono rounded-lg transition-all cursor-pointer text-center truncate ${
                  activePhoto === key
                    ? 'bg-[#00E59B] text-[#050807] font-bold shadow-[0_0_10px_rgba(0,229,155,0.4)]'
                    : 'text-[#87938D] hover:text-[#F5F8F6]'
                }`}
              >
                {isKhmer ? photos[key].labelKh : photos[key].labelEn}
              </button>
            ))}
          </div>

          {/* Quick Meta from Authentic Profile Card */}
          <div className="w-full max-w-sm mt-4 p-4 rounded-2xl bg-[#050807] border border-[#00E59B]/20 space-y-2 text-xs font-mono text-[#87938D]">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-[#00E59B]" />
                Location
              </span>
              <strong className="text-[#F5F8F6]">Phnom Penh, Cambodia</strong>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Send className="w-3.5 h-3.5 text-[#39FFC0]" />
                Telegram
              </span>
              <strong className="text-[#39FFC0]">0968288832</strong>
            </div>
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <GraduationCap className="w-3.5 h-3.5 text-emerald-400" />
                Education / Role
              </span>
              <strong className="text-[#F5F8F6]">Howard University / Creator</strong>
            </div>
          </div>
        </div>

        {/* Right Column: Dynamic Interactive Tabbed Portfolio */}
        <div className="lg:col-span-7 flex flex-col">
          {/* Navigation Tabs */}
          <div className="flex items-center gap-1.5 p-1 rounded-2xl bg-[#050807] border border-[#00E59B]/25 overflow-x-auto mb-6 text-xs font-mono">
            {[
              { id: 'story', labelEn: 'About & Story', labelKh: 'ប្រវត្តិ & ទស្សនវិស័យ' },
              { id: 'skills', labelEn: 'Skills & Stack', labelKh: 'ជំនាញ & បច្ចេកវិទ្យា' },
              { id: 'projects', labelEn: 'Projects', labelKh: 'គម្រោងស្នូល' },
              { id: 'terminal', labelEn: 'Terminal', labelKh: 'ផ្ទាំង Terminal' },
              { id: 'contact', labelEn: 'Contact', labelKh: 'ទំនាក់ទំនង' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-3.5 py-2 rounded-xl transition-all cursor-pointer font-bold whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-[#00E59B] text-[#050807] shadow-[0_0_12px_rgba(0,229,155,0.4)]'
                    : 'text-[#87938D] hover:text-[#F5F8F6]'
                }`}
              >
                {isKhmer ? tab.labelKh : tab.labelEn}
              </button>
            ))}
          </div>

          {/* TAB 1: About & Founder Story */}
          {activeTab === 'story' && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <h3 className="text-3xl sm:text-4xl font-extrabold text-[#F5F8F6] tracking-tight">
                  HENG TAIKRY
                </h3>
                <p className="text-sm sm:text-base font-mono text-[#00E59B] font-semibold mt-1">
                  Founder | Full Stack Developer | AI Engineer
                </p>
              </div>

              {/* Official Quote from Authentic Card */}
              <blockquote className="p-4 rounded-2xl bg-[#050807] border-l-4 border-[#00E59B] text-sm sm:text-base italic text-[#F5F8F6] leading-relaxed shadow-inner">
                “Code is not just what I write, it's how I solve problems and create the future.”
              </blockquote>

              {/* Authentic About Me text from Developer Card */}
              <div className="p-5 rounded-2xl bg-[#050807]/70 border border-[#00E59B]/20 space-y-3">
                <span className="text-xs font-mono uppercase tracking-wider text-[#39FFC0] font-bold block">
                  {isKhmer ? 'អំពីខ្ញុំ (About Me)' : 'About Me & Mission'}
                </span>
                <p className="text-xs sm:text-sm text-[#F5F8F6] leading-relaxed">
                  Passionate Full Stack Developer with strong experience in building scalable web applications, AI solutions, and automated trading systems. I love turning ideas into real products and solving complex problems with clean, efficient code.
                </p>
                <p className="text-xs sm:text-sm text-[#87938D] leading-relaxed">
                  {isKhmer
                    ? 'ZYROX AI ត្រូវបានបង្កើតឡើង និងអភិវឌ្ឍន៍ដោយ ហេង តៃគ្រី (Heng Taikry) ដើម្បីរួមបញ្ចូលគ្នានូវក្បួនដោះស្រាយគណិតវិទ្យាទីផ្សារ គោលគំនិត Smart Money Concepts (SMC) / ICT និងការស្រុះស្រួលរបស់ភ្នាក់ងារ AI ស្វ័យប្រវត្ត ទៅជាប្រព័ន្ធវិភាគទីផ្សារកម្រិតស្ថាប័ន។'
                    : 'ZYROX AI was designed and engineered from the ground up by Heng Taikry to bridge the gap between complex quantitative algorithmic models, ICT/SMC market mechanics, and accessible, high-speed visual interfaces for modern traders worldwide.'}
                </p>
              </div>

              {/* Core Focus Pillars from Authentic Card */}
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-[#87938D] block mb-3 font-semibold">
                  Engineering Principles (My Focus)
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                  {[
                    { title: 'Clean Code', desc: 'Maintainable & Robust' },
                    { title: 'Performance', desc: 'Sub-second Latency' },
                    { title: 'Security', desc: 'End-to-End Integrity' },
                    { title: 'Scalability', desc: 'Decoupled Microservices' },
                    { title: 'Automation', desc: '24/7 Autonomous Loops' },
                    { title: 'Innovation', desc: 'Next-Gen AI Systems' },
                  ].map((p, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-xl bg-[#050807] border border-[#00E59B]/15 hover:border-[#00E59B]/35 transition-colors"
                    >
                      <span className="text-xs font-mono font-bold text-[#F5F8F6] block">
                        {p.title}
                      </span>
                      <span className="text-[10px] text-[#87938D] mt-0.5 block">
                        {p.desc}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Skills Visualization */}
          {activeTab === 'skills' && (
            <div className="space-y-6 animate-fade-in">
              <div>
                <h4 className="text-sm font-mono uppercase tracking-wider text-[#00E59B] font-bold mb-1">
                  Categorized Core Skills
                </h4>
                <p className="text-xs text-[#87938D]">
                  Authentic specialized capabilities directly from official profile.
                </p>
              </div>

              {/* Category Pills */}
              <div className="flex items-center gap-2 overflow-x-auto pb-1">
                {skillCategories.map((cat, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveSkillCat(idx)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-mono transition-all cursor-pointer whitespace-nowrap ${
                      activeSkillCat === idx
                        ? 'bg-[#00E59B] text-[#050807] font-bold shadow-[0_0_10px_rgba(0,229,155,0.3)]'
                        : 'bg-[#050807] text-[#87938D] hover:text-[#F5F8F6] border border-[#00E59B]/20'
                    }`}
                  >
                    {cat.icon}
                    <span>{isKhmer ? cat.titleKh : cat.titleEn}</span>
                  </button>
                ))}
              </div>

              {/* Active Category Skills List */}
              <div className="p-4 rounded-2xl bg-[#050807] border border-[#00E59B]/25 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {(isKhmer
                  ? skillCategories[activeSkillCat].skillsKh
                  : skillCategories[activeSkillCat].skillsEn
                ).map((skill, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 p-2 rounded-xl bg-white/5 border border-white/5 text-xs font-mono text-[#F5F8F6]"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#00E59B] shrink-0" />
                    <span>{skill}</span>
                  </div>
                ))}
              </div>

              {/* Proficiency Level Progress Bars */}
              <div>
                <h4 className="text-xs font-mono uppercase tracking-wider text-[#87938D] font-bold mb-3 flex items-center justify-between">
                  <span>Proficiency Ratings (Expert In)</span>
                  <span className="text-[#00E59B]">Verified Benchmarks</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {proficiencies.map((item, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-[#050807] border border-[#00E59B]/15">
                      <div className="flex items-center justify-between text-xs font-mono mb-1.5">
                        <span className="font-bold text-[#F5F8F6]">{item.name}</span>
                        <span className="text-[#39FFC0]">{item.pct}%</span>
                      </div>
                      <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-[#00E59B] to-[#39FFC0] h-full rounded-full transition-all duration-700"
                          style={{ width: `${item.pct}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: Featured Projects Showcase */}
          {activeTab === 'projects' && (
            <div className="space-y-4 animate-fade-in">
              {projects.map((proj, idx) => (
                <div
                  key={idx}
                  className="p-5 rounded-2xl bg-[#050807] border border-[#00E59B]/20 hover:border-[#00E59B]/50 transition-all duration-300 group shadow-lg flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between gap-3 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm sm:text-base text-[#F5F8F6] group-hover:text-[#39FFC0] transition-colors">
                          {proj.title}
                        </span>
                        {proj.featured && (
                          <span className="text-[9px] font-mono uppercase px-2 py-0.5 rounded-full bg-[#00E59B]/15 text-[#00E59B] border border-[#00E59B]/30 font-bold">
                            FLAGSHIP
                          </span>
                        )}
                      </div>
                      <a
                        href={proj.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#87938D] hover:text-[#00E59B] transition-colors p-1"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>

                    <span className="text-[11px] font-mono text-[#39FFC0] block mb-2">
                      {proj.category}
                    </span>

                    <p className="text-xs text-[#87938D] leading-relaxed">
                      {isKhmer ? proj.descKh : proj.descEn}
                    </p>
                  </div>

                  {/* Stack Badges */}
                  <div className="mt-4 pt-3 border-t border-[#00E59B]/10 flex flex-wrap gap-1.5">
                    {proj.stack.map((s, i) => (
                      <span
                        key={i}
                        className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 border border-white/5 text-[#F5F8F6]"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 4: Interactive Terminal */}
          {activeTab === 'terminal' && (
            <div className="p-5 rounded-2xl bg-[#050807] border border-[#00E59B]/30 font-mono text-xs text-[#F5F8F6] space-y-3 animate-fade-in shadow-inner">
              <div className="flex items-center justify-between pb-2 border-b border-white/10 text-[#87938D]">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80" />
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                  <span className="ml-2 text-[11px]">taikry@fintech-workstation:~$</span>
                </div>
                <span className="text-[10px] text-[#00E59B]">ONLINE</span>
              </div>

              <div>
                <p className="text-[#00E59B]">$ whoami</p>
                <p className="text-[#87938D] ml-2">
                  HENG TAIKRY — Founder | Full Stack Developer | AI Solutions Architect | MQL4/MQL5 Quant
                </p>
              </div>

              <div>
                <p className="text-[#00E59B]">$ cat /etc/zyrox/manifest.json</p>
                <pre className="text-[#39FFC0] ml-2 text-[11px] whitespace-pre-wrap">
{`{
  "project": "ZYROX AI",
  "founder": "HENG TAIKRY",
  "tagline": "Intelligence Beyond The Market",
  "architecture": "React 19 + Python FastAPI + PostgreSQL + MT5",
  "multi_agent_consensus": "6 Specialized Neural Agents",
  "status": "OPERATIONAL"
}`}
                </pre>
              </div>

              <div>
                <p className="text-[#00E59B]">$ ping -c 1 telegram.org</p>
                <p className="text-[#87938D] ml-2">
                  Direct Telegram dispatch active on @0968288832 (latency: 14ms)
                </p>
              </div>
            </div>
          )}

          {/* TAB 5: Contact & Official Verification */}
          {activeTab === 'contact' && (
            <div className="space-y-6 animate-fade-in">
              <div className="p-5 rounded-2xl bg-[#050807] border border-[#00E59B]/25 space-y-4">
                <span className="text-xs font-mono uppercase tracking-wider text-[#00E59B] font-bold block">
                  Direct Verification Channels
                </span>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-[#87938D] block">Telegram</span>
                      <strong className="text-[#39FFC0]">0968288832</strong>
                    </div>
                    <button
                      onClick={() => copyToClipboard('0968288832', 'telegram')}
                      className="px-2 py-1 rounded bg-[#00E59B]/15 text-[#00E59B] text-[10px] hover:bg-[#00E59B]/30 cursor-pointer"
                    >
                      {copiedText === 'telegram' ? 'Copied' : 'Copy'}
                    </button>
                  </div>

                  <div className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-[#87938D] block">Location</span>
                      <strong className="text-[#F5F8F6]">Phnom Penh, Cambodia</strong>
                    </div>
                    <span className="text-[10px] text-[#00E59B]">UTC+7</span>
                  </div>
                </div>
              </div>

              {/* Official Social Links */}
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-[#87938D] font-bold block mb-3">
                  Official Creator Channels
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {socialChannels.map((chan, idx) => (
                    <a
                      key={idx}
                      href={chan.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`flex flex-col p-3.5 rounded-xl bg-[#050807] border border-[#00E59B]/20 transition-all duration-300 group cursor-pointer ${chan.color}`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center gap-2">
                          {chan.icon}
                          <span className="font-bold text-xs text-[#F5F8F6] group-hover:text-inherit transition-colors">
                            {chan.name}
                          </span>
                        </div>
                        <ExternalLink className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all" />
                      </div>
                      <span className="text-[11px] font-mono text-[#87938D] truncate">
                        {chan.handle}
                      </span>
                      <span className="text-[9px] font-mono text-[#00E59B] mt-1 opacity-80">
                        {chan.meta}
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Bottom Persistent Bar: Social Verification & Repo Share */}
          <div className="mt-8 pt-6 border-t border-[#00E59B]/15 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-[#87938D]">
                Verified Developer Identity:
              </span>
              <span className="text-xs font-mono font-bold text-[#00E59B] flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                HENG TAIKRY
              </span>
            </div>

            <button
              onClick={() => copyToClipboard('https://github.com/Taikry/Taikry-AI-Trading', 'repo')}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#050807] border border-[#00E59B]/25 text-xs font-mono text-[#39FFC0] hover:border-[#00E59B]/60 hover:text-[#00E59B] transition-colors cursor-pointer"
            >
              {copiedText === 'repo' ? (
                <>
                  <Check className="w-3.5 h-3.5 text-[#00E59B]" />
                  <span>Link Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Share Repository</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
