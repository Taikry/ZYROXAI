import { AIAgent } from '../types';

export const AI_AGENTS: AIAgent[] = [
  {
    id: "market-analysis",
    nameEn: "Market Analysis Agent",
    nameKh: "ភ្នាក់ងារវិភាគបរិបទទីផ្សារ",
    roleEn: "Macro Regime & Volume Profiler",
    roleKh: "អ្នកវាយតម្លៃចរន្តបរិមាណ និងស្ថានភាពម៉ាក្រូ",
    descriptionEn: "Identifies dominant market regime (Trend, Range, Accumulation, Distribution) and gauges institutional order flow dynamics.",
    descriptionKh: "កំណត់ស្ថានភាពទីផ្សារ (Trend, Range, Accumulation) និងវាស់ស្ទង់ចរន្តបញ្ជាទិញ-លក់របស់ស្ថាប័នធំៗ។",
    status: "ACTIVE",
    capabilitiesEn: ["Regime Classification", "Order Flow Footprints", "Volume Profile POC", "Liquidity Density"],
    capabilitiesKh: ["កំណត់ប្រភេទ Regime", "វិភាគ Order Flow", " Volume Profile POC", "ដង់ស៊ីតេ Liquidity"],
    icon: "TrendingUp",
    latencyMs: 42,
    confidence: 96
  },
  {
    id: "technical-analysis",
    nameEn: "Technical Analysis Agent",
    nameKh: "ភ្នាក់ងារវិភាគបច្ចេកទេសពហុចន្លោះពេល",
    roleEn: "Multi-Timeframe Trend Specialist",
    roleKh: "អ្នកជំនាញរចនាសម្ព័ន្ធពហុ Timeframe",
    descriptionEn: "Computes exponential moving average alignment (20/50/200), multi-timeframe RSI momentum divergence, and ATR dynamic bands.",
    descriptionKh: "គណនាតម្រឹមខ្សែ EMA (20/50/200), ការបង្វែរ Momentum នៃ RSI ពហុ Timeframe និងគម្លាត ATR បែបឌីណាមិក។",
    status: "PROCESSING",
    capabilitiesEn: ["EMA Alignment 20/50/200", "RSI Momentum Divergence", "ATR Volatility Expansion", "Key SR Boundaries"],
    capabilitiesKh: ["តម្រឹម EMA 20/50/200", "RSI Divergence", "ការពង្រីក ATR Volatility", "បន្ទាត់ទប់ SR សំខាន់"],
    icon: "BarChart3",
    latencyMs: 38,
    confidence: 94
  },
  {
    id: "ict-concepts",
    nameEn: "ICT Concepts Agent",
    nameKh: "ភ្នាក់ងារវិភាគក្បួនដោះស្រាយ ICT & SMC",
    roleEn: "Smart Money Structure Scanner",
    roleKh: "អ្នកស្កេនរចនាសម្ព័ន្ធលុយឆ្លាតវៃ",
    descriptionEn: "Scans for Order Blocks, Fair Value Gaps (FVG), Buy/Sell Side Liquidity Sweeps, and structural Breaks of Structure (BOS / CHoCH).",
    descriptionKh: "ស្វែងរក Order Blocks, Fair Value Gaps (FVG), ការបោសសម្អាត Liquidity Sweeps និងការបំបែករចនាសម្ព័ន្ធ (BOS / CHoCH)។",
    status: "ACTIVE",
    capabilitiesEn: ["Order Block Mapping", "FVG Imbalance Detection", "Liquidity Sweep Triggers", "CHoCH & BOS Signatures"],
    capabilitiesKh: ["កំណត់ទីតាំង Order Block", "រកឃើញ FVG Imbalance", "ចាប់យក Liquidity Sweep", "សញ្ញា CHoCH & BOS"],
    icon: "Layers",
    latencyMs: 51,
    confidence: 98
  },
  {
    id: "risk-management",
    nameEn: "Risk Management Agent",
    nameKh: "ភ្នាក់ងារគ្រប់គ្រងហានិភ័យស្ថាប័ន",
    roleEn: "Capital Preservation Guard",
    roleKh: "អ្នកការពារដើមទុន និងគ្រប់គ្រងទំហំបញ្ជា",
    descriptionEn: "Enforces strict mathematical R:R thresholds (minimum 1:2.0), position size calculations, and daily drawdown protection gates.",
    descriptionKh: "អនុវត្តសមាមាត្រ R:R យ៉ាងហោចណាស់ 1:2.0 គណនាទំហំ Position និងកំណត់កម្រិតខាតអតិបរមាប្រចាំថ្ងៃ។",
    status: "ACTIVE",
    capabilitiesEn: ["Dynamic R:R Gate (>= 1:2)", "Lot Sizing Optimization", "Drawdown Circuit Breakers", "Correlation Hedging"],
    capabilitiesKh: ["ត្រួតពិនិត្យ R:R (>= 1:2)", "បង្កើនប្រសិទ្ធភាពទំហំ Lot", "ប្រព័ន្ធកាត់បន្ថយ Drawdown", "ការកាត់បន្ថយ Hedging"],
    icon: "ShieldAlert",
    latencyMs: 19,
    confidence: 99
  },
  {
    id: "signal-validation",
    nameEn: "Signal Validation Agent",
    nameKh: "ភ្នាក់ងារផ្ទៀងផ្ទាត់ និងសម្រេចសញ្ញា",
    roleEn: "Consensus Arbiter & Gatekeeper",
    roleKh: "អាជ្ញាកណ្តាលបោះឆ្នោតស្រុះស្រួលសញ្ញា",
    descriptionEn: "Requires minimum 80% weighted consensus across all peer agents before authorizing any signal dispatch or webhook alert.",
    descriptionKh: "ទាមទារការបោះឆ្នោតគាំទ្រយ៉ាងតិច ៨០% ពីគ្រប់ភ្នាក់ងារទាំងអស់ មុនពេលអនុញ្ញាតឱ្យបញ្ជូនសញ្ញាជួញដូរ។",
    status: "CONSENSUS",
    capabilitiesEn: ["Multi-Agent Weighted Voting", "Confirmation Candle Closes", "False Breakout Filtering", "Webhook Dispatch Gate"],
    capabilitiesKh: ["ការបោះឆ្នោតទម្ងន់ពហុភ្នាក់ងារ", "ផ្ទៀងផ្ទាត់ទៀនបិទ", "ច្រោះការបំបែកក្លែងក្លាយ", "ច្រកបញ្ជូន Webhook"],
    icon: "CheckCheck",
    latencyMs: 31,
    confidence: 95
  },
  {
    id: "news-intelligence",
    nameEn: "Market News Intelligence Agent",
    nameKh: "ភ្នាក់ងារព័ត៌មាន និងម៉ាក្រូសេដ្ឋកិច្ច",
    roleEn: "Economic Sentiment & Event Filter",
    roleKh: "អ្នកតាមដានព័ត៌មាន និងព្រឹត្តិការណ៍សេដ្ឋកិច្ច",
    descriptionEn: "Parses high-impact macroeconomic releases (CPI, NFP, FOMC) and automatically activates blackout protection windows around volatility spikes.",
    descriptionKh: "វិភាគព្រឹត្តិការណ៍សេដ្ឋកិច្ចធំៗ (CPI, NFP, FOMC) និងបិទប្រព័ន្ធជួញដូរជាបណ្តោះអាសន្នក្នុងអំឡុងពេលប្រកាសព័ត៌មានគ្រោះថ្នាក់។",
    status: "ACTIVE",
    capabilitiesEn: ["High-Impact Event Blackouts", "NLP Sentiment Extraction", "Central Bank Rate Shifts", "Volatility Surge Previews"],
    capabilitiesKh: ["ផ្អាកពេលមានព័ត៌មានធំៗ", "វិភាគមនោសញ្ចេតនា NLP", "ការផ្លាស់ប្តូរអត្រាការប្រាក់", "ព្យាករណ៍ការកើនឡើង Volatility"],
    icon: "Radio",
    latencyMs: 64,
    confidence: 91
  }
];

