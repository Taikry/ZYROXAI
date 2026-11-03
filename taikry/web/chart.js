/**
 * TAIKRY SIGNAL AI — PROFESSIONAL INTERACTIVE FINANCIAL CHART WORKSPACE
 * =====================================================================
 * High-performance, institutional quantitative charting engine for XAUUSD (Gold),
 * Forex pairs, and Cryptocurrencies.
 *
 * Core Features:
 * - Powered by TradingView Lightweight Charts (v4.2.1 Offline Vendored)
 * - Multi-Mode Chart: Candlestick, OHLC Bar, Line, and Area
 * - Dual-Engine Switcher: "⚡ Taikry Native Pro Terminal" vs "🌐 TradingView Cloud Embed"
 * - Indicators Suite:
 *   * Trend: EMA 9, 20, 50, 100, 200; SMA 20, 50, 200; Multi-timeframe trend alignment
 *   * Momentum: Wilder's RSI 14 (with 70/30 levels), MACD (12, 26, 9), Stochastic Oscillator
 *   * Volatility: ATR 14, Bollinger Bands (20, 2), Keltner Channels (20, 14, 1.5)
 *   * Price & Volume: Session VWAP, Volume Histogram, Daily Open, PDH, PDL, Floor Pivots
 * - Smart Money Concepts (ICT / SMC) Live Overlays:
 *   * BOS (Break of Structure - Trend Continuation)
 *   * CHoCH (Change of Character - Trend Reversal)
 *   * FVG (Bullish & Bearish Fair Value Gaps with CE 50% & Mitigation Tracking)
 *   * Order Blocks (Institutional OB High/Low/Body Boundaries)
 *   * Liquidity Sweeps (Buy-Side BSL / Sell-Side SSL Rejection Traps)
 *   * Active Trade Signal Overlay (Entry, Stop Loss, TP1, TP2, R:R Box)
 * - Interactive Vector Drawing Tools:
 *   * Crosshair, Trendline, Horizontal Ray, Fibonacci Retracement (0.618, 0.705 OTE), Ruler, Clear
 * - Data Freshness & Provenance HUD (Provider, UTC & Cambodia GMT+7 Timestamps, Live Status)
 * - Bilingual Support: Khmer-First (Default) + English Toggle
 */

