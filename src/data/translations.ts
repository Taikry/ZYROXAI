export interface TranslationDictionary {
  nav: {
    home: string;
    features: string;
    agents: string;
    markets: string;
    analysis: string;
    technology: string;
    developer: string;
    launch: string;
    terminalPreview: string;
  };
  hero: {
    badge: string;
    titlePart1: string;
    titlePart2: string;
    subtitle: string;
    ctaLaunch: string;
    ctaFeatures: string;
    ctaAgents: string;
    statsAgents: string;
    statsMarkets: string;
    statsLatency: string;
    statsConsensus: string;
    demoNote: string;
  };
  markets: {
    badge: string;
    title: string;
    subtitle: string;
    disclaimerTitle: string;
    disclaimerText: string;
    commodities: string;
    crypto: string;
    forex: string;
    bias: string;
    sentiment: string;
    volatility: string;
    spread: string;
    high24h: string;
    low24h: string;
    timeframe: string;
    connectBackend: string;
  };
  agents: {
    badge: string;
    title: string;
    subtitle: string;
    workflowTitle: string;
    workflowSubtitle: string;
    statusActive: string;
    statusProcessing: string;
    statusConsensus: string;
    statusStandby: string;
    capabilities: string;
    consensusRate: string;
    latency: string;
    integrationNote: string;
  };
  technical: {
    badge: string;
    title: string;
    subtitle: string;
    tabsAll: string;
    tabsSmc: string;
    tabsIct: string;
    tabsClassic: string;
    coreRule: string;
    marketApplication: string;
    viewInAction: string;
  };
  signals: {
    badge: string;
    title: string;
    subtitle: string;
    demoBadge: string;
    demoWarning: string;
    direction: string;
    entry: string;
    stopLoss: string;
    takeProfit1: string;
    takeProfit2: string;
    takeProfit3: string;
    riskReward: string;
    confidence: string;
    confluenceFactors: string;
    validationStatus: string;
    toggleBuy: string;
    toggleSell: string;
    simulatedPips: string;
  };
  features: {
    badge: string;
    title: string;
    subtitle: string;
    exploreAll: string;
  };
  architecture: {
    badge: string;
    title: string;
    subtitle: string;
    specsTitle: string;
    specsSubtitle: string;
    cloudReady: string;
    securityNote: string;
  };
  developer: {
    badge: string;
    title: string;
    subtitle: string;
    role: string;
    bio: string;
    aboutTitle: string;
    aboutText: string;
    skillsTitle: string;
    connectTitle: string;
    verifiedDev: string;
    viewGithub: string;
    viewFacebook: string;
    viewTiktok: string;
    location: string;
    education: string;
    openSourceProjects: string;
  };
  footer: {
    tagline: string;
    description: string;
    quickLinks: string;
    legal: string;
    resources: string;
    social: string;
    disclaimer: string;
    rights: string;
    developerCredit: string;
  };
  modal: {
    title: string;
    subtitle: string;
    demoTag: string;
    systemStatus: string;
    operational: string;
    runScan: string;
    scanning: string;
    scanComplete: string;
    consensusScore: string;
    close: string;
  };
}

