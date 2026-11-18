/**
 * ZYROX AI V6.2.1 — Institutional Interactive Dashboard Tutorial & Spotlight Walkthrough
 * 
 * Features:
 * - 14 Comprehensive Step-by-Step Guides covering every Dashboard capability
 * - Real DOM Spotlight Cutout with dynamic position tracking and smooth auto-scroll
 * - Natural, institutional bilingual support (English and Khmer)
 * - Immediate language switching without progress loss
 * - Full responsiveness: smart desktop popover + mobile bottom-sheet docking
 * - Persistent backend state: onboarding_completed, onboarding_step, tutorial_version
 * - Keyboard accessibility: Alt+T (Start), Esc (Close), ArrowRight (Next), ArrowLeft (Prev)
 */
(function (window, document) {
  "use strict";

  let currentStepIndex = 0;
  let isTutorialActive = false;
  let cachedUserOnboarding = null;

  const ZYROX_TUTORIAL_STEPS = [
    {
      id: "overview",
      icon: "📊",
      selector: ["#btn-nav-overview", "#top-btn-account"],
      pane: "overview",
      title_en: "1. Dashboard Overview",
      title_kh: "១. ទិដ្ឋភាពទូទៅនៃ Dashboard",
      subtitle_en: "Real-time command center & telemetry",
      subtitle_kh: "មជ្ឈមណ្ឌលបញ្ជា និងតាមដានស្ថានភាពប្រព័ន្ធ",
      what_is_it_en: "The Overview tab gives an instant high-level summary of active global market sessions, MT5 bridge freshness, and multi-asset scanner metrics.",
      what_is_it_kh: "ផ្ទាំងទិដ្ឋភាពទូទៅផ្តល់នូវព័ត៌មានសង្ខេបអំពីវគ្គជួញដូរសកល (London/NY/Asia), ភាពស្រស់នៃទិន្នន័យ MT5 និងការត្រួតពិនិត្យឧបករណ៍ហិរញ្ញវត្ថុរហ័ស។",
      instructions_en: [
        "Review current active market session (London, New York, or Asian overlap).",
        "Check system status and verified quote latency.",
        "Use quick-launch buttons to inspect institutional setups."
      ],
      instructions_kh: [
        "ពិនិត្យវគ្គជួញដូរសកម្មបច្ចុប្បន្ន (London, New York ឬ Asian).",
        "ផ្ទៀងផ្ទាត់ស្ថានភាពប្រព័ន្ធ និង Latency នៃតម្លៃ.",
        "ចុចប៊ូតុងរហ័សដើម្បីពិនិត្យមើល Setup ស្ថាប័ន."
      ],
      expected_en: "Live session indicators, data freshness status, and fast market screening rows.",
      expected_kh: "សូចនាករវគ្គជួញដូរផ្ទាល់, ស្ថានភាពទិន្នន័យ និងតារាងសង្ខេបទីផ្សាររហ័ស។",
      tip_en: "The best institutional trading opportunities typically occur during London / New York session overlap (13:00 - 17:00 UTC).",
      tip_kh: "ឱកាសជួញដូរស្ថាប័នល្អបំផុតច្រើនកើតឡើងនៅពេលជាន់គ្នារវាងវគ្គ London និង New York (13:00 - 17:00 UTC)។",
      warning_en: "Never execute trades when market data feed reports STALE or DISCONNECTED.",
      warning_kh: "កុំចូលជួញដូរដាច់ខាតនៅពេលប្រព័ន្ធបង្ហាញស្ថានភាពទិន្នន័យ STALE ឬ DISCONNECTED។"
    },
    {
      id: "market_data",
      icon: "💰",
      selector: [".active-symbol-pill", "#top-active-ticker"],
      pane: "charts",
      title_en: "2. XAUUSD Live Market Data",
      title_kh: "២. ទិន្នន័យផ្សារផ្ទាល់ XAUUSD",
      subtitle_en: "Executable Gold spot prices & bid/ask spread",
      subtitle_kh: "តម្លៃមាសផ្ទាល់ Bid/Ask Spread និងស្ថានភាពផ្សារ",
      what_is_it_en: "This ticker displays verified real-time XAUUSD pricing directly from your configured broker feed with live bid, ask, and spread tracking.",
      what_is_it_kh: "ផ្ទាំង Ticker នេះបង្ហាញតម្លៃមាស XAUUSD ផ្ទាល់ពី Broker របស់អ្នក ដោយរួមមានតម្លៃ Bid, Ask, Spread និងភាពស្រស់នៃទិន្នន័យ។",
      instructions_en: [
        "Observe the live bid and ask quotes for spread widening.",
        "Click the pill to switch between XAUUSD and other monitored assets.",
        "Confirm the market state displays 'Open' before planning entries."
      ],
      instructions_kh: [
        "សង្កេតតម្លៃ Bid និង Ask ដើម្បីដឹងពីការរីកធំនៃ Spread.",
        "ចុចលើ Pill នេះដើម្បីប្តូររវាង XAUUSD និងរូបិយប័ណ្ណផ្សេងៗ.",
        "ផ្ទៀងផ្ទាត់ថាស្ថានភាពទីផ្សារបង្ហាញ 'Open' មុនពេលរៀបចំការជួញដូរ."
      ],
      expected_en: "Real-time tick updates with green/red flashing on price changes.",
      expected_kh: "ការផ្លាស់ប្តូរតម្លៃភ្លាមៗជាមួយភ្លើងពណ៌បៃតង/ក្រហមពេលតម្លៃប្រែប្រួល។",
      tip_en: "A tight spread (< 25 points on standard MT5) signifies optimal liquidity.",
      tip_kh: "Spread តូច (< 25 points លើ MT5) បញ្ជាក់ពីសន្ទុះសាច់ប្រាក់ងាយស្រួលល្អបំផុត។",
      warning_en: "During high-impact news releases (NFP, CPI, FOMC), spreads can widen substantially.",
      warning_kh: "អំឡុងពេលព័ត៌មានធំៗចេញផ្សាយ (NFP, CPI, FOMC) Spread អាចកើនឡើងខ្លាំង។"
    },
    {
      id: "mt5_connection",
      icon: "🔌",
      selector: ["#top-bridge-status-pill"],
      pane: null,
      title_en: "3. Exness MT5 Connection Status",
      title_kh: "៣. ស្ថានភាពភ្ជាប់ Exness MT5",
      subtitle_en: "Windows MT5 bridge telemetry & quote authorization",
      subtitle_kh: "ការតភ្ជាប់ទៅកាន់កម្មវិធី Exness MT5 លើ Windows",
      what_is_it_en: "The MT5 status pill monitors your local Windows Exness terminal bridge. Under ZYROX safety rules, only MT5 quotes can authorize executable signals.",
      what_is_it_kh: "ប៊ូតុងនេះបង្ហាញស្ថានភាពតភ្ជាប់ទៅកាន់ Exness MT5 លើ Windows។ តាមច្បាប់សុវត្ថិភាព ZYROX មានតែតម្លៃពី MT5 ប៉ុណ្ណោះដែលអាចបញ្ជាក់សញ្ញាជួញដូរបាន។",
      instructions_en: [
        "Click this pill to open the MT5 Bridge management modal.",
        "Ensure the status dot is GREEN ('CONNECTED · EXECUTABLE').",
        "If STANDBY or OFFLINE, verify that python bridge is running on your Windows terminal."
      ],
      instructions_kh: [
        "ចុចលើប៊ូតុងនេះដើម្បីបើកផ្ទាំងគ្រប់គ្រង MT5 Bridge.",
        "ត្រូវប្រាកដថាភ្លើងមានពណ៌បៃតង ('CONNECTED · EXECUTABLE').",
        "ប្រសិនបើ STANDBY ឬ OFFLINE សូមពិនិត្យមើលថាតើ Python Bridge កំពុងដំណើរការដែរឬទេ។"
      ],
      expected_en: "Latency metrics, broker name (Exness), and tick freshness counters.",
      expected_kh: "កម្រិត Latency, ឈ្មោះ Broker (Exness) និងចំនួន Ticks ស្រស់ដែលទទួលបាន។",
      tip_en: "Reference feeds like OANDA and Yahoo remain available for macro viewing, but MT5 is the sole executable benchmark.",
      tip_kh: "ប្រភព OANDA និង Yahoo ប្រើសម្រាប់យោងតែប៉ុណ្ណោះ មានតែ MT5 ដែលជាប្រភពជួញដូរផ្លូវការ។",
      warning_en: "The signal engine automatically locks into WAIT mode if MT5 bridge is disconnected.",
      warning_kh: "ប្រព័ន្ធវិភាគនឹងប្តូរទៅ WAIT Mode ដោយស្វ័យប្រវត្តិប្រសិនបើ MT5 ត្រូវបានផ្តាច់។"
    },
    {
      id: "ai_analysis",
      icon: "🧠",
      selector: ["#btn-cockpit-analyze", "#btn-nav-analysis"],
      pane: "charts",
      title_en: "4. AI Market Analysis",
      title_kh: "៤. ការវិភាគទីផ្សារដោយ AI",
      subtitle_en: "Institutional SMC & multi-timeframe engine",
      subtitle_kh: "ម៉ាស៊ីនវិភាគស្ថាប័នពហុពេលវេលា (ICT & SMC)",
      what_is_it_en: "Triggers multi-timeframe deep algorithmic scans combining Order Flow, Liquidity Sweeps, Fair Value Gaps (FVG), and Break of Structure (BOS).",
      what_is_it_kh: "ដំណើរការការវិភាគក្បួនដោះស្រាយពហុពេលវេលា ដោយរួមបញ្ចូល Order Flow, Liquidity Sweeps, Fair Value Gaps (FVG) និង Break of Structure (BOS)។",
      instructions_en: [
        "Select your desired trading timeframe (M5, M15, H1, H4).",
        "Click the golden 'ANALYZE' button in the cockpit.",
        "Wait for the institutional scanner to compute confluence metrics."
      ],
      instructions_kh: [
        "ជ្រើសរើស Timeframe ដែលចង់វិភាគ (M5, M15, H1, H4).",
        "ចុចប៊ូតុងពណ៌មាស 'ANALYZE' នៅលើផ្ទាំង Cockpit.",
        "រង់ចាំម៉ាស៊ីនស្កេនគណនាពិន្ទុ Confluence ស្ថាប័ន."
      ],
      expected_en: "Market bias (BULLISH/BEARISH/NEUTRAL), key support/resistance levels, and confluence score.",
      expected_kh: "ទិសដៅទីផ្សារ (BULLISH/BEARISH/NEUTRAL), កម្រិតគន្លឹះ និងពិន្ទុ Confluence។",
      tip_en: "Higher timeframes (H1/H4) provide greater directional reliability than M5 scalping.",
      tip_kh: "Timeframe ធំ (H1/H4) ផ្តល់នូវភាពជឿជាក់ខ្ពស់ជាង Timeframe តូច M5។",
      warning_en: "Do not spam the analyze button repeatedly; allow each scan to finish its multi-agent evaluation.",
      warning_kh: "កុំចុចប៊ូតុងវិភាគញឹកញាប់ពេក សូមទុកពេលឱ្យប្រព័ន្ធបញ្ចប់ការគណនាពេញលេញ។"
    },
    {
      id: "best_setup",
      icon: "🎯",
      selector: ["#disp-best-setup-box", "#disp-setup-status"],
      pane: "charts",
      title_en: "5. Best Setup Recommendations",
      title_kh: "៥. អនុសាសន៍ Setup ល្អបំផុត",
      subtitle_en: "High-probability entry, stop loss, and target levels",
      subtitle_kh: "កម្រិតចូលផ្សារ (Entry), Stop Loss និងគោលដៅចំណេញ",
      what_is_it_en: "Displays the single highest-probability trading setup identified by ZYROX AI, complete with entry zone, stop loss, take profit targets, and invalidation criteria.",
      what_is_it_kh: "បង្ហាញនូវ Setup ជួញដូរដែលមានប្រូបាប៊ីលីតេខ្ពស់បំផុត រួមជាមួយតំបន់ចូល (Entry), Stop Loss, គោលដៅ Take Profit និងលក្ខខណ្ឌមោឃភាព។",
      instructions_en: [
        "Review the setup status badge (e.g. 'VALID SETUP' or 'WAIT / NO TRADE').",
        "Inspect the proposed Risk-to-Reward ratio (minimum 1:2 R:R required).",
        "Check confirmation checklist: Liquidity Sweep + FVG Re-test + Confluence >= 75."
      ],
      instructions_kh: [
        "ពិនិត្យមើលស្លាកស្ថានភាព Setup (ឧ. 'VALID SETUP' ឬ 'WAIT / NO TRADE').",
        "ត្រួតពិនិត្យសមាមាត្រ Risk-to-Reward (យ៉ាងតិច 1:2 R:R).",
        "ផ្ទៀងផ្ទាត់បញ្ជីលក្ខខណ្ឌ៖ Liquidity Sweep + FVG Re-test + ពិន្ទុ Confluence >= 75."
      ],
      expected_en: "Clear entry price, stop-loss protection, multiple take-profit milestones (TP1, TP2, TP3).",
      expected_kh: "តម្លៃចូលច្បាស់លាស់, កម្រិត Stop Loss ការពារដើមទុន, និងគោលដៅ TP1, TP2, TP3។",
      tip_en: "When the setup status indicates 'WAIT / NO TRADE', patience is your greatest edge.",
      tip_kh: "នៅពេលប្រព័ន្ធបង្ហាញ 'WAIT / NO TRADE' ការអត់ធ្មត់គឺជាយុទ្ធសាស្ត្រល្អបំផុតរបស់អ្នក។",
      warning_en: "Never enter a trade if price has already crossed the Stop Loss invalidation line.",
      warning_kh: "កុំចូលជួញដូរដាច់ខាតប្រសិនបើតម្លៃបានឆ្លងកាត់បន្ទាត់ Stop Loss រួចទៅហើយ។"
    },
    {
      id: "live_chart",
      icon: "📈",
      selector: ["#tv_chart_container", "#btn-nav-charts"],
      pane: "charts",
      title_en: "6. Live Interactive Trading Chart",
      title_kh: "៦. ក្រាហ្វិកជួញដូរផ្ទាល់",
      subtitle_en: "Institutional candlestick canvas & drawings",
      subtitle_kh: "ក្រាហ្វិកទៀនជប៉ុនជាមួយការគូស Key Levels ស្វ័យប្រវត្តិ",
      what_is_it_en: "Institutional lightweight financial chart rendering candlesticks, auto-detected Liquidity Sweeps, Fair Value Gaps (FVG), Volume Profile, and Market Structure.",
      what_is_it_kh: "ក្រាហ្វិកហិរញ្ញវត្ថុទំនើបដែលបង្ហាញទៀនជប៉ុន, ការស្វែងរក Liquidity Sweeps ដោយស្វ័យប្រវត្តិ, Fair Value Gaps (FVG) និងរចនាសម្ព័ន្ធទីផ្សារ។",
      instructions_en: [
        "Scroll with your mouse wheel or pinch on mobile to zoom in/out.",
        "Click and drag to pan across historical bars.",
        "Use the timeframe selector pills at the top of the canvas to switch intervals."
      ],
      instructions_kh: [
        "រំកិលកង់ Mouse ឬពង្រីកលើអេក្រង់ទូរស័ព្ទដើម្បី Zoom In/Out.",
        "ចុចទាញដើម្បីមើលទិន្នន័យប្រវត្តិសាស្ត្រ.",
        "ប្រើប៊ូតុង Timeframe ខាងលើក្រាហ្វិកដើម្បីប្តូរចន្លោះពេល (M5, M15, H1, H4, D1)."
      ],
      expected_en: "Smooth 60 FPS candlestick charts with overlaid institutional zones and session dividers.",
      expected_kh: "ក្រាហ្វិកទៀនរលូនកម្រិត 60 FPS ជាមួយតំបន់ស្ថាប័ន និងបន្ទាត់ចែកវគ្គជួញដូរ។",
      tip_en: "Use keyboard shortcut 'Alt+3' anywhere in the terminal to jump directly back to the chart.",
      tip_kh: "ប្រើ Shortcut 'Alt+3' ដើម្បីត្រលប់មកផ្ទាំងក្រាហ្វិកវិញបានភ្លាមៗគ្រប់ពេលវេលា។",
      warning_en: "Avoid adding dozens of conflicting traditional lagging indicators; keep your canvas clean.",
      warning_kh: "ជៀសវាងការដាក់ Indicator ច្រើនពេកដែលធ្វើឱ្យស្មុគស្មាញដល់ការមើល Price Action។"
    },
    {
      id: "ai_agents",
      icon: "🤖",
      selector: ["#cockpit-agents-strip", "#btn-nav-debate"],
      pane: "charts",
      title_en: "7. AI Agents Consensus Fleet",
      title_kh: "៧. ក្រុមភ្នាក់ងារ AI និងការស្របមតិ",
      subtitle_en: "5 specialized neural agents with quorum governance",
      subtitle_kh: "ភ្នាក់ងារ AI ទាំង ៥ និងប្រព័ន្ធបោះឆ្នោតស្របមតិ",
      what_is_it_en: "ZYROX AI employs 5 distinct agents: Sentinel (Microstructure), Quantitative (Order Flow), Risk Manager (Veto Guard), Macro (Catalysts), and Strategy Lead.",
      what_is_it_kh: "ZYROX AI ប្រើភ្នាក់ងារ AI ចំនួន ៥ ផ្សេងគ្នា៖ Sentinel (រចនាសម្ព័ន្ធ), Quant (លំហូរសាច់ប្រាក់), Risk Manager (ការពារហានិភ័យ), Macro (សេដ្ឋកិច្ច) និង Strategy Lead។",
      instructions_en: [
        "Observe the consensus quorum gauge in the sidebar.",
        "Check each agent card for individual stance (BULLISH, BEARISH, NEUTRAL).",
        "A signal requires at least 60% agreement AND zero Risk Manager vetoes."
      ],
      instructions_kh: [
        "សង្កេតរង្វាស់សម្លេងស្របមតិ (Consensus Quorum) នៅលើ Sidebar.",
        "ពិនិត្យជំហររបស់ភ្នាក់ងារនីមួយៗ (BULLISH, BEARISH, NEUTRAL).",
        "សញ្ញាជួញដូរទាមទារសម្លេងគាំទ្រយ៉ាងតិច ៦០% និងគ្មានការជំទាស់ពី Risk Manager។"
      ],
      expected_en: "Agent telemetry cards showing live voting weight, confidence scores, and brief rationale.",
      expected_kh: "កាតទិន្នន័យភ្នាក់ងារ AI ដែលបង្ហាញពិន្ទុទំនុកចិត្ត និងហេតុផលសង្ខេប។",
      tip_en: "If the Risk Manager agent issues a VETO, the setup is blocked immediately regardless of other agents.",
      tip_kh: "ប្រសិនបើ Risk Manager ធ្វើការ VETO (ជំទាស់) សញ្ញាជួញដូរនឹងត្រូវរារាំងភ្លាមៗ។",
      warning_en: "Agent consensus reflects real algorithmic analysis, never simulated or randomized scores.",
      warning_kh: "សម្លេងស្របមតិរបស់ភ្នាក់ងារគឺកើតចេញពីការវិភាគពិតប្រាកដ មិនមែនជាទិន្នន័យក្លែងក្លាយឡើយ។"
    },
    {
      id: "signals",
      icon: "⚡",
      selector: ["#btn-nav-signals"],
      pane: "signals",
      title_en: "8. Trading Signals Center",
      title_kh: "៨. មជ្ឈមណ្ឌលសញ្ញាជួញដូរ (Signals)",
      subtitle_en: "Institutional confluence >= 75/100 verified setups",
      subtitle_kh: "សញ្ញាជួញដូរដែលមានពិន្ទុ Confluence >= ៧៥/១០០",
      what_is_it_en: "The Signal Center stores real-time and historical XAUUSD signals that have satisfied strict multi-filter validation (Confluence >= 75, Quorum >= 60%).",
      what_is_it_kh: "មជ្ឈមណ្ឌលសញ្ញាជួញដូរកត់ត្រារាល់សញ្ញា XAUUSD ផ្ទាល់ និងប្រវត្តិ ដែលបានឆ្លងកាត់ការត្រួតពិនិត្យតឹងរ៉ឹង (Confluence >= 75, Quorum >= 60%)។",
      instructions_en: [
        "Click '5. Signal Center' in the navigation bar (Alt+5).",
        "Inspect active signal cards for execution mode (PAPER/SHADOW).",
        "Read detailed technical thesis before deciding to replicate in your brokerage."
      ],
      instructions_kh: [
        "ចុច '5. Signal Center' លើរបារ Menu (Alt+5).",
        "ពិនិត្យកាតសញ្ញាសកម្មសម្រាប់ទម្រង់ប្រតិបត្តិ (PAPER/SHADOW).",
        "អានការពន្យល់លម្អិតពីមូលហេតុបច្ចេកទេសមុនពេលសម្រេចចិត្តជួញដូរ។"
      ],
      expected_en: "Signal card with timestamp, symbol, action (BUY/SELL), entry price, SL, TP1-3, and confluence.",
      expected_kh: "កាតសញ្ញាជាមួយពេលវេលា, គូជួញដូរ, សកម្មភាព (BUY/SELL), តម្លៃចូល, SL, TP1-3 និងពិន្ទុ Confluence។",
      tip_en: "Signals are strictly XAUUSD only for verified accuracy and safety.",
      tip_kh: "សញ្ញាជួញដូរត្រូវបានកំណត់ត្រឹមតែមាស XAUUSD ប៉ុណ្ណោះ ដើម្បីធានាភាពសុក្រឹតខ្ពស់បំផុត។",
      warning_en: "ZYROX AI provides analysis and intelligence only; automatic broker execution is not performed.",
      warning_kh: "ZYROX AI ផ្តល់នូវការវិភាគនិងសញ្ញាយោងតែប៉ុណ្ណោះ មិនមានការកាត់ប្រាក់ឬបើក Order ស្វ័យប្រវត្តិឡើយ។"
    },
    {
      id: "risk_mgmt",
      icon: "🛡️",
      selector: ["#cockpit-risk-profile", "#btn-nav-risk"],
      pane: "charts",
      title_en: "9. Risk Management Engine",
      title_kh: "៩. ការគ្រប់គ្រងហានិភ័យ (Risk Management)",
      subtitle_en: "Dynamic position sizing, R:R protection, and loss caps",
      subtitle_kh: "ការគណនាទំហំ Lot សុវត្ថិភាព និងដែនកំណត់ខាតបង់",
      what_is_it_en: "Enforces strict mathematical capital preservation rules with selectable risk tiers: Conservative (0.8%), Balanced (1.5%), or Aggressive (2.5%).",
      what_is_it_kh: "អនុវត្តច្បាប់ការពារដើមទុនយ៉ាងតឹងរ៉ឹងជាមួយជម្រើសកម្រិតហានិភ័យ៖ Conservative (0.8%), Balanced (1.5%) ឬ Aggressive (2.5%)។",
      instructions_en: [
        "Choose your preferred Risk Profile dropdown in the Pro Cockpit.",
        "Set your account capital to calculate exact recommended Lot Size.",
        "Respect the system maximum daily loss ceiling (2.5% max)."
      ],
      instructions_kh: [
        "ជ្រើសរើស Risk Profile ដែលអ្នកពេញចិត្តនៅលើ Cockpit.",
        "បញ្ចូលដើមទុនគណនីរបស់អ្នកដើម្បីឱ្យប្រព័ន្ធគណនាទំហំ Lot សុវត្ថិភាព.",
        "គោរពដែនកំណត់ខាតបង់អតិបរមាប្រចាំថ្ងៃ (មិនលើសពី 2.5%)។"
      ],
      expected_en: "Real-time lot sizing recommendations, maximum dollar risk, and drawdown alarms.",
      expected_kh: "ការណែនាំទំហំ Lot ជាក់លាក់, ចំនួនទឹកប្រាក់ប្រឈមហានិភ័យ និងការជូនដំណឹង Drawdown។",
      tip_en: "Professional prop firm traders rarely risk more than 0.5% - 1.0% per trade setup.",
      tip_kh: "Trader អាជីពស្ថាប័នកម្រប្រថុយហានិភ័យលើសពី 0.5% ទៅ 1.0% ក្នុងមួយ Trade ណាស់។",
      warning_en: "Over-leveraging is the #1 cause of retail trading failure. Never disable stop loss limits.",
      warning_kh: "ការប្រើប្រាស់ទំហំ Lot ធំជ្រុលគឺជាមូលហេតុចម្បងនៃការបាត់បង់ដើមទុន។ ហាមដោះ Stop Loss ដាច់ខាត។"
    },
    {
      id: "backtesting",
      icon: "🧪",
      selector: ["#btn-nav-analytics"],
      pane: "analytics",
      title_en: "10. Backtesting & Walk-Forward Validation",
      title_kh: "១០. ការធ្វើតេស្តត្រលប់ក្រោយ (Backtest)",
      subtitle_en: "Historical simulation & multi-regime statistical audit",
      subtitle_kh: "ការធ្វើតេស្តស្ថិតិប្រវត្តិសាស្ត្រដើម្បីវាស់ស្ទង់ Win Rate",
      what_is_it_en: "The Analytics engine stress-tests ZYROX strategies across historical trend, ranging, and high-volatility market regimes without lookahead bias.",
      what_is_it_kh: "ម៉ាស៊ីន Analytics ធ្វើតេស្តយុទ្ធសាស្ត្រ ZYROX ជាមួយទិន្នន័យអតីតកាលលើគ្រប់ស្ថានភាពទីផ្សារ (Trend, Ranging, Volatile) ដោយគ្មានភាពលម្អៀង។",
      instructions_en: [
        "Navigate to '7. Performance Analytics' in the sidebar (Alt+7).",
        "Review historical Win Rate, Profit Factor, and Expectancy metrics.",
        "Inspect trade distribution charts across London and New York hours."
      ],
      instructions_kh: [
        "ចូលទៅកាន់ '7. Performance Analytics' លើ Menu ឆ្វេង (Alt+7).",
        "ពិនិត្យ Win Rate ជាមធ្យម, Profit Factor និង Expectancy.",
        "មើលក្រាហ្វិកបែងចែកការជួញដូរតាមម៉ោង London និង New York."
      ],
      expected_en: "Verified statistical performance graphs, maximum historical drawdown, and recovery curves.",
      expected_kh: "ក្រាហ្វិកស្ថិតិដែលបានផ្ទៀងផ្ទាត់, កម្រិត Drawdown អតិបរមា និងតារាងផលចំណេញ។",
      tip_en: "Look for strategies with a Profit Factor above 1.8 and a maximum historical drawdown below 8%.",
      tip_kh: "ស្វែងរកយុទ្ធសាស្ត្រដែលមាន Profit Factor លើសពី 1.8 និង Drawdown អតិបរមាក្រោម 8%។",
      warning_en: "Past backtested performance is an essential guide but cannot guarantee future market behavior.",
      warning_kh: "ទិន្នន័យប្រវត្តិសាស្ត្រគឺជាមគ្គុទ្ទេសក៍ដ៏សំខាន់ ប៉ុន្តែមិនធានា ១០០% លើទីផ្សារអនាគតឡើយ។"
    },
    {
      id: "trading_journal",
      icon: "📓",
      selector: ["#btn-open-trade-journal"],
      pane: null,
      title_en: "11. Institutional Trading Journal",
      title_kh: "១១. សៀវភៅកត់ត្រាការជួញដូរ (Trading Journal)",
      subtitle_en: "Paper trade execution tracking & mistake diagnostics",
      subtitle_kh: "កត់ត្រាការជួញដូរ Paper Trade និងការវិភាគកំហុសដោយ AI",
      what_is_it_en: "A dedicated institutional logbook recording every simulated and paper trade, including psychological notes, screenshots, emotions, and AI post-trade review.",
      what_is_it_kh: "សៀវភៅកំណត់ហេតុជួញដូរស្ថាប័នដែលកត់ត្រារាល់ការ Trade បែប Paper Trade ដោយរួមមានកំណត់ចំណាំចិត្តសាស្ត្រ និងការវិភាគកែលម្អដោយ AI។",
      instructions_en: [
        "Click the 'Journal' button in the top header or press Alt+J.",
        "Log entry price, actual exit, emotions, and mistake tags.",
        "Receive automated AI feedback on your discipline and execution quality."
      ],
      instructions_kh: [
        "ចុចប៊ូតុង 'Journal' នៅលើរបារខាងលើ ឬចុច Alt+J.",
        "កត់ត្រាតម្លៃចូល, ចំណុចចេញ, អារម្មណ៍ និងស្លាកកំហុស.",
        "ទទួលការផ្តល់យោបល់កែលម្អដោយស្វ័យប្រវត្តិពី AI លើវិន័យជួញដូររបស់អ្នក។"
      ],
      expected_en: "Complete trading history, cumulative PnL curve, and execution scorecards.",
      expected_kh: "ប្រវត្តិការជួញដូរពេញលេញ, ខ្សែកោង PnL សរុប និងតារាងពិន្ទុវិន័យ។",
      tip_en: "Reviewing your losing trades weekly in the journal is the fastest route to consistently profitable trading.",
      tip_kh: "ការពិនិត្យមើល Trade ដែលខាតបង់រៀងរាល់ចុងសប្តាហ៍គឺជាវិធីលឿនបំផុតដើម្បីអភិវឌ្ឍខ្លួន។",
      warning_en: "Be completely honest in your journal; hiding mistakes prevents long-term improvement.",
      warning_kh: "សូមកត់ត្រាដោយស្មោះត្រង់ ព្រោះការលាក់កំហុសនឹងរារាំងដល់ការរីកចម្រើនរបស់អ្នក។"
    },
    {
      id: "ai_copilot",
      icon: "💬",
      selector: [".btn-ask-ai"],
      pane: null,
      title_en: "12. AI Copilot Chat Assistant",
      title_kh: "១២. ជំនួយការឆ្លាតវៃ AI Copilot",
      subtitle_en: "Natural language market Q&A, ICT tutor, and setup checker",
      subtitle_kh: "ជជែកសាកសួរផ្ទាល់ពីក្បួន ICT, ព័ត៌មានទីផ្សារ និងផែនការជួញដូរ",
      what_is_it_en: "An institutional conversational AI assistant powered by your configured LLM gateway (Groq, Gemini, DeepSeek, Claude, or deterministic Quant).",
      what_is_it_kh: "ជំនួយការសន្ទនា AI ឆ្លាតវៃដែលដំណើរការដោយ LLM Gateway (Groq, Gemini, DeepSeek, Claude ឬ Quant) សម្រាប់ឆ្លើយតបសំណួរទីផ្សារ។",
      instructions_en: [
        "Click the glowing 'Ask AI' button in the top header or press Alt+C.",
        "Type your question in natural English or Khmer (e.g. 'What is current XAUUSD bias?').",
        "Ask Copilot to explain any ICT concept like Order Block or Liquidity Sweep."
      ],
      instructions_kh: [
        "ចុចប៊ូតុង 'Ask AI' នៅលើរបារខាងលើ ឬចុច Alt+C.",
        "សួរសំណួររបស់អ្នកជាភាសាខ្មែរ ឬអង់គ្លេស (ឧ. 'តើទិសដៅមាសថ្ងៃនេះយ៉ាងម៉េចដែរ?').",
        "ស្នើសុំ Copilot ពន្យល់ពីក្បួន ICT ដូចជា Order Block ឬ FVG។"
      ],
      expected_en: "Precise, structured, institutional responses with cited price levels and technical explanations.",
      expected_kh: "ចម្លើយច្បាស់លាស់តាមលក្ខណៈស្ថាប័ន ជាមួយកម្រិតតម្លៃជាក់លាក់ និងការពន្យល់បច្ចេកទេស។",
      tip_en: "You can ask Copilot to review a specific trade idea before entering: 'I want to buy Gold at 2650 with SL at 2642, critique this plan.'",
      tip_kh: "អ្នកអាចឱ្យ Copilot ជួយត្រួតពិនិត្យផែនការមុនចូលជួញដូរ៖ 'ខ្ញុំចង់ Buy មាសនៅ 2650 SL 2642 តើល្អទេ?'។",
      warning_en: "AI Copilot offers educational market perspectives; it does not provide personalized financial advice.",
      warning_kh: "AI Copilot ផ្តល់នូវទស្សនៈអប់រំបច្ចេកទេសទីផ្សារ មិនមែនជាការផ្តល់ប្រឹក្សាហិរញ្ញវត្ថុផ្លូវការឡើយ។"
    },
    {
      id: "telegram",
      icon: "✈️",
      selector: ["#btn-nav-telegram"],
      pane: "telegram",
      title_en: "13. Telegram Signals & Bot Integration",
      title_kh: "១៣. ការជូនដំណឹងតាម Telegram",
      subtitle_en: "Instant mobile push alerts with charts & daily performance",
      subtitle_kh: "ទទួលសញ្ញាជួញដូរភ្លាមៗតាម Telegram Bot ជាមួយរូបភាពក្រាហ្វិក",
      what_is_it_en: "Connects your account to the official ZYROX AI Telegram Bot for real-time mobile push notifications whenever a verified confluence trade setup triggers.",
      what_is_it_kh: "ភ្ជាប់គណនីរបស់អ្នកទៅកាន់ ZYROX AI Telegram Bot ផ្លូវការ ដើម្បីទទួលការជូនដំណឹងភ្លាមៗលើទូរស័ព្ទដៃនៅពេលមានសញ្ញាជួញដូរ។",
      instructions_en: [
        "Navigate to '10. Telegram Alerts & Bot' in the sidebar.",
        "Click the 'Connect Telegram Bot' button to link your account via deep-link.",
        "Configure custom notification filters (entry alerts, take-profit hit, daily summary)."
      ],
      instructions_kh: [
        "ចូលទៅកាន់ '10. Telegram Alerts & Bot' លើ Menu ឆ្វេង.",
        "ចុចប៊ូតុង 'Connect Telegram Bot' ដើម្បីភ្ជាប់គណនីរបស់អ្នក.",
        "កំណត់ជម្រើសជូនដំណឹងតាមតម្រូវការ (សញ្ញាចូល, ពេលដល់ TP, សង្ខេបប្រចាំថ្ងៃ)។"
      ],
      expected_en: "Telegram signal message with symbol, direction, entry, SL, TP1-3, chart snapshot, and confluence score.",
      expected_kh: "សារសញ្ញាលើ Telegram ជាមួយរូបភាពក្រាហ្វិក, តម្លៃចូល, SL, TP1-3 និងពិន្ទុ Confluence។",
      tip_en: "Signal delivery is strictly rate-limited (max 4 per day) to preserve highest quality and avoid spam.",
      tip_kh: "ការផ្ញើសញ្ញាត្រូវបានកំណត់យ៉ាងច្រើន ៤ ដងក្នុងមួយថ្ងៃ ដើម្បីធានាបាននូវគុណភាពខ្ពស់បំផុត។",
      warning_en: "Only rely on signals from the verified official bot username: @ZyroxAiTradingBot.",
      warning_kh: "សូមជឿជាក់តែលើ Bot ផ្លូវការដែលមាន Username ត្រឹមត្រូវ៖ @ZyroxAiTradingBot។"
    },
    {
      id: "account_settings",
      icon: "⚙️",
      selector: ["#top-btn-account", "#btn-nav-account"],
      pane: "account",
      title_en: "14. Account, Profile & Settings",
      title_kh: "១៤. គណនី ប្រវត្តិរូប និងការកំណត់",
      subtitle_en: "Subscription tier, single-device session security, and language",
      subtitle_kh: "កញ្ចប់ Subscription, សុវត្ថិភាពឧបករណ៍ Login និងភាសា",
      what_is_it_en: "Manage your personal profile, 14-day Pro trial entitlement, active sign-in sessions (single-device protection), password security, and language preferences.",
      what_is_it_kh: "គ្រប់គ្រងប្រវត្តិរូបផ្ទាល់ខ្លួន, សិទ្ធិប្រើប្រាស់សាកល្បង Pro 14 ថ្ងៃ, ប្រវត្តិឧបករណ៍ Sign-in (សុវត្ថិភាពឧបករណ៍តែមួយ), ពាក្យសម្ងាត់ និងភាសា។",
      instructions_en: [
        "Click the 'Account' button in the top header or visit '/dashboard/profile'.",
        "Review your active subscription plan and daily scan quota.",
        "Inspect Device History to verify no unauthorized logins have occurred.",
        "Click 'Account settings' to update your name, phone number, or password."
      ],
      instructions_kh: [
        "ចុចប៊ូតុង 'Account' នៅខាងលើ ឬចូលទៅកាន់ '/dashboard/profile'.",
        "ពិនិត្យមើលកញ្ចប់ Subscription និងកូតាស្កេនប្រចាំថ្ងៃរបស់អ្នក.",
        "ពិនិត្យប្រវត្តិ Device History ដើម្បីធានាថាមិនមានការលួច Login.",
        "ចុច 'Account settings' ដើម្បីកែសម្រួលឈ្មោះ, លេខទូរស័ព្ទ ឬពាក្យសម្ងាត់។"
      ],
      expected_en: "Clean institutional profile cards showing plan details, user info, verified badges, and active session devices.",
      expected_kh: "កាតប្រវត្តិរូបស្អាតទាក់ទាញ បង្ហាញព័ត៌មានគម្រោង, ព័ត៌មានអ្នកប្រើ, សញ្ញា Verified និងឧបករណ៍សកម្ម។",
      tip_en: "You can restart this interactive tutorial at any time by clicking the 'Dashboard Tutorial' button in the top header or from the Help Center.",
      tip_kh: "អ្នកអាចចាប់ផ្តើមមគ្គុទ្ទេសក៍នេះឡើងវិញគ្រប់ពេល ដោយចុចប៊ូតុង 'Dashboard Tutorial' នៅលើរបារខាងលើ។",
      warning_en: "Logging into your account from a new device automatically signs out any previously active sessions for security.",
      warning_kh: "ការ Login លើឧបករណ៍ថ្មីនឹង Sign out ឧបករណ៍ចាស់ដោយស្វ័យប្រវត្តិ ដើម្បីការពារសុវត្ថិភាពគណនីរបស់អ្នក។"
    }
  ];

  function getTutorialTargetElement(step) {
    if (!step || !step.selector) return null;
    const selectors = Array.isArray(step.selector) ? step.selector : [step.selector];
    for (let i = 0; i < selectors.length; i++) {
      const el = document.querySelector(selectors[i]);
      if (el && (el.offsetWidth > 0 || el.offsetHeight > 0)) {
        return el;
      }
    }
    for (let i = 0; i < selectors.length; i++) {
      const el = document.querySelector(selectors[i]);
      if (el) return el;
    }
    return null;
  }

  function startInteractiveTutorial(isManual = false, initialStep = 1) {
    const backdrop = document.getElementById("zyrox-tutorial-backdrop");
    if (!backdrop) return;

    isTutorialActive = true;
    backdrop.classList.remove("tutorial-hidden");

    let targetStep = initialStep;
    if (!isManual && cachedUserOnboarding && cachedUserOnboarding.step) {
      targetStep = cachedUserOnboarding.step;
    }

    currentStepIndex = Math.max(0, Math.min(ZYROX_TUTORIAL_STEPS.length - 1, targetStep - 1));
    renderTutorialStep(currentStepIndex);

    // Save initial open state if manual
    if (isManual) {
      persistOnboardingState(currentStepIndex + 1, false, false);
    }
  }

  function renderTutorialStep(index) {
    if (index < 0 || index >= ZYROX_TUTORIAL_STEPS.length) return;
    currentStepIndex = index;

    const step = ZYROX_TUTORIAL_STEPS[index];
    const isKhmer = Boolean(window.isKhmer || document.body.classList.contains("khmer-mode"));

    // 1. Switch to appropriate tab if step requires it
    if (step.pane && typeof window.switchNavPane === "function") {
      try {
        window.switchNavPane(step.pane);
      } catch (err) {
        console.debug("Tutorial pane switch note:", err);
      }
    }

    // 2. Update step counter & progress bar
    const stepNum = index + 1;
    const totalSteps = ZYROX_TUTORIAL_STEPS.length;
    const counterEl = document.getElementById("tutorial-step-counter");
    if (counterEl) {
      counterEl.textContent = isKhmer ? `ជំហានទី ${stepNum} នៃ ${totalSteps}` : `Step ${stepNum} of ${totalSteps}`;
    }

    const progBar = document.getElementById("tutorial-progress-bar");
    if (progBar) {
      const pct = Math.round((stepNum / totalSteps) * 100);
      progBar.style.width = pct + "%";
    }

    // 3. Update icon, title, subtitle
    const iconEl = document.getElementById("tutorial-step-icon");
    if (iconEl) iconEl.textContent = step.icon || "💡";

    const titleEl = document.getElementById("tutorial-card-title");
    if (titleEl) titleEl.textContent = isKhmer ? step.title_kh : step.title_en;

    const subEl = document.getElementById("tutorial-card-subtitle");
    if (subEl) subEl.textContent = isKhmer ? step.subtitle_kh : step.subtitle_en;

    // 4. Update body content
    const bodyEl = document.getElementById("tutorial-card-body");
    if (bodyEl) {
      const whatIsIt = isKhmer ? step.what_is_it_kh : step.what_is_it_en;
      const instructions = isKhmer ? step.instructions_kh : step.instructions_en;
      const expected = isKhmer ? step.expected_kh : step.expected_en;
      const tip = isKhmer ? step.tip_kh : step.tip_en;
      const warning = isKhmer ? step.warning_kh : step.warning_en;

      const instListHtml = Array.isArray(instructions)
        ? `<ol class="tutorial-steps-list">${instructions.map(it => `<li>${it}</li>`).join("")}</ol>`
        : "";

      bodyEl.innerHTML = `
        <div class="tutorial-section-lead">${whatIsIt}</div>
        <div style="font-weight: 700; color: #FFFFFF; font-size: 12px; margin-top: 10px;">
          ${isKhmer ? "របៀបប្រើប្រាស់ជំហានបន្ទាប់៖" : "Step-by-step instructions:"}
        </div>
        ${instListHtml}
        <div style="font-size: 11.5px; color: #9CA3AF; margin-top: 6px;">
          <b style="color: #E5E7EB;">${isKhmer ? "លទ្ធផលរំពឹងទុក៖ " : "Expected Output: "}</b>${expected}
        </div>
        ${tip ? `<div class="tutorial-tip-box">💡 <b>${isKhmer ? "គន្លឹះស្ថាប័ន៖ " : "Pro Tip: "}</b>${tip}</div>` : ""}
        ${warning ? `<div class="tutorial-warn-box">⚠️ <b>${isKhmer ? "ការប្រុងប្រយ័ត្ន៖ " : "Risk Warning: "}</b>${warning}</div>` : ""}
      `;
    }

    // 5. Update Dots
    const dotsContainer = document.getElementById("tutorial-dots-container");
    if (dotsContainer) {
      dotsContainer.innerHTML = ZYROX_TUTORIAL_STEPS.map((s, idx) => {
        let cls = "tutorial-dot";
        if (idx === index) cls += " active";
        else if (idx < index) cls += " completed";
        return `<span class="${cls}" onclick="renderTutorialStep(${idx})" title="Step ${idx + 1}: ${s.title_en}"></span>`;
      }).join("");
    }

    // 6. Update buttons
    const prevBtn = document.getElementById("tutorial-btn-prev");
    if (prevBtn) {
      prevBtn.disabled = index === 0;
      prevBtn.textContent = isKhmer ? "← ត្រឡប់ក្រោយ" : "← Back";
    }

    const nextBtn = document.getElementById("tutorial-btn-next");
    if (nextBtn) {
      const isLast = index === totalSteps - 1;
      nextBtn.textContent = isLast
        ? (isKhmer ? "✓ បញ្ចប់មគ្គុទ្ទេសក៍" : "✓ Finish Tour")
        : (isKhmer ? "បន្ទាប់ →" : "Next →");
      nextBtn.onclick = isLast ? finishTutorialAction : nextTutorialStep;
    }

    const skipBtn = document.getElementById("tutorial-btn-skip");
    if (skipBtn) {
      skipBtn.textContent = isKhmer ? "រំលង" : "Skip Tour";
    }

    // 7. Spotlight positioning
    window.setTimeout(() => {
      const targetEl = getTutorialTargetElement(step);
      positionTutorialSpotlightAndCard(targetEl);
    }, 120);

    // 8. Persist step progress to backend
    persistOnboardingState(stepNum, false, false);
  }

  function positionTutorialSpotlightAndCard(targetEl) {
    const spotlight = document.getElementById("zyrox-tutorial-spotlight");
    const card = document.getElementById("zyrox-tutorial-card");
    if (!spotlight || !card) return;

    if (!targetEl) {
      // If no element found, hide spotlight cutout and center card
      spotlight.style.display = "none";
      card.style.top = "50%";
      card.style.left = "50%";
      card.style.transform = "translate(-50%, -50%)";
      return;
    }

    spotlight.style.display = "block";
    try {
      targetEl.scrollIntoView({ behavior: "smooth", block: "center", inline: "center" });
    } catch (e) {}

    const rect = targetEl.getBoundingClientRect();
    const pad = 6;
    const spotTop = Math.max(0, rect.top - pad);
    const spotLeft = Math.max(0, rect.left - pad);
    const spotWidth = rect.width + pad * 2;
    const spotHeight = rect.height + pad * 2;

    spotlight.style.top = `${spotTop}px`;
    spotlight.style.left = `${spotLeft}px`;
    spotlight.style.width = `${spotWidth}px`;
    spotlight.style.height = `${spotHeight}px`;

    // Position card
    const isMobile = window.innerWidth <= 640;
    if (isMobile) {
      // In mobile view, CSS fixes card to bottom sheet
      card.style.top = "auto";
      card.style.left = "12px";
      card.style.transform = "none";
      return;
    }

    card.style.transform = "none";
    const cardWidth = card.offsetWidth || 440;
    const cardHeight = card.offsetHeight || 380;
    const viewportW = window.innerWidth;
    const viewportH = window.innerHeight;

    let cardTop = rect.bottom + 14;
    let cardLeft = rect.left;

    // If overflows bottom, position above target
    if (cardTop + cardHeight > viewportH - 20) {
      cardTop = Math.max(16, rect.top - cardHeight - 14);
    }

    // If overflows right, shift left
    if (cardLeft + cardWidth > viewportW - 20) {
      cardLeft = Math.max(16, viewportW - cardWidth - 20);
    }

    card.style.top = `${cardTop}px`;
    card.style.left = `${cardLeft}px`;
  }

  function nextTutorialStep() {
    if (currentStepIndex < ZYROX_TUTORIAL_STEPS.length - 1) {
      renderTutorialStep(currentStepIndex + 1);
    } else {
      finishTutorialAction();
    }
  }

  function prevTutorialStep() {
    if (currentStepIndex > 0) {
      renderTutorialStep(currentStepIndex - 1);
    }
  }

  function skipTutorialAction() {
    closeTutorialUI();
    persistOnboardingState(currentStepIndex + 1, false, true);
    if (window.ZyroxToast) {
      const isKhmer = Boolean(window.isKhmer || document.body.classList.contains("khmer-mode"));
      window.ZyroxToast.info(
        isKhmer ? "បានរំលងមគ្គុទ្ទេសក៍" : "Tutorial Dismissed",
        isKhmer ? "អ្នកអាចចាប់ផ្តើមម្តងទៀតគ្រប់ពេលដោយចុចប៊ូតុង 'មគ្គុទ្ទេសក៍ Dashboard'។" : "You can restart the tour anytime by clicking 'Dashboard Tutorial' in the header."
      );
    }
  }

  function finishTutorialAction() {
    closeTutorialUI();
    persistOnboardingState(14, true, false);
    if (window.ZyroxToast) {
      const isKhmer = Boolean(window.isKhmer || document.body.classList.contains("khmer-mode"));
      window.ZyroxToast.success(
        isKhmer ? "អបអរសាទរ! បានបញ្ចប់មគ្គុទ្ទេសក៍" : "Tutorial Completed!",
        isKhmer ? "ឥឡូវនេះអ្នកត្រៀមខ្លួនរួចរាល់ក្នុងការប្រើប្រាស់ ZYROX AI Dashboard ពេញលេញ។" : "You are all set to harness the full power of ZYROX AI market intelligence."
      );
    }
  }

  function restartTutorialAction() {
    fetch("/api/v1/user/onboarding/reset", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" }
    }).catch(() => {});
    startInteractiveTutorial(true, 1);
  }

  function closeTutorialUI() {
    isTutorialActive = false;
    const backdrop = document.getElementById("zyrox-tutorial-backdrop");
    if (backdrop) backdrop.classList.add("tutorial-hidden");
  }

  function handleTutorialBackdropClick(event) {
    if (event.target && event.target.id === "zyrox-tutorial-backdrop") {
      skipTutorialAction();
    }
  }

  async function persistOnboardingState(step, completed, dismissed) {
    try {
      const res = await fetch("/api/v1/user/onboarding", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          step: step,
          completed: completed,
          dismissed: dismissed,
          tutorial_version: "v6.2.1"
        })
      });
      if (res.ok) {
        const payload = await res.json();
        cachedUserOnboarding = payload.data || { step, completed, dismissed };
      }
    } catch (e) {
      console.debug("Onboarding sync note:", e);
    }
  }

  async function checkUserOnboardingOnStartup() {
    try {
      const res = await fetch("/api/v1/user/onboarding", { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        cachedUserOnboarding = data;
        // If not completed and not dismissed, auto-start first-time tutorial!
        if (!data.onboarding_completed && !data.onboarding_dismissed) {
          window.setTimeout(() => {
            startInteractiveTutorial(false, data.onboarding_step || 1);
          }, 650);
        }
      }
    } catch (e) {
      console.debug("Startup onboarding check note:", e);
    }
  }

  // Keyboard Navigation: Alt+T (Start), Esc (Close), ArrowRight (Next), ArrowLeft (Prev)
  window.addEventListener("keydown", function (e) {
    if ((e.altKey && (e.key === "t" || e.key === "T")) || (e.ctrlKey && e.altKey && e.key === "t")) {
      e.preventDefault();
      startInteractiveTutorial(true, 1);
      return;
    }

    if (!isTutorialActive) return;

    if (e.key === "Escape") {
      e.preventDefault();
      skipTutorialAction();
    } else if (e.key === "ArrowRight" || e.key === "Enter") {
      e.preventDefault();
      nextTutorialStep();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      prevTutorialStep();
    }
  });

  // Reposition on window resize / scroll
  let resizeTimer = null;
  window.addEventListener("resize", function () {
    if (!isTutorialActive) return;
    if (resizeTimer) cancelAnimationFrame(resizeTimer);
    resizeTimer = requestAnimationFrame(() => {
      const step = ZYROX_TUTORIAL_STEPS[currentStepIndex];
      const targetEl = getTutorialTargetElement(step);
      positionTutorialSpotlightAndCard(targetEl);
    });
  });

  // Auto-init when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", checkUserOnboardingOnStartup);
  } else {
    window.setTimeout(checkUserOnboardingOnStartup, 100);
  }

  // Export functions to global window namespace
  window.ZYROX_TUTORIAL_STEPS = ZYROX_TUTORIAL_STEPS;
  window.startInteractiveTutorial = startInteractiveTutorial;
  window.renderTutorialStep = renderTutorialStep;
  window.nextTutorialStep = nextTutorialStep;
  window.prevTutorialStep = prevTutorialStep;
  window.skipTutorialAction = skipTutorialAction;
  window.finishTutorialAction = finishTutorialAction;
  window.restartTutorialAction = restartTutorialAction;
  window.handleTutorialBackdropClick = handleTutorialBackdropClick;

})(window, document);
