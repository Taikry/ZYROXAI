import { PlatformFeature } from '../types';

export const PLATFORM_FEATURES: PlatformFeature[] = [
  {
    id: "ai-copilot",
    titleEn: "AI Copilot Assistant",
    titleKh: "ជំនួយការឆ្លាតវៃ AI Copilot",
    descEn: "Natural language conversational trader that explains technical confluence, answers portfolio questions, and runs on-demand multi-asset scans.",
    descKh: "ជំនួយការជជែកឆ្លាតវៃដែលពន្យល់ពីហេតុផលបច្ចេកទេស ឆ្លើយសំណួរអំពីផលប័ត្រ និងស្កេនទីផ្សារតាមការស្នើសុំ។",
    icon: "Bot",
    badgeEn: "INTERACTIVE",
    badgeKh: "អន្តរកម្ម",
    metrics: "< 80ms Response"
  },
  {
    id: "ai-agents",
    titleEn: "Multi-Agent Consensus System",
    titleKh: "ប្រព័ន្ធស្រុះស្រួលពហុភ្នាក់ងារ AI",
    descEn: "Six independent neural agents cross-validate market structure, volatility, and macro news before reaching cryptographic consensus.",
    descKh: "ភ្នាក់ងារឯករាជ្យចំនួន ៦ ត្រួតពិនិត្យរចនាសម្ព័ន្ធទីផ្សារ កម្រិតបំរែបំរួល និងព័ត៌មាន មុននឹងឈានដល់ការសម្រេចចិត្តរួម។",
    icon: "Users",
    badgeEn: "AUTONOMOUS",
    badgeKh: "ស្វ័យប្រវត្ត",
    metrics: "6 Active Agents"
  },
  {
    id: "smart-technical",
    titleEn: "Smart Technical Analysis",
    titleKh: "ការវិភាគបច្ចេកទេសឆ្លាតវៃ",
    descEn: "Automated real-time plotting of Order Blocks, Fair Value Gaps, Liquidity Sweeps, and key supply/demand imbalances directly on your chart.",
    descKh: "គូសបង្ហាញ Order Blocks, Fair Value Gaps, Liquidity Sweeps និងតុល្យភាពផ្គត់ផ្គង់-តម្រូវការលើតារាងដោយស្វ័យប្រវត្ត។",
    icon: "Activity",
    badgeEn: "PRECISION",
    badgeKh: "ភាពជាក់លាក់",
    metrics: "14+ SMC Indicators"
  },
  {
    id: "best-setups",
    titleEn: "Best Setup Recommendations",
    titleKh: "ការណែនាំឱកាសជួញដូរល្អបំផុត",
    descEn: "High-probability algorithmic trade setups scored by historical edge, multi-factor confluence, and expected risk-adjusted return.",
    descKh: "រៀបចំឱកាសជួញដូរដែលមានប្រូបាប៊ីលីតេខ្ពស់ ដោយផ្អែកលើទិន្នន័យប្រវត្តិសាស្ត្រ និងការផ្គុំភស្តុតាងជាច្រើន។",
    icon: "Sparkles",
    badgeEn: "ALGORITHMIC",
    badgeKh: "ក្បួនគណិត",
    metrics: "R:R >= 1:2.0"
  },
  {
    id: "multi-market",
    titleEn: "Multi-Market Intelligence",
    titleKh: "ការតាមដានពហុទីផ្សារសកល",
    descEn: "Simultaneous institutional tracking of Commodities (Gold, Silver), Forex Majors, and Cryptocurrencies (Bitcoin, Ethereum, Solana).",
    descKh: "តាមដានទីផ្សារអន្តរជាតិសំខាន់ៗក្នុងពេលតែមួយ រួមមាន មាស (Gold), ប្រាក់ (Silver), Forex និងរូបិយប័ណ្ណឌីជីថល (Crypto)។",
    icon: "Globe2",
    badgeEn: "REAL-TIME",
    badgeKh: "ពេលជាក់ស្តែង",
    metrics: "20+ Liquid Assets"
  },
  {
    id: "trading-heatmap",
    titleEn: "Dynamic Trading Heatmap",
    titleKh: "តារាងកំដៅទីផ្សារ Trading Heatmap",
    descEn: "Visual multi-timeframe correlation matrix revealing real-time institutional capital rotation across currency sectors and asset classes.",
    descKh: "តារាងម៉ាទ្រីសដែលបង្ហាញពីចរន្តលំហូរដើមទុនរបស់ស្ថាប័នរវាងវិស័យរូបិយប័ណ្ណ និងប្រភេទទ្រព្យសកម្មនីមួយៗ។",
    icon: "Grid",
    badgeEn: "HEATMAP",
    badgeKh: "ម៉ាទ្រីសកំដៅ",
    metrics: "6 Timeframes"
  },
  {
    id: "trading-journal",
    titleEn: "Automated Trading Journal",
    titleKh: "កំណត់ហេតុជួញដូរស្វ័យប្រវត្ត",
    descEn: "Automatic logging of every signal, entry, stop loss, target hit, and post-trade performance analytics with zero manual data entry required.",
    descKh: "កត់ត្រារាល់សញ្ញាជួញដូរ តម្លៃចូល ចំណុចកាត់ខាត និងលទ្ធផលសម្រេចដោយស្វ័យប្រវត្ត ដោយមិនចាំបាច់បញ្ចូលដោយដៃ។",
    icon: "BookOpen",
    badgeEn: "ANALYTICS",
    badgeKh: "ស្ថិតិវិភាគ",
    metrics: "100% Automated"
  },
  {
    id: "backtesting",
    titleEn: "Walk-Forward Strategy Backtesting",
    titleKh: "ការធ្វើតេស្តយុទ្ធសាស្ត្រ Backtesting",
    descEn: "Rigorous historical simulation engine with Monte Carlo simulations, slippage modeling, and maximum drawdown stress tests.",
    descKh: "ម៉ាស៊ីនតេស្តទិន្នន័យប្រវត្តិសាស្ត្រកម្រិតខ្ពស់ រួមជាមួយការគណនា Slippage និងការវាយតម្លៃសម្ពាធ Drawdown។",
    icon: "History",
    badgeEn: "QUANTITATIVE",
    badgeKh: "បរិមាណវិភាគ",
    metrics: "Tick-by-Tick Engine"
  },
  {
    id: "news-intelligence",
    titleEn: "Market News Intelligence",
    titleKh: "ការវិភាគព័ត៌មានម៉ាក្រូសេដ្ឋកិច្ច",
    descEn: "Real-time NLP sentiment parsing of central bank statements, CPI inflation data, and economic calendar volatility windows.",
    descKh: "ការវិភាគមនោសញ្ចេតនាលើសេចក្តីថ្លែងការណ៍ធនាគារកណ្តាល អតិផរណា CPI និងប្រតិទិនសេដ្ឋកិច្ចដោយបច្ចេកវិទ្យា NLP។",
    icon: "Newspaper",
    badgeEn: "NLP SENTIMENT",
    badgeKh: "បច្ចេកវិទ្យា NLP",
    metrics: "Global Feeds"
  },
  {
    id: "telegram-alerts",
    titleEn: "Instant Telegram Alerts",
    titleKh: "ការជូនដំណឹងរហ័សតាម Telegram",
    descEn: "Rich bilingual alerts dispatched within milliseconds to private Telegram channels with chart snapshots, entry, SL, and TP levels.",
    descKh: "ការជូនដំណឹងជាពីភាសាភ្លាមៗទៅកាន់ Telegram ជាមួយរូបភាពតារាងបច្ចេកទេស តម្លៃចូល SL និងកម្រិត TP ច្បាស់លាស់។",
    icon: "Send",
    badgeEn: "LIGHTNING",
    badgeKh: "ល្បឿនផ្លេកបន្ទោរ",
    metrics: "< 50ms Push"
  },
  {
    id: "risk-management",
    titleEn: "Institutional Risk Management",
    titleKh: "ការគ្រប់គ្រងហានិភ័យកម្រិតស្ថាប័ន",
    descEn: "Dynamic lot calculation based on portfolio equity, maximum risk percentage caps per trade (1-2%), and automated breakeven triggers.",
    descKh: "គណនាទំហំ Lot ដោយស្វ័យប្រវត្តតាមទំហំដើមទុន កំណត់ហានិភ័យត្រឹម ១-២% ក្នុងមួយបញ្ជា និងរុញ SL ទៅ Breakeven ដោយស្វ័យប្រវត្ត។",
    icon: "ShieldCheck",
    badgeEn: "GOVERNANCE",
    badgeKh: "សុវត្ថិភាពខ្ពស់",
    metrics: "Strict 1-2% Rule"
  },
  {
    id: "mtf-analysis",
    titleEn: "Multi-Timeframe Analysis",
    titleKh: "ការវិភាគតម្រឹមពហុចន្លោះពេល",
    descEn: "Simultaneous scanning of Monthly, Weekly, Daily, 4-Hour, 1-Hour, 15-Minute, and 5-Minute structures for true fractal alignment.",
    descKh: "ការស្កេនរចនាសម្ព័ន្ធ Monthly, Weekly, Daily, 4H, 1H, 15M និង 5M ក្នុងពេលតែមួយ ដើម្បីទទួលបានការតម្រឹមទិសដៅពិតប្រាកដ។",
    icon: "Maximize2",
    badgeEn: "FRACTAL",
    badgeKh: "រចនាសម្ព័ន្ធ Fractal",
    metrics: "M to 5M Coverage"
  }
];

