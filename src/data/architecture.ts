import { ArchitectureNode } from '../types';

export const ARCHITECTURE_LAYERS: ArchitectureNode[] = [
  {
    step: 1,
    titleEn: "Frontend Dashboard",
    titleKh: "ផ្ទាំងគ្រប់គ្រង Frontend",
    tech: "React 19 + TypeScript + Tailwind + Motion",
    roleEn: "High-density institutional trading cockpit with real-time reactive updates and sub-second renders.",
    roleKh: "ផ្ទាំងបញ្ជាជួញដូរកម្រិតស្ថាប័ន ជាមួយការធ្វើបច្ចុប្បន្នភាពទិន្នន័យភ្លាមៗ និងក្រាហ្វិកច្បាស់លាស់។",
    detailEn: "Virtual DOM optimizations, glassmorphic design token system, and zero-layout-shift responsive viewport scaling.",
    detailKh: "ការបង្កើនល្បឿន Virtual DOM, ប្រព័ន្ធរចនា Glassmorphic និងការបង្ហាញសមស្របគ្រប់ទំហំអេក្រង់។",
    icon: "Layout"
  },
  {
    step: 2,
    titleEn: "Backend API Gateway",
    titleKh: "ច្រកទ្វារ Backend API",
    tech: "Python FastAPI + Uvicorn + Asynchronous Workers",
    roleEn: "High-throughput asynchronous REST endpoints and WebSocket channels for tick streaming and user authentication.",
    roleKh: "សេវា REST API និង WebSocket ល្បឿនលឿនសម្រាប់បញ្ជូនទិន្នន័យ Ticks និងគ្រប់គ្រងសុវត្ថិភាពអ្នកប្រើប្រាស់។",
    detailEn: "Non-blocking event loop handling hundreds of concurrent connection requests with Pydantic type safety.",
    detailKh: "ប្រព័ន្ធ Non-blocking Event Loop គ្រប់គ្រងការភ្ជាប់ច្រើនក្នុងពេលតែមួយជាមួយសុវត្ថិភាពទិន្នន័យ Pydantic។",
    icon: "Server"
  },
  {
    step: 3,
    titleEn: "AI Orchestration Layer",
    titleKh: "ស្រទាប់សម្របសម្រួល AI",
    tech: "Dynamic Agent Consensus Router & Arbiter",
    roleEn: "Distributes market state to specialized agents, aggregates evaluation vectors, and executes consensus voting.",
    roleKh: "បែងចែកទិន្នន័យទីផ្សារទៅកាន់ភ្នាក់ងារឯកទេស ប្រមូលពិន្ទុវាយតម្លៃ និងអនុវត្តការបោះឆ្នោតស្រុះស្រួល។",
    detailEn: "Enforces 80% minimum confluence gate before generating validated signal payloads.",
    detailKh: "តម្រូវឱ្យមានការយល់ព្រមយ៉ាងតិច ៨០% មុនពេលអនុញ្ញាតឱ្យបង្កើតសញ្ញាជួញដូរផ្លូវការ។",
    icon: "Cpu"
  },
  {
    step: 4,
    titleEn: "Specialized AI Agents",
    titleKh: "ភ្នាក់ងារ AI ជំនាញឯកទេស",
    tech: "6 Autonomous Neural & Algorithmic Agents",
    roleEn: "Parallel execution of Market Regime, Technical Indicators, ICT SMC structures, Risk Sizing, and News Sentiment.",
    roleKh: "ដំណើរការស្របគ្នានូវការវិភាគរបបទីផ្សារ សូចនាករបច្ចេកទេស រចនាសម្ព័ន្ធ ICT SMC និងព័ត៌មានម៉ាក្រូ។",
    detailEn: "Sub-50ms execution window per agent with isolated memory state and deterministic math bounds.",
    detailKh: "ដំណើរការក្រោម 50ms សម្រាប់ភ្នាក់ងារនីមួយៗ ជាមួយអង្គចងចាំដាច់ដោយឡែក និងក្បួនគណិតច្បាស់លាស់។",
    icon: "BrainCircuit"
  },
  {
    step: 5,
    titleEn: "Market Data Services",
    titleKh: "សេវាទិន្នន័យទីផ្សារ",
    tech: "MetaTrader 5 Bridge + OANDA + Binance REST/WS",
    roleEn: "Multi-market tick aggregation, spread monitoring, and live order book order-flow telemetry.",
    roleKh: "ប្រមូលទិន្នន័យ Ticks ពហុទីផ្សារ ត្រួតពិនិត្យគម្លាត Spread និងចរន្តបញ្ជាទិញ-លក់ក្នុងពេលជាក់ស្តែង។",
    detailEn: "Self-healing socket connections with automated reconnection buffers and heartbeat monitoring.",
    detailKh: "ការភ្ជាប់បណ្តាញ Socket ដែលអាចជួសជុលខ្លួនឯងបាន និងមានប្រព័ន្ធពិនិត្យសុខភាព Heartbeat 24/7។",
    icon: "RadioReceiver"
  },
  {
    step: 6,
    titleEn: "Database & Audit Persistence",
    titleKh: "មូលដ្ឋានទិន្នន័យ & កំណត់ត្រាប្រតិបត្តិការ",
    tech: "PostgreSQL 16 + SQLAlchemy ORM + Alembic Migrations",
    roleEn: "ACID-compliant storage of historical signals, user subscriptions, Bakong/ABA payment ledger, and audit logs.",
    roleKh: "រក្សាទុកទិន្នន័យប្រវត្តិសញ្ញា ការជាវសមាជិក បញ្ជីទូទាត់ប្រាក់ Bakong/ABA និងកំណត់ត្រាសវនកម្ម។",
    detailEn: "Indexed relational tables guaranteeing instant retrieval of backtest samples and walk-forward verification.",
    detailKh: "តារាងទិន្នន័យ Indexed Relational ធានាការទាញយកទិន្នន័យ Backtest បានរហ័សទាន់ចិត្ត។",
    icon: "Database"
  }
];

