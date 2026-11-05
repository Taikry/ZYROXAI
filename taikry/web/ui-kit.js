/* ZYROX AI — accessible, dependency-free loading and state components. */
(function (root) {
  "use strict";

  const stateLabels = {
    IDLE: "Idle",
    QUEUED: "Queued",
    RUNNING: "Running",
    COMPLETED: "Completed",
    FAILED: "Failed",
    SKIPPED: "Skipped"
  };
  const stateLabelsKh = {
    IDLE: "រង់ចាំ",
    QUEUED: "កំពុងរង់ចាំជួរ",
    RUNNING: "កំពុងដំណើរការ",
    COMPLETED: "បានបញ្ចប់",
    FAILED: "បរាជ័យ",
    SKIPPED: "រំលង"
  };

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function mount(host, component) {
    if (!host || !component) return null;
    host.replaceChildren(component);
    return component;
  }

  function Spinner(label = "Loading") {
    const spinner = element("span", "zyrox-spinner");
    spinner.setAttribute("aria-hidden", "true");
    spinner.dataset.label = label;
    return spinner;
  }

    const APP_STARTUP_STAGES = [
    { id: "app", en: "Loading application workspace", kh: "កំពុងផ្ទុកកន្លែងធ្វើការកម្មវិធី", pct: 15 },
    { id: "auth", en: "Authenticating security session", kh: "កំពុងផ្ទៀងផ្ទាត់សម័យសុវត្ថិភាព", pct: 35 },
    { id: "profile", en: "Loading account profile & paper balance", kh: "កំពុងផ្ទុកប្រវត្តិរូប និងសមតុល្យ Paper", pct: 55 },
    { id: "market", en: "Connecting live market feeds & calendar", kh: "កំពុងតភ្ជាប់សេវាទិន្នន័យទីផ្សារផ្ទាល់", pct: 75 },
    { id: "workspace", en: "Initializing native financial chart engine", kh: "កំពុងដំណើរការម៉ាស៊ីនក្រាហ្វិកហិរញ្ញវត្ថុ", pct: 90 },
    { id: "ready", en: "Terminal Ready", kh: "ផ្ទាំងជួញដូររួចរាល់", pct: 100 }
  ];

  function FullScreenLoader(options = {}) {
    const isKh = options.language === "kh";
    const rootNode = element("div", "zyrox-fullscreen-loader");
    rootNode.setAttribute("role", "status");
    rootNode.setAttribute("aria-live", "polite");
    rootNode.setAttribute("aria-busy", "true");

    const brand = element("div", "zyrox-loader-brand");
    const logo = element("img", "zyrox-loader-logo");
    logo.src = options.logo || "assets/brand/zyrox-logo-loop.svg";
    logo.alt = "ZYROX AI";
    logo.onerror = function () {
      if (logo.src.indexOf("zyrox-logo-icon.svg") === -1) {
        logo.src = "assets/brand/zyrox-logo-icon.svg";
      }
    };
    brand.append(logo, element("span", "zyrox-loader-brand-name", "ZYROX AI"));

    const spinner = Spinner(options.status || (isKh ? "កំពុងរៀបចំកន្លែងធ្វើការ" : "Preparing your workspace"));
    const titleEl = element("h1", "zyrox-loader-title", options.title || (isKh ? "កំពុងរៀបចំកន្លែងធ្វើការ" : "Preparing your workspace"));
    const copyEl = element("p", "zyrox-loader-copy", options.status || (isKh ? "កំពុងតភ្ជាប់ទៅសេវាទីផ្សារផ្ទាល់…" : "Connecting to live services…"));

    rootNode.append(brand, spinner, titleEl, copyEl);

    // Percentage indicator
    const pctEl = element("div", "zyrox-loader-pct", "15%");
    rootNode.append(pctEl);

    // Progress Bar
    const progressTrack = element("div", "zyrox-progress-track");
    const progressFill = element("div", "zyrox-progress-fill");
    progressFill.style.width = "15%";
    progressTrack.append(progressFill);
    rootNode.append(progressTrack);

    // Staged list
    const stagesList = element("div", "zyrox-loader-stages");
    APP_STARTUP_STAGES.forEach((stage, idx) => {
      const item = element("div", `zyrox-loader-stage-item${idx === 0 ? " is-active" : ""}`);
      item.dataset.stageIndex = String(idx);
      const bullet = element("span", "zyrox-stage-bullet", String(idx + 1));
      const lbl = element("span", "zyrox-stage-label", isKh ? stage.kh : stage.en);
      item.append(bullet, lbl);
      stagesList.append(item);
    });
    rootNode.append(stagesList);

    const actionHost = element("div", "zyrox-loader-actions");
    actionHost.hidden = true;
    rootNode.append(actionHost);

    rootNode._status = copyEl;
    rootNode._actionHost = actionHost;
    rootNode._pctEl = pctEl;
    rootNode._progressFill = progressFill;
    rootNode._stagesList = stagesList;

    rootNode.setStage = function (stageIdx, customMsg) {
      const safeIdx = Math.max(0, Math.min(APP_STARTUP_STAGES.length - 1, Number(stageIdx) || 0));
      const targetStage = APP_STARTUP_STAGES[safeIdx];
      const pct = targetStage.pct;

      if (pctEl) pctEl.textContent = `${pct}%`;
      if (progressFill) progressFill.style.width = `${pct}%`;
      if (copyEl) copyEl.textContent = customMsg || (isKh ? targetStage.kh : targetStage.en);

      const items = stagesList.querySelectorAll(".zyrox-loader-stage-item");
      items.forEach((it, idx) => {
        const bullet = it.querySelector(".zyrox-stage-bullet");
        if (idx < safeIdx) {
          it.className = "zyrox-loader-stage-item is-done";
          if (bullet) bullet.textContent = "✓";
        } else if (idx === safeIdx) {
          it.className = "zyrox-loader-stage-item is-active";
          if (bullet) bullet.textContent = String(idx + 1);
        } else {
          it.className = "zyrox-loader-stage-item";
          if (bullet) bullet.textContent = String(idx + 1);
        }
      });
    };

    return rootNode;
  }

  function PageLoader(options = {}) {
    const box = element("div", "zyrox-page-loader");
    box.setAttribute("role", "status");
    box.setAttribute("aria-live", "polite");
    box.append(Spinner(options.label || "Loading page"));
    box.append(element("span", "zyrox-state-copy", options.label || "Loading page…"));
    return box;
  }

  function SectionLoader(options = {}) {
    const box = element("div", "zyrox-section-loader");
    box.setAttribute("role", "status");
    box.setAttribute("aria-live", "polite");
    box.append(Spinner(options.label || "Loading section"));
    box.append(element("span", "zyrox-state-copy", options.label || "Loading section…"));
    return box;
  }

  function SkeletonLoader(options = {}) {
    const lines = Math.max(1, Math.min(8, Number(options.lines) || 3));
    const box = element("div", `zyrox-skeleton ${options.className || ""}`.trim());
    box.setAttribute("aria-hidden", "true");
    for (let index = 0; index < lines; index += 1) {
      const line = element("span", "zyrox-skeleton-line");
      if (index === lines - 1) line.classList.add("zyrox-skeleton-line-short");
      box.append(line);
    }
    return box;
  }

  function ChartSkeleton(options = {}) {
    const chart = element("div", "zyrox-chart-skeleton");
    chart.setAttribute("aria-hidden", "true");
    const label = options.language === "kh" ? "កំពុងផ្ទុកទិន្នន័យទៀនដែលបានផ្ទៀងផ្ទាត់" : "Loading verified candles";
    chart.append(element("span", "zyrox-chart-skeleton-label", options.label || label));
    const candles = element("div", "zyrox-chart-skeleton-candles");
    const bars = [
      [10, 56, 8, 25, -9, true], [16, 46, 12, 33, -11, false],
      [22, 51, 10, 30, -10, true], [28, 39, 13, 39, -13, true],
      [34, 43, 9, 28, -9, false], [40, 32, 14, 42, -14, true],
      [46, 36, 10, 31, -10, false], [52, 26, 14, 44, -15, true],
      [58, 31, 9, 28, -9, true], [64, 20, 13, 41, -14, false],
      [70, 25, 10, 32, -11, true], [76, 15, 14, 43, -14, true],
      [82, 20, 9, 29, -9, false], [88, 10, 13, 40, -13, true]
    ];
    bars.forEach(([x, top, body, wick, wickTop, bullish]) => {
      const candle = element("span", `zyrox-chart-candle${bullish ? " is-up" : " is-down"}`);
      candle.style.left = `${x}%`;
      candle.style.top = `${top}%`;
      candle.style.height = `${body}%`;
      candle.style.setProperty("--wick-top", `${wickTop}px`);
      candle.style.setProperty("--wick-height", `${wick}px`);
      candles.append(candle);
    });
    chart.append(candles, element("span", "zyrox-chart-scan-line"));
    chart.append(element("span", "zyrox-chart-skeleton-axis zyrox-chart-skeleton-axis-y"));
    chart.append(element("span", "zyrox-chart-skeleton-axis zyrox-chart-skeleton-axis-x"));
    return chart;
  }

  function TableSkeleton(options = {}) {
    const rows = Math.max(1, Math.min(10, Number(options.rows) || 4));
    const columns = Math.max(1, Math.min(8, Number(options.columns) || 4));
    const table = element("div", "zyrox-table-skeleton");
    table.setAttribute("aria-hidden", "true");
    for (let rowIndex = 0; rowIndex < rows; rowIndex += 1) {
      const row = element("div", `zyrox-table-skeleton-row${rowIndex === 0 ? " is-header" : ""}`);
      row.style.gridTemplateColumns = `repeat(${columns}, minmax(0, 1fr))`;
      for (let columnIndex = 0; columnIndex < columns; columnIndex += 1) {
        row.append(element("span", "zyrox-skeleton-line"));
      }
      table.append(row);
    }
    return table;
  }

  function CardSkeleton(options = {}) {
    const card = element("div", "zyrox-card-skeleton");
    card.setAttribute("aria-hidden", "true");
    card.append(element("span", "zyrox-card-skeleton-mark"));
    card.append(SkeletonLoader({ lines: options.lines || 3 }));
    return card;
  }

  function ButtonLoader(button, options = {}) {
    if (!button) return { restore() {} };
    const original = {
      children: Array.from(button.childNodes).map(node => node.cloneNode(true)),
      disabled: button.disabled,
      ariaBusy: button.getAttribute("aria-busy")
    };
    button.disabled = true;
    button.setAttribute("aria-busy", "true");
    button.classList.add("is-busy");
    button.replaceChildren(Spinner(options.label || "Working"), element("span", "", options.label || "Working…"));
    let restored = false;
    return {
      restore() {
        if (restored) return;
        restored = true;
        button.replaceChildren(...original.children);
        button.disabled = original.disabled;
        button.classList.remove("is-busy");
        if (original.ariaBusy === null) button.removeAttribute("aria-busy");
        else button.setAttribute("aria-busy", original.ariaBusy);
      }
    };
  }

  function ProgressLoader(options = {}) {
    const wrap = element("div", "zyrox-progress-loader");
    const label = options.label || "In progress";
    wrap.setAttribute("role", "status");
    wrap.setAttribute("aria-live", "polite");
    wrap.append(Spinner(label), element("span", "zyrox-state-copy", label));
    if (Number.isFinite(options.value) && options.value >= 0 && options.value <= 100) {
      wrap.setAttribute("role", "progressbar");
      wrap.setAttribute("aria-valuemin", "0");
      wrap.setAttribute("aria-valuemax", "100");
      wrap.setAttribute("aria-valuenow", String(Math.round(options.value)));
      wrap.append(element("span", "zyrox-progress-track"));
      const fill = element("span", "zyrox-progress-fill");
      fill.style.width = `${Math.round(options.value)}%`;
      wrap.querySelector(".zyrox-progress-track").append(fill);
    }
    return wrap;
  }

  function displayTime(value) {
    if (!value) return "";
    const timestamp = new Date(value);
    return Number.isNaN(timestamp.getTime()) ? "" : timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function SignalRadar(options = {}) {
    const radar = element("span", "zyrox-signal-radar");
    radar.setAttribute("aria-hidden", "true");
    radar.append(element("span", "zyrox-radar-ring ring-outer"));
    radar.append(element("span", "zyrox-radar-ring ring-inner"));
    radar.append(element("span", "zyrox-radar-sweep"));
    radar.append(element("span", "zyrox-radar-ping"));
    const symbol = String(options.symbol || "AI").replace(/[^a-z0-9]/gi, "").slice(0, 5) || "AI";
    radar.append(element("span", "zyrox-radar-symbol", symbol));
    return radar;
  }

  function AIThinkingLoader(options = {}) {
    const panel = element("section", "zyrox-ai-thinking");
    panel.setAttribute("aria-live", "polite");
    panel.setAttribute("aria-busy", options.requestState === "RUNNING" ? "true" : "false");
    const heading = element("div", "zyrox-ai-thinking-heading");
    const titleGroup = element("div", "zyrox-ai-thinking-title-group");
    titleGroup.append(element("h3", "", options.title || "AI analysis activity"));
    titleGroup.append(element("p", "", options.task || "Live state reported by the analysis service."));
    const labels = options.language === "kh" ? stateLabelsKh : stateLabels;
    const overall = element("span", `zyrox-state-badge state-${String(options.requestState || "IDLE").toLowerCase()}`, labels[options.requestState] || labels.IDLE);
    if (options.radarSymbol) {
      const main = element("div", "zyrox-ai-thinking-main");
      main.append(SignalRadar({ symbol: options.radarSymbol }), titleGroup);
      heading.append(main, overall);
    } else {
      heading.append(titleGroup, overall);
    }
    panel.append(heading);

    const agents = Array.isArray(options.agents) ? options.agents : [];
    if (agents.length) {
      const grid = element("div", "zyrox-agent-state-grid");
      agents.forEach(agent => {
        const agentState = String(agent.execution_state || "IDLE").toUpperCase();
        const safeState = Object.prototype.hasOwnProperty.call(stateLabels, agentState) ? agentState : "IDLE";
        const card = element("article", `zyrox-agent-state state-${safeState.toLowerCase()}`);
        const row = element("div", "zyrox-agent-state-row");
        row.append(element("span", "zyrox-agent-state-name", agent.name || agent.agent_name || agent.agent_id || "Agent"));
        row.append(element("span", `zyrox-state-badge state-${safeState.toLowerCase()}`, labels[safeState]));
        card.append(row);
        const task = safeState === "RUNNING" || safeState === "QUEUED" ? agent.current_task : (agent.last_task || agent.current_task);
        if (task) card.append(element("p", "zyrox-agent-task", task));
        const time = safeState === "RUNNING" ? displayTime(agent.last_started_at) : displayTime(agent.last_completed_at);
        if (time) card.append(element("time", "zyrox-agent-time", `${safeState === "RUNNING" ? "Started" : "Updated"} ${time}`));
        if (safeState === "FAILED" && agent.last_error) card.append(element("p", "zyrox-agent-error", agent.last_error));
        grid.append(card);
      });
      panel.append(grid);
    } else {
      panel.append(element("p", "zyrox-ai-no-telemetry", options.emptyMessage || "Waiting for live agent telemetry from the server."));
    }

    if (options.notice) panel.append(element("p", "zyrox-ai-telemetry-note", options.notice));
    return panel;
  }

  function PaymentProcessingLoader(options = {}) {
    const box = element("div", "zyrox-payment-processing");
    box.setAttribute("role", "status");
    box.setAttribute("aria-live", "assertive");
    box.setAttribute("aria-busy", "true");
    box.append(Spinner("Verifying your payment"));
    box.append(element("strong", "", options.title || "Verifying your payment securely…"));
    box.append(element("p", "", options.detail || "The server will confirm the transaction before access changes."));
    return box;
  }

  function EmptyState(options = {}) {
    const box = element("div", "zyrox-empty-state");
    box.setAttribute("role", "status");
    box.append(element("span", "zyrox-empty-icon", options.icon || "◇"));
    box.append(element("strong", "", options.title || "Nothing to show yet"));
    if (options.message) box.append(element("p", "", options.message));
    return box;
  }

  function ErrorState(options = {}) {
    const box = element("div", "zyrox-error-state");
    box.setAttribute("role", "alert");
    box.append(element("strong", "", options.title || "This section could not be loaded"));
    if (options.message) box.append(element("p", "", options.message));
    if (typeof options.onRetry === "function") {
      const retry = element("button", "zyrox-retry-button", options.retryLabel || "Try again");
      retry.type = "button";
      retry.addEventListener("click", options.onRetry, { once: true });
      box.append(retry);
    }
    return box;
  }

  function beginStartup(options = {}) {
    let overlay = document.getElementById("zyrox-startup-loader");
    if (!overlay) return Promise.resolve();
    const renderedLoader = FullScreenLoader(options);
    renderedLoader.id = overlay.id;
    overlay.replaceWith(renderedLoader);
    overlay = renderedLoader;

    const timeoutMs = Math.max(1000, Number(options.timeoutMs) || 14000);
    let finished = false;
    let timeoutId;

    const dismiss = () => {
      if (finished) return;
      finished = true;
      clearTimeout(timeoutId);
      overlay.setAttribute("aria-busy", "false");
      overlay.classList.add("is-dismissed");
      window.setTimeout(() => overlay.remove(), 300);
    };

    const showTimeout = () => {
      if (finished) return;
      const status = overlay._status || overlay.querySelector(".zyrox-loader-copy");
      if (status) {
        status.textContent = options.language === "kh"
          ? "សេវាផ្ទាល់ចំណាយពេលយូរ។ អ្នកអាចព្យាយាមភ្ជាប់ម្តងទៀត ឬបើកផ្ទាំងជួញដូរ Offline។"
          : "Live services are taking longer than expected. You can retry connection or enter offline workspace.";
      }
      const actions = overlay._actionHost || overlay.querySelector(".zyrox-loader-actions");
      if (actions) {
        actions.hidden = false;
        const retry = element("button", "zyrox-retry-button", options.language === "kh" ? "ព្យាយាមម្តងទៀត" : "Retry Connection");
        retry.type = "button";
        retry.style.marginRight = "10px";
        retry.onclick = () => window.location.reload();

        const proceed = element("button", "btn btn-outline btn-sm", options.language === "kh" ? "បើកផ្ទាំងជួញដូរ Offline" : "Open Offline Workspace");
        proceed.type = "button";
        proceed.onclick = () => {
          dismiss();
          if (root.ZyroxToast) {
            root.ZyroxToast.warning(
              options.language === "kh" ? "របៀបគ្មានអ៊ីនធឺណិត" : "Offline Mode",
              options.language === "kh" ? "កំពុងដំណើរការក្នុងរបៀប Offline។" : "Running workspace in offline inspection mode."
            );
          }
        };
        actions.replaceChildren(retry, proceed);
      }
      overlay.classList.add("has-timeout");
    };

    timeoutId = window.setTimeout(showTimeout, timeoutMs);
    const tasks = Array.isArray(options.tasks) ? options.tasks : [];

    // Advance through the 6 stages dynamically as promises resolve
    renderedLoader.setStage(1); // Stage 1: Authenticating session
    let settled = 0;
    tasks.forEach(t => {
      Promise.resolve(t).finally(() => {
        settled += 1;
        const nextStage = Math.min(4, 1 + settled);
        renderedLoader.setStage(nextStage);
      });
    });

    return Promise.allSettled(tasks).then(() => {
      renderedLoader.setStage(5, options.language === "kh" ? "ផ្ទាំងជួញដូររួចរាល់" : "Ready");
      window.setTimeout(() => {
        if (!finished) dismiss();
      }, 450);
    });
  }

  /* =========================================================================
     ZYROX TOAST NOTIFICATION ENGINE
     ========================================================================= */
  const ZyroxToast = (function () {
    let container = null;
    const MAX_TOASTS = 4;
    const recentToasts = new Map();
    const DEDUP_MS = 2000;

    function getContainer() {
      if (!container || !document.body.contains(container)) {
        container = document.getElementById("zyrox-toast-container");
        if (!container) {
          container = element("div");
          container.id = "zyrox-toast-container";
          container.setAttribute("role", "region");
          container.setAttribute("aria-label", "Notifications");
          container.setAttribute("aria-live", "polite");
          document.body.appendChild(container);
        }
      }
      return container;
    }

    function show(options = {}) {
      const type = options.type || "info";
      const title = options.title || (type.charAt(0).toUpperCase() + type.slice(1));
      const message = options.message || "";
      const durationMs = options.durationMs || (type === "error" ? 6000 : 4000);
      const symbol = options.symbol || "";
      const isGold = options.isGold || (String(symbol).toUpperCase().includes("XAU"));

      // Deduplication
      const dedupKey = `${type}:${title}:${message}`;
      const now = Date.now();
      if (recentToasts.has(dedupKey) && (now - recentToasts.get(dedupKey)) < DEDUP_MS) {
        return null;
      }
      recentToasts.set(dedupKey, now);

      const host = getContainer();

      // Enforce max 4 visible toasts
      while (host.children.length >= MAX_TOASTS) {
        dismissToast(host.firstElementChild);
      }

      const toast = element("div", `zyrox-toast is-${type}${isGold ? " is-gold" : ""}`);
      toast.setAttribute("role", type === "error" ? "alert" : "status");

      const iconMap = {
        success: "✓",
        error: "✕",
        warning: "⚠",
        info: "ℹ",
        signal: isGold ? "🥇" : "⚡"
      };

      const icon = element("span", "zyrox-toast-icon", iconMap[type] || "ℹ");
      const content = element("div", "zyrox-toast-content");

      const titleEl = element("div", "zyrox-toast-title", title);
      if (symbol) {
        const badge = element("span", `zyrox-toast-sym-badge${isGold ? " is-gold" : ""}`, symbol);
        titleEl.appendChild(badge);
      }

      const msgEl = element("div", "zyrox-toast-message", message);
      content.appendChild(titleEl);
      content.appendChild(msgEl);

      const closeBtn = element("button", "zyrox-toast-close", "×");
      closeBtn.type = "button";
      closeBtn.setAttribute("aria-label", "Close notification");
      closeBtn.onclick = () => dismissToast(toast);

      const progress = element("div", "zyrox-toast-progress");
      progress.style.transition = `transform ${durationMs}ms linear`;

      toast.appendChild(icon);
      toast.appendChild(content);
      toast.appendChild(closeBtn);
      toast.appendChild(progress);
      host.appendChild(toast);

      requestAnimationFrame(() => {
        toast.classList.add("is-visible");
        progress.style.transform = "scaleX(0)";
      });

      let timerId;
      let remaining = durationMs;
      let start = Date.now();

      function startTimer() {
        start = Date.now();
        timerId = window.setTimeout(() => dismissToast(toast), remaining);
      }

      function pauseTimer() {
        window.clearTimeout(timerId);
        remaining -= (Date.now() - start);
      }

      toast.addEventListener("mouseenter", pauseTimer);
      toast.addEventListener("mouseleave", startTimer);

      startTimer();
      return toast;
    }

    function dismissToast(t) {
      if (!t || t.classList.contains("is-hiding")) return;
      t.classList.remove("is-visible");
      t.classList.add("is-hiding");
      window.setTimeout(() => {
        if (t.parentNode) t.parentNode.removeChild(t);
      }, 300);
    }

    return Object.freeze({
      show,
      success: (title, message, dur) => show({ type: "success", title, message, durationMs: dur }),
      error: (title, message, dur) => show({ type: "error", title, message, durationMs: dur }),
      warning: (title, message, dur) => show({ type: "warning", title, message, durationMs: dur }),
      info: (title, message, dur) => show({ type: "info", title, message, durationMs: dur }),
      signal: (sym, title, message, dur) => show({ type: "signal", symbol: sym, title, message, durationMs: dur, isGold: String(sym).includes("XAU") })
    });
  })();

  /* =========================================================================
     PIPELINE STAGE LOADER FOR SMART ANALYSIS & BEST SETUP
     ========================================================================= */
  const PIPELINE_STAGES = [
    { id: "candles", label: "Ingesting verified OHLCV market candles", labelKh: "កំពុងទាញយកទៀនតម្លៃដែលបានផ្ទៀងផ្ទាត់" },
    { id: "mtf", label: "Multi-Timeframe Trend & Momentum Matrix", labelKh: "កំពុងវិភាគទិសដៅ និងសន្ទុះពហុពេលវេលា" },
    { id: "smc", label: "SMC Order Blocks & Liquidity Mapping", labelKh: "កំពុងកំណត់ Order Block & សន្ទនីយភាព SMC" },
    { id: "risk", label: "Risk Gate & Volatility Spread Validation", labelKh: "កំពុងត្រួតពិនិត្យហានិភ័យ និង Spread" },
    { id: "consensus", label: "Multi-Agent Consensus & Plan Execution", labelKh: "កំពុងបង្កើតផែនការជួញដូរស្របតាមស្ថាប័ន" }
  ];

  function PipelineLoader(options = {}) {
    const isKh = options.language === "kh";
    const box = element("div", "zyrox-pipeline-loader");
    box.setAttribute("role", "status");
    box.setAttribute("aria-live", "polite");

    const header = element("div", "zyrox-pipeline-header");
    header.appendChild(Spinner(isKh ? "កំពុងវិភាគ..." : "Running AI Analysis..."));
    header.appendChild(element("strong", "", isKh ? "ដំណើរការវិភាគពហុភ្នាក់ងារ AI" : "Autonomous AI Analysis Pipeline"));
    box.appendChild(header);

    const list = element("div", "zyrox-loader-stages");
    const currentIdx = Math.max(0, Math.min(PIPELINE_STAGES.length - 1, Number(options.currentStage) || 0));

    PIPELINE_STAGES.forEach((stg, idx) => {
      const item = element("div", `zyrox-loader-stage-item${idx < currentIdx ? " is-done" : (idx === currentIdx ? " is-active" : "")}`);
      item.dataset.stageIndex = String(idx);
      const bullet = element("span", "zyrox-stage-bullet", idx < currentIdx ? "✓" : String(idx + 1));
      const lbl = element("span", "zyrox-stage-label", isKh ? stg.labelKh : stg.label);
      item.appendChild(bullet);
      item.appendChild(lbl);
      list.appendChild(item);
    });

    box.appendChild(list);

    box.updateStage = function (stageIdx) {
      const items = list.querySelectorAll(".zyrox-loader-stage-item");
      items.forEach((it, idx) => {
        const bullet = it.querySelector(".zyrox-stage-bullet");
        if (idx < stageIdx) {
          it.className = "zyrox-loader-stage-item is-done";
          if (bullet) bullet.textContent = "✓";
        } else if (idx === stageIdx) {
          it.className = "zyrox-loader-stage-item is-active";
          if (bullet) bullet.textContent = String(idx + 1);
        } else {
          it.className = "zyrox-loader-stage-item";
          if (bullet) bullet.textContent = String(idx + 1);
        }
      });
    };

    return box;
  }

    root.ZyroxToast = ZyroxToast;

  root.ZyroxUI = Object.freeze({
    mount, Spinner, FullScreenLoader, PageLoader, SectionLoader, SkeletonLoader,
    ChartSkeleton, TableSkeleton, CardSkeleton, ButtonLoader, AIThinkingLoader,
    PaymentProcessingLoader, ProgressLoader, SignalRadar, EmptyState, ErrorState,
    PipelineLoader, ZyroxToast, beginStartup
  });
})(window);