export const translations: Record<'en' | 'kh', TranslationDictionary> = {
  en: {
    nav: {
      home: "Home",
      features: "Features",
      agents: "AI Agents",
      markets: "Markets",
      analysis: "Smart Analysis",
      technology: "Architecture",
      developer: "Founder & Dev",
      launch: "Launch ZYROX AI",
      terminalPreview: "Terminal Demo",
    },
    hero: {
      badge: "Institutional AI Trading Engine v4.0",
      titlePart1: "THE FUTURE OF AI",
      titlePart2: "TRADING INTELLIGENCE",
      subtitle: "Experience intelligent market analysis powered by advanced AI agents, multi-market intelligence, and professional trading tools.",
      ctaLaunch: "Launch ZYROX AI",
      ctaFeatures: "Explore Features",
      ctaAgents: "Meet Our AI",
      statsAgents: "Specialized AI Agents",
      statsMarkets: "Global Liquid Markets",
      statsLatency: "Sub-Second Processing",
      statsConsensus: "Multi-Agent Consensus",
      demoNote: "All figures represent institutional research models and educational demonstration.",
    },
    markets: {
      badge: "Real-Time Multi-Asset Intelligence",
      title: "Cross-Market Intelligence Hub",
      subtitle: "Unified telemetry across Commodities, Forex, and Crypto with institutional order flow monitoring.",
      disclaimerTitle: "Illustrative Demonstration Environment",
      disclaimerText: "Data presented is synthetic simulated telemetry for technical demonstration. Real-world order execution connects directly to authenticated MT5/OANDA APIs.",
      commodities: "Commodities & Metals",
      crypto: "Cryptocurrency",
      forex: "Major Forex Pairs",
      bias: "AI Market Bias",
      sentiment: "Market Sentiment",
      volatility: "Volatility Index",
      spread: "Typical Spread",
      high24h: "24h High",
      low24h: "24h Low",
      timeframe: "Chart Timeframe",
      connectBackend: "Connect ZYROX API for Live Stream",
    },
    agents: {
      badge: "Autonomous Multi-Agent Consensus",
      title: "Specialized Intelligence Agents",
      subtitle: "Six autonomous neural agents collaborate in real time to filter market noise and validate trade confluence.",
      workflowTitle: "End-to-End AI Consensus Pipeline",
      workflowSubtitle: "From raw tick ingestion to cryptographic risk gating before any signal approval.",
      statusActive: "Online & Monitoring",
      statusProcessing: "Evaluating Order Flow",
      statusConsensus: "Voting on Confluence",
      statusStandby: "Calibrating Model",
      capabilities: "Core Capabilities",
      consensusRate: "Confluence Threshold",
      latency: "Execution Latency",
      integrationNote: "Agent weights and consensus voting operate in tandem via the FastAPI backend orchestration layer.",
    },
    technical: {
      badge: "Institutional Edge Mechanics",
      title: "Smart Money & ICT Technical Core",
      subtitle: "Algorithmic detection of Liquidity Pools, Order Blocks, and Fair Value Gaps across multiple timeframes.",
      tabsAll: "All Concepts",
      tabsSmc: "Smart Money (SMC)",
      tabsIct: "Inner Circle Trader (ICT)",
      tabsClassic: "Indicators & Confluence",
      coreRule: "Algorithmic Rule",
      marketApplication: "Market Application",
      viewInAction: "Interactive Analysis Breakdown",
    },
    signals: {
      badge: "Verified Setup Architecture",
      title: "Institutional Signal Telemetry",
      subtitle: "Strict multi-gate structure with verified Entry, Invalidation (SL), and scaled Take-Profit targets.",
      demoBadge: "DEMONSTRATION SAMPLE",
      demoWarning: "Simulated demonstration setup. ZYROX AI does not guarantee financial profits or trading outcomes.",
      direction: "Direction Bias",
      entry: "Entry Price",
      stopLoss: "Invalidation (Stop Loss)",
      takeProfit1: "Target 1 (1:2 RR)",
      takeProfit2: "Target 2 (1:3.5 RR)",
      takeProfit3: "Runner Target (1:5 RR)",
      riskReward: "Risk / Reward Ratio",
      confidence: "AI Confidence Score",
      confluenceFactors: "Confluence Signatures",
      validationStatus: "Validation State",
      toggleBuy: "Preview Long (BUY)",
      toggleSell: "Preview Short (SELL)",
      simulatedPips: "Expected R-Multiple",
    },
    features: {
      badge: "Platform Capabilities",
      title: "Engineered for Market Mastery",
      subtitle: "Comprehensive suite of algorithmic and intelligence utilities designed for professional traders and funds.",
      exploreAll: "Explore All Capabilities",
    },
    architecture: {
      badge: "Full-Stack System Topology",
      title: "Resilient Cloud Architecture",
      subtitle: "Engineered with React, Python FastAPI, PostgreSQL, MT5 Bridge, and asynchronous event streams.",
      specsTitle: "Enterprise Engineering Standards",
      specsSubtitle: "Decoupled services guarantee sub-100ms algorithmic scoring and zero single points of failure.",
      cloudReady: "Ready for Render & Cloud Run",
      securityNote: "End-to-end encrypted telemetry with zero client-side credential exposure.",
    },
    developer: {
      badge: "Founder & Lead Architect",
      title: "Built by HENG TAIKRY",
      subtitle: "Pioneering the intersection of Artificial Intelligence, Automated Systems, and Modern Fintech.",
      role: "Founder | Full Stack Developer | AI Engineer",
      bio: "“I build intelligent software solutions, AI-powered applications, fintech systems, and modern digital experiences.”",
      aboutTitle: "Vision & Philosophy",
      aboutText: "ZYROX AI was conceived and engineered by Heng Taikry to bridge the gap between complex algorithmic quantitative finance and accessible, high-precision visual intelligence. Blending full-stack software craftsmanship with autonomous AI agent coordination, the platform delivers institutional-grade analytics for traders worldwide.",
      skillsTitle: "Core Technical Stack",
      connectTitle: "Official Channels & Social Verification",
      verifiedDev: "Verified Identity & Developer Profile",
      viewGithub: "Inspect GitHub Repository",
      viewFacebook: "Connect on Facebook",
      viewTiktok: "Follow on TikTok",
      location: "Phnom Penh, Cambodia",
      education: "Howard University / Digital Creator",
      openSourceProjects: "Flagship Project: ZYROX AI Market Intelligence",
    },
    footer: {
      tagline: "Intelligence Beyond The Market.",
      description: "Next-generation multi-market AI intelligence platform combining autonomous agent consensus, ICT algorithms, and institutional risk governance.",
      quickLinks: "Platform Navigation",
      legal: "Compliance & Governance",
      resources: "Developer & Community",
      social: "Official Creator Channels",
      disclaimer: "ZYROX AI provides analytical tools and educational market insights. Trading involves substantial risk. No profit or trading outcome is guaranteed. Past performance is not indicative of future market results.",
      rights: "All Rights Reserved.",
      developerCredit: "Designed & Developed by HENG TAIKRY",
    },
    modal: {
      title: "ZYROX AI Terminal Simulation",
      subtitle: "Simulated multi-agent consensus scanner running in sandbox environment.",
      demoTag: "SANDBOX MODE",
      systemStatus: "System Telemetry",
      operational: "All 6 Agents Operational",
      runScan: "Run Multi-Agent Consensus Scan",
      scanning: "Neural Agents Analyzing Order Blocks...",
      scanComplete: "Confluence Scan Completed (6/6 Agents Approved)",
      consensusScore: "Consensus Score: 94.6%",
      close: "Close Terminal",
    },
  },
  kh: {
    nav: {
      home: "ទំព័រដើម",
      features: "មុខងារពិសេស",
      agents: "ភ្នាក់ងារ AI",
      markets: "ទីផ្សារហិរញ្ញវត្ថុ",
      analysis: "ការវិភាគបច្ចេកទេស",
      technology: "ស្ថាបត្យកម្ម",
      developer: "ស្ថាបនិក & អ្នកអភិវឌ្ឍន៍",
      launch: "បើក ZYROX AI",
      terminalPreview: "សាកល្បង Terminal",
    },
    hero: {
      badge: "ប្រព័ន្ធវិភាគទីផ្សារ AI កម្រិតស្ថាប័ន v4.0",
      titlePart1: "អនាគតនៃបច្ចេកវិទ្យា",
      titlePart2: "AI វិភាគទីផ្សារហិរញ្ញវត្ថុ",
      subtitle: "ស្វែងយល់ពីអនាគតនៃការវិភាគទីផ្សារជាមួយបច្ចេកវិទ្យា AI ដ៏ឆ្លាតវៃ ភ្នាក់ងារស្វ័យប្រវត្ត និងឧបករណ៍ជួញដូរអាជីព។",
      ctaLaunch: "បើកដំណើរការ ZYROX AI",
      ctaFeatures: "ស្វែងយល់មុខងារ",
      ctaAgents: "ជួបជាមួយ AI របស់យើង",
      statsAgents: "ភ្នាក់ងារ AI ជំនាញពិសេស",
      statsMarkets: "ទីផ្សារសកលសំខាន់ៗ",
      statsLatency: "ល្បឿនវិភាគក្រោម ១ វិនាទី",
      statsConsensus: "ការស្រុះស្រួលពហុភ្នាក់ងារ",
      demoNote: "តួលេខទាំងអស់ជាទិន្នន័យស្រាវជ្រាវគំរូ និងសម្រាប់ការអប់រំបច្ចេកវិទ្យាប៉ុណ្ណោះ។",
    },
    markets: {
      badge: "ទិន្នន័យទីផ្សារពហុទ្រព្យសកម្ម",
      title: "មជ្ឈមណ្ឌលវិភាគទីផ្សារអន្តរជាតិ",
      subtitle: "ត្រួតពិនិត្យចរន្តទីផ្សារទំនិញ (មាស), រូបិយប័ណ្ណបរទេស Forex និងរូបិយប័ណ្ណឌីជីថល Crypto ក្នុងផ្ទាំងតែមួយ។",
      disclaimerTitle: "បរិស្ថានបង្ហាញគំរូ (Demonstration)",
      disclaimerText: "ទិន្នន័យដែលបានបង្ហាញជាការក្លែងបន្លំគំរូបច្ចេកទេស។ ការជួញដូរជាក់ស្តែងនឹងតភ្ជាប់ទៅកាន់ API ផ្ទាល់របស់ MT5 ឬ OANDA។",
      commodities: "ទំនិញ & លោហៈធាតុមានតម្លៃ",
      crypto: "រូបិយប័ណ្ណឌីជីថល",
      forex: "គូរូបិយប័ណ្ណសំខាន់ៗ",
      bias: "ទិសដៅ AI",
      sentiment: "មនោសញ្ចេតនាទីផ្សារ",
      volatility: "កម្រិតបំរែបំរួល",
      spread: "គម្លាតតម្លៃ Spread",
      high24h: "ខ្ពស់បំផុត 24h",
      low24h: "ទាបបំផុត 24h",
      timeframe: "ចន្លោះពេល Timeframe",
      connectBackend: "ភ្ជាប់ ZYROX API សម្រាប់ទិន្នន័យផ្ទាល់",
    },
    agents: {
      badge: "ការស្រុះស្រួលភ្នាក់ងារ AI ស្វ័យប្រវត្ត",
      title: "ភ្នាក់ងារ AI ជំនាញឯកទេស",
      subtitle: "ភ្នាក់ងារ Neural Network ស្វ័យប្រវត្តចំនួន ៦ សហការគ្នាក្នុងពេលជាក់ស្តែង ដើម្បីជម្រុះភាពមិនច្បាស់លាស់ និងផ្ទៀងផ្ទាត់សញ្ញាជួញដូរ។",
      workflowTitle: "លំហូរការងារវិភាគរបស់ AI ទាំងស្រុង",
      workflowSubtitle: "ចាប់ពីការទទួលបានទិន្នន័យ Ticks រហូតដល់ការត្រួតពិនិត្យហានិភ័យមុននឹងអនុម័តសញ្ញា។",
      statusActive: "កំពុងដំណើរការ & តាមដាន",
      statusProcessing: "កំពុងវាយតម្លៃ Order Flow",
      statusConsensus: "កំពុងបោះឆ្នោតផ្ទៀងផ្ទាត់",
      statusStandby: "ត្រៀមលក្ខណៈ & គណនា",
      capabilities: "សមត្ថភាពស្នូល",
      consensusRate: "កម្រិតការស្រុះស្រួល",
      latency: "ល្បឿនដំណើរការ",
      integrationNote: "ទម្ងន់នៃភ្នាក់ងារ និងការបោះឆ្នោតដំណើរការរួមគ្នាលើប្រព័ន្ធ FastAPI Backend Orchestration។",
    },
    technical: {
      badge: "យុទ្ធសាស្ត្រជួញដូរកម្រិតស្ថាប័ន",
      title: "បច្ចេកទេស Smart Money & ICT",
      subtitle: "ការស្វែងរក Liquidity Pools, Order Blocks, និង Fair Value Gaps ដោយស្វ័យប្រវត្តលើពហុ Timeframe។",
      tabsAll: "គោលគំនិតទាំងអស់",
      tabsSmc: "Smart Money (SMC)",
      tabsIct: "Inner Circle Trader (ICT)",
      tabsClassic: "សូចនាករបុរាណ & Confluence",
      coreRule: "គោលការណ៍គណិតវិទ្យា",
      marketApplication: "ការអនុវត្តលើទីផ្សារ",
      viewInAction: "ការវិភាគគំរូលម្អិត",
    },
    signals: {
      badge: "ស្ថាបត្យកម្មសញ្ញាដែលបានផ្ទៀងផ្ទាត់",
      title: "ការបង្ហាញទម្រង់សញ្ញាជួញដូរ",
      subtitle: "រចនាសម្ព័ន្ធតឹងរ៉ឹងជាមួយតម្លៃចូល (Entry), ចំណុចកាត់ខាត (SL), និងគោលដៅប្រាក់ចំណេញ (TP1, TP2, TP3)។",
      demoBadge: "គំរូសម្រាប់បង្ហាញ (DEMO)",
      demoWarning: "នេះជាទម្រង់គំរូសាកល្បង។ ZYROX AI មិនធានាប្រាក់ចំណេញ ឬលទ្ធផលហិរញ្ញវត្ថុណាមួយឡើយ។",
      direction: "ទិសដៅជួញដូរ",
      entry: "តម្លៃចូល (Entry)",
      stopLoss: "ចំណុចកាត់ខាត (SL)",
      takeProfit1: "គោលដៅទី១ (1:2 RR)",
      takeProfit2: "គោលដៅទី២ (1:3.5 RR)",
      takeProfit3: "គោលដៅទី៣ (1:5 RR)",
      riskReward: "សមាមាត្រហានិភ័យ / ផលចំណេញ",
      confidence: "កម្រិតទំនុកចិត្ត AI",
      confluenceFactors: "ភស្តុតាងផ្គុំចូលគ្នា",
      validationStatus: "ស្ថានភាពផ្ទៀងផ្ទាត់",
      toggleBuy: "មើលគំរូ BUY (ទិញ)",
      toggleSell: "មើលគំរូ SELL (លក់)",
      simulatedPips: "សមាមាត្រ R-Multiple រំពឹងទុក",
    },
    features: {
      badge: "សមត្ថភាពនៃប្រព័ន្ធ",
      title: "រចនាឡើងសម្រាប់ភាពជាក់លាក់លើទីផ្សារ",
      subtitle: "កញ្ចប់ឧបករណ៍ឆ្លាតវៃ និងស្វ័យប្រវត្តដែលបង្កើតឡើងសម្រាប់ Trader អាជីព និងស្ថាប័នវិនិយោគ។",
      exploreAll: "ស្វែងយល់មុខងារទាំងអស់",
    },
    architecture: {
      badge: "ស្ថាបត្យកម្មប្រព័ន្ធពេញលេញ",
      title: "ហេដ្ឋារចនាសម្ព័ន្ធ Cloud ប្រកបដោយភាពរឹងមាំ",
      subtitle: "បង្កើតឡើងជាមួយ React, Python FastAPI, PostgreSQL, MT5 Bridge និងប្រព័ន្ធ Asynchronous Event Stream។",
      specsTitle: "ស្តង់ដារវិស្វកម្មកម្រិតសហគ្រាស",
      specsSubtitle: "សេវាកម្មឯករាជ្យធានាល្បឿនគណនាក្រោម 100ms និងគ្មានចំណុចខូចទាំងស្រុងតែមួយ (Zero SPOF)។",
      cloudReady: "ត្រៀមរួចរាល់សម្រាប់ Render & Cloud Run",
      securityNote: "ការការពារទិន្នន័យដោយការបំលែងកូដ End-to-End និងគ្មានការលេចធ្លាយ Credentials នៅ Client-Side។",
    },
    developer: {
      badge: "ស្ថាបនិក & វិស្វករស្ថាបត្យកម្មប្រព័ន្ធ",
      title: "បង្កើតឡើងដោយ HENG TAIKRY",
      subtitle: "ឈានមុខគេក្នុងការរួមបញ្ចូលគ្នានៃបញ្ញាសិប្បនិម្មិត (AI) ប្រព័ន្ធស្វ័យប្រវត្ត និងបច្ចេកវិទ្យាហិរញ្ញវត្ថុទំនើប។",
      role: "Founder | Full Stack Developer | AI Engineer",
      bio: "“ខ្ញុំបង្កើតប្រព័ន្ធ Software ឆ្លាតវៃ កម្មវិធី AI និងបច្ចេកវិទ្យាហិរញ្ញវត្ថុទំនើប។”",
      aboutTitle: "ទស្សនវិស័យ និងគោលជំហរ",
      aboutText: "ZYROX AI ត្រូវបានបង្កើតឡើង និងអភិវឌ្ឍន៍ដោយ ហេង តៃគ្រី (Heng Taikry) ក្នុងគោលបំណងផ្សារភ្ជាប់រវាងការវិភាគហិរញ្ញវត្ថុកម្រិតខ្ពស់ និងផ្ទាំងទស្សន៍ទាយដែលងាយស្រួលយល់ និងមានភាពជាក់លាក់ខ្ពស់។ ដោយរួមបញ្ចូលការអភិវឌ្ឍ Software ពេញលេញជាមួយការសម្របសម្រួលភ្នាក់ងារ AI ស្វ័យប្រវត្ត ប្រព័ន្ធនេះផ្តល់នូវការវិភាគកម្រិតស្ថាប័នដល់អ្នកជួញដូរជុំវិញពិភពលោក។",
      skillsTitle: "ជំនាញបច្ចេកទេសស្នូល",
      connectTitle: "បណ្តាញទំនាក់ទំនងផ្លូវការ",
      verifiedDev: "អត្តសញ្ញាណ និងប្រវត្តិរូបអ្នកអភិវឌ្ឍន៍ពិតប្រាកដ",
      viewGithub: "ចូលមើលកូដលើ GitHub",
      viewFacebook: "ភ្ជាប់ទំនាក់ទំនងលើ Facebook",
      viewTiktok: "តាមដានលើ TikTok",
      location: "រាជធានីភ្នំពេញ កម្ពុជា",
      education: "Howard University / Digital Creator",
      openSourceProjects: "គម្រោងស្នូល: ZYROX AI Market Intelligence",
    },
    footer: {
      tagline: "ភាពវៃឆ្លាតលើសពីទីផ្សារ។",
      description: "ប្រព័ន្ធ AI វិភាគទីផ្សារហិរញ្ញវត្ថុជំនាន់ថ្មី ដែលរួមបញ្ចូលការស្រុះស្រួលរបស់ភ្នាក់ងារស្វ័យប្រវត្ត ក្បួនដោះស្រាយ ICT និងការគ្រប់គ្រងហានិភ័យកម្រិតស្ថាប័ន។",
      quickLinks: "ការរុករកក្នុងប្រព័ន្ធ",
      legal: "ច្បាប់ និងអនុលោមភាព",
      resources: "អ្នកអភិវឌ្ឍន៍ និងសហគមន៍",
      social: "បណ្តាញផ្លូវការរបស់ស្ថាបនិក",
      disclaimer: "ZYROX AI ផ្តល់ជូននូវឧបករណ៍វិភាគ និងការយល់ដឹងអំពីទីផ្សារសម្រាប់គោលបំណងអប់រំប៉ុណ្ណោះ។ ការជួញដូរមានហានិភ័យខ្ពស់។ គ្មានប្រាក់ចំណេញ ឬលទ្ធផលជួញដូរណាមួយត្រូវបានធានាឡើយ។ លទ្ធផលកន្លងមកមិនមែនជាការធានានូវលទ្ធផលនាពេលអនាគតទេ។",
      rights: "រក្សាសិទ្ធិគ្រប់យ៉ាង។",
      developerCredit: "រចនា និងអភិវឌ្ឍន៍ដោយ HENG TAIKRY",
    },
    modal: {
      title: "ការសាកល្បង ZYROX AI Terminal",
      subtitle: "ម៉ាស៊ីនស្កេនស្រុះស្រួលរបស់ភ្នាក់ងារ AI កំពុងដំណើរការក្នុងបរិស្ថាន Sandbox។",
      demoTag: "ទម្រង់សាកល្បង (SANDBOX)",
      systemStatus: "ស្ថានភាពប្រព័ន្ធ",
      operational: "ភ្នាក់ងារ AI ទាំង ៦ កំពុងដំណើរការយ៉ាងរលូន",
      runScan: "ដំណើរការស្កេនស្រុះស្រួល AI",
      scanning: "ភ្នាក់ងារ Neural កំពុងស្កេន Order Blocks...",
      scanComplete: "ការស្កេនបានបញ្ចប់ដោយជោគជ័យ (៦/៦ ភ្នាក់ងារបានអនុម័ត)",
      consensusScore: "ពិន្ទុស្រុះស្រួល: ៩៤.៦%",
      close: "បិទផ្ទាំង Terminal",
    },
  },
};