export const AI_WORKFLOW_STEPS = [
  {
    step: 1,
    titleEn: "Market Data Ingestion",
    titleKh: "ការទទួលទិន្នន័យទីផ្សារ",
    descEn: "Real-time tick capture via MT5 Bridge & multi-asset providers",
    descKh: "ចាប់យកទិន្នន័យ Ticks តាម MT5 Bridge និងប្រភពទិន្នន័យសកល",
    agent: "Market Analysis Agent",
    time: "12ms"
  },
  {
    step: 2,
    titleEn: "Technical Analysis",
    titleKh: "ការវិភាគបច្ចេកទេស",
    descEn: "EMA alignment, multi-timeframe momentum, and ATR expansion",
    descKh: "តម្រឹមខ្សែ EMA, Momentum ពហុចន្លោះពេល និងគម្លាត ATR",
    agent: "Technical Analysis Agent",
    time: "24ms"
  },
  {
    step: 3,
    titleEn: "ICT Concept Detection",
    titleKh: "ការរករចនាសម្ព័ន្ធ ICT",
    descEn: "Order Block mapping, Fair Value Gap validation, and Liquidity Sweeps",
    descKh: "កំណត់ Order Block, ផ្ទៀងផ្ទាត់ FVG និង Liquidity Sweeps",
    agent: "ICT Concepts Agent",
    time: "38ms"
  },
  {
    step: 4,
    titleEn: "Risk Validation Gate",
    titleKh: "ច្រកត្រួតពិនិត្យហានិភ័យ",
    descEn: "Mathematical R:R validation (>= 1:2.0) and position size calculations",
    descKh: "ផ្ទៀងផ្ទាត់សមាមាត្រ R:R (>= 1:2.0) និងទំហំបញ្ជាជួញដូរ",
    agent: "Risk Management Agent",
    time: "18ms"
  },
  {
    step: 5,
    titleEn: "AI Multi-Agent Consensus",
    titleKh: "ការបោះឆ្នោតស្រុះស្រួល AI",
    descEn: "Weighted consensus threshold verification (>= 80% agreement)",
    descKh: "ការផ្ទៀងផ្ទាត់ពិន្ទុស្រុះស្រួលរួម (ទាមទារយ៉ាងតិច ៨០%)",
    agent: "Signal Validation Agent",
    time: "22ms"
  },
  {
    step: 6,
    titleEn: "Final Trading Analysis",
    titleKh: "ការបង្កើតសញ្ញាសម្រេច",
    descEn: "Institutional report generation with Telegram & Webhook dispatch",
    descKh: "បង្កើតរបាយការណ៍ស្ថាប័ន រួមជាមួយការជូនដំណឹង Telegram",
    agent: "Orchestration Engine",
    time: "15ms"
  }
];