(function (window) {
  'use strict';

  // 1. BILINGUAL CHART DICTIONARY (Khmer-first)
  const CHART_I18N = {
    kh: {
      chart_title: "ក្រាហ្វិកវិភាគទីផ្សារកម្រិតស្ថាប័ន TAIKRY PRO",
      candles: "ទៀនជប៉ុន (Candlesticks)",
      bars: "របារថ្លៃ (OHLC Bars)",
      line: "បន្ទាត់ (Line)",
      area: "ផ្ទៃពណ៌ (Area)",
      indicators: "សូចនាករបច្ចេកទេស (Indicators)",
      smc_overlays: "រចនាសម្ព័ន្ធ SMC (ICT Overlays)",
      drawings: "ឧបករណ៍គូសវាស (Drawing Tools)",
      fullscreen: "ពេញអេក្រង់ (Fullscreen)",
      reset_view: "កំណត់ឡើងវិញ (Reset View)",
      engine_native: "⚡ ម៉ាស៊ីន Native Pro",
      engine_tv: "🌐 TradingView Cloud",
      cursor: "ទ្រនិច (Cursor)",
      trendline: "បន្ទាត់និន្នាការ (Trendline)",
      ray: "កាំរស្មីផ្តេក (Horizontal Ray)",
      fibo: "ហ្វីបូណាឈី (Fibonacci Retracement)",
      ruler: "បន្ទាត់វាស់ចម្ងាយ (Measure Ruler)",
      clear_draw: "លុបគំនូរទាំងអស់ (Clear Drawings)",
      open: "បើក (O)",
      high: "ខ្ពស់ (H)",
      low: "ទាប (L)",
      close: "បិទ (C)",
      vol: "បរិមាណ (Vol)",
      live_fresh: "● ផ្សាយផ្ទាល់ LIVE (Fresh)",
      delayed: "▲ ពន្យារពេលបន្តិច (Delayed)",
      stale: "⚠️ ទិន្នន័យចាស់ (Stale)",
      weekend_closed: "🔒 ទីផ្សារចុងសប្តាហ៍បិទ (Weekend Closed)",
      provider: "ប្រភព",
      asia_session: "អាស៊ី · តូក្យូ",
      london_session: "ឡុងដ៍",
      new_york_session: "ញូវយ៉ក",
      session_open: "បើក",
      session_closed: "បិទ",
      session_clock_title: "ម៉ោងទីផ្សារ · ម៉ោងក្នុងតំបន់",
      entry: "ចំណុចចូល (Entry)",
      sl: "កាត់ខាត (SL)",
      tp1: "ចំណេញ ១ (TP1)",
      tp2: "ចំណេញ ២ (TP2)",
      bos: "បំបែករចនាសម្ព័ន្ធ (BOS)",
      choch: "ផ្លាស់ប្តូរចរិតលក្ខណៈ (CHoCH)",
      fvg: "គម្លាតតម្លៃអតុល្យភាព (FVG)",
      ob: "ប្លុកបញ្ជាទិញ (Order Block)",
      sweep: "ការស្រង់សន្ទនីយភាព (Liquidity Sweep)",
      saved: "បានរក្សាទុក"
    },
    en: {
      chart_title: "TAIKRY PRO Institutional Market Chart",
      candles: "Candlesticks",
      bars: "OHLC Bars",
      line: "Line",
      area: "Area",
      indicators: "Indicators",
      smc_overlays: "SMC Overlays",
      drawings: "Drawing Tools",
      fullscreen: "Fullscreen",
      reset_view: "Reset View",
      engine_native: "⚡ Native Pro Engine",
      engine_tv: "🌐 TV Cloud Embed",
      cursor: "Cursor",
      trendline: "Trendline",
      ray: "Horizontal Ray",
      fibo: "Fibonacci Retracement",
      ruler: "Measure Ruler",
      clear_draw: "Clear Drawings",
      open: "O",
      high: "H",
      low: "L",
      close: "C",
      vol: "Vol",
      live_fresh: "● LIVE (Fresh)",
      delayed: "▲ Delayed",
      stale: "⚠️ Stale Data",
      weekend_closed: "🔒 Weekend Closed",
      provider: "Provider",
      asia_session: "Asia · Tokyo",
      london_session: "London",
      new_york_session: "New York",
      session_open: "OPEN",
      session_closed: "CLOSED",
      session_clock_title: "Market sessions · local time",
      entry: "Entry",
      sl: "Stop Loss",
      tp1: "Take Profit 1",
      tp2: "Take Profit 2",
      bos: "Break of Structure (BOS)",
      choch: "Change of Character (CHoCH)",
      fvg: "Fair Value Gap (FVG)",
      ob: "Order Block (OB)",
      sweep: "Liquidity Sweep",
      saved: "Saved"
    }
  };

  // 2. DEFAULT INDICATOR PRESETS CONFIGURATION
  const DEFAULT_INDICATOR_SETTINGS = {
    // Trend Overlays
    ema_9: false,
    ema_20: true,
    ema_50: true,
    ema_100: false,
    ema_200: true,
    sma_20: false,
    sma_50: false,
    sma_200: false,
    vwap: true,
    bollinger: false,
    keltner: false,
    session_levels: true,
    // Lower Subpanes
    volume: true,
    rsi: true,
    macd: true,
    stochastic: false,
    // SMC Structural Overlays
    smc_bos: true,
    smc_choch: true,
    smc_fvg: true,
    smc_ob: true,
    smc_sweeps: true,
    trade_signals: true
  };

  class TaikryChartWorkspaceController {
    constructor() {
      this.currentSymbol = "XAUUSD";
      this.currentTimeframe = "M15";
      this.currentChartType = "candles"; // 'candles', 'bars', 'line', 'area'
      this.currentEngineMode = "native"; // 'native' | 'tv_cloud'
      this.lang = "kh"; // Khmer-first by default

      // Chart Instances & Series References
      this.chart = null;
      this.chartContainer = null;
      this.mainSeries = null;
      this.volumeSeries = null;
      this.rsiChart = null;
      this.rsiSeries = null;
      this.stochChart = null;
      this.stochKSeries = null;
      this.stochDSeries = null;
      this.macdChart = null;
      this.macdLineSeries = null;
      this.macdSignalSeries = null;
      this.macdHistSeries = null;

      // Indicator Overlay Series Maps
      this.lineSeriesMap = {};

      // Data Caches
      this.candlesData = [];
      this.annotationsData = {};
      this.metadata = {};
      this.sessionLevels = {};

      // User Indicator Settings (Loaded from LocalStorage)
      this.indicatorSettings = this.loadSavedSettings();

      // Active Drawing Tools State
      this.activeTool = "cursor"; // 'cursor' | 'trendline' | 'ray' | 'fibo' | 'ruler'
      this.drawings = [];
      this.drawingPoints = [];

      // Overlay Canvas & SVG
      this.overlaySvg = null;
      this.drawingSvg = null;

      // Resizing & Animation RAF
      this._resizeObserver = null;
      this._rafId = null;

      // Realtime Incremental Update Buffer & Performance State
      this.lastTickTime = null;
      this._candleAbortController = null;
      this.candleCache = {};
      this.proWorkspaceWrapper = null;
      this.tvEmbedWrapper = null;
      this._isSyncingRange = false;
      this.sessionClockTimer = null;
      this.sessionClockContainer = null;
    }

    // -------------------------------------------------------------------------
    // SETTINGS & LOCAL STORAGE
    // -------------------------------------------------------------------------

    loadSavedSettings() {
      try {
        const stored = localStorage.getItem("taikry_chart_indicator_settings");
        if (stored) {
          return Object.assign({}, DEFAULT_INDICATOR_SETTINGS, JSON.parse(stored));
        }
      } catch (e) {
        console.warn("Could not load indicator settings from localStorage:", e);
      }
      return Object.assign({}, DEFAULT_INDICATOR_SETTINGS);
    }

    saveSettings() {
      try {
        localStorage.setItem("taikry_chart_indicator_settings", JSON.stringify(this.indicatorSettings));
      } catch (e) {
        console.warn("Could not save indicator settings to localStorage:", e);
      }
    }

    t(key) {
      const dict = CHART_I18N[this.lang] || CHART_I18N.kh;
      return dict[key] || key;
    }

    setLanguage(lang) {
      this.lang = lang === "en" ? "en" : "kh";
      this.updateToolbarLabels();
      this.updateSessionClocks();
    }

    // -------------------------------------------------------------------------
    // INITIALIZATION & DOM MOUNTING
    // -------------------------------------------------------------------------

    init(containerId = "tradingview-container") {
      this.chartContainer = document.getElementById(containerId);
      if (!this.chartContainer) {
        console.error(`Chart container #${containerId} not found.`);
        return;
      }

      this.setupWorkspaceStructure();

      // Check current engine mode preference
      const savedEngine = localStorage.getItem("taikry_chart_engine_mode");
      if (savedEngine === "tv_cloud") {
        this.switchEngineMode("tv_cloud");
      } else {
        this.switchEngineMode("native");
      }
    }

    setupWorkspaceStructure() {
      if (!this.chartContainer) return;
      if (this.sessionClockTimer) {
        window.clearInterval(this.sessionClockTimer);
        this.sessionClockTimer = null;
      }
      this.chartContainer.innerHTML = "";
      this.chartContainer.style.display = "flex";
      this.chartContainer.style.flexDirection = "column";
      this.chartContainer.style.minHeight = "0";

      this.sessionClockContainer = document.createElement("div");
      this.sessionClockContainer.className = "taikry-session-clock-bar";
      this.sessionClockContainer.setAttribute("aria-label", this.t("session_clock_title"));
      this.sessionClockContainer.innerHTML = `
        <div class="session-clock-heading" id="session-clock-heading">${this.t("session_clock_title")}</div>
        <div class="session-clock-grid">
          <div class="session-clock-card" data-session="asia">
            <div class="session-clock-name" id="session-clock-asia-name">${this.t("asia_session")}</div>
            <div class="session-clock-time" id="session-clock-asia-time">--:--:--</div>
            <div class="session-clock-date" id="session-clock-asia-date">---</div>
            <div class="session-clock-status" id="session-clock-asia-status">---</div>
          </div>
          <div class="session-clock-card" data-session="london">
            <div class="session-clock-name" id="session-clock-london-name">${this.t("london_session")}</div>
            <div class="session-clock-time" id="session-clock-london-time">--:--:--</div>
            <div class="session-clock-date" id="session-clock-london-date">---</div>
            <div class="session-clock-status" id="session-clock-london-status">---</div>
          </div>
          <div class="session-clock-card" data-session="new-york">
            <div class="session-clock-name" id="session-clock-new-york-name">${this.t("new_york_session")}</div>
            <div class="session-clock-time" id="session-clock-new-york-time">--:--:--</div>
            <div class="session-clock-date" id="session-clock-new-york-date">---</div>
            <div class="session-clock-status" id="session-clock-new-york-status">---</div>
          </div>
        </div>
      `;
      this.chartContainer.appendChild(this.sessionClockContainer);

      // 1. Native Pro Chart Workspace Wrapper
      this.proWorkspaceWrapper = document.createElement("div");
      this.proWorkspaceWrapper.id = "pro-chart-workspace-wrapper";
      this.proWorkspaceWrapper.className = "taikry-pro-chart-workspace";
      this.proWorkspaceWrapper.style.display = "none";
      this.proWorkspaceWrapper.style.width = "100%";
      this.proWorkspaceWrapper.style.height = "0";
      this.proWorkspaceWrapper.style.flex = "1 1 0";
      this.proWorkspaceWrapper.style.minHeight = "0";
      this.proWorkspaceWrapper.style.position = "relative";
      this.chartContainer.appendChild(this.proWorkspaceWrapper);

      // 2. TradingView Cloud Embed Wrapper
      this.tvEmbedWrapper = document.createElement("div");
      this.tvEmbedWrapper.id = "tv-cloud-embed-wrapper";
      this.tvEmbedWrapper.className = "tv-cloud-embed-wrapper";
      this.tvEmbedWrapper.style.display = "none";
      this.tvEmbedWrapper.style.width = "100%";
      this.tvEmbedWrapper.style.height = "0";
      this.tvEmbedWrapper.style.flex = "1 1 0";
      this.tvEmbedWrapper.style.minHeight = "0";
      this.tvEmbedWrapper.style.position = "relative";
      this.chartContainer.appendChild(this.tvEmbedWrapper);
      this.updateSessionClocks();
      this.sessionClockTimer = window.setInterval(() => this.updateSessionClocks(), 1000);
    }

    updateSessionClocks() {
      if (!this.sessionClockContainer) return;
      const heading = this.sessionClockContainer.querySelector("#session-clock-heading");
      if (heading) heading.textContent = this.t("session_clock_title");
      this.sessionClockContainer.setAttribute("aria-label", this.t("session_clock_title"));
      const now = new Date();
      const sessions = [
        { id: "asia", zone: "Asia/Tokyo", open: 9 * 60, close: 18 * 60, label: "asia_session" },
        { id: "london", zone: "Europe/London", open: 8 * 60, close: 17 * 60, label: "london_session" },
        { id: "new-york", zone: "America/New_York", open: 8 * 60, close: 17 * 60, label: "new_york_session" },
      ];

      sessions.forEach(session => {
        try {
          const parts = new Intl.DateTimeFormat("en-GB", {
            timeZone: session.zone,
            weekday: "short",
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
            hourCycle: "h23",
          }).formatToParts(now).reduce((acc, part) => {
            acc[part.type] = part.value;
            return acc;
          }, {});
          const dateLabel = new Intl.DateTimeFormat(this.lang === "kh" ? "km-KH" : "en-GB", {
            timeZone: session.zone,
            weekday: "short",
            day: "2-digit",
            month: "short",
          }).format(now);
          const hour = Number(parts.hour || 0);
          const minute = Number(parts.minute || 0);
          const weekday = String(parts.weekday || "").toLowerCase();
          const minuteOfDay = hour * 60 + minute;
          const weekdayOpen = weekday !== "sat" && weekday !== "sun";
          const isOpen = weekdayOpen && minuteOfDay >= session.open && minuteOfDay < session.close;
          const timeNode = document.getElementById(`session-clock-${session.id}-time`);
          const dateNode = document.getElementById(`session-clock-${session.id}-date`);
          const statusNode = document.getElementById(`session-clock-${session.id}-status`);
          const nameNode = document.getElementById(`session-clock-${session.id}-name`);
          const card = this.sessionClockContainer.querySelector(`[data-session="${session.id}"]`);
          if (nameNode) nameNode.textContent = this.t(session.label);
          if (timeNode) timeNode.textContent = `${parts.hour}:${parts.minute}:${parts.second}`;
          if (dateNode) dateNode.textContent = `${dateLabel} · ${session.zone}`;
          if (statusNode) statusNode.textContent = isOpen ? this.t("session_open") : this.t("session_closed");
          if (card) {
            card.classList.toggle("is-open", isOpen);
            card.classList.toggle("is-closed", !isOpen);
          }
        } catch (error) {
          console.warn(`Could not render ${session.zone} session clock:`, error);
        }
      });
    }

    // -------------------------------------------------------------------------
    // NATIVE PRO CHART ENGINE WORKSPACE
    // -------------------------------------------------------------------------

    renderNativeWorkspace() {
      if (!this.proWorkspaceWrapper) return;
      this.proWorkspaceWrapper.innerHTML = "";

      // 1. Build Toolbar Markup
      const toolbarHtml = `
        <div class="pro-chart-toolbar" id="pro-chart-toolbar">
          <!-- Left: Symbol & Type Selector -->
          <div class="pro-toolbar-left">
            <div class="pro-sym-badge" id="pro-sym-badge">
              <span class="pro-sym-icon">🪙</span>
              <span class="pro-sym-name" id="pro-sym-display">${this.currentSymbol} · ${this.currentTimeframe}</span>
            </div>

            <!-- Chart Style Dropdown -->
            <div class="pro-tool-group">
              <select id="pro-chart-type-select" class="pro-select" onchange="window.taikryChart.switchChartType(this.value)">
                <option value="candles" ${this.currentChartType === 'candles' ? 'selected' : ''}>🕯️ ${this.t('candles')}</option>
                <option value="bars" ${this.currentChartType === 'bars' ? 'selected' : ''}>📊 ${this.t('bars')}</option>
                <option value="line" ${this.currentChartType === 'line' ? 'selected' : ''}>📈 ${this.t('line')}</option>
                <option value="area" ${this.currentChartType === 'area' ? 'selected' : ''}>🌊 ${this.t('area')}</option>
              </select>
            </div>

            <!-- Indicator Manager Button -->
            <button class="pro-toolbar-btn ${this.hasActiveIndicators() ? 'active' : ''}" id="btn-open-indicators" onclick="window.taikryChart.openIndicatorModal()" title="Configure Technical Indicators">
              <span>📈</span>
              <span id="t-toolbar-indicators">${this.t('indicators')}</span>
            </button>

            <!-- SMC Overlays Button -->
            <button class="pro-toolbar-btn ${this.indicatorSettings.smc_fvg ? 'active' : ''}" id="btn-toggle-smc" onclick="window.taikryChart.toggleSMCOverlaysModal()" title="Configure Smart Money Concepts (BOS, FVG, OB)">
              <span>🏛️</span>
              <span id="t-toolbar-smc">${this.t('smc_overlays')}</span>
            </button>
          </div>

          <!-- Center: Drawing Tools Palette -->
          <div class="pro-toolbar-center">
            <div class="pro-draw-tools-group">
              <button class="pro-tool-icon-btn ${this.activeTool === 'cursor' ? 'active' : ''}" onclick="window.taikryChart.setDrawingTool('cursor', this)" title="${this.t('cursor')}">✛</button>
              <button class="pro-tool-icon-btn ${this.activeTool === 'trendline' ? 'active' : ''}" onclick="window.taikryChart.setDrawingTool('trendline', this)" title="${this.t('trendline')}">╱</button>
              <button class="pro-tool-icon-btn ${this.activeTool === 'ray' ? 'active' : ''}" onclick="window.taikryChart.setDrawingTool('ray', this)" title="${this.t('ray')}">⟶</button>
              <button class="pro-tool-icon-btn ${this.activeTool === 'fibo' ? 'active' : ''}" onclick="window.taikryChart.setDrawingTool('fibo', this)" title="${this.t('fibo')}">≣</button>
              <button class="pro-tool-icon-btn ${this.activeTool === 'ruler' ? 'active' : ''}" onclick="window.taikryChart.setDrawingTool('ruler', this)" title="${this.t('ruler')}">📐</button>
              <button class="pro-tool-icon-btn pro-tool-btn-danger" onclick="window.taikryChart.clearDrawings()" title="${this.t('clear_draw')}">🗑️</button>
            </div>
          </div>

          <!-- Right: HUD Status, Engine Switcher & Fullscreen -->
          <div class="pro-toolbar-right">
            <!-- Data Freshness & Provider Pill -->
            <div class="pro-data-freshness-pill" id="pro-data-freshness-pill" title="Provider Provenance & Freshness Status">
              <span class="freshness-dot gray" id="freshness-dot"></span>
              <span id="freshness-text">CONNECTING · verified candles</span>
            </div>

            <!-- Engine Mode Switcher -->
            <button class="pro-engine-btn" onclick="window.taikryChart.switchEngineMode('tv_cloud')" title="Switch to TradingView Cloud Widget Embed">
              <span>🌐</span>
              <span class="engine-text">TV Cloud</span>
            </button>

            <!-- Reset Chart View -->
            <button class="pro-icon-btn" onclick="window.taikryChart.resetView()" title="${this.t('reset_view')}">↺</button>

            <!-- Fullscreen Toggle -->
            <button class="pro-icon-btn" onclick="window.taikryChart.toggleFullscreen()" title="${this.t('fullscreen')}">⛶</button>
          </div>
        </div>

        <!-- OHLC Quote Bar HUD -->
        <div class="pro-quote-hud" id="pro-quote-hud">
          <span class="quote-sym" id="hud-symbol">${this.currentSymbol}</span>
          <span class="quote-item">O: <b id="hud-open">---</b></span>
          <span class="quote-item">H: <b id="hud-high">---</b></span>
          <span class="quote-item">L: <b id="hud-low">---</b></span>
          <span class="quote-item">C: <b id="hud-close">---</b></span>
          <span class="quote-item" id="hud-change-wrap">Chg: <b id="hud-change">---</b></span>
          <span class="quote-item">Vol: <b id="hud-vol">---</b></span>
          <span class="quote-item">ATR 14: <b id="hud-atr">---</b></span>
          <span class="quote-time" id="hud-time">---</span>
        </div>

        <!-- Chart Main Stage & Panes -->
        <div class="pro-chart-stage" id="pro-chart-stage">
          <div class="pro-chart-main-pane" id="pro-chart-main-pane">
            <!-- SVG Overlays inside main pane so coordinates match 1:1 without spilling into subpanes -->
            <svg class="pro-chart-svg-overlay" id="pro-chart-svg-overlay"></svg>
            <svg class="pro-chart-drawing-overlay" id="pro-chart-drawing-overlay"></svg>
          </div>
          <div class="pro-chart-state-overlay" id="pro-chart-state-overlay" hidden aria-live="polite"></div>
          <div class="pro-chart-subpane" id="pro-chart-rsi-pane" style="display: ${this.indicatorSettings.rsi ? 'block' : 'none'};"></div>
          <div class="pro-chart-subpane" id="pro-chart-stoch-pane" style="display: ${this.indicatorSettings.stochastic ? 'block' : 'none'};"></div>
          <div class="pro-chart-subpane" id="pro-chart-macd-pane" style="display: ${this.indicatorSettings.macd ? 'block' : 'none'};"></div>
        </div>
      `;

      this.proWorkspaceWrapper.innerHTML = toolbarHtml;

      this.overlaySvg = document.getElementById("pro-chart-svg-overlay");
      this.drawingSvg = document.getElementById("pro-chart-drawing-overlay");

      // Setup Drawing Tool Event Handlers
      this.setupDrawingEvents();

      // Initialize Lightweight Charts with full kinetic zoom/scroll options
      this.initLightweightCharts();

      // Fetch or render cached data
      this.loadCandlesAndOverlays(this.currentSymbol, this.currentTimeframe);
    }

    // -------------------------------------------------------------------------
    // LIGHTWEIGHT CHARTS CREATION & CONFIGURATION
    // -------------------------------------------------------------------------

    initLightweightCharts() {
      if (typeof LightweightCharts === "undefined") {
        console.error("LightweightCharts library is not loaded.");
        return;
      }

      const mainContainer = document.getElementById("pro-chart-main-pane");
      if (!mainContainer) return;

      const chartTheme = {
        layout: {
          background: { color: "#080c14" },
          textColor: "#94a3b8",
          fontSize: 11,
          fontFamily: "'Inter', 'Battambang', sans-serif"
        },
        grid: {
          vertLines: { color: "rgba(255, 255, 255, 0.04)" },
          horzLines: { color: "rgba(255, 255, 255, 0.04)" }
        },
        crosshair: {
          mode: LightweightCharts.CrosshairMode.Normal,
          vertLine: {
            color: "rgba(212, 175, 55, 0.5)",
            width: 1,
            style: 2, // Dashed
            labelBackgroundColor: "#1e293b"
          },
          horzLine: {
            color: "rgba(212, 175, 55, 0.5)",
            width: 1,
            style: 2,
            labelBackgroundColor: "#1e293b"
          }
        },
        rightPriceScale: {
          visible: true,
          borderColor: "rgba(255, 255, 255, 0.12)",
          scaleMargins: {
            top: 0.1,
            bottom: 0.15
          },
          autoScale: true,
          alignLabels: true
        },
        timeScale: {
          borderColor: "rgba(255, 255, 255, 0.12)",
          timeVisible: true,
          secondsVisible: false,
          shiftVisibleRangeOnNewBar: true,
          allowBoldLabels: true,
          rightOffset: 12,
          barSpacing: 8,
          minBarSpacing: 1,
          fixLeftEdge: false,
          fixRightEdge: false
        },
        handleScroll: {
          mouseWheel: true,
          pressedMouseMove: true,
          horzTouchDrag: true,
          vertTouchDrag: true
        },
        handleScale: {
          axisPressedMouseMove: {
            time: true,
            price: true
          },
          axisDoubleClickReset: {
            time: true,
            price: true
          },
          mouseWheel: true,
          pinch: true
        },
        kineticScroll: {
          touch: true,
          mouse: true
        }
      };

      // 1. Create Main Chart
      this.chart = LightweightCharts.createChart(mainContainer, Object.assign({}, chartTheme, {
        width: mainContainer.clientWidth || 800,
        height: mainContainer.clientHeight || 450
      }));

      // Create Selected Price Series (Candles, Bars, Line, Area)
      this.createMainPriceSeries();

      // Create Volume Histogram (Overlaid on bottom 20% of main scale)
      if (this.indicatorSettings.volume) {
        this.volumeSeries = this.chart.addHistogramSeries({
          color: "#22c55e",
          priceFormat: { type: "volume" },
          priceScaleId: "", // Overlay on main pane with separate scale margins
          scaleMargins: {
            top: 0.8,
            bottom: 0.0
          }
        });
      }

      // 2. Create RSI Subpane if enabled
      this.initRsiPane(chartTheme);

      // 3. Create MACD Subpane if enabled
      this.initMacdPane(chartTheme);

      // 4. Create Stochastic Subpane if enabled
      this.initStochasticPane(chartTheme);

      // 5. Synchronize all active panes without cyclic ping-pong
      this.syncAllCharts();

      // 5. Crosshair Move Handler for Quote HUD
      this.chart.subscribeCrosshairMove(param => {
        this.onCrosshairMove(param);
      });

      // 6. TimeScale Visible Range Changes (Re-draw SVG Overlays)
      this.chart.timeScale().subscribeVisibleLogicalRangeChange(() => {
        this.scheduleOverlayRepaint();
      });

      // 7. Responsive Auto-Resize and Screen Rotation Listeners
      if (window.ResizeObserver && this.proWorkspaceWrapper) {
        this._resizeObserver = new ResizeObserver(() => {
          this.handleResize();
        });
        this._resizeObserver.observe(this.proWorkspaceWrapper);
      } else {
        window.addEventListener("resize", () => this.handleResize());
      }

      window.addEventListener("orientationchange", () => {
        setTimeout(() => this.handleResize(), 150);
      });
    }

    initRsiPane(theme) {
      if (!this.indicatorSettings.rsi) return;
      const rsiContainer = document.getElementById("pro-chart-rsi-pane");
      if (!rsiContainer) return;
      rsiContainer.style.display = "block";

      if (this.rsiChart) return;

      const chartTheme = theme || {
        layout: { background: { color: "#080c14" }, textColor: "#94a3b8", fontSize: 10 },
        grid: { vertLines: { color: "rgba(255, 255, 255, 0.04)" }, horzLines: { color: "rgba(255, 255, 255, 0.04)" } },
        handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: true },
        handleScale: { mouseWheel: true, pinch: true, axisPressedMouseMove: { time: true, price: true } }
      };

      this.rsiChart = LightweightCharts.createChart(rsiContainer, Object.assign({}, chartTheme, {
        height: 100,
        rightPriceScale: {
          borderColor: "rgba(255, 255, 255, 0.12)",
          scaleMargins: { top: 0.1, bottom: 0.1 }
        },
        timeScale: {
          visible: false
        }
      }));

      this.rsiSeries = this.rsiChart.addLineSeries({
        color: "#f59e0b",
        lineWidth: 2,
        title: "RSI 14"
      });

      this.rsiSeries.createPriceLine({ price: 70, color: "rgba(239, 68, 68, 0.6)", lineWidth: 1, lineStyle: 2, title: "OB 70" });
      this.rsiSeries.createPriceLine({ price: 30, color: "rgba(34, 197, 94, 0.6)", lineWidth: 1, lineStyle: 2, title: "OS 30" });
      this.rsiSeries.createPriceLine({ price: 50, color: "rgba(148, 163, 184, 0.3)", lineWidth: 1, lineStyle: 3 });
    }

    initMacdPane(theme) {
      if (!this.indicatorSettings.macd) return;
      const macdContainer = document.getElementById("pro-chart-macd-pane");
      if (!macdContainer) return;
      macdContainer.style.display = "block";

      if (this.macdChart) return;

      const chartTheme = theme || {
        layout: { background: { color: "#080c14" }, textColor: "#94a3b8", fontSize: 10 },
        grid: { vertLines: { color: "rgba(255, 255, 255, 0.04)" }, horzLines: { color: "rgba(255, 255, 255, 0.04)" } },
        handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: true },
        handleScale: { mouseWheel: true, pinch: true, axisPressedMouseMove: { time: true, price: true } }
      };

      this.macdChart = LightweightCharts.createChart(macdContainer, Object.assign({}, chartTheme, {
        height: 100,
        rightPriceScale: {
          borderColor: "rgba(255, 255, 255, 0.12)",
          scaleMargins: { top: 0.1, bottom: 0.1 }
        },
        timeScale: {
          visible: false
        }
      }));

      this.macdHistSeries = this.macdChart.addHistogramSeries({
        color: "#38bdf8",
        lineWidth: 2,
        title: "Hist"
      });

      this.macdLineSeries = this.macdChart.addLineSeries({
        color: "#38bdf8",
        lineWidth: 2,
        title: "MACD"
      });

      this.macdSignalSeries = this.macdChart.addLineSeries({
        color: "#f43f5e",
        lineWidth: 1,
        title: "Signal"
      });
    }

    initStochasticPane(theme) {
      if (!this.indicatorSettings.stochastic) return;
      const container = document.getElementById("pro-chart-stoch-pane");
      if (!container) return;
      container.style.display = "block";
      if (this.stochChart) return;

      const chartTheme = theme || {
        layout: { background: { color: "#080c14" }, textColor: "#94a3b8", fontSize: 10 },
        grid: { vertLines: { color: "rgba(255, 255, 255, 0.04)" }, horzLines: { color: "rgba(255, 255, 255, 0.04)" } },
      };
      this.stochChart = LightweightCharts.createChart(container, Object.assign({}, chartTheme, {
        height: 100,
        rightPriceScale: { borderColor: "rgba(255, 255, 255, 0.12)", scaleMargins: { top: 0.1, bottom: 0.1 } },
        timeScale: { visible: false },
      }));
      this.stochKSeries = this.stochChart.addLineSeries({ color: "#a78bfa", lineWidth: 2, title: "%K 14,3" });
      this.stochDSeries = this.stochChart.addLineSeries({ color: "#38bdf8", lineWidth: 1, title: "%D 3" });
      this.stochKSeries.createPriceLine({ price: 80, color: "rgba(239, 68, 68, 0.6)", lineWidth: 1, lineStyle: 2, title: "OB 80" });
      this.stochKSeries.createPriceLine({ price: 20, color: "rgba(34, 197, 94, 0.6)", lineWidth: 1, lineStyle: 2, title: "OS 20" });
      this.stochKSeries.createPriceLine({ price: 50, color: "rgba(148, 163, 184, 0.3)", lineWidth: 1, lineStyle: 3 });
    }

    createMainPriceSeries() {
      if (!this.chart) return;
      if (this.mainSeries) {
        this.chart.removeSeries(this.mainSeries);
        this.mainSeries = null;
      }

      const upColor = "#10b981";
      const downColor = "#ef4444";

      switch (this.currentChartType) {
        case "bars":
          this.mainSeries = this.chart.addBarSeries({
            upColor: upColor,
            downColor: downColor,
            openVisible: true,
            thinBars: false
          });
          break;
        case "line":
          this.mainSeries = this.chart.addLineSeries({
            color: "#38bdf8",
            lineWidth: 2
          });
          break;
        case "area":
          this.mainSeries = this.chart.addAreaSeries({
            topColor: "rgba(56, 189, 248, 0.4)",
            bottomColor: "rgba(56, 189, 248, 0.0)",
            lineColor: "#38bdf8",
            lineWidth: 2
          });
          break;
        case "candles":
        default:
          this.mainSeries = this.chart.addCandlestickSeries({
            upColor: upColor,
            downColor: downColor,
            borderVisible: false,
            wickUpColor: upColor,
            wickDownColor: downColor
          });
          break;
      }
    }

    syncAllCharts() {
      const getActiveCharts = () => [
        this.chart,
        this.indicatorSettings.rsi ? this.rsiChart : null,
        this.indicatorSettings.stochastic ? this.stochChart : null,
        this.indicatorSettings.macd ? this.macdChart : null,
      ].filter(Boolean);
      const all = getActiveCharts();
      if (all.length <= 1) return;

      all.forEach(src => {
        if (src._taikrySyncHandler) return;
        src._taikrySyncHandler = range => {
          if (!range || this._isSyncingRange) return;
          this._isSyncingRange = true;
          try {
            getActiveCharts().forEach(target => {
              if (target !== src) {
                const cur = target.timeScale().getVisibleLogicalRange();
                if (!cur || Math.abs(cur.from - range.from) > 0.01 || Math.abs(cur.to - range.to) > 0.01) {
                  target.timeScale().setVisibleLogicalRange(range);
                }
              }
            });
          } catch (e) {
            // ignore range boundaries
          } finally {
            this._isSyncingRange = false;
          }
        };
        src.timeScale().subscribeVisibleLogicalRangeChange(src._taikrySyncHandler);
      });
    }

    handleResize() {
      if (!this.chart || !this.proWorkspaceWrapper) return;
      const mainPane = document.getElementById("pro-chart-main-pane");
      if (mainPane) {
        const w = mainPane.clientWidth;
        const h = mainPane.clientHeight;
        if (w > 0 && h > 0) {
          this.chart.applyOptions({ width: w, height: h });
        }
      }

      if (this.rsiChart) {
        const rsiPane = document.getElementById("pro-chart-rsi-pane");
        if (rsiPane && rsiPane.clientWidth > 0) {
          this.rsiChart.applyOptions({ width: rsiPane.clientWidth, height: rsiPane.clientHeight || 100 });
        }
      }

      if (this.stochChart) {
        const pane = document.getElementById("pro-chart-stoch-pane");
        if (pane && pane.clientWidth > 0) {
          this.stochChart.applyOptions({ width: pane.clientWidth, height: pane.clientHeight || 100 });
        }
      }

      if (this.macdChart) {
        const macdPane = document.getElementById("pro-chart-macd-pane");
        if (macdPane && macdPane.clientWidth > 0) {
          this.macdChart.applyOptions({ width: macdPane.clientWidth, height: macdPane.clientHeight || 100 });
        }
      }

      this.scheduleOverlayRepaint();
    }

    // -------------------------------------------------------------------------
    // DATA FETCHING & POPULATION (WITH PERSISTENT IN-MEMORY CACHE)
    // -------------------------------------------------------------------------

    setChartState(type, options = {}) {
      const host = document.getElementById("pro-chart-state-overlay");
      if (!host || !window.ZyroxUI) return;
      if (!type) {
        host.hidden = true;
        host.replaceChildren();
        return;
      }
      host.hidden = false;
      if (type === "loading") {
        window.ZyroxUI.mount(host, window.ZyroxUI.ChartSkeleton({ language: this.lang }));
      } else if (type === "empty") {
        const dot = document.getElementById("freshness-dot");
        const label = document.getElementById("freshness-text");
        if (dot) dot.className = "freshness-dot gray";
        if (label) label.textContent = "UNAVAILABLE · no verified candles";
        window.ZyroxUI.mount(host, window.ZyroxUI.EmptyState({
          icon: "⌁",
          title: options.title || "No chart data",
          message: options.message || "No verified candles were returned for this symbol and timeframe."
        }));
      } else {
        const dot = document.getElementById("freshness-dot");
        const label = document.getElementById("freshness-text");
        if (dot) dot.className = "freshness-dot red";
        if (label) label.textContent = "UNAVAILABLE · candle refresh failed";
        window.ZyroxUI.mount(host, window.ZyroxUI.ErrorState({
          title: options.title || "Chart refresh failed",
          message: options.message || "The chart service could not return verified candles.",
          retryLabel: options.retryLabel || "Retry chart",
          onRetry: () => this.loadCandlesAndOverlays(this.currentSymbol, this.currentTimeframe, true)
        }));
      }
    }

    async loadCandlesAndOverlays(symbol = "XAUUSD", timeframe = "M15", forceRefresh = false) {
      if (this._candleAbortController) this._candleAbortController.abort();
      const controller = new AbortController();
      this._candleAbortController = controller;
      this.currentSymbol = symbol;
      this.currentTimeframe = timeframe;

      const symDisplay = document.getElementById("pro-sym-display");
      if (symDisplay) {
        symDisplay.innerText = `${symbol} · ${timeframe}`;
      }

      const hudSym = document.getElementById("hud-symbol");
      if (hudSym) {
        hudSym.innerText = symbol;
      }

      const tfMap = { "1": "M1", "5": "M5", "15": "M15", "30": "M30", "60": "H1", "240": "H4", "D": "D1", "W": "W1" };
      const cleanTf = tfMap[timeframe] || timeframe;
      const cacheKey = `${symbol}_${cleanTf}`;
      const cachedSnapshot = this.candleCache[cacheKey];
      const hasCachedData = Boolean(cachedSnapshot && Array.isArray(cachedSnapshot.candles) && cachedSnapshot.candles.length);

      // Show only a matching symbol/timeframe snapshot while fetching its update.
      if (hasCachedData) {
        const cached = cachedSnapshot;
        this.candlesData = cached.candles || [];
        this.annotationsData = cached.annotations || {};
        this.metadata = cached.metadata || {};
        this.sessionLevels = this.annotationsData.session_levels || {};

        this.populateMainSeries();
        this.populateIndicatorOverlays();
        this.populateVolumeSeries();
        this.populateOscillatorPanes();
        this.updateDataFreshnessHud();
        this.scheduleOverlayRepaint();

        if (this.chart) {
          this.chart.timeScale().fitContent();
        }
        this.setChartState(null);
      } else {
        // Do not leave the previous instrument's candles under a new symbol label.
        this.candlesData = [];
        if (this.mainSeries) this.mainSeries.setData([]);
        if (this.volumeSeries) this.volumeSeries.setData([]);
        Object.values(this.lineSeriesMap || {}).forEach(series => {
          if (series && typeof series.setData === "function") series.setData([]);
        });
        if (this.rsiSeries) this.rsiSeries.setData([]);
        if (this.stochKSeries) this.stochKSeries.setData([]);
        if (this.stochDSeries) this.stochDSeries.setData([]);
        if (this.macdLineSeries) this.macdLineSeries.setData([]);
        if (this.macdSignalSeries) this.macdSignalSeries.setData([]);
        if (this.macdHistSeries) this.macdHistSeries.setData([]);
        this.setChartState("loading");
      }

      try {
        // Fetch fresh verified candles in background
        // 300 bars provide enough warm-up for EMA/SMA 200 and a cleaner initial EMA.
        const endpoint = `/api/v1/chart/candles?symbol=${encodeURIComponent(symbol)}&timeframe=${encodeURIComponent(cleanTf)}&limit=300`;
        const res = await fetch(endpoint, { signal: controller.signal });
        if (controller.signal.aborted) return;
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        if (!data || !data.candles || data.candles.length === 0) {
          if (!hasCachedData) this.setChartState("empty");
          return;
        }

        // Cache response for instant future switches
        this.candleCache[cacheKey] = {
          candles: data.candles,
          annotations: data.annotations || {},
          metadata: data.metadata || {}
        };

        this.candlesData = data.candles;
        this.annotationsData = data.annotations || {};
        this.metadata = data.metadata || {};
        this.sessionLevels = this.annotationsData.session_levels || {};

        // 1. Populate Main Price Series
        this.populateMainSeries();

        // 2. Populate Technical Indicators (EMA, SMA, BB, Keltner, VWAP)
        this.populateIndicatorOverlays();

        // 3. Populate Volume Series
        this.populateVolumeSeries();

        // 4. Populate RSI & MACD Panes
        this.populateOscillatorPanes();

        // 5. Update Data Freshness Badge & HUD
        this.updateDataFreshnessHud();

        // 6. Repaint SVG Overlays
        this.scheduleOverlayRepaint();

        // 7. Auto-fit chart if newly loaded
        if (this.chart && (!this.candleCache[cacheKey] || forceRefresh)) {
          this.chart.timeScale().fitContent();
        }
        this.setChartState(null);

      } catch (err) {
        if (err && err.name === "AbortError") return;
        console.error("Failed to load chart data:", err);
        if (hasCachedData) {
          const freshness = document.getElementById("freshness-text");
          const dot = document.getElementById("freshness-dot");
          if (dot) dot.className = "freshness-dot yellow";
          if (freshness) freshness.textContent = "Refresh delayed · showing cached candles";
        } else {
          this.setChartState("error", { message: err.message || "The chart service could not be reached." });
        }
      }
    }

    populateMainSeries() {
      if (!this.mainSeries || !this.candlesData.length) return;

      if (this.currentChartType === "line" || this.currentChartType === "area") {
        const lineData = this.candlesData.map(c => ({
          time: c.time,
          value: c.close
        }));
        this.mainSeries.setData(lineData);
      } else {
        const ohlcData = this.candlesData.map(c => ({
          time: c.time,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close
        }));
        this.mainSeries.setData(ohlcData);
      }

      // Update Latest Quote HUD
      const last = this.candlesData[this.candlesData.length - 1];
      this.updateHudWithCandle(last);
    }

    populateVolumeSeries() {
      if (!this.volumeSeries || !this.candlesData.length) return;
      const volData = this.candlesData.map(c => ({
        time: c.time,
        value: c.volume,
        color: c.close >= c.open ? "rgba(34, 197, 94, 0.4)" : "rgba(239, 68, 68, 0.4)"
      }));
      this.volumeSeries.setData(volData);
    }

    populateIndicatorOverlays() {
      if (!this.chart || !this.candlesData.length) return;

      // Define Indicator Overlay Specs
      const overlays = [
        { id: "ema_9", key: "ema_9", color: "#38bdf8", width: 1 },
        { id: "ema_20", key: "ema_20", color: "#22c55e", width: 2 },
        { id: "ema_50", key: "ema_50", color: "#f59e0b", width: 2 },
        { id: "ema_100", key: "ema_100", color: "#a855f7", width: 1 },
        { id: "ema_200", key: "ema_200", color: "#ef4444", width: 2 },
        { id: "sma_20", key: "sma_20", color: "#94a3b8", width: 1 },
        { id: "sma_50", key: "sma_50", color: "#64748b", width: 1 },
        { id: "sma_200", key: "sma_200", color: "#e2e8f0", width: 2 },
        { id: "vwap", key: "vwap", color: "#eab308", width: 1, lineStyle: 2 },
        { id: "bb_upper", key: "bb_upper", color: "rgba(129, 140, 248, 0.8)", width: 1 },
        { id: "bb_lower", key: "bb_lower", color: "rgba(129, 140, 248, 0.8)", width: 1 },
        { id: "kc_upper", key: "kc_upper", color: "rgba(6, 182, 212, 0.8)", width: 1, lineStyle: 2 },
        { id: "kc_lower", key: "kc_lower", color: "rgba(6, 182, 212, 0.8)", width: 1, lineStyle: 2 }
      ];

      overlays.forEach(spec => {
        const isEnabled = (spec.id.startsWith("bb_") && this.indicatorSettings.bollinger) ||
                          (spec.id.startsWith("kc_") && this.indicatorSettings.keltner) ||
                          this.indicatorSettings[spec.id];

        if (isEnabled) {
          if (!this.lineSeriesMap[spec.id]) {
            this.lineSeriesMap[spec.id] = this.chart.addLineSeries({
              color: spec.color,
              lineWidth: spec.width || 1,
              lineStyle: spec.lineStyle || 0,
              crosshairMarkerVisible: false,
              priceLineVisible: false
            });
          }

          const seriesData = this.candlesData
            .filter(c => c[spec.key] !== null && c[spec.key] !== undefined && !isNaN(c[spec.key]))
            .map(c => ({
              time: c.time,
              value: c[spec.key]
            }));

          this.lineSeriesMap[spec.id].setData(seriesData);
        } else if (this.lineSeriesMap[spec.id]) {
          this.chart.removeSeries(this.lineSeriesMap[spec.id]);
          delete this.lineSeriesMap[spec.id];
        }
      });
    }

    populateOscillatorPanes() {
      // 1. RSI Data
      if (this.rsiSeries && this.candlesData.length) {
        const rsiData = this.candlesData
          .filter(c => c.rsi_14 !== null && c.rsi_14 !== undefined && !isNaN(c.rsi_14))
          .map(c => ({
            time: c.time,
            value: c.rsi_14
          }));
        this.rsiSeries.setData(rsiData);
      }

      // 2. Stochastic oscillator (%K / %D)
      if (this.stochKSeries && this.candlesData.length) {
        const kData = this.candlesData
          .filter(c => c.stoch_k !== null && c.stoch_k !== undefined && Number.isFinite(Number(c.stoch_k)))
          .map(c => ({ time: c.time, value: Number(c.stoch_k) }));
        const dData = this.candlesData
          .filter(c => c.stoch_d !== null && c.stoch_d !== undefined && Number.isFinite(Number(c.stoch_d)))
          .map(c => ({ time: c.time, value: Number(c.stoch_d) }));
        this.stochKSeries.setData(kData);
        this.stochDSeries.setData(dData);
      }

      // 3. MACD Data
      if (this.macdLineSeries && this.candlesData.length) {
        const macdData = [];
        const signalData = [];
        const histData = [];

        this.candlesData.forEach(c => {
          if (c.macd !== null && !isNaN(c.macd)) {
            macdData.push({ time: c.time, value: c.macd });
          }
          if (c.macd_signal !== null && !isNaN(c.macd_signal)) {
            signalData.push({ time: c.time, value: c.macd_signal });
          }
          if (c.macd_hist !== null && !isNaN(c.macd_hist)) {
            histData.push({
              time: c.time,
              value: c.macd_hist,
              color: c.macd_hist >= 0 ? "rgba(34, 197, 94, 0.7)" : "rgba(239, 68, 68, 0.7)"
            });
          }
        });

        this.macdLineSeries.setData(macdData);
        this.macdSignalSeries.setData(signalData);
        this.macdHistSeries.setData(histData);
      }
    }

    // -------------------------------------------------------------------------
    // INCREMENTAL REAL-TIME CANDLE UPDATES (Zero Lookahead & Continuous Feed)
    // -------------------------------------------------------------------------

    calculateLatestIndicatorValues() {
      const rows = this.candlesData || [];
      const closes = rows.map(c => Number(c.close));
      if (!closes.length || closes.some(value => !Number.isFinite(value))) return null;
      const emaSeries = (values, period) => {
        if (!values.length) return [];
        const alpha = 2 / (period + 1);
        const result = [values[0]];
        for (let i = 1; i < values.length; i++) result.push(alpha * values[i] + (1 - alpha) * result[i - 1]);
        return result;
      };
      const smaLast = (values, period) => values.length < period ? null : values.slice(-period).reduce((a, b) => a + b, 0) / period;
      const ema9 = emaSeries(closes, 9).at(-1);
      const ema20Series = emaSeries(closes, 20);
      const ema50Series = emaSeries(closes, 50);
      const ema100Series = emaSeries(closes, 100);
      const ema200Series = emaSeries(closes, 200);
      const fast = emaSeries(closes, 12);
      const slow = emaSeries(closes, 26);
      const macdSeries = fast.map((value, index) => value - slow[index]);
      const signalSeries = emaSeries(macdSeries, 9);

      const gains = [];
      const losses = [];
      for (let i = 0; i < closes.length; i++) {
        const delta = i ? closes[i] - closes[i - 1] : 0;
        gains.push(Math.max(0, delta));
        losses.push(Math.max(0, -delta));
      }
      // Recalculate Wilder smoothing with its exact alpha rather than EMA's 2/(n+1).
      const wilderLast = values => values.reduce((prev, current, index) => index ? ((prev * 13) + current) / 14 : current, 0);
      const avgGain = wilderLast(gains);
      const avgLoss = wilderLast(losses);
      const rsi = avgLoss <= 0 ? (avgGain > 0 ? 100 : 50) : 100 - (100 / (1 + avgGain / avgLoss));

      const trueRanges = rows.map((c, index) => {
        const high = Number(c.high), low = Number(c.low);
        if (!Number.isFinite(high) || !Number.isFinite(low)) return null;
        if (!index) return high - low;
        const prevClose = closes[index - 1];
        return Math.max(high - low, Math.abs(high - prevClose), Math.abs(low - prevClose));
      });
      let atr = null;
      if (trueRanges.length >= 14 && trueRanges.slice(0, 14).every(Number.isFinite)) {
        atr = trueRanges.slice(0, 14).reduce((a, b) => a + b, 0) / 14;
        for (let i = 14; i < trueRanges.length; i++) {
          if (Number.isFinite(trueRanges[i])) atr = ((atr * 13) + trueRanges[i]) / 14;
        }
      }

      const highs = rows.map(c => Number(c.high));
      const lows = rows.map(c => Number(c.low));
      const rawStoch = [];
      for (let i = 0; i < rows.length; i++) {
        const start = Math.max(0, i - 13);
        const highest = Math.max(...highs.slice(start, i + 1));
        const lowest = Math.min(...lows.slice(start, i + 1));
        rawStoch.push(highest === lowest ? 50 : 100 * (closes[i] - lowest) / (highest - lowest));
      }
      const kSeries = rawStoch.map((_, index) => {
        const window = rawStoch.slice(Math.max(0, index - 2), index + 1);
        return window.reduce((a, b) => a + b, 0) / window.length;
      });
      const dSeries = kSeries.map((_, index) => {
        const window = kSeries.slice(Math.max(0, index - 2), index + 1);
        return window.reduce((a, b) => a + b, 0) / window.length;
      });

      const last20 = closes.slice(-20);
      const bbMiddle = last20.reduce((a, b) => a + b, 0) / last20.length;
      const bbVariance = last20.length > 1 ? last20.reduce((sum, value) => sum + ((value - bbMiddle) ** 2), 0) / (last20.length - 1) : 0;
      const bbStd = Math.sqrt(bbVariance);

      const last = rows[rows.length - 1];
      const utcDate = new Date(Number(last.time) * 1000).toISOString().slice(0, 10);
      let pv = 0, totalVolume = 0;
      rows.forEach(c => {
        if (new Date(Number(c.time) * 1000).toISOString().slice(0, 10) !== utcDate) return;
        const volume = Number(c.volume || 0);
        if (!Number.isFinite(volume) || volume <= 0) return;
        pv += ((Number(c.high) + Number(c.low) + Number(c.close)) / 3) * volume;
        totalVolume += volume;
      });
      const ema20 = ema20Series.at(-1);
      return {
        ema_9: ema9,
        ema_20: ema20,
        ema_50: rows.length >= 50 ? ema50Series.at(-1) : null,
        ema_100: rows.length >= 100 ? ema100Series.at(-1) : null,
        ema_200: rows.length >= 200 ? ema200Series.at(-1) : null,
        sma_20: smaLast(closes, 20),
        sma_50: smaLast(closes, 50),
        sma_200: smaLast(closes, 200),
        vwap: totalVolume > 0 ? pv / totalVolume : null,
        bb_upper: bbMiddle + (2 * bbStd),
        bb_lower: bbMiddle - (2 * bbStd),
        kc_upper: ema20 + (1.5 * (atr || 0)),
        kc_lower: ema20 - (1.5 * (atr || 0)),
        rsi_14: rsi,
        stoch_k: kSeries.at(-1),
        stoch_d: dSeries.at(-1),
        macd: macdSeries.at(-1),
        macd_signal: signalSeries.at(-1),
        macd_hist: macdSeries.at(-1) - signalSeries.at(-1),
        atr_14: atr,
      };
    }

    updateRealtimeIndicators(candle) {
      if (!candle) return;
      const values = this.calculateLatestIndicatorValues();
      if (!values) return;
      Object.assign(candle, values);
      const specs = {
        ema_9: values.ema_9, ema_20: values.ema_20, ema_50: values.ema_50,
        ema_100: values.ema_100, ema_200: values.ema_200, sma_20: values.sma_20,
        sma_50: values.sma_50, sma_200: values.sma_200, vwap: values.vwap,
        bb_upper: values.bb_upper, bb_lower: values.bb_lower,
        kc_upper: values.kc_upper, kc_lower: values.kc_lower,
      };
      Object.entries(specs).forEach(([id, value]) => {
        if (this.lineSeriesMap[id] && Number.isFinite(value)) {
          this.lineSeriesMap[id].update({ time: candle.time, value });
        }
      });
      if (this.rsiSeries && Number.isFinite(values.rsi_14)) this.rsiSeries.update({ time: candle.time, value: values.rsi_14 });
      if (this.stochKSeries && Number.isFinite(values.stoch_k)) this.stochKSeries.update({ time: candle.time, value: values.stoch_k });
      if (this.stochDSeries && Number.isFinite(values.stoch_d)) this.stochDSeries.update({ time: candle.time, value: values.stoch_d });
      if (this.macdLineSeries && Number.isFinite(values.macd)) this.macdLineSeries.update({ time: candle.time, value: values.macd });
      if (this.macdSignalSeries && Number.isFinite(values.macd_signal)) this.macdSignalSeries.update({ time: candle.time, value: values.macd_signal });
      if (this.macdHistSeries && Number.isFinite(values.macd_hist)) {
        this.macdHistSeries.update({
          time: candle.time,
          value: values.macd_hist,
          color: values.macd_hist >= 0 ? "rgba(34, 197, 94, 0.7)" : "rgba(239, 68, 68, 0.7)",
        });
      }
      if (this.volumeSeries) {
        this.volumeSeries.update({
          time: candle.time,
          value: Number(candle.volume || 0),
          color: candle.close >= candle.open ? "rgba(34, 197, 94, 0.4)" : "rgba(239, 68, 68, 0.4)",
        });
      }
    }

    updateRealtimeTick(price, volume = 0, timestamp = null) {
      if (!this.mainSeries || !this.candlesData.length) return;

      const p = parseFloat(price);
      if (!Number.isFinite(p) || p <= 0) return;
      const lastCandle = this.candlesData[this.candlesData.length - 1];
      const parsedTimestamp = timestamp
        ? (typeof timestamp === "number"
          ? (timestamp > 1e12 ? timestamp : timestamp * 1000)
          : new Date(timestamp).getTime())
        : Date.now();
      const nowUnix = Number.isFinite(parsedTimestamp) ? Math.floor(parsedTimestamp / 1000) : Math.floor(Date.now() / 1000);
      const tfSecondsMap = {
        "1": 60, M1: 60, "5": 300, M5: 300, "15": 900, M15: 900,
        "30": 1800, M30: 1800, "60": 3600, H1: 3600,
        "240": 14400, H4: 14400, D: 86400, D1: 86400, W: 604800, W1: 604800,
      };
      const tfSec = tfSecondsMap[this.currentTimeframe] || 900;
      const candleTime = Math.floor(nowUnix / tfSec) * tfSec;
      if (candleTime < Number(lastCandle.time)) return;

      const tickVolume = Number.isFinite(Number(volume)) && Number(volume) > 0 ? Number(volume) : 0;
      let updatedCandle;
      let historyTrimmed = false;
      if (candleTime > Number(lastCandle.time)) {
        updatedCandle = {
          time: candleTime,
          open: p,
          high: p,
          low: p,
          close: p,
          volume: tickVolume,
        };
        this.candlesData.push(updatedCandle);
        if (this.candlesData.length > 500) {
          this.candlesData.shift();
          historyTrimmed = true;
        }
        if (this.currentChartType === "line" || this.currentChartType === "area") {
          this.mainSeries.update({ time: updatedCandle.time, value: p });
        } else {
          this.mainSeries.update(updatedCandle);
        }
      } else {
        updatedCandle = lastCandle;
        updatedCandle.high = Math.max(Number(updatedCandle.high), p);
        updatedCandle.low = Math.min(Number(updatedCandle.low), p);
        updatedCandle.close = p;
        if (tickVolume > 0) updatedCandle.volume = (Number(updatedCandle.volume) || 0) + tickVolume;
        if (this.currentChartType === "line" || this.currentChartType === "area") {
          this.mainSeries.update({ time: updatedCandle.time, value: p });
        } else {
          this.mainSeries.update({
            time: updatedCandle.time,
            open: updatedCandle.open,
            high: updatedCandle.high,
            low: updatedCandle.low,
            close: updatedCandle.close,
          });
        }
      }

      this.updateRealtimeIndicators(updatedCandle);
      if (historyTrimmed) {
        this.populateMainSeries();
        this.populateVolumeSeries();
        this.populateIndicatorOverlays();
        this.populateOscillatorPanes();
      }
      this.updateHudWithCandle(updatedCandle);
    }

    // -------------------------------------------------------------------------
    // HUD & DATA FRESHNESS BANNER
    // -------------------------------------------------------------------------

    getPricePrecision() {
      const configured = Number(this.metadata?.price_precision);
      if (Number.isInteger(configured) && configured >= 0 && configured <= 10) return configured;
      const symbol = String(this.currentSymbol || "").toUpperCase();
      if (symbol.includes("XAU")) return 2;
      if (symbol.includes("JPY") || symbol.includes("XAG")) return 3;
      if (/^[A-Z]{6}$/.test(symbol)) return 5;
      return 2;
    }

    formatPrice(value) {
      const number = Number(value);
      return Number.isFinite(number) ? number.toFixed(this.getPricePrecision()) : "---";
    }

    updateHudWithCandle(c) {
      if (!c) return;
      const elOpen = document.getElementById("hud-open");
      const elHigh = document.getElementById("hud-high");
      const elLow = document.getElementById("hud-low");
      const elClose = document.getElementById("hud-close");
      const elChg = document.getElementById("hud-change");
      const elVol = document.getElementById("hud-vol");
      const elAtr = document.getElementById("hud-atr");
      const elTime = document.getElementById("hud-time");

      if (elOpen) elOpen.innerText = this.formatPrice(c.open);
      if (elHigh) elHigh.innerText = this.formatPrice(c.high);
      if (elLow) elLow.innerText = this.formatPrice(c.low);
      if (elClose) {
        elClose.innerText = this.formatPrice(c.close);
        elClose.style.color = c.close >= c.open ? "#10b981" : "#ef4444";
      }
      if (elChg) {
        const chg = c.close - c.open;
        const pct = c.open > 0 ? (chg / c.open) * 100 : 0;
        elChg.innerText = `${chg >= 0 ? '+' : ''}${this.formatPrice(chg)} (${pct.toFixed(2)}%)`;
        elChg.style.color = chg >= 0 ? "#10b981" : "#ef4444";
      }
      if (elVol) elVol.innerText = (c.volume || 0).toLocaleString();
      if (elAtr) elAtr.innerText = c.atr_14 == null ? "---" : this.formatPrice(c.atr_14);
      if (elTime) {
        if (c.timestamp_cambodia) {
          elTime.innerText = `${c.timestamp_cambodia} (KH)`;
        } else if (Number.isFinite(Number(c.time))) {
          elTime.innerText = `${new Date(Number(c.time) * 1000).toLocaleString("en-GB", { timeZone: "Asia/Phnom_Penh" })} (KH)`;
        }
      }
    }

    onCrosshairMove(param) {
      if (!param || !param.time || !param.seriesData) return;
      const priceData = param.seriesData.get(this.mainSeries);
      if (priceData) {
        this.updateHudWithCandle({
          open: priceData.open !== undefined ? priceData.open : priceData.value,
          high: priceData.high !== undefined ? priceData.high : priceData.value,
          low: priceData.low !== undefined ? priceData.low : priceData.value,
          close: priceData.close !== undefined ? priceData.close : priceData.value,
          volume: priceData.volume || 0,
          timestamp_cambodia: new Date(param.time * 1000).toLocaleTimeString("en-GB", { timeZone: "Asia/Phnom_Penh" })
        });
      }
    }

    updateDataFreshnessHud() {
      const dot = document.getElementById("freshness-dot");
      const text = document.getElementById("freshness-text");
      if (!dot || !text) return;

      const status = this.metadata.freshness_status || "LIVE_FRESH";
      const provider = this.metadata.provider_display || this.metadata.provider || "verified_feed";
      const quoteType = this.metadata.quote_type ? ` · ${this.metadata.quote_type}` : "";
      const hasExecutionQuote = this.metadata.execution_quote_available === true;

      switch (status) {
        case "LIVE_FRESH":
          dot.className = hasExecutionQuote ? "freshness-dot pulse green" : "freshness-dot yellow";
          text.innerText = hasExecutionQuote
            ? `● LIVE · ${this.metadata.execution_quote_provider || provider}${quoteType}`
            : `◷ REFERENCE ONLY · ${provider}${quoteType}`;
          break;
        case "SLIGHTLY_DELAYED":
          dot.className = "freshness-dot yellow";
          text.innerText = `▲ DELAYED (${this.metadata.candle_age_seconds || 0}s) · ${provider}`;
          break;
        case "WEEKEND_CLOSED":
          dot.className = "freshness-dot gray";
          text.innerText = `🔒 WEEKEND CLOSED · ${provider}`;
          break;
        case "STALE":
        default:
          dot.className = "freshness-dot red";
          text.innerText = `⚠️ STALE DATA · ${provider}`;
          break;
      }
    }

    // -------------------------------------------------------------------------
    // VECTOR ANNOTATIONS & ICT/SMC OVERLAYS (SVG LAYER)
    // -------------------------------------------------------------------------

    scheduleOverlayRepaint() {
      if (this._rafId) cancelAnimationFrame(this._rafId);
      this._rafId = requestAnimationFrame(() => {
        this.paintSMCOverlays();
        this.paintDrawings();
      });
    }

    paintSMCOverlays() {
      if (!this.overlaySvg || !this.chart || !this.mainSeries || !this.candlesData.length) return;
      this.overlaySvg.innerHTML = "";

      const timeScale = this.chart.timeScale();
      const visibleRange = timeScale.getVisibleLogicalRange();
      if (!visibleRange) return;

      const minLogical = Math.max(0, Math.floor(visibleRange.from) - 8);
      const maxLogical = Math.min(this.candlesData.length - 1, Math.ceil(visibleRange.to) + 8);

      const mainPane = document.getElementById("pro-chart-main-pane");
      const paneWidth = mainPane ? mainPane.clientWidth : 800;

      const timeToX = (unixTime) => timeScale.timeToCoordinate(unixTime);
      const priceToY = (price) => this.mainSeries.priceToCoordinate(price);

      let svgElements = "";

      // 1. FAIR VALUE GAPS (FVG) - With spatial culling
      if (this.indicatorSettings.smc_fvg && this.annotationsData.fair_value_gaps) {
        this.annotationsData.fair_value_gaps.forEach(fvg => {
          const cIdx = fvg.confirmation_index;
          if (cIdx === undefined || cIdx >= this.candlesData.length) return;

          const mIdx = fvg.mitigated_index;
          if (mIdx !== undefined && mIdx < minLogical) return;
          if (cIdx > maxLogical) return;

          const startCandle = this.candlesData[fvg.creation_index] || this.candlesData[cIdx];
          const endCandle = mIdx !== undefined && mIdx < this.candlesData.length
            ? this.candlesData[mIdx]
            : this.candlesData[this.candlesData.length - 1];

          const x1 = timeToX(startCandle.time);
          const x2 = timeToX(endCandle.time);
          if (x1 === null || x2 === null) return;
          if (Math.max(x1, x2) < -50 || Math.min(x1, x2) > paneWidth + 50) return;

          const yTop = priceToY(fvg.top);
          const yBottom = priceToY(fvg.bottom);
          const yMid = priceToY(fvg.midpoint_ce);

          if (yTop !== null && yBottom !== null) {
            const isBull = fvg.type === "BULLISH_FVG";
            const boxColor = isBull ? "rgba(16, 185, 129, 0.18)" : "rgba(244, 63, 94, 0.18)";
            const strokeColor = isBull ? "rgba(16, 185, 129, 0.7)" : "rgba(244, 63, 94, 0.7)";
            const width = Math.max(10, x2 - x1);
            const height = Math.abs(yBottom - yTop);
            const topY = Math.min(yTop, yBottom);

            svgElements += `
              <rect x="${x1}" y="${topY}" width="${width}" height="${height}" fill="${boxColor}" stroke="${strokeColor}" stroke-dasharray="3,3" stroke-width="1" rx="2" />
              <!-- Consequent Encroachment (CE 50%) Midline -->
              <line x1="${x1}" y1="${yMid}" x2="${x1 + width}" y2="${yMid}" stroke="${strokeColor}" stroke-width="1" opacity="0.6" stroke-dasharray="2,2" />
              <!-- FVG Tag -->
              <text x="${x1 + 4}" y="${topY + 12}" fill="${strokeColor}" font-size="9" font-family="'Inter', sans-serif" font-weight="600">
                ${isBull ? '+FVG' : '-FVG'} ${fvg.status === 'OPEN' ? '⚡' : '✓'}
              </text>
            `;
          }
        });
      }

      // 2. INSTITUTIONAL ORDER BLOCKS (OB) - With spatial culling
      if (this.indicatorSettings.smc_ob && this.annotationsData.order_blocks) {
        this.annotationsData.order_blocks.forEach(ob => {
          const cIdx = ob.candle_index;
          if (cIdx === undefined || cIdx >= this.candlesData.length) return;

          const mIdx = ob.mitigated_index;
          if (mIdx !== undefined && mIdx < minLogical) return;
          if (cIdx > maxLogical) return;

          const startCandle = this.candlesData[cIdx];
          const endCandle = mIdx !== undefined && mIdx < this.candlesData.length
            ? this.candlesData[mIdx]
            : this.candlesData[this.candlesData.length - 1];

          const x1 = timeToX(startCandle.time);
          const x2 = timeToX(endCandle.time);
          if (x1 === null || x2 === null) return;
          if (Math.max(x1, x2) < -50 || Math.min(x1, x2) > paneWidth + 50) return;

          const yHigh = priceToY(ob.high);
          const yLow = priceToY(ob.low);

          if (yHigh !== null && yLow !== null) {
            const isBull = ob.type === "BULLISH_ORDER_BLOCK";
            const boxColor = isBull ? "rgba(34, 197, 94, 0.12)" : "rgba(168, 85, 247, 0.12)";
            const strokeColor = isBull ? "#22c55e" : "#a855f7";
            const width = Math.max(10, x2 - x1);
            const height = Math.abs(yLow - yHigh);
            const topY = Math.min(yHigh, yLow);

            svgElements += `
              <rect x="${x1}" y="${topY}" width="${width}" height="${height}" fill="${boxColor}" stroke="${strokeColor}" stroke-width="1.2" rx="3" />
              <text x="${x1 + 4}" y="${topY + 12}" fill="${strokeColor}" font-size="9" font-weight="bold">
                ${isBull ? '🟢 BULL OB' : '🟣 BEAR OB'} [${ob.status}]
              </text>
            `;
          }
        });
      }

      // 3. BREAK OF STRUCTURE (BOS) & CHANGE OF CHARACTER (CHOCH)
      if ((this.indicatorSettings.smc_bos || this.indicatorSettings.smc_choch) && this.annotationsData.structure_breaks) {
        this.annotationsData.structure_breaks.forEach(sb => {
          const isChoch = sb.category === "CHOCH";
          if (isChoch && !this.indicatorSettings.smc_choch) return;
          if (!isChoch && !this.indicatorSettings.smc_bos) return;

          const pIdx = sb.pivot_index;
          const bIdx = sb.break_index;
          if (pIdx === undefined || bIdx === undefined || pIdx >= this.candlesData.length || bIdx >= this.candlesData.length) return;

          if (bIdx < minLogical || pIdx > maxLogical) return;

          const candlePivot = this.candlesData[pIdx];
          const candleBreak = this.candlesData[bIdx];

          const x1 = timeToX(candlePivot.time);
          const x2 = timeToX(candleBreak.time);
          if (x1 === null || x2 === null) return;
          if (Math.max(x1, x2) < -50 || Math.min(x1, x2) > paneWidth + 50) return;

          const y = priceToY(sb.broken_level);

          if (y !== null) {
            const color = isChoch ? "#f59e0b" : "#38bdf8"; // Amber for CHoCH, Cyan for BOS
            svgElements += `
              <line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke="${color}" stroke-width="${isChoch ? 1.8 : 1.2}" stroke-dasharray="${isChoch ? 'none' : '4,3'}" />
              <circle cx="${x1}" cy="${y}" r="2.5" fill="${color}" />
              <rect x="${x2 - 32}" y="${y - 14}" width="42" height="13" fill="#090d16" stroke="${color}" stroke-width="0.8" rx="2" />
              <text x="${x2 - 30}" y="${y - 4}" fill="${color}" font-size="8.5" font-weight="bold">
                ${sb.category} (${sb.direction[0]})
              </text>
            `;
          }
        });
      }

      // 4. LIQUIDITY SWEEPS (BSL / SSL)
      if (this.indicatorSettings.smc_sweeps && this.annotationsData.liquidity_sweeps) {
        this.annotationsData.liquidity_sweeps.forEach(ls => {
          const sIdx = ls.sweep_index;
          if (sIdx === undefined || sIdx >= this.candlesData.length) return;
          if (sIdx < minLogical || sIdx > maxLogical) return;

          const c = this.candlesData[sIdx];
          const x = timeToX(c.time);
          if (x === null || x < -20 || x > paneWidth + 20) return;

          const yWick = ls.type === "BUY_SIDE_LIQUIDITY_SWEEP" ? priceToY(ls.wick_high) : priceToY(ls.wick_low);

          if (yWick !== null) {
            const isBSL = ls.type === "BUY_SIDE_LIQUIDITY_SWEEP";
            const color = isBSL ? "#f43f5e" : "#10b981";
            const arrowY = isBSL ? yWick - 12 : yWick + 12;

            svgElements += `
              <polygon points="${x},${yWick} ${x - 4},${arrowY} ${x + 4},${arrowY}" fill="${color}" />
              <text x="${x + 6}" y="${yWick + (isBSL ? -4 : 10)}" fill="${color}" font-size="8.5" font-weight="bold">
                ${isBSL ? '▼ BSL SWEEP' : '▲ SSL SWEEP'}
              </text>
            `;
          }
        });
      }

      // 5. SESSION LEVELS (DO, PDH, PDL, PIVOT)
      if (this.indicatorSettings.session_levels && this.sessionLevels) {
        const levels = [
          { label: "PDH", price: this.sessionLevels.previous_day_high, color: "#f43f5e" },
          { label: "PDL", price: this.sessionLevels.previous_day_low, color: "#10b981" },
          { label: "DO", price: this.sessionLevels.daily_open, color: "#eab308" },
          { label: "PIVOT", price: this.sessionLevels.pivot_point, color: "#94a3b8" }
        ];

        levels.forEach(lvl => {
          if (!lvl.price || isNaN(lvl.price)) return;
          const y = priceToY(lvl.price);
          if (y !== null) {
            svgElements += `
              <line x1="0" y1="${y}" x2="100%" y2="${y}" stroke="${lvl.color}" stroke-width="0.8" stroke-dasharray="5,4" opacity="0.6" />
              <text x="8" y="${y - 3}" fill="${lvl.color}" font-size="8.5" opacity="0.85">${lvl.label}: ${this.formatPrice(lvl.price)}</text>
            `;
          }
        });
      }

      this.overlaySvg.innerHTML = svgElements;
    }

    // -------------------------------------------------------------------------
    // INTERACTIVE VECTOR DRAWING TOOLS
    // -------------------------------------------------------------------------

    setupDrawingEvents() {
      if (!this.drawingSvg) return;

      this.drawingSvg.addEventListener("click", (e) => {
        if (this.activeTool === "cursor") return;

        const rect = this.drawingSvg.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickY = e.clientY - rect.top;

        this.handleDrawingClick(clickX, clickY);
      });
    }

    setDrawingTool(toolName, btnEl) {
      this.activeTool = toolName;
      this.drawingPoints = [];

      document.querySelectorAll(".pro-tool-icon-btn").forEach(b => b.classList.remove("active"));
      if (btnEl) btnEl.classList.add("active");

      if (this.drawingSvg) {
        if (toolName === "cursor") {
          this.drawingSvg.style.pointerEvents = "none";
          this.drawingSvg.classList.remove("drawing-active");
        } else {
          this.drawingSvg.style.pointerEvents = "auto";
          this.drawingSvg.classList.add("drawing-active");
        }
      }
    }

    resetDrawingToolToCursor() {
      this.activeTool = "cursor";
      this.drawingPoints = [];
      document.querySelectorAll(".pro-tool-icon-btn").forEach(b => {
        b.classList.toggle("active", b.getAttribute("title") === this.t("cursor") || b.innerText === "✛");
      });
      if (this.drawingSvg) {
        this.drawingSvg.style.pointerEvents = "none";
        this.drawingSvg.classList.remove("drawing-active");
      }
    }

    handleDrawingClick(x, y) {
      if (!this.chart || !this.mainSeries) return;

      const timeScale = this.chart.timeScale();
      const time = timeScale.coordinateToTime(x);
      const price = this.mainSeries.coordinateToPrice(y);

      if (!time || !price) return;

      this.drawingPoints.push({ x, y, time, price });

      if (this.activeTool === "ray") {
        // Horizontal Ray needs 1 click
        this.drawings.push({
          type: "ray",
          price: price,
          color: "#38bdf8"
        });
        this.drawingPoints = [];
        this.paintDrawings();
        this.resetDrawingToolToCursor();
      } else if (this.activeTool === "trendline" && this.drawingPoints.length === 2) {
        // Trendline needs 2 clicks
        this.drawings.push({
          type: "trendline",
          p1: this.drawingPoints[0],
          p2: this.drawingPoints[1],
          color: "#f59e0b"
        });
        this.drawingPoints = [];
        this.paintDrawings();
        this.resetDrawingToolToCursor();
      } else if (this.activeTool === "fibo" && this.drawingPoints.length === 2) {
        // Fibonacci Retracement needs 2 clicks (High and Low)
        this.drawings.push({
          type: "fibo",
          p1: this.drawingPoints[0],
          p2: this.drawingPoints[1]
        });
        this.drawingPoints = [];
        this.paintDrawings();
        this.resetDrawingToolToCursor();
      } else if (this.activeTool === "ruler" && this.drawingPoints.length === 2) {
        // Measure ruler needs 2 clicks
        this.drawings.push({
          type: "ruler",
          p1: this.drawingPoints[0],
          p2: this.drawingPoints[1]
        });
        this.drawingPoints = [];
        this.paintDrawings();
        this.resetDrawingToolToCursor();
      }
    }

    paintDrawings() {
      if (!this.drawingSvg || !this.chart || !this.mainSeries) return;
      this.drawingSvg.innerHTML = "";

      const timeScale = this.chart.timeScale();
      const timeToX = (t) => timeScale.timeToCoordinate(t);
      const priceToY = (p) => this.mainSeries.priceToCoordinate(p);

      let svg = "";

      this.drawings.forEach(d => {
        if (d.type === "ray") {
          const y = priceToY(d.price);
          if (y !== null) {
            svg += `
              <line x1="0" y1="${y}" x2="100%" y2="${y}" stroke="${d.color}" stroke-width="1.5" />
              <text x="12" y="${y - 4}" fill="${d.color}" font-size="9" font-weight="bold">RAY: ${this.formatPrice(d.price)}</text>
            `;
          }
        } else if (d.type === "trendline") {
          const x1 = timeToX(d.p1.time);
          const y1 = priceToY(d.p1.price);
          const x2 = timeToX(d.p2.time);
          const y2 = priceToY(d.p2.price);

          if (x1 !== null && y1 !== null && x2 !== null && y2 !== null) {
            svg += `
              <line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${d.color}" stroke-width="2" />
              <circle cx="${x1}" cy="${y1}" r="3" fill="${d.color}" />
              <circle cx="${x2}" cy="${y2}" r="3" fill="${d.color}" />
            `;
          }
        } else if (d.type === "fibo") {
          const highP = Math.max(d.p1.price, d.p2.price);
          const lowP = Math.min(d.p1.price, d.p2.price);
          const diff = highP - lowP;

          const fibRatios = [
            { r: 0.0, label: "0.0%", color: "#64748b" },
            { r: 0.382, label: "38.2%", color: "#94a3b8" },
            { r: 0.50, label: "50.0% EQ", color: "#eab308" },
            { r: 0.618, label: "61.8% OTE", color: "#22c55e" },
            { r: 0.705, label: "70.5% SWEET", color: "#10b981" },
            { r: 0.786, label: "78.6% OTE", color: "#06b6d4" },
            { r: 1.0, label: "100.0%", color: "#ef4444" }
          ];

          fibRatios.forEach(f => {
            const levelPrice = highP - (diff * f.r);
            const y = priceToY(levelPrice);
            if (y !== null) {
              svg += `
                <line x1="0" y1="${y}" x2="100%" y2="${y}" stroke="${f.color}" stroke-width="1" stroke-dasharray="3,3" opacity="0.8" />
                <text x="8" y="${y - 3}" fill="${f.color}" font-size="8.5" font-weight="600">${f.label} (${this.formatPrice(levelPrice)})</text>
              `;
            }
          });
        } else if (d.type === "ruler") {
          const x1 = timeToX(d.p1.time);
          const y1 = priceToY(d.p1.price);
          const x2 = timeToX(d.p2.time);
          const y2 = priceToY(d.p2.price);

          if (x1 !== null && y1 !== null && x2 !== null && y2 !== null) {
            const pDiff = Math.abs(d.p2.price - d.p1.price);
            const pPct = d.p1.price > 0 ? (pDiff / d.p1.price) * 100 : 0;
            const topY = Math.min(y1, y2);
            const height = Math.abs(y2 - y1);
            const leftX = Math.min(x1, x2);
            const width = Math.abs(x2 - x1);

            svg += `
              <rect x="${leftX}" y="${topY}" width="${width}" height="${height}" fill="rgba(56, 189, 248, 0.15)" stroke="#38bdf8" stroke-width="1.2" stroke-dasharray="4,2" />
              <rect x="${leftX + (width / 2) - 40}" y="${topY + (height / 2) - 10}" width="80" height="20" fill="#090d16" stroke="#38bdf8" rx="3" />
              <text x="${leftX + (width / 2)}" y="${topY + (height / 2) + 4}" fill="#38bdf8" font-size="9" font-weight="bold" text-anchor="middle">
                ${this.formatPrice(pDiff)} (${pPct.toFixed(2)}%)
              </text>
            `;
          }
        }
      });

      this.drawingSvg.innerHTML = svg;
    }

    clearDrawings() {
      this.drawings = [];
      this.drawingPoints = [];
      if (this.drawingSvg) this.drawingSvg.innerHTML = "";
    }

    // -------------------------------------------------------------------------
    // TOOLBAR CONTROLS & MODALS
    // -------------------------------------------------------------------------

    switchChartType(type) {
      this.currentChartType = type;
      this.createMainPriceSeries();
      this.populateMainSeries();
      this.scheduleOverlayRepaint();
    }

    resetView() {
      if (this.chart) {
        this.chart.timeScale().fitContent();
      }
    }

    toggleFullscreen() {
      if (!this.chartContainer) return;
      if (!document.fullscreenElement) {
        this.chartContainer.requestFullscreen().catch(err => {
          console.warn("Fullscreen request failed:", err);
        });
      } else {
        document.exitFullscreen();
      }
    }

    hasActiveIndicators() {
      return Object.keys(this.indicatorSettings).some(key => this.indicatorSettings[key] === true);
    }

    openIndicatorModal() {
      let modal = document.getElementById("pro-indicator-settings-modal");
      if (!modal) {
        modal = document.createElement("div");
        modal.id = "pro-indicator-settings-modal";
        modal.className = "modal-backdrop modal-hidden";
        document.body.appendChild(modal);
      }

      modal.innerHTML = `
        <div class="modal-card pro-indicator-modal-card">
          <div class="modal-header">
            <div class="modal-title">📈 <span>${this.t('indicators')} Manager</span></div>
            <button class="modal-close-btn" onclick="window.taikryChart.closeIndicatorModal()">✕</button>
          </div>
          <div class="indicator-settings-body">
            <!-- Trend Indicators -->
            <div class="ind-group-section">
              <div class="ind-group-title">Trend & Moving Averages</div>
              <div class="ind-options-grid">
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-ema-9" ${this.indicatorSettings.ema_9 ? 'checked' : ''}> EMA 9 (Fast Momentum)</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-ema-20" ${this.indicatorSettings.ema_20 ? 'checked' : ''}> EMA 20 (Dynamic Support)</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-ema-50" ${this.indicatorSettings.ema_50 ? 'checked' : ''}> EMA 50 (Trend Baseline)</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-ema-100" ${this.indicatorSettings.ema_100 ? 'checked' : ''}> EMA 100 (Macro Mid)</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-ema-200" ${this.indicatorSettings.ema_200 ? 'checked' : ''}> EMA 200 (Institutional)</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-sma-20" ${this.indicatorSettings.sma_20 ? 'checked' : ''}> SMA 20</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-sma-50" ${this.indicatorSettings.sma_50 ? 'checked' : ''}> SMA 50</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-sma-200" ${this.indicatorSettings.sma_200 ? 'checked' : ''}> SMA 200</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-vwap" ${this.indicatorSettings.vwap ? 'checked' : ''}> Session VWAP</label>
              </div>
            </div>

            <!-- Volatility -->
            <div class="ind-group-section">
              <div class="ind-group-title">Volatility & Envelopes</div>
              <div class="ind-options-grid">
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-bb" ${this.indicatorSettings.bollinger ? 'checked' : ''}> Bollinger Bands (20, 2.0)</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-kc" ${this.indicatorSettings.keltner ? 'checked' : ''}> Keltner Channels (20, 1.5 ATR)</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-levels" ${this.indicatorSettings.session_levels ? 'checked' : ''}> Session Levels (DO, PDH, PDL, Pivots)</label>
              </div>
            </div>

            <!-- Lower Oscillators -->
            <div class="ind-group-section">
              <div class="ind-group-title">Lower Subpanes</div>
              <div class="ind-options-grid">
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-vol" ${this.indicatorSettings.volume ? 'checked' : ''}> Volume Histogram</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-rsi" ${this.indicatorSettings.rsi ? 'checked' : ''}> Wilder's RSI 14</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-stochastic" ${this.indicatorSettings.stochastic ? 'checked' : ''}> Stochastic (14, 3, 3)</label>
                <label class="ind-checkbox-item"><input type="checkbox" id="ind-chk-macd" ${this.indicatorSettings.macd ? 'checked' : ''}> MACD (12, 26, 9)</label>
              </div>
            </div>

            <div class="modal-footer-actions">
              <button class="btn btn-secondary" onclick="window.taikryChart.closeIndicatorModal()">Cancel</button>
              <button class="btn btn-gold" onclick="window.taikryChart.applyIndicatorSettings()">Apply & Save</button>
            </div>
          </div>
        </div>
      `;

      modal.classList.remove("modal-hidden");
    }

    closeIndicatorModal() {
      const modal = document.getElementById("pro-indicator-settings-modal");
      if (modal) modal.classList.add("modal-hidden");
    }

    applyIndicatorSettings() {
      this.indicatorSettings.ema_9 = document.getElementById("ind-chk-ema-9")?.checked || false;
      this.indicatorSettings.ema_20 = document.getElementById("ind-chk-ema-20")?.checked || false;
      this.indicatorSettings.ema_50 = document.getElementById("ind-chk-ema-50")?.checked || false;
      this.indicatorSettings.ema_100 = document.getElementById("ind-chk-ema-100")?.checked || false;
      this.indicatorSettings.ema_200 = document.getElementById("ind-chk-ema-200")?.checked || false;
      this.indicatorSettings.sma_20 = document.getElementById("ind-chk-sma-20")?.checked || false;
      this.indicatorSettings.sma_50 = document.getElementById("ind-chk-sma-50")?.checked || false;
      this.indicatorSettings.sma_200 = document.getElementById("ind-chk-sma-200")?.checked || false;
      this.indicatorSettings.vwap = document.getElementById("ind-chk-vwap")?.checked || false;
      this.indicatorSettings.bollinger = document.getElementById("ind-chk-bb")?.checked || false;
      this.indicatorSettings.keltner = document.getElementById("ind-chk-kc")?.checked || false;
      this.indicatorSettings.session_levels = document.getElementById("ind-chk-levels")?.checked || false;
      this.indicatorSettings.volume = document.getElementById("ind-chk-vol")?.checked || false;
      this.indicatorSettings.rsi = document.getElementById("ind-chk-rsi")?.checked || false;
      this.indicatorSettings.stochastic = document.getElementById("ind-chk-stochastic")?.checked || false;
      this.indicatorSettings.macd = document.getElementById("ind-chk-macd")?.checked || false;

      this.saveSettings();
      this.closeIndicatorModal();

      // Instant update without tearing down the chart
      this.updateIndicatorsVisibility();
    }

    updateIndicatorsVisibility() {
      // 1. Line overlays (EMA, SMA, BB, Keltner, VWAP)
      this.populateIndicatorOverlays();

      // 2. Volume series
      if (this.indicatorSettings.volume) {
        if (!this.volumeSeries && this.chart) {
          this.volumeSeries = this.chart.addHistogramSeries({
            color: "#22c55e",
            priceFormat: { type: "volume" },
            priceScaleId: "",
            scaleMargins: { top: 0.8, bottom: 0.0 }
          });
        }
        this.populateVolumeSeries();
      } else if (this.volumeSeries && this.chart) {
        this.chart.removeSeries(this.volumeSeries);
        this.volumeSeries = null;
      }

      // 3. RSI Subpane
      const rsiPane = document.getElementById("pro-chart-rsi-pane");
      if (this.indicatorSettings.rsi) {
        if (rsiPane) rsiPane.style.display = "block";
        if (!this.rsiChart) {
          this.initRsiPane();
        }
        this.populateOscillatorPanes();
      } else {
        if (rsiPane) rsiPane.style.display = "none";
      }

      // 4. Stochastic Subpane
      const stochPane = document.getElementById("pro-chart-stoch-pane");
      if (this.indicatorSettings.stochastic) {
        if (stochPane) stochPane.style.display = "block";
        if (!this.stochChart) this.initStochasticPane();
        this.populateOscillatorPanes();
      } else if (stochPane) {
        stochPane.style.display = "none";
      }

      // 5. MACD Subpane
      const macdPane = document.getElementById("pro-chart-macd-pane");
      if (this.indicatorSettings.macd) {
        if (macdPane) macdPane.style.display = "block";
        if (!this.macdChart) {
          this.initMacdPane();
        }
        this.populateOscillatorPanes();
      } else {
        if (macdPane) macdPane.style.display = "none";
      }

      // 6. Re-sync all charts & resize
      this.syncAllCharts();
      this.handleResize();

      const btnInd = document.getElementById("btn-open-indicators");
      if (btnInd) {
        btnInd.className = `pro-toolbar-btn ${this.hasActiveIndicators() ? 'active' : ''}`;
      }
    }

    toggleSMCOverlaysModal() {
      let modal = document.getElementById("pro-smc-settings-modal");
      if (!modal) {
        modal = document.createElement("div");
        modal.id = "pro-smc-settings-modal";
        modal.className = "modal-backdrop modal-hidden";
        document.body.appendChild(modal);
      }

      modal.innerHTML = `
        <div class="modal-card pro-indicator-modal-card">
          <div class="modal-header">
            <div class="modal-title">🏛️ <span>Smart Money Concepts (ICT/SMC)</span></div>
            <button class="modal-close-btn" onclick="document.getElementById('pro-smc-settings-modal').classList.add('modal-hidden')">✕</button>
          </div>
          <div class="indicator-settings-body">
            <div class="ind-options-grid">
              <label class="ind-checkbox-item"><input type="checkbox" id="smc-chk-bos" ${this.indicatorSettings.smc_bos ? 'checked' : ''}> Break of Structure (BOS - Continuation)</label>
              <label class="ind-checkbox-item"><input type="checkbox" id="smc-chk-choch" ${this.indicatorSettings.smc_choch ? 'checked' : ''}> Change of Character (CHoCH - Reversal)</label>
              <label class="ind-checkbox-item"><input type="checkbox" id="smc-chk-fvg" ${this.indicatorSettings.smc_fvg ? 'checked' : ''}> Fair Value Gaps (Bullish & Bearish FVG)</label>
              <label class="ind-checkbox-item"><input type="checkbox" id="smc-chk-ob" ${this.indicatorSettings.smc_ob ? 'checked' : ''}> Institutional Order Blocks (OB)</label>
              <label class="ind-checkbox-item"><input type="checkbox" id="smc-chk-sweeps" ${this.indicatorSettings.smc_sweeps ? 'checked' : ''}> Liquidity Sweeps (BSL / SSL Traps)</label>
              <label class="ind-checkbox-item"><input type="checkbox" id="smc-chk-trades" ${this.indicatorSettings.trade_signals ? 'checked' : ''}> AI Signal Markers (Entry / SL / TP Lines)</label>
            </div>
            <div class="modal-footer-actions">
              <button class="btn btn-secondary" onclick="document.getElementById('pro-smc-settings-modal').classList.add('modal-hidden')">Cancel</button>
              <button class="btn btn-gold" onclick="window.taikryChart.applySMCSettings()">Apply & Save</button>
            </div>
          </div>
        </div>
      `;

      modal.classList.remove("modal-hidden");
    }

    applySMCSettings() {
      this.indicatorSettings.smc_bos = document.getElementById("smc-chk-bos")?.checked || false;
      this.indicatorSettings.smc_choch = document.getElementById("smc-chk-choch")?.checked || false;
      this.indicatorSettings.smc_fvg = document.getElementById("smc-chk-fvg")?.checked || false;
      this.indicatorSettings.smc_ob = document.getElementById("smc-chk-ob")?.checked || false;
      this.indicatorSettings.smc_sweeps = document.getElementById("smc-chk-sweeps")?.checked || false;
      this.indicatorSettings.trade_signals = document.getElementById("smc-chk-trades")?.checked || false;

      this.saveSettings();
      const modal = document.getElementById("pro-smc-settings-modal");
      if (modal) modal.classList.add("modal-hidden");

      const btnSmc = document.getElementById("btn-toggle-smc");
      if (btnSmc) {
        btnSmc.className = `pro-toolbar-btn ${this.indicatorSettings.smc_fvg ? 'active' : ''}`;
      }

      this.scheduleOverlayRepaint();
    }

    // -------------------------------------------------------------------------
    // ENGINE MODE SWITCHER (NATIVE vs TRADINGVIEW CLOUD)
    // -------------------------------------------------------------------------

    switchEngineMode(mode) {
      this.currentEngineMode = mode;
      localStorage.setItem("taikry_chart_engine_mode", mode);

      if (!this.proWorkspaceWrapper || !this.tvEmbedWrapper) {
        this.setupWorkspaceStructure();
      }

      if (mode === "tv_cloud") {
        if (this.proWorkspaceWrapper) this.proWorkspaceWrapper.style.display = "none";
        if (this.tvEmbedWrapper) {
          this.tvEmbedWrapper.style.display = "block";
          this.renderTVCloudEmbed();
        }
      } else {
        if (this.tvEmbedWrapper) this.tvEmbedWrapper.style.display = "none";
        if (this.proWorkspaceWrapper) {
          this.proWorkspaceWrapper.style.display = "flex";
          if (!this.chart) {
            this.renderNativeWorkspace();
          } else {
            // Instant 0ms switch without tearing down:
            this.handleResize();
            if (this.chart) {
              this.chart.timeScale().fitContent();
            }
            this.scheduleOverlayRepaint();
          }
        }
      }
    }

    renderTVCloudEmbed() {
      if (!this.tvEmbedWrapper) return;

      // Resolve TradingView widget symbol from backend metadata, global alignment, or fallback map
      const tvMap = {
        "XAUUSD": this.metadata?.tv_reference_symbol || window.TAIKRY_TV_REFERENCE_SYMBOL || "OANDA:XAUUSD",
        "XAGUSD": "OANDA:XAGUSD",
        "EURUSD": "FX:EURUSD",
        "GBPUSD": "FX:GBPUSD",
        "USDJPY": "FX:USDJPY",
        "BTCUSDT": "BINANCE:BTCUSDT",
        "ETHUSDT": "BINANCE:ETHUSDT",
        "SOLUSDT": "BINANCE:SOLUSDT"
      };
      const tvSymbol = (this.metadata?.symbol === this.currentSymbol && this.metadata?.tv_reference_symbol)
        ? this.metadata.tv_reference_symbol
        : (tvMap[this.currentSymbol] || `OANDA:${this.currentSymbol}`);
      const tvInterval = this.currentTimeframe === "D1" || this.currentTimeframe === "D" ? "D" : this.currentTimeframe.replace("M", "");

      this.tvEmbedWrapper.innerHTML = `
        <div class="tv-embed-header-bar">
          <div class="tv-embed-title">🌐 TradingView Cloud Embed · ${this.currentSymbol}</div>
          <button class="pro-engine-btn btn-engine-native" onclick="window.taikryChart.switchEngineMode('native')" title="Switch to Native Interactive Pro Chart">
            <span>⚡</span>
            <span>Switch to Native Pro</span>
          </button>
        </div>
        <iframe
          src="https://s.tradingview.com/widgetembed/?frameElementId=tradingview_widget&symbol=${tvSymbol}&interval=${tvInterval}&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=f1f3f6&studies=%5B%5D&theme=dark&style=1&timezone=Asia%2FPhnom_Penh&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en&utm_source=localhost"
          width="100%"
          height="calc(100% - 36px)"
          frameborder="0"
          allowtransparency="true"
          scrolling="no">
        </iframe>
      `;
    }
  }

  // Instantiate Global Controller
  window.taikryChart = new TaikryChartWorkspaceController();

})(window);
