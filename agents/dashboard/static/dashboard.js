/* =================================================================
   FUNDAMENTAL TERMINAL — command-driven, multi-panel
   ================================================================= */

// -----------------------------------------------------------------
// STATE
// -----------------------------------------------------------------
const STATE = {
  layout: '1',                // '1' | '2h' | '2v' | '4'
  panels: [],                 // { id, ticker, fn, data, lastPrice, charts:{} }
  focused: 0,                 // panel index
  lastCmd: '',
  history: JSON.parse(localStorage.getItem('ft_history') || '[]'),
  histIdx: -1,
};

const PANEL_LIMIT = { '1': 1, '2h': 2, '2v': 2, '4': 4 };

// -----------------------------------------------------------------
// FUNCTION CODE REGISTRY
// (code → { description, fetch(ticker), render(panel, data) })
// -----------------------------------------------------------------
const FN = {};

function defineFn(code, desc, fetchFn, renderFn) {
  FN[code] = { code, desc, fetch: fetchFn, render: renderFn };
}

// -----------------------------------------------------------------
// FORMATTERS
// -----------------------------------------------------------------
const fmt = {
  price(v) {
    if (v == null || isNaN(v)) return '—';
    if (v >= 10000) return v.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return v.toFixed(2);
  },
  pct(v, withSign = true) {
    if (v == null || isNaN(v)) return '—';
    const s = withSign && v >= 0 ? '+' : '';
    return `${s}${v.toFixed(2)}%`;
  },
  num(v, d = 2) {
    if (v == null || isNaN(v)) return '—';
    return v.toFixed(d);
  },
  big(v) {
    if (v == null || isNaN(v) || v === 0) return '—';
    const abs = Math.abs(v);
    if (abs >= 1e12) return (v / 1e12).toFixed(2) + 'T';
    if (abs >= 1e9) return (v / 1e9).toFixed(2) + 'B';
    if (abs >= 1e6) return (v / 1e6).toFixed(2) + 'M';
    if (abs >= 1e3) return (v / 1e3).toFixed(2) + 'K';
    return v.toFixed(2);
  },
  vol(v) { return fmt.big(v); },
  signClass(v) { return v >= 0 ? 'up' : 'down'; },
  ago(ts) {
    const diff = Date.now() / 1000 - ts;
    if (diff < 60) return `${Math.floor(diff)}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  },
  heatColor(pct) {
    const p = Math.max(-5, Math.min(5, pct)) / 5;
    if (p >= 0) {
      const a = 0.12 + p * 0.55;
      return `rgba(0,217,126,${a})`;
    } else {
      const a = 0.12 + Math.abs(p) * 0.55;
      return `rgba(255,59,59,${a})`;
    }
  },
};

// -----------------------------------------------------------------
// PANEL MANAGER
// -----------------------------------------------------------------
function newPanelObj(idx) {
  return { id: `p${idx}`, ticker: null, fn: null, data: null, lastPrice: null, charts: {} };
}

function ensurePanels() {
  const need = PANEL_LIMIT[STATE.layout];
  while (STATE.panels.length < need) STATE.panels.push(newPanelObj(STATE.panels.length));
  while (STATE.panels.length > need) {
    const p = STATE.panels.pop();
    destroyPanelCharts(p);
  }
  if (STATE.focused >= need) STATE.focused = 0;
}

function destroyPanelCharts(panel) {
  if (!panel) return;
  Object.values(panel.charts || {}).forEach(c => { try { c.destroy(); } catch (e) {} });
  panel.charts = {};
  if (panel.network) { try { panel.network.destroy(); } catch (e) {} panel.network = null; }
}

function renderWorkspace() {
  ensurePanels();
  const ws = document.getElementById('workspace');
  ws.className = `workspace layout-${STATE.layout}`;
  ws.innerHTML = '';
  STATE.panels.forEach((p, i) => {
    const el = document.createElement('div');
    el.className = 'panel' + (i === STATE.focused ? ' focused' : '');
    el.dataset.idx = i;
    el.onclick = () => { STATE.focused = i; updateFocusedUI(); };
    el.innerHTML = panelHTML(p, i);
    ws.appendChild(el);
    // re-render contents if there's data
    if (p.fn) renderPanelInto(i);
  });
  document.getElementById('status-layout').textContent = STATE.layout.toUpperCase();
  document.getElementById('status-panel').textContent = STATE.focused + 1;
}

function panelHTML(p, idx) {
  const ticker = p.ticker || '—';
  const fn = p.fn || 'EMPTY';
  const title = (p.fn && FN[p.fn]) ? FN[p.fn].desc : 'No function loaded';
  return `
    <div class="panel-header">
      <span class="panel-num">${idx + 1}</span>
      <span class="panel-ticker">${ticker}</span>
      <span class="panel-fn">${fn}</span>
      <span class="panel-title">${title}</span>
      <div class="panel-actions">
        <button class="panel-action" onclick="event.stopPropagation();reloadPanel(${idx})" title="Reload">↻</button>
        <button class="panel-action" onclick="event.stopPropagation();clearPanel(${idx})" title="Clear">✕</button>
      </div>
    </div>
    <div class="panel-body" id="panel-body-${idx}">
      ${p.fn ? '<div class="loader-inline">LOADING</div>' : emptyHTML()}
    </div>
  `;
}

function emptyHTML() {
  return `
    <div class="panel-empty">
      <div class="big">FUNDAMENTAL TERMINAL</div>
      <div>Type a command and press <span class="kbd">ENTER</span>:</div>
      <div class="hint">
        <code>AAPL GO</code> &nbsp;·&nbsp; <code>NVDA FA</code> &nbsp;·&nbsp; <code>TSLA GIP</code><br>
        <code>HEAT</code> &nbsp;·&nbsp; <code>N AAPL</code> &nbsp;·&nbsp; <code>ECO</code> &nbsp;·&nbsp; <code>EQS</code> &nbsp;·&nbsp; <code>HELP</code>
      </div>
    </div>`;
}

function updateFocusedUI() {
  document.querySelectorAll('.panel').forEach((el, i) => {
    el.classList.toggle('focused', i === STATE.focused);
  });
  document.getElementById('status-panel').textContent = STATE.focused + 1;
}

function setLayout(l) {
  STATE.layout = l;
  document.querySelectorAll('.layout-btn').forEach(b => b.classList.toggle('active', b.dataset.layout === l));
  renderWorkspace();
}

function clearPanel(idx) {
  destroyPanelCharts(STATE.panels[idx]);
  STATE.panels[idx] = newPanelObj(idx);
  renderWorkspace();
}

function reloadPanel(idx) {
  const p = STATE.panels[idx];
  if (!p.fn) return;
  loadIntoPanel(idx, p.ticker, p.fn);
}

// -----------------------------------------------------------------
// COMMAND PARSER
// -----------------------------------------------------------------
function parseCommand(raw) {
  // Normalize: uppercase, trim, collapse whitespace
  const s = raw.trim().toUpperCase().replace(/\s+/g, ' ');
  if (!s) return null;
  const parts = s.split(' ');

  // HELP / single-function code (no ticker needed)
  const NO_TICKER = new Set(['HELP', 'HEAT', 'ECO', 'EQS', 'GAINERS', 'LOSERS', 'W', 'WATCH', 'EVTS', 'MKT']);

  // Pure single token
  if (parts.length === 1) {
    const tk = parts[0].replace(/^\//, '');
    if (NO_TICKER.has(tk)) return { ticker: null, fn: tk };
    if (FN[tk]) return { ticker: null, fn: tk };
    // Single token that isn't a function = ticker with default GIP
    return { ticker: tk, fn: 'GIP' };
  }

  // Strip trailing GO (Bloomberg execution token)
  if (parts[parts.length - 1] === 'GO') parts.pop();
  if (parts.length === 0) return null;
  if (parts.length === 1) {
    const tk = parts[0];
    if (NO_TICKER.has(tk) || FN[tk]) return { ticker: null, fn: tk };
    return { ticker: tk, fn: 'GIP' };
  }

  // Two-token forms:
  //   TICKER FN     →  AAPL FA
  //   FN TICKER     →  N AAPL  or  DES TSLA
  const a = parts[0], b = parts[1];
  if (FN[a] && !FN[b]) return { ticker: b, fn: a };
  if (FN[b]) return { ticker: a, fn: b };
  if (NO_TICKER.has(a)) return { ticker: b, fn: a };
  // Comparison: comma-list or 3+ tokens → COMP
  if (parts.length >= 2 && parts.every(t => /^[A-Z\-\.]{1,8}$/.test(t))) {
    return { ticker: parts.join(','), fn: 'COMP' };
  }
  return { ticker: a, fn: b };
}

async function executeCommand() {
  const input = document.getElementById('cmd-input');
  const raw = input.value;
  if (!raw.trim()) return;
  STATE.history.unshift(raw.trim());
  STATE.history = STATE.history.slice(0, 50);
  localStorage.setItem('ft_history', JSON.stringify(STATE.history));
  STATE.histIdx = -1;
  STATE.lastCmd = raw.trim().toUpperCase();
  document.getElementById('status-last-cmd').textContent = STATE.lastCmd;

  const parsed = parseCommand(raw);
  input.value = '';
  closeSuggest();
  if (!parsed) return;

  await loadIntoPanel(STATE.focused, parsed.ticker, parsed.fn);
}

async function loadIntoPanel(idx, ticker, fn) {
  const p = STATE.panels[idx];
  if (!p) return;
  const entry = FN[fn];
  if (!entry) {
    setPanelBody(idx, `<div class="panel-empty"><div class="big" style="color:var(--red);">UNKNOWN FUNCTION: ${fn}</div><div class="hint">Type <code>HELP</code> for command reference.</div></div>`);
    return;
  }
  destroyPanelCharts(p);
  p.ticker = ticker || (p.ticker || '—');
  p.fn = fn;
  // header reflects new state
  const ws = document.getElementById('workspace');
  const panelEl = ws.children[idx];
  if (panelEl) {
    panelEl.querySelector('.panel-ticker').textContent = p.ticker;
    panelEl.querySelector('.panel-fn').textContent = fn;
    panelEl.querySelector('.panel-title').textContent = entry.desc;
  }
  setPanelBody(idx, '<div class="loader-inline">LOADING</div>');
  try {
    const data = await entry.fetch(ticker);
    p.data = data;
    entry.render(p, idx);
  } catch (err) {
    setPanelBody(idx, `<div class="panel-empty"><div class="big" style="color:var(--red);">ERROR</div><div class="hint">${escapeHTML(err.message || String(err))}</div></div>`);
  }
}

async function renderPanelInto(idx) {
  const p = STATE.panels[idx];
  if (!p.fn || !FN[p.fn]) return;
  if (!p.data) {
    return loadIntoPanel(idx, p.ticker, p.fn);
  }
  FN[p.fn].render(p, idx);
}

function setPanelBody(idx, html) {
  const el = document.getElementById(`panel-body-${idx}`);
  if (el) el.innerHTML = html;
}

function escapeHTML(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// -----------------------------------------------------------------
// FETCH HELPERS
// -----------------------------------------------------------------
async function api(path) {
  const res = await fetch(path);
  if (!res.ok) {
    let msg = `${res.status}`;
    try { const j = await res.json(); msg = j.detail || msg; } catch (e) {}
    throw new Error(msg);
  }
  return res.json();
}

function requireTicker(ticker) {
  if (!ticker || ticker === '—') throw new Error('Function requires a ticker. Try: AAPL FA');
}

// -----------------------------------------------------------------
// COMMON: stock header strip (used by DES/FA/GIP)
// -----------------------------------------------------------------
function quoteBlockHTML(d) {
  const cls = d.price.change_pct >= 0 ? 'pos' : 'neg';
  const sign = d.price.change_pct >= 0 ? '+' : '';
  return `
    <div class="quote-block">
      <div class="quote-ticker-name">
        <span class="quote-ticker">${d.ticker}</span>
        <span class="quote-name">${escapeHTML(d.name || '')} · ${escapeHTML(d.sector || 'N/A')}</span>
      </div>
      <div class="quote-price ${cls}">${fmt.price(d.price.current)}</div>
      <div class="quote-change ${cls}">${sign}${fmt.num(d.price.change)} (${sign}${fmt.num(d.price.change_pct)}%)</div>
    </div>`;
}

// =================================================================
// FUNCTION CODES — implementations
// =================================================================

// ---- DES — Description ----
defineFn('DES', 'Company Description & Key Facts',
  async (t) => { requireTicker(t); return api(`/api/stock/${t}?period=1mo`); },
  (panel, idx) => {
    const d = panel.data;
    const f = d.fundamentals, p = d.price;
    const html = `
      ${quoteBlockHTML(d)}
      <div class="t-section-title">Identity</div>
      <div class="kv-list">
        <div class="kv-k">Ticker</div><div class="kv-v">${d.ticker}</div>
        <div class="kv-k">Name</div><div class="kv-v">${escapeHTML(d.name || '—')}</div>
        <div class="kv-k">Sector</div><div class="kv-v">${escapeHTML(d.sector || '—')}</div>
        <div class="kv-k">Industry</div><div class="kv-v">${escapeHTML(d.industry || '—')}</div>
        <div class="kv-k">Country</div><div class="kv-v">${escapeHTML(d.country || '—')}</div>
        <div class="kv-k">Employees</div><div class="kv-v">${d.employees ? d.employees.toLocaleString() : '—'}</div>
        <div class="kv-k">Website</div><div class="kv-v">${d.website ? `<a href="${d.website}" target="_blank">${escapeHTML(d.website.replace(/^https?:\/\//,''))}</a>` : '—'}</div>
      </div>
      <div class="t-section-title">Quote</div>
      <div class="kv-list">
        <div class="kv-k">Open</div><div class="kv-v">${fmt.price(p.open)}</div>
        <div class="kv-k">Prev Close</div><div class="kv-v">${fmt.price(p.prev_close)}</div>
        <div class="kv-k">Day High</div><div class="kv-v">${fmt.price(p.high)}</div>
        <div class="kv-k">Day Low</div><div class="kv-v">${fmt.price(p.low)}</div>
        <div class="kv-k">52W High</div><div class="kv-v">${fmt.price(p.high_52w)}</div>
        <div class="kv-k">52W Low</div><div class="kv-v">${fmt.price(p.low_52w)}</div>
        <div class="kv-k">Volume</div><div class="kv-v">${fmt.vol(p.volume)}</div>
        <div class="kv-k">Avg Volume</div><div class="kv-v">${fmt.vol(p.avg_volume)}</div>
        <div class="kv-k">Market Cap</div><div class="kv-v">${fmt.big(f.market_cap)}</div>
        <div class="kv-k">Beta</div><div class="kv-v">${fmt.num(f.beta)}</div>
      </div>
      <div class="t-section-title">Business</div>
      <div style="font-size:11px;line-height:1.5;color:var(--text-dim);max-width:80ch;">
        ${escapeHTML((d.description || '').slice(0, 1200))}${d.description && d.description.length > 1200 ? '…' : ''}
      </div>`;
    setPanelBody(idx, html);
  }
);

// ---- FA — Fundamentals ----
defineFn('FA', 'Fundamental Analysis',
  async (t) => { requireTicker(t); return api(`/api/stock/${t}?period=1y`); },
  (panel, idx) => {
    const d = panel.data;
    const f = d.fundamentals, p = d.performance;
    const html = `
      ${quoteBlockHTML(d)}
      <div class="t-section-title">Valuation</div>
      <div class="kv-list">
        <div class="kv-k">Market Cap</div><div class="kv-v">${fmt.big(f.market_cap)}</div>
        <div class="kv-k">P/E (TTM)</div><div class="kv-v">${f.pe_ratio > 0 ? f.pe_ratio.toFixed(2) + 'x' : '—'}</div>
        <div class="kv-k">P/E (Fwd)</div><div class="kv-v">${f.forward_pe > 0 ? f.forward_pe.toFixed(2) + 'x' : '—'}</div>
        <div class="kv-k">PEG</div><div class="kv-v">${f.peg_ratio > 0 ? f.peg_ratio.toFixed(2) : '—'}</div>
        <div class="kv-k">P/B</div><div class="kv-v">${f.price_to_book > 0 ? f.price_to_book.toFixed(2) : '—'}</div>
        <div class="kv-k">EPS (TTM)</div><div class="kv-v">${fmt.price(f.eps)}</div>
        <div class="kv-k">Book Value</div><div class="kv-v">${fmt.price(f.book_value)}</div>
        <div class="kv-k">Beta</div><div class="kv-v">${fmt.num(f.beta)}</div>
      </div>
      <div class="t-section-title">Profitability</div>
      <div class="kv-list">
        <div class="kv-k">Revenue (TTM)</div><div class="kv-v">${fmt.big(f.revenue)}</div>
        <div class="kv-k">Rev Growth YoY</div><div class="kv-v ${f.revenue_growth >= 0 ? 'pos' : 'neg'}">${fmt.pct(f.revenue_growth)}</div>
        <div class="kv-k">Gross Margin</div><div class="kv-v">${fmt.pct(f.gross_margins, false)}</div>
        <div class="kv-k">Operating Margin</div><div class="kv-v">${fmt.pct(f.operating_margins, false)}</div>
        <div class="kv-k">Net Margin</div><div class="kv-v">${fmt.pct(f.profit_margin, false)}</div>
        <div class="kv-k">ROE</div><div class="kv-v">${fmt.pct(f.roe, false)}</div>
        <div class="kv-k">Free Cash Flow</div><div class="kv-v">${fmt.big(f.free_cash_flow)}</div>
        <div class="kv-k">Div Yield</div><div class="kv-v">${f.dividend_yield > 0 ? fmt.pct(f.dividend_yield, false) : '—'}</div>
      </div>
      <div class="t-section-title">Balance / Risk</div>
      <div class="kv-list">
        <div class="kv-k">Debt/Equity</div><div class="kv-v">${f.debt_to_equity > 0 ? f.debt_to_equity.toFixed(2) : '—'}</div>
        <div class="kv-k">Current Ratio</div><div class="kv-v">${fmt.num(f.current_ratio)}</div>
        <div class="kv-k">Volatility (Ann.)</div><div class="kv-v">${fmt.pct(p.volatility, false)}</div>
      </div>
      <div class="t-section-title">Performance</div>
      <div class="kv-list">
        <div class="kv-k">1D</div><div class="kv-v ${p.perf_1d >= 0 ? 'pos' : 'neg'}">${fmt.pct(p.perf_1d)}</div>
        <div class="kv-k">1W</div><div class="kv-v ${p.perf_1w >= 0 ? 'pos' : 'neg'}">${fmt.pct(p.perf_1w)}</div>
        <div class="kv-k">1M</div><div class="kv-v ${p.perf_1m >= 0 ? 'pos' : 'neg'}">${fmt.pct(p.perf_1m)}</div>
        <div class="kv-k">3M</div><div class="kv-v ${p.perf_3m >= 0 ? 'pos' : 'neg'}">${fmt.pct(p.perf_3m)}</div>
        <div class="kv-k">1Y</div><div class="kv-v ${p.perf_1y >= 0 ? 'pos' : 'neg'}">${fmt.pct(p.perf_1y)}</div>
      </div>`;
    setPanelBody(idx, html);
  }
);

// ---- GIP — Graph Intraday Price (candlestick + indicators) ----
defineFn('GIP', 'Graph Intraday Price',
  async (t) => { requireTicker(t); return api(`/api/stock/${t}?period=1y`); },
  (panel, idx) => {
    const d = panel.data;
    setPanelBody(idx, `
      ${quoteBlockHTML(d)}
      <div style="display:flex;gap:4px;margin-bottom:4px;font-size:10px;flex-wrap:wrap;">
        ${['1mo','3mo','6mo','1y','2y','5y'].map(p => `<button class="fn-code-btn" data-period="${p}" onclick="gipChangePeriod(${idx},'${p}')">${p.toUpperCase()}</button>`).join('')}
        <span style="color:var(--text-very-dim);margin:0 6px;">│</span>
        ${[['SMA20','sma_20'],['SMA50','sma_50'],['SMA200','sma_200'],['BB','bb']].map(([lbl,k]) => `<button class="fn-code-btn" onclick="gipToggle(${idx},'${k}',this)">${lbl}</button>`).join('')}
      </div>
      <div class="chart-host" id="gip-chart-${idx}" style="height:260px;"></div>
      <div class="chart-host" id="gip-vol-${idx}" style="height:90px;margin-top:4px;"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:6px;">
        <div><div class="t-section-title">RSI(14)</div><div class="chart-host" id="gip-rsi-${idx}" style="height:120px;"></div></div>
        <div><div class="t-section-title">MACD(12,26,9)</div><div class="chart-host" id="gip-macd-${idx}" style="height:120px;"></div></div>
      </div>
    `);
    panel._gipIndicators = panel._gipIndicators || new Set(['sma_20', 'bb']);
    renderGIPCharts(panel, idx);
  }
);

window.gipChangePeriod = async function(idx, period) {
  const p = STATE.panels[idx];
  if (!p || !p.ticker) return;
  setPanelBody(idx, '<div class="loader-inline">LOADING</div>');
  try {
    const d = await api(`/api/stock/${p.ticker}?period=${period}`);
    p.data = d;
    FN.GIP.render(p, idx);
  } catch (e) {
    setPanelBody(idx, `<div class="panel-empty"><div class="big" style="color:var(--red);">ERROR</div><div class="hint">${escapeHTML(e.message)}</div></div>`);
  }
};

window.gipToggle = function(idx, key, btn) {
  const p = STATE.panels[idx];
  p._gipIndicators = p._gipIndicators || new Set();
  if (p._gipIndicators.has(key)) p._gipIndicators.delete(key);
  else p._gipIndicators.add(key);
  if (btn) btn.style.color = p._gipIndicators.has(key) ? 'var(--amber)' : '';
  destroyPanelCharts(p);
  renderGIPCharts(p, idx);
};

function renderGIPCharts(panel, idx) {
  const d = panel.data;
  const dates = d.chart.dates.map(s => new Date(s).getTime());
  const ohlc = dates.map((x, i) => ({ x, y: [d.chart.open[i], d.chart.high[i], d.chart.low[i], d.chart.close[i]] }));
  const indicators = panel._gipIndicators || new Set(['sma_20', 'bb']);
  const series = [{ name: 'OHLC', type: 'candlestick', data: ohlc }];
  const overlayColors = [];
  function addLine(name, arr, color) {
    series.push({ name, type: 'line', data: dates.map((x, i) => ({ x, y: arr[i] })).filter(p => p.y != null) });
    overlayColors.push(color);
  }
  if (indicators.has('sma_20'))  addLine('SMA20',  d.technicals.sma_20,  '#4dafff');
  if (indicators.has('sma_50'))  addLine('SMA50',  d.technicals.sma_50,  '#ffd700');
  if (indicators.has('sma_200')) addLine('SMA200', d.technicals.sma_200, '#ff4dff');
  if (indicators.has('bb')) {
    addLine('BB Upper', d.technicals.bb_upper, 'rgba(255,153,0,0.5)');
    addLine('BB Lower', d.technicals.bb_lower, 'rgba(255,153,0,0.5)');
  }

  const baseDark = (h) => ({
    chart: { height: h, background: 'transparent', toolbar: { show: false }, animations: { enabled: false }, foreColor: '#8a8a8a', fontFamily: 'JetBrains Mono, monospace' },
    grid: { borderColor: '#1a1a1a', strokeDashArray: 0 },
    theme: { mode: 'dark' },
    xaxis: { type: 'datetime', labels: { style: { fontSize: '9px' } }, axisBorder: { color: '#2a2a2a' }, axisTicks: { color: '#2a2a2a' } },
    yaxis: { labels: { style: { fontSize: '9px' } } },
    tooltip: { theme: 'dark' },
    legend: { fontSize: '9px', labels: { colors: '#8a8a8a' }, markers: { size: 6 } },
  });

  // Candle chart
  panel.charts.candle = new ApexCharts(document.getElementById(`gip-chart-${idx}`), {
    ...baseDark(260),
    series,
    colors: ['#ff9900', ...overlayColors],
    stroke: { width: [1, ...overlayColors.map(() => 1.5)] },
    plotOptions: { candlestick: { colors: { upward: '#00d97e', downward: '#ff3b3b' } } },
    legend: { ...baseDark().legend, show: series.length > 1, position: 'top', horizontalAlign: 'left' },
  });
  panel.charts.candle.render();

  // Volume bar chart
  const volSeries = dates.map((x, i) => ({ x, y: d.chart.volume[i], fillColor: d.chart.close[i] >= d.chart.open[i] ? 'rgba(0,217,126,0.6)' : 'rgba(255,59,59,0.6)' }));
  panel.charts.vol = new ApexCharts(document.getElementById(`gip-vol-${idx}`), {
    ...baseDark(90),
    series: [{ name: 'Volume', data: volSeries }],
    chart: { ...baseDark(90).chart, type: 'bar' },
    plotOptions: { bar: { columnWidth: '85%', distributed: true } },
    dataLabels: { enabled: false },
    yaxis: { labels: { style: { fontSize: '9px' }, formatter: v => fmt.big(v) } },
    legend: { show: false },
    tooltip: { theme: 'dark', y: { formatter: v => fmt.big(v) } },
  });
  panel.charts.vol.render();

  // RSI
  const rsiData = dates.map((x, i) => ({ x, y: d.technicals.rsi[i] })).filter(p => p.y != null);
  panel.charts.rsi = new ApexCharts(document.getElementById(`gip-rsi-${idx}`), {
    ...baseDark(120),
    series: [{ name: 'RSI', data: rsiData }],
    chart: { ...baseDark(120).chart, type: 'line' },
    colors: ['#4dafff'],
    stroke: { width: 1.5 },
    yaxis: { min: 0, max: 100, labels: { style: { fontSize: '9px' } } },
    annotations: {
      yaxis: [
        { y: 70, borderColor: 'rgba(255,59,59,0.5)', strokeDashArray: 2 },
        { y: 30, borderColor: 'rgba(0,217,126,0.5)', strokeDashArray: 2 },
      ],
    },
    legend: { show: false },
  });
  panel.charts.rsi.render();

  // MACD
  const macd = dates.map((x, i) => ({ x, y: d.technicals.macd_line[i] })).filter(p => p.y != null);
  const sig = dates.map((x, i) => ({ x, y: d.technicals.macd_signal[i] })).filter(p => p.y != null);
  const hist = dates.map((x, i) => {
    const v = d.technicals.macd_histogram[i];
    return v != null ? { x, y: v, fillColor: v >= 0 ? 'rgba(0,217,126,0.6)' : 'rgba(255,59,59,0.6)' } : null;
  }).filter(p => p);
  panel.charts.macd = new ApexCharts(document.getElementById(`gip-macd-${idx}`), {
    ...baseDark(120),
    series: [
      { name: 'MACD', type: 'line', data: macd },
      { name: 'Signal', type: 'line', data: sig },
      { name: 'Hist', type: 'bar', data: hist },
    ],
    chart: { ...baseDark(120).chart, type: 'line' },
    colors: ['#ff9900', '#4dafff', '#888'],
    stroke: { width: [1.5, 1.5, 0] },
    plotOptions: { bar: { columnWidth: '60%', distributed: true } },
    dataLabels: { enabled: false },
    legend: { ...baseDark().legend, show: true, position: 'top' },
  });
  panel.charts.macd.render();
}

// ---- GO / Q — Quick Quote (alias of DES) ----
defineFn('GO', 'Quick Quote',
  async (t) => { requireTicker(t); return api(`/api/stock/${t}?period=1mo`); },
  (panel, idx) => FN.DES.render(panel, idx)
);
defineFn('Q', 'Quick Quote', FN.GO.fetch, FN.GO.render);

// ---- HEAT — Sector Heatmap ----
defineFn('HEAT', 'Sector Heatmap',
  async () => api('/api/sector-heatmap'),
  (panel, idx) => {
    const d = panel.data;
    let html = `<div class="t-section-title">S&P Sectors · Intraday Change</div><div class="heatmap sectors">`;
    for (const s of d.sectors) {
      const bg = fmt.heatColor(s.change_pct);
      const cls = s.change_pct >= 0 ? 'pos' : 'neg';
      const sign = s.change_pct >= 0 ? '+' : '';
      html += `
        <div class="heat-sector" onclick="cmd('${s.etf} GIP')">
          <div class="heat-sector-bg" style="background:${bg};"></div>
          <div class="heat-sector-head">
            <span class="heat-sector-label">${s.label}</span>
            <span class="heat-sector-etf">${s.etf} · ${fmt.price(s.price)}</span>
          </div>
          <div class="heat-sector-pct ${cls}">${sign}${fmt.num(s.change_pct)}%</div>
          <div class="heatmap constituents">
            ${s.constituents.map(c => `
              <div class="heat-tile" onclick="event.stopPropagation();cmd('${c.symbol} GIP')">
                <div class="heat-tile-bg" style="background:${fmt.heatColor(c.change_pct)};"></div>
                <span class="heat-tile-sym">${c.symbol}</span>
                <span class="heat-tile-pct">${c.change_pct >= 0 ? '+' : ''}${fmt.num(c.change_pct)}%</span>
              </div>`).join('')}
          </div>
        </div>`;
    }
    html += `</div>`;
    setPanelBody(idx, html);
  }
);

// ---- N — News Feed ----
function escapeAttr(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function renderNewsItems(news, filter) {
  const filtered = filter === 'relevant' ? news.filter(n => n.relevance > 0)
                 : filter === 'title'    ? news.filter(n => n.relevance === 2)
                 :                          news;
  if (!filtered.length) {
    return '<div class="muted" style="padding:12px;">No items match this filter. Click ALL to see every headline.</div>';
  }
  return filtered.map(n => {
    const dim = n.relevance === 0 ? 'opacity:0.85;' : '';
    const badge = n.relevance === 2
      ? '<span style="color:var(--amber);font-size:9px;font-weight:700;">● TITLE</span>'
      : n.relevance === 1
        ? '<span style="color:var(--blue);font-size:9px;font-weight:700;">● BODY</span>'
        : '<span style="color:var(--text-very-dim);font-size:9px;">○ RELATED</span>';
    const summaryHtml = n.summary
      ? `<div class="news-summary muted" style="font-size:10px;margin-top:3px;max-width:90ch;line-height:1.4;">${escapeHTML(n.summary.slice(0, 220))}${n.summary.length > 220 ? '…' : ''}</div>`
      : '';
    const clickable = n.link ? 'clickable' : '';
    return `
      <div class="news-item ${clickable}" data-href="${escapeAttr(n.link)}" style="${dim}">
        <div class="news-time">
          ${n.time_str}
          <span class="news-date">${n.date_str}</span>
        </div>
        <div>
          <div class="news-title">${escapeHTML(n.title)}</div>
          <div class="news-meta">
            ${badge}
            <span class="news-publisher">${escapeHTML(n.publisher || 'Unknown')}</span>
            <span class="muted">${fmt.ago(n.timestamp)}</span>
          </div>
          ${summaryHtml}
        </div>
      </div>`;
  }).join('');
}

function bindNewsClicks(idx) {
  const listEl = document.getElementById(`news-list-${idx}`);
  if (!listEl) return;
  listEl.querySelectorAll('.news-item[data-href]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      const href = el.getAttribute('data-href');
      if (href) window.open(href, '_blank', 'noopener,noreferrer');
    });
  });
}

defineFn('N', 'News Feed',
  async (t) => { requireTicker(t); return api(`/api/news/${t}`); },
  (panel, idx) => {
    const d = panel.data;
    if (!d.news.length) {
      setPanelBody(idx, `<div class="t-section-title">${d.ticker} News</div><div class="muted" style="padding:8px;">No recent headlines available.</div>`);
      return;
    }
    const c = d.counts || { total: d.news.length, title: 0, summary: 0, related: 0 };
    const initialFilter = 'all';   // Always show everything by default; filters are a visual aid, not a hide-by-default toggle.
    const aliasStr = (d.aliases && d.aliases.length > 1) ? ` (matching ${d.aliases.join(', ')})` : '';
    const html = `
      <div class="t-section-title">${d.ticker} · ${c.total} Headlines${aliasStr}</div>
      <div style="display:flex;gap:4px;margin-bottom:8px;font-size:10px;flex-wrap:wrap;align-items:center;">
        <span class="muted" style="margin-right:4px;">FILTER:</span>
        <button class="fn-code-btn news-filter-btn" data-filter="all" onclick="newsFilter(${idx},'all',this)">ALL (${c.total})</button>
        <button class="fn-code-btn news-filter-btn" data-filter="relevant" onclick="newsFilter(${idx},'relevant',this)">RELEVANT (${c.title + c.summary})</button>
        <button class="fn-code-btn news-filter-btn" data-filter="title" onclick="newsFilter(${idx},'title',this)">TITLE HITS (${c.title})</button>
      </div>
      <div class="news-list" id="news-list-${idx}">
        ${renderNewsItems(d.news, initialFilter)}
      </div>`;
    setPanelBody(idx, html);
    const bar = document.querySelector(`#panel-body-${idx} .news-filter-btn[data-filter="${initialFilter}"]`);
    if (bar) bar.style.color = 'var(--amber)';
    bindNewsClicks(idx);
  }
);

window.newsFilter = function(idx, filter, btn) {
  const p = STATE.panels[idx];
  if (!p || !p.data) return;
  const listEl = document.getElementById(`news-list-${idx}`);
  if (listEl) {
    listEl.innerHTML = renderNewsItems(p.data.news, filter);
    bindNewsClicks(idx);
  }
  if (btn && btn.parentElement) {
    btn.parentElement.querySelectorAll('.news-filter-btn').forEach(b => { b.style.color = ''; });
    btn.style.color = 'var(--amber)';
  }
};

// ---- ECO — Economic Calendar ----
defineFn('ECO', 'Economic Calendar',
  async () => api('/api/economic-calendar'),
  (panel, idx) => {
    const d = panel.data;
    const html = `
      <div class="t-section-title">Upcoming Macro & Earnings Events</div>
      <table class="t-table eco-table">
        <thead><tr><th>DATE</th><th>TIME</th><th>CC</th><th>EVENT</th><th>IMP</th><th class="num">FCST</th><th class="num">PREV</th></tr></thead>
        <tbody>
          ${d.events.map(e => `
            <tr>
              <td class="sym">${e.date}</td>
              <td>${e.time}</td>
              <td>${e.country}</td>
              <td>${escapeHTML(e.event)}</td>
              <td class="imp-${e.importance === 'high' ? 'high' : (e.importance === 'med' ? 'med' : 'low')}">${e.importance.toUpperCase()}</td>
              <td class="num">${e.forecast}</td>
              <td class="num">${e.previous}</td>
            </tr>`).join('')}
        </tbody>
      </table>`;
    setPanelBody(idx, html);
  }
);

// ---- EQS / GAINERS / LOSERS / MKT — Screener ----
function screenerRender(mode, title) {
  return {
    fetch: async () => api(`/api/screener?mode=${mode}`),
    render: (panel, idx) => {
      const d = panel.data;
      const html = `
        <div class="t-section-title">${title}</div>
        <table class="t-table">
          <thead><tr><th>SYM</th><th>NAME</th><th class="num">PRICE</th><th class="num">CHG%</th><th class="num">VOL</th><th class="num">MKT CAP</th><th class="num">P/E</th></tr></thead>
          <tbody>
            ${d.rows.map(r => `
              <tr class="clickable" onclick="cmd('${r.symbol} GIP')">
                <td class="sym">${r.symbol}</td>
                <td>${escapeHTML(r.name).slice(0, 28)}</td>
                <td class="num">${fmt.price(r.price)}</td>
                <td class="num ${r.change_pct >= 0 ? 'pos' : 'neg'}">${r.change_pct >= 0 ? '+' : ''}${fmt.num(r.change_pct)}%</td>
                <td class="num">${fmt.vol(r.volume)}</td>
                <td class="num">${fmt.big(r.market_cap)}</td>
                <td class="num">${r.pe_ratio > 0 ? r.pe_ratio.toFixed(1) + 'x' : '—'}</td>
              </tr>`).join('')}
          </tbody>
        </table>`;
      setPanelBody(idx, html);
    },
  };
}
const _eqs = screenerRender('gainers', 'Equity Screener · Top Gainers');
defineFn('EQS', 'Equity Screener', _eqs.fetch, _eqs.render);
const _gn = screenerRender('gainers', 'Top Gainers');
defineFn('GAINERS', 'Top Gainers', _gn.fetch, _gn.render);
const _ls = screenerRender('losers', 'Top Losers');
defineFn('LOSERS', 'Top Losers', _ls.fetch, _ls.render);
const _act = screenerRender('volume', 'Most Active');
defineFn('MKT', 'Market Most Active', _act.fetch, _act.render);

// ---- W / WATCH — Watchlist ----
let WATCH = JSON.parse(localStorage.getItem('ft_watch') || '["AAPL","MSFT","GOOG","NVDA","TSLA","META","AMZN","PLTR"]');
defineFn('W', 'Watchlist',
  async () => {
    const out = [];
    for (const sym of WATCH) {
      try {
        const q = await api(`/api/live-quote/${sym}`);
        out.push(q);
      } catch (e) { /* skip */ }
    }
    return { rows: out };
  },
  (panel, idx) => {
    const d = panel.data;
    const html = `
      <div class="t-section-title">Watchlist · ${d.rows.length} symbols</div>
      <div style="display:flex;gap:4px;margin-bottom:6px;">
        <input id="wl-add-${idx}" placeholder="ADD TICKER" style="border:1px solid var(--border-bright);padding:2px 6px;color:var(--amber);font-size:11px;width:120px;text-transform:uppercase;">
        <button class="fn-code-btn" onclick="watchlistAdd(${idx})">+ ADD</button>
      </div>
      <table class="t-table">
        <thead><tr><th>SYM</th><th>NAME</th><th class="num">PRICE</th><th class="num">CHG</th><th class="num">CHG%</th><th class="num">VOL</th><th></th></tr></thead>
        <tbody>
          ${d.rows.map(r => `
            <tr class="clickable" onclick="cmd('${r.ticker} GIP')">
              <td class="sym">${r.ticker}</td>
              <td>${escapeHTML(r.name || '').slice(0, 28)}</td>
              <td class="num">${fmt.price(r.price)}</td>
              <td class="num ${r.change >= 0 ? 'pos' : 'neg'}">${r.change >= 0 ? '+' : ''}${fmt.num(r.change)}</td>
              <td class="num ${r.change_pct >= 0 ? 'pos' : 'neg'}">${r.change_pct >= 0 ? '+' : ''}${fmt.num(r.change_pct)}%</td>
              <td class="num">${fmt.vol(r.volume)}</td>
              <td><button class="panel-action" onclick="event.stopPropagation();watchlistRemove('${r.ticker}',${idx})">✕</button></td>
            </tr>`).join('')}
        </tbody>
      </table>`;
    setPanelBody(idx, html);
  }
);
window.watchlistAdd = function(idx) {
  const v = (document.getElementById(`wl-add-${idx}`).value || '').toUpperCase().trim();
  if (v && !WATCH.includes(v)) {
    WATCH.push(v);
    localStorage.setItem('ft_watch', JSON.stringify(WATCH));
    reloadPanel(idx);
  }
};
window.watchlistRemove = function(sym, idx) {
  WATCH = WATCH.filter(s => s !== sym);
  localStorage.setItem('ft_watch', JSON.stringify(WATCH));
  reloadPanel(idx);
};

// ---- COMP — Compare ----
defineFn('COMP', 'Comparison',
  async (t) => {
    if (!t) throw new Error('COMP needs 2+ tickers, e.g.  AAPL,MSFT,GOOG COMP');
    return api(`/api/compare?tickers=${encodeURIComponent(t)}`);
  },
  (panel, idx) => {
    const d = panel.data;
    setPanelBody(idx, `
      <div class="t-section-title">Relative Performance (Indexed = 100, 1Y)</div>
      <div class="chart-host" id="comp-chart-${idx}" style="height:260px;"></div>
      <div class="t-section-title">Fundamental Comparison</div>
      <div id="comp-table-${idx}"></div>
    `);
    const colors = ['#ff9900', '#4dafff', '#00d97e', '#ff4dff', '#ffd700', '#00d4d4'];
    const series = d.stocks.map(s => ({ name: s.ticker, data: s.dates.map((dt, i) => ({ x: new Date(dt).getTime(), y: s.normalized[i] })) }));
    panel.charts.comp = new ApexCharts(document.getElementById(`comp-chart-${idx}`), {
      series,
      chart: { height: 260, type: 'line', background: 'transparent', toolbar: { show: false }, foreColor: '#8a8a8a', fontFamily: 'JetBrains Mono, monospace', animations: { enabled: false } },
      colors,
      stroke: { width: 1.5, curve: 'smooth' },
      grid: { borderColor: '#1a1a1a' },
      xaxis: { type: 'datetime', labels: { style: { fontSize: '9px' } } },
      yaxis: { labels: { style: { fontSize: '9px' }, formatter: v => v.toFixed(0) } },
      legend: { position: 'top', fontSize: '10px', labels: { colors: '#e8e8e8' } },
      tooltip: { theme: 'dark' },
      annotations: { yaxis: [{ y: 100, borderColor: '#3a3a3a', strokeDashArray: 4 }] },
    });
    panel.charts.comp.render();

    const rows = [
      ['Price', s => fmt.price(s.current_price)],
      ['Chg%', s => `<span class="${s.change_pct >= 0 ? 'pos' : 'neg'}">${s.change_pct >= 0 ? '+' : ''}${fmt.num(s.change_pct)}%</span>`],
      ['YTD', s => `<span class="${s.perf_ytd >= 0 ? 'pos' : 'neg'}">${s.perf_ytd >= 0 ? '+' : ''}${fmt.num(s.perf_ytd)}%</span>`],
      ['Mkt Cap', s => fmt.big(s.market_cap)],
      ['P/E', s => s.pe_ratio > 0 ? s.pe_ratio.toFixed(1) + 'x' : '—'],
      ['PEG', s => s.peg_ratio > 0 ? s.peg_ratio.toFixed(2) : '—'],
      ['EPS', s => fmt.price(s.eps)],
      ['Rev Gr', s => fmt.pct(s.revenue_growth)],
      ['Margin', s => fmt.pct(s.profit_margin, false)],
      ['ROE', s => fmt.pct(s.roe, false)],
      ['Beta', s => fmt.num(s.beta)],
      ['Div%', s => s.dividend_yield > 0 ? fmt.pct(s.dividend_yield, false) : '—'],
      ['D/E', s => s.debt_to_equity > 0 ? s.debt_to_equity.toFixed(2) : '—'],
    ];
    document.getElementById(`comp-table-${idx}`).innerHTML = `
      <table class="t-table">
        <thead><tr><th>METRIC</th>${d.stocks.map(s => `<th class="num">${s.ticker}</th>`).join('')}</tr></thead>
        <tbody>${rows.map(([lbl, fn]) => `<tr><td>${lbl}</td>${d.stocks.map(s => `<td class="num">${fn(s)}</td>`).join('')}</tr>`).join('')}</tbody>
      </table>`;
  }
);

// ---- STAT — Live Statistical Foundation (any ticker) ----
function renderStatPanel(panel, idx, period) {
  const d = panel.data;
  if (!d || !d.ticker) { setPanelBody(idx, '<div class="muted" style="padding:12px;">No data.</div>'); return; }
  const r = d.returns_summary;
  const t = d.tests;
  const jb = t.jarque_bera || {};
  const sw = t.shapiro_wilk;
  const adf = t.adf || {};

  const mkBtn = (active, onClick, label) => `<button class="fn-code-btn" style="${active ? 'color:var(--amber);background:var(--amber-bg);border-color:var(--border-amber);' : ''}" onclick="${onClick}">${label}</button>`;
  const periodBtns = ['3mo','6mo','1y','2y','5y'].map(p => mkBtn(p === period, `statReload(${idx},'${p}')`, p.toUpperCase())).join('');

  const controls = `
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px;font-size:10px;">
      <span class="muted">PERIOD:</span>${periodBtns}
      <span class="muted" style="margin-left:8px;">${d.first_date} → ${d.last_date} · ${d.observations} obs</span>
    </div>`;

  // Summary stats card
  const summary = `
    <div class="t-section-title">${d.ticker} · Daily Log-Return Moments</div>
    <div class="kv-list">
      <div class="kv-k">Annualized Mean</div><div class="kv-v ${r.annualized_mean_pct >= 0 ? 'pos' : 'neg'}">${r.annualized_mean_pct >= 0 ? '+' : ''}${fmt.num(r.annualized_mean_pct, 2)}%</div>
      <div class="kv-k">Annualized Vol</div><div class="kv-v amber">${fmt.num(r.annualized_vol_pct, 2)}%</div>
      <div class="kv-k">Daily Mean (log)</div><div class="kv-v">${fmt.num(r.mean_daily_log, 5)}</div>
      <div class="kv-k">Daily Std (log)</div><div class="kv-v">${fmt.num(r.std_dev_daily, 5)}</div>
      <div class="kv-k">Skewness</div><div class="kv-v ${Math.abs(r.skewness) > 0.5 ? 'amber' : ''}">${r.skewness >= 0 ? '+' : ''}${fmt.num(r.skewness, 3)}</div>
      <div class="kv-k">Excess Kurtosis</div><div class="kv-v ${r.excess_kurtosis > 1 ? 'amber' : ''}">${r.excess_kurtosis >= 0 ? '+' : ''}${fmt.num(r.excess_kurtosis, 3)}</div>
      <div class="kv-k">Min daily return</div><div class="kv-v neg">${fmt.num(r.min * 100, 2)}%</div>
      <div class="kv-k">Max daily return</div><div class="kv-v pos">+${fmt.num(r.max * 100, 2)}%</div>
    </div>`;

  // Hypothesis tests table
  const swRow = sw ? `<tr><td>Shapiro-Wilk</td><td class="num">${fmt.num(sw.statistic, 4)}</td><td class="num">${fmt.num(sw.p_value, 4)}</td><td class="${sw.reject_normal_at_5pct ? 'neg' : 'pos'}">${sw.reject_normal_at_5pct ? 'REJECT Normal' : 'CANNOT REJECT'}</td></tr>` : '';
  const adfRow = adf.statistic != null ? `<tr><td>ADF (Dickey-Fuller)</td><td class="num">${fmt.num(adf.statistic, 4)}</td><td class="num">~${fmt.num(adf.p_value_approx, 3)}</td><td class="${adf.is_stationary_at_5pct ? 'pos' : 'neg'}">${adf.is_stationary_at_5pct ? 'STATIONARY' : 'UNIT ROOT (non-stationary)'}</td></tr>` : '';

  const tests = `
    <div class="t-section-title">Hypothesis Tests</div>
    <table class="t-table">
      <thead><tr><th>TEST</th><th class="num">STAT</th><th class="num">p</th><th>VERDICT</th></tr></thead>
      <tbody>
        <tr><td>Jarque-Bera (skew+kurt vs Normal)</td><td class="num">${fmt.num(jb.statistic, 4)}</td><td class="num">${fmt.num(jb.p_value, 4)}</td><td class="${jb.reject_normal_at_5pct ? 'neg' : 'pos'}">${jb.reject_normal_at_5pct ? 'REJECT Normal' : 'CANNOT REJECT'}</td></tr>
        ${swRow}
        ${adfRow}
      </tbody>
    </table>
    <div class="muted tiny" style="margin-top:4px;line-height:1.45;">
      <b>Distribution label:</b> <span class="amber" style="font-weight:700;">${escapeHTML(d.distribution_label)}</span>.
      JB / SW test Normality of returns; ADF tests stationarity of the price series (rejecting unit root → stationary).
      ADF p-value here is interpolated from MacKinnon critical values (no scipy/statsmodels dependency).
    </div>`;

  // Outliers panel
  const o = d.outliers;
  const outliers = `
    <div class="t-section-title">Tail / Outliers</div>
    <div class="kv-list">
      <div class="kv-k">Method</div><div class="kv-v">${escapeHTML(o.method)}</div>
      <div class="kv-k">Count</div><div class="kv-v amber">${o.count} (${fmt.num(o.pct, 2)}%)</div>
      <div class="kv-k">Expected under Normal</div><div class="kv-v muted">~0.27%</div>
    </div>
    <div class="muted tiny" style="margin-top:4px;">A Normal distribution predicts ~0.27% of daily returns beyond ±3σ. Higher empirical fraction = fat-tailed.</div>`;

  setPanelBody(idx, `
    ${controls}
    ${summary}
    ${tests}
    ${outliers}
    <div class="t-section-title">Returns Distribution vs Normal Overlay</div>
    <div class="chart-host" id="stat-hist-${idx}" style="height:220px;"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
      <div>
        <div class="t-section-title">Q-Q Plot (Normality)</div>
        <div class="chart-host" id="stat-qq-${idx}" style="height:220px;"></div>
        <div class="muted tiny">Points on the diagonal = Normal. Heavy fat tails curve <b>upward</b> at the right and <b>downward</b> at the left.</div>
      </div>
      <div>
        <div class="t-section-title">Autocorrelation (ACF, lags 1–${d.acf.lags.length})</div>
        <div class="chart-host" id="stat-acf-${idx}" style="height:220px;"></div>
        <div class="muted tiny">Bars beyond the dashed ±${fmt.num(d.acf.confidence_band_95, 3)} band reject white-noise at 95%.</div>
      </div>
    </div>
  `);

  const baseDark = (h) => ({
    chart: { height: h, background: 'transparent', toolbar: { show: false }, animations: { enabled: false }, foreColor: '#8a8a8a', fontFamily: 'JetBrains Mono, monospace' },
    grid: { borderColor: '#1a1a1a' },
    xaxis: { labels: { style: { fontSize: '9px' } }, axisBorder: { color: '#2a2a2a' } },
    yaxis: { labels: { style: { fontSize: '9px' } } },
    tooltip: { theme: 'dark' },
    legend: { fontSize: '9px', labels: { colors: '#e8e8e8' } },
  });

  // Histogram + normal overlay
  panel.charts.hist = new ApexCharts(document.getElementById(`stat-hist-${idx}`), {
    ...baseDark(220),
    series: [
      { name: 'Returns count', type: 'column', data: d.histogram.bin_centers.map((x, i) => ({ x: (x * 100).toFixed(2) + '%', y: d.histogram.counts[i] })) },
      { name: 'Normal expected', type: 'line', data: d.histogram.bin_centers.map((x, i) => ({ x: (x * 100).toFixed(2) + '%', y: d.histogram.normal_overlay[i] })) },
    ],
    chart: { ...baseDark(220).chart, type: 'line' },
    colors: ['#ff9900', '#4dafff'],
    stroke: { width: [0, 2], curve: 'smooth' },
    plotOptions: { bar: { columnWidth: '95%' } },
    xaxis: { ...baseDark().xaxis, type: 'category', labels: { ...baseDark().xaxis.labels, rotate: -45, hideOverlappingLabels: true } },
    dataLabels: { enabled: false },
    legend: { ...baseDark().legend, show: true, position: 'top' },
  });
  panel.charts.hist.render();

  // Q-Q plot
  panel.charts.qq = new ApexCharts(document.getElementById(`stat-qq-${idx}`), {
    ...baseDark(220),
    series: [{ name: 'Sample vs Normal', data: d.qq_plot.theoretical.map((x, i) => [x, d.qq_plot.sample[i]]) }],
    chart: { ...baseDark(220).chart, type: 'scatter', zoom: { enabled: false } },
    colors: ['#ff9900'],
    markers: { size: 3 },
    xaxis: { ...baseDark().xaxis, type: 'numeric', title: { text: 'Theoretical (Normal quantile)', style: { fontSize: '9px', color: '#8a8a8a' } } },
    yaxis: { ...baseDark().yaxis, title: { text: 'Sample (log return)', style: { fontSize: '9px', color: '#8a8a8a' } } },
    legend: { show: false },
    annotations: (() => {
      // Reference line y = mean + std * x (Normal). Compute endpoints.
      const xmin = Math.min(...d.qq_plot.theoretical);
      const xmax = Math.max(...d.qq_plot.theoretical);
      return { points: [], xaxis: [{ x: 0, borderColor: '#3a3a3a', strokeDashArray: 4 }], yaxis: [{ y: 0, borderColor: '#3a3a3a', strokeDashArray: 4 }] };
    })(),
  });
  panel.charts.qq.render();

  // ACF
  panel.charts.acf = new ApexCharts(document.getElementById(`stat-acf-${idx}`), {
    ...baseDark(220),
    series: [{ name: 'ACF', data: d.acf.values.map((v, i) => ({ x: d.acf.lags[i], y: v, fillColor: Math.abs(v) > d.acf.confidence_band_95 ? '#ff9900' : '#4dafff' })) }],
    chart: { ...baseDark(220).chart, type: 'bar' },
    plotOptions: { bar: { columnWidth: '50%', distributed: true } },
    dataLabels: { enabled: false },
    xaxis: { ...baseDark().xaxis, type: 'numeric', title: { text: 'lag', style: { fontSize: '9px', color: '#8a8a8a' } } },
    yaxis: { ...baseDark().yaxis, min: -1, max: 1 },
    legend: { show: false },
    annotations: {
      yaxis: [
        { y: d.acf.confidence_band_95, borderColor: 'rgba(255,153,0,0.5)', strokeDashArray: 2 },
        { y: -d.acf.confidence_band_95, borderColor: 'rgba(255,153,0,0.5)', strokeDashArray: 2 },
      ],
    },
  });
  panel.charts.acf.render();
}

defineFn('STAT', 'Live Statistical Foundation',
  async (t) => {
    if (!t || t === '—') throw new Error('STAT needs a ticker. Try: AAPL STAT (or any symbol).');
    return api(`/api/statistical/${t}?period=1y`);
  },
  (panel, idx) => {
    panel._statPeriod = panel._statPeriod || (panel.data && panel.data.period) || '1y';
    renderStatPanel(panel, idx, panel._statPeriod);
  }
);

window.statReload = async function(idx, period) {
  const p = STATE.panels[idx];
  if (!p || !p.ticker) return;
  setPanelBody(idx, '<div class="loader-inline">LOADING</div>');
  destroyPanelCharts(p);
  try {
    const d = await api(`/api/statistical/${p.ticker}?period=${period}`);
    p.data = d;
    p._statPeriod = period;
    renderStatPanel(p, idx, period);
  } catch (e) {
    setPanelBody(idx, `<div class="panel-empty"><div class="big" style="color:var(--red);">ERROR</div><div class="hint">${escapeHTML(e.message)}</div></div>`);
  }
};

// Legacy pipeline overview preserved as STATP
defineFn('STATP', 'Pipeline Statistical Foundation (TSLA/NVDA/PLTR)',
  async (t) => {
    const all = await api('/api/statistical-foundation');
    if (!t) return { all };
    const match = all.find(x => x.company === t.toUpperCase());
    if (!match) throw new Error(`STATP only has TSLA/NVDA/PLTR. Use STAT <ticker> for any other.`);
    return { single: match };
  },
  (panel, idx) => {
    const d = panel.data;
    if (d.all && !d.single) {
      const html = `
        <div class="t-section-title">Pipeline Statistical Foundation · TSLA / NVDA / PLTR</div>
        <table class="t-table">
          <thead><tr><th>SYM</th><th class="num">MEAN</th><th class="num">STD</th><th class="num">SKEW</th><th class="num">KURT</th><th class="num">JB p</th><th>DIST</th><th>STATIONARY</th></tr></thead>
          <tbody>
            ${d.all.map(x => `<tr class="clickable" onclick="cmd('${x.company} STAT')">
              <td class="sym">${x.company}</td>
              <td class="num">${fmt.num(x.mean)}</td>
              <td class="num">${fmt.num(x.std_dev)}</td>
              <td class="num">${fmt.num(x.skewness)}</td>
              <td class="num">${fmt.num(x.kurtosis)}</td>
              <td class="num">${fmt.num(x.jarque_bera_p_value, 3)}</td>
              <td>${x.distribution_type}</td>
              <td>${x.is_stationary ? 'YES' : 'NO'}</td>
            </tr>`).join('')}
          </tbody>
        </table>
        <div class="muted" style="margin-top:8px;font-size:10.5px;">Click a row to drill into a live single-ticker STAT panel.</div>`;
      setPanelBody(idx, html);
      return;
    }
    const s = d.single;
    setPanelBody(idx, `
      <div class="t-section-title">${s.company} · Pipeline Statistical Foundation</div>
      <div class="kv-list">
        <div class="kv-k">Mean</div><div class="kv-v">${fmt.num(s.mean)}</div>
        <div class="kv-k">Median</div><div class="kv-v">${fmt.num(s.median)}</div>
        <div class="kv-k">Std Dev</div><div class="kv-v">${fmt.num(s.std_dev)}</div>
        <div class="kv-k">Skewness</div><div class="kv-v">${fmt.num(s.skewness)}</div>
        <div class="kv-k">Kurtosis</div><div class="kv-v">${fmt.num(s.kurtosis)}</div>
        <div class="kv-k">Jarque-Bera p</div><div class="kv-v">${fmt.num(s.jarque_bera_p_value, 3)}</div>
        <div class="kv-k">Distribution</div><div class="kv-v amber">${s.distribution_type}</div>
        <div class="kv-k">ADF Stat</div><div class="kv-v">${fmt.num(s.adf_statistic)}</div>
        <div class="kv-k">ADF p</div><div class="kv-v">${fmt.num(s.adf_p_value, 3)}</div>
        <div class="kv-k">Stationary</div><div class="kv-v ${s.is_stationary ? 'pos' : 'neg'}">${s.is_stationary ? 'YES' : 'NO'}</div>
        <div class="kv-k">Imputed %</div><div class="kv-v">${fmt.num(s.missing_values_pct)}%</div>
        <div class="kv-k">Outliers</div><div class="kv-v">${s.outliers_detected}</div>
      </div>
      <div class="muted tiny" style="margin-top:6px;">Use <code>${s.company} STAT</code> for the live multi-chart panel (histogram, Q-Q, ACF).</div>
    `);
  }
);

// ---- CORR — Live correlation matrix across any tickers ----
function corrCellBg(v) {
  if (v == null) return '#111';
  const a = Math.min(0.85, Math.abs(v));
  return v >= 0 ? `rgba(0,217,126,${a})` : `rgba(255,59,59,${a})`;
}

function renderCorrHeatmap(panel, idx, period, order) {
  const d = panel.data;
  const tickers = d.tickers || [];
  const m = d.matrix || [];
  if (!tickers.length) {
    setPanelBody(idx, '<div class="muted" style="padding:12px;">No correlation data.</div>');
    return;
  }
  const droppedHtml = (d.dropped && d.dropped.length)
    ? `<span class="muted tiny" style="margin-left:8px;">(dropped: ${d.dropped.join(', ')})</span>` : '';
  const banner = `
    <div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:10px;margin-bottom:4px;">
      <span style="color:var(--amber);font-weight:700;font-size:12px;letter-spacing:0.04em;">
        Pearson Correlation · ${tickers.length}×${tickers.length} · period ${d.period.toUpperCase()} · ${d.observations} obs · avg ρ = ${fmt.num(d.avg_correlation, 3)}
      </span>${droppedHtml}
    </div>`;

  const periodBtns = ['3mo','6mo','1y','2y','5y'].map(p => {
    const active = p === period;
    return `<button class="fn-code-btn" style="${active ? 'color:var(--amber);background:var(--amber-bg);border-color:var(--border-amber);' : ''}" onclick="corrReload(${idx},'${p}','${order}')">${p.toUpperCase()}</button>`;
  }).join('');
  const orderBtns = ['input','cluster','avg'].map(o => {
    const active = o === order;
    return `<button class="fn-code-btn" style="${active ? 'color:var(--amber);background:var(--amber-bg);border-color:var(--border-amber);' : ''}" onclick="corrReload(${idx},'${period}','${o}')">${o.toUpperCase()}</button>`;
  }).join('');
  const controls = `
    <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:6px;font-size:10px;">
      <span class="muted">PERIOD:</span>${periodBtns}
      <span class="muted" style="margin-left:8px;">ORDER:</span>${orderBtns}
      <input id="corr-univ-${idx}" placeholder="custom tickers (e.g. AAPL,MSFT,GOOG)" style="border:1px solid var(--border-bright);padding:2px 6px;color:var(--amber);font-size:10.5px;min-width:280px;flex:1;text-transform:uppercase;">
      <button class="fn-code-btn" onclick="corrApplyUniverse(${idx})">APPLY</button>
      <button class="fn-code-btn" onclick="corrApplyUniverse(${idx},true)">DEFAULT-30</button>
    </div>`;

  // Render the table. First col + first row sticky for scrollability.
  let head = `<th style="position:sticky;left:0;background:var(--bg-panel);z-index:3;">·</th>`;
  for (const t of tickers) {
    head += `<th class="num" style="font-size:9.5px;background:var(--bg-panel);">${t}</th>`;
  }
  let rows = '';
  for (let i = 0; i < tickers.length; i++) {
    rows += `<tr><td class="sym" style="position:sticky;left:0;background:var(--bg-panel-2);z-index:2;">${tickers[i]}</td>`;
    for (let j = 0; j < tickers.length; j++) {
      const v = m[i][j];
      const isDiag = (i === j);
      const text = v == null ? '—' : (isDiag ? '1' : v.toFixed(2).replace(/^0/, '').replace(/^-0/, '-'));
      const bg = isDiag ? 'var(--bg-header)' : corrCellBg(v);
      const cls = !isDiag && v != null && Math.abs(v) >= 0.8 ? 'font-weight:700;' : '';
      const click = !isDiag && v != null ? `onclick="cmd('${tickers[i]},${tickers[j]} COMP')"` : '';
      rows += `<td class="num" style="background:${bg};color:#fff;font-size:9.5px;cursor:${isDiag?'default':'pointer'};${cls}" ${click} title="${tickers[i]} ↔ ${tickers[j]} = ${v == null ? 'NA' : v.toFixed(3)}">${text}</td>`;
    }
    rows += '</tr>';
  }
  const table = `
    <div style="overflow:auto;max-height:60vh;border:1px solid var(--border);">
      <table class="t-table" style="font-size:9.5px;border-collapse:separate;border-spacing:0;">
        <thead><tr>${head}</tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;

  const pairsTable = (title, rows, cls) => `
    <div style="flex:1;min-width:260px;">
      <div class="t-section-title">${title}</div>
      <table class="t-table" style="font-size:10.5px;">
        <thead><tr><th>A</th><th>B</th><th class="num">ρ</th></tr></thead>
        <tbody>${rows.map(p => `<tr class="clickable" onclick="cmd('${p.a},${p.b} COMP')"><td class="sym">${p.a}</td><td class="sym">${p.b}</td><td class="num ${cls}">${fmt.num(p.corr, 3)}</td></tr>`).join('') || '<tr><td colspan="3" class="muted">—</td></tr>'}</tbody>
      </table>
    </div>`;

  setPanelBody(idx, `
    ${banner}
    ${controls}
    ${table}
    <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;">
      ${pairsTable('Most Correlated Pairs', d.highest_pairs || [], 'pos')}
      ${pairsTable('Least Correlated Pairs', d.lowest_pairs || [], 'neg')}
    </div>
    <div class="muted tiny" style="margin-top:6px;line-height:1.45;">
      Correlation of daily log-returns. Click any off-diagonal cell or pair-table row → COMP overlay of the two tickers.
      Override the universe via the input box (≤ 60 symbols). <b>ORDER:</b> <i>input</i> = type order, <i>cluster</i> = greedy nearest-neighbor (block-diagonal look), <i>avg</i> = sort by average pairwise ρ.
    </div>
  `);
}

defineFn('CORR', 'Cross-Asset Correlation Matrix',
  async (t) => {
    const tickers = t ? `&tickers=${encodeURIComponent(t)}` : '';
    return api(`/api/correlation-matrix?period=1y&order=cluster${tickers}`);
  },
  (panel, idx) => {
    panel._corrPeriod = panel._corrPeriod || (panel.data && panel.data.period) || '1y';
    panel._corrOrder = panel._corrOrder || (panel.data && panel.data.order) || 'cluster';
    renderCorrHeatmap(panel, idx, panel._corrPeriod, panel._corrOrder);
  }
);

window.corrReload = async function(idx, period, order) {
  const p = STATE.panels[idx];
  if (!p) return;
  setPanelBody(idx, '<div class="loader-inline">LOADING</div>');
  try {
    const tickers = p.ticker && p.ticker !== '—' ? `&tickers=${encodeURIComponent(p.ticker)}` : '';
    const d = await api(`/api/correlation-matrix?period=${period}&order=${order}${tickers}`);
    p.data = d;
    p._corrPeriod = period;
    p._corrOrder = order;
    renderCorrHeatmap(p, idx, period, order);
  } catch (e) {
    setPanelBody(idx, `<div class="panel-empty"><div class="big" style="color:var(--red);">ERROR</div><div class="hint">${escapeHTML(e.message)}</div></div>`);
  }
};

window.corrApplyUniverse = function(idx, useDefault) {
  const p = STATE.panels[idx];
  if (!p) return;
  let raw = '';
  if (!useDefault) {
    const inp = document.getElementById(`corr-univ-${idx}`);
    raw = (inp && inp.value || '').trim();
    if (!raw) return;
  }
  p.ticker = useDefault ? '—' : raw.toUpperCase();
  corrReload(idx, p._corrPeriod || '1y', p._corrOrder || 'cluster');
};

// Legacy static pipeline matrix preserved as CORRP
defineFn('CORRP', 'Pipeline Static Correlation (TSLA/NVDA/PLTR)',
  async () => api('/api/correlation-analyzer'),
  (panel, idx) => {
    const d = panel.data;
    const matrix = d.correlation_matrix || {};
    const labels = Object.keys(matrix);
    if (!labels.length) { setPanelBody(idx, '<div class="muted">No correlation data.</div>'); return; }
    let html = `<div class="t-section-title">Pipeline Static Matrix · ${labels.length}×${labels.length}</div>`;
    html += `<table class="t-table" style="font-size:10px;"><thead><tr><th></th>${labels.map(l => `<th class="num">${l}</th>`).join('')}</tr></thead><tbody>`;
    for (const r of labels) {
      html += `<tr><td class="sym">${r}</td>`;
      for (const c of labels) {
        const v = (matrix[r] || {})[c];
        const val = (typeof v === 'number') ? v : 0;
        const bg = corrCellBg(val);
        html += `<td class="num" style="background:${bg};color:#fff;">${val.toFixed(2)}</td>`;
      }
      html += '</tr>';
    }
    html += '</tbody></table>';
    if (d.risk_warnings && d.risk_warnings.length) {
      html += `<div class="t-section-title">Risk Warnings</div><ul style="font-size:11px;padding-left:18px;color:var(--red);">${d.risk_warnings.map(w => `<li>${escapeHTML(typeof w === 'string' ? w : w.message || JSON.stringify(w))}</li>`).join('')}</ul>`;
    }
    setPanelBody(idx, html);
  }
);

// ---- MACRO ----
defineFn('MACRO', 'Macro Context & Rate Sensitivity',
  async () => api('/api/macro-indicators'),
  (panel, idx) => {
    const d = panel.data;
    const hs = d.historical_series || {};
    const regimeBlock = d.regime_analysis || {};
    const cur = regimeBlock.current_regime || {};
    const regimes = regimeBlock.regimes || [];
    const adj = d.macro_adjusted_valuations || {};
    const scenarios = d.interest_rate_scenarios || {};

    // --- Current regime banner ---
    const curBanner = (cur && cur.name) ? `
      <div style="border:1px solid var(--border-amber);background:var(--amber-bg);padding:6px 10px;margin-bottom:8px;">
        <div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px;">
          <span style="color:var(--amber);font-weight:700;font-size:12px;letter-spacing:0.04em;">CURRENT REGIME · ${escapeHTML(cur.name || '—')}</span>
          <span class="muted" style="font-size:10px;">${escapeHTML(cur.rate_environment || '')}</span>
        </div>
        ${cur.inflation_cpi ? `<div class="muted" style="font-size:10.5px;margin-top:3px;">Inflation: ${escapeHTML(cur.inflation_cpi)}</div>` : ''}
        ${cur.investment_implication ? `<div style="font-size:11px;margin-top:4px;color:var(--text);max-width:100ch;line-height:1.4;">${escapeHTML(cur.investment_implication)}</div>` : ''}
      </div>` : '';

    // --- Macro-adjusted valuations table (with corrected field names) ---
    const adjRows = Object.entries(adj).map(([sym, v]) => {
      const cur_pe = v.current_pe;
      const just_pe = v.justified_pe_bond_yield;
      const adj_pe  = v.macro_adjusted_pe;
      const factor  = v.macro_adjustment_factor;
      const gap_pct = (cur_pe && adj_pe) ? ((cur_pe - adj_pe) / adj_pe) * 100 : null;
      const gapCls = gap_pct == null ? '' : (gap_pct >= 0 ? 'neg' : 'pos'); // current > adjusted → overvalued (neg for investor)
      return `<tr class="clickable" onclick="cmd('${sym} MC')">
        <td class="sym">${sym}</td>
        <td class="num">${fmt.num(cur_pe, 1)}x</td>
        <td class="num">${fmt.num(just_pe, 1)}x</td>
        <td class="num">${fmt.num(adj_pe, 1)}x</td>
        <td class="num">${fmt.num(factor, 3)}</td>
        <td class="num ${gapCls}">${gap_pct == null ? '—' : (gap_pct >= 0 ? '+' : '') + fmt.num(gap_pct, 1) + '%'}</td>
        <td class="muted" style="white-space:normal;max-width:60ch;font-size:10.5px;">${escapeHTML(v.thesis || '')}</td>
      </tr>`;
    }).join('');

    const adjTable = `
      <table class="t-table">
        <thead><tr>
          <th>SYM</th>
          <th class="num">CURRENT P/E</th>
          <th class="num">JUSTIFIED P/E</th>
          <th class="num">MACRO-ADJ P/E</th>
          <th class="num">ADJ FACTOR</th>
          <th class="num">GAP</th>
          <th>THESIS</th>
        </tr></thead>
        <tbody>${adjRows || '<tr><td colspan="7" class="muted">No data.</td></tr>'}</tbody>
      </table>
      <div class="muted tiny" style="margin-top:4px;line-height:1.45;">
        <b>JUSTIFIED P/E</b> = Gordon-growth target given current 10Y bond yield. &nbsp;
        <b>MACRO-ADJ P/E</b> = justified P/E × adjustment factor (sector/sentiment overlay). &nbsp;
        <b>GAP</b> = how stretched the current multiple is vs. macro-implied fair.
        Click any row → Monte Carlo.
      </div>`;

    // --- Rate sensitivity grid: one mini-table per ticker ---
    const scenarioBlocks = Object.entries(scenarios).map(([sym, rows]) => {
      const rowsHtml = (Array.isArray(rows) ? rows : []).map(r => {
        const chg = r.price_change_pct;
        const cls = chg >= 0 ? 'pos' : 'neg';
        return `<tr>
          <td>${escapeHTML(r.scenario || '')}</td>
          <td class="num">${fmt.num(r.target_pe, 1)}x</td>
          <td class="num">${fmt.price(r.projected_fair_price)}</td>
          <td class="num ${cls}">${chg >= 0 ? '+' : ''}${fmt.num(chg, 1)}%</td>
        </tr>`;
      }).join('');
      return `
        <div style="flex:1;min-width:260px;">
          <div style="color:var(--amber);font-weight:700;font-size:11px;letter-spacing:0.04em;margin-bottom:3px;cursor:pointer;" onclick="cmd('${sym} MC')">${sym} →</div>
          <table class="t-table" style="font-size:10.5px;">
            <thead><tr><th>SCENARIO</th><th class="num">P/E</th><th class="num">FAIR</th><th class="num">Δ</th></tr></thead>
            <tbody>${rowsHtml || '<tr><td colspan="4" class="muted">—</td></tr>'}</tbody>
          </table>
        </div>`;
    }).join('');

    // --- Historical regimes ---
    const regimeCards = regimes.map(r => `
      <div style="border:1px solid var(--border);padding:6px 10px;background:var(--bg-panel-2);">
        <div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:6px;">
          <span style="color:var(--amber);font-weight:600;font-size:11px;">${escapeHTML(r.regime_name || '')}</span>
          <span class="muted tiny">${escapeHTML(r.duration || '')}</span>
        </div>
        <div class="muted" style="font-size:10.5px;margin-top:2px;">${escapeHTML(r.characteristics || '')}</div>
        <div style="display:flex;gap:14px;margin-top:4px;font-size:10px;">
          <span><span class="muted">avg 10Y:</span> <b>${fmt.num(r.avg_10y_yield, 2)}%</b></span>
          <span><span class="muted">avg M2 gr:</span> <b>${fmt.num(r.avg_m2_growth, 1)}%</b></span>
        </div>
        ${r.impact_growth_stocks ? `<div style="font-size:10.5px;margin-top:4px;color:var(--text);line-height:1.4;">${escapeHTML(r.impact_growth_stocks)}</div>` : ''}
      </div>`).join('');

    setPanelBody(idx, `
      ${curBanner}
      <div class="t-section-title">Macro Drivers · 5Y</div>
      <div class="chart-host" id="macro-chart-${idx}" style="height:240px;"></div>
      <div class="t-section-title">Macro-Adjusted Valuations</div>
      ${adjTable}
      <div class="t-section-title">Interest-Rate Sensitivity Scenarios</div>
      <div style="display:flex;flex-wrap:wrap;gap:12px;">${scenarioBlocks || '<div class="muted">No data.</div>'}</div>
      <div class="t-section-title">Historical Regimes</div>
      <div style="display:flex;flex-direction:column;gap:6px;">${regimeCards || '<div class="muted">No data.</div>'}</div>
    `);

    // --- Render the 5Y macro drivers chart ---
    if (hs.dates && hs.dates.length) {
      const xs = hs.dates.map(s => new Date(s).getTime());
      const mkSeries = (name, arr) => ({ name, data: xs.map((x, i) => ({ x, y: arr ? arr[i] : null })).filter(p => p.y != null) });
      const series = [
        mkSeries('Fed Funds (%)', hs.fed_funds),
        mkSeries('10Y Yield (%)', hs.yield_10y),
        mkSeries('CPI YoY (%)', hs.cpi),
        mkSeries('M2 Growth (%)', hs.m2_growth),
        mkSeries('Fed B/S ($T)', hs.fed_balance_sheet),
      ];
      panel.charts.macro = new ApexCharts(document.getElementById(`macro-chart-${idx}`), {
        series,
        chart: { height: 240, type: 'line', background: 'transparent', toolbar: { show: false }, animations: { enabled: false }, foreColor: '#8a8a8a', fontFamily: 'JetBrains Mono, monospace' },
        colors: ['#ff9900', '#4dafff', '#ff3b3b', '#00d97e', '#00d4d4'],
        stroke: { width: 1.6, curve: 'smooth' },
        grid: { borderColor: '#1a1a1a' },
        xaxis: { type: 'datetime', labels: { style: { fontSize: '9px' } }, axisBorder: { color: '#2a2a2a' } },
        yaxis: [
          { seriesName: ['Fed Funds (%)', '10Y Yield (%)', 'CPI YoY (%)', 'M2 Growth (%)'], labels: { style: { fontSize: '9px' }, formatter: v => v == null ? '' : v.toFixed(1) + '%' }, title: { text: 'rates / inflation / M2', style: { fontSize: '9px', color: '#8a8a8a' } } },
          { seriesName: 'Fed B/S ($T)', opposite: true, labels: { style: { fontSize: '9px' }, formatter: v => v == null ? '' : '$' + v.toFixed(1) + 'T' }, title: { text: 'balance sheet', style: { fontSize: '9px', color: '#8a8a8a' } } },
        ],
        legend: { position: 'top', fontSize: '10px', labels: { colors: '#e8e8e8' }, markers: { size: 6 } },
        tooltip: { theme: 'dark', shared: true, x: { format: 'MMM yyyy' } },
      });
      panel.charts.macro.render();
    }
  }
);

// ---- GRAPH — Asset Correlation Network (Mantegna) ----
const CLUSTER_PALETTE = [
  '#ff9900', '#4dafff', '#00d97e', '#ff4dff', '#ffd700', '#00d4d4',
  '#ff3b3b', '#a855f7', '#10b981', '#ec4899', '#0ea5e9', '#f59e0b',
];
function clusterColor(cid) {
  if (cid == null || cid < 0) return '#5a5a5a';
  return CLUSTER_PALETTE[cid % CLUSTER_PALETTE.length];
}

function renderNetworkPanel(panel, idx, method, period, threshold) {
  const d = panel.data;
  if (!d || !d.nodes || !d.nodes.length) {
    setPanelBody(idx, '<div class="muted" style="padding:12px;">No network data.</div>');
    return;
  }

  const mkBtn = (active, onClick, label) => `<button class="fn-code-btn" style="${active ? 'color:var(--amber);background:var(--amber-bg);border-color:var(--border-amber);' : ''}" onclick="${onClick}">${label}</button>`;

  const methodBtns = ['mst', 'threshold', 'knn']
    .map(m => mkBtn(m === method, `netReload(${idx},'${m}','${period}',${threshold})`, m.toUpperCase()))
    .join('');
  const periodBtns = ['3mo','6mo','1y','2y']
    .map(p => mkBtn(p === period, `netReload(${idx},'${method}','${p}',${threshold})`, p.toUpperCase()))
    .join('');

  const isThr = method === 'threshold';
  const droppedHtml = (d.dropped && d.dropped.length)
    ? `<span class="muted tiny" style="margin-left:8px;">dropped: ${d.dropped.join(', ')}</span>` : '';
  const isolatedHtml = (d.isolated && d.isolated.length)
    ? `<span class="muted tiny" style="margin-left:8px;">isolated: ${d.isolated.join(', ')}</span>` : '';

  const banner = `
    <div style="color:var(--amber);font-weight:700;font-size:12px;letter-spacing:0.04em;margin-bottom:4px;">
      ${method.toUpperCase()} · ${d.n_nodes} nodes · ${d.n_edges} edges · ${d.n_components} component${d.n_components !== 1 ? 's' : ''} · ${d.clusters.length} cluster${d.clusters.length !== 1 ? 's' : ''} · ${d.observations} obs
      ${droppedHtml}${isolatedHtml}
    </div>`;

  const controls = `
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px;font-size:10px;">
      <span class="muted">METHOD:</span>${methodBtns}
      <span class="muted" style="margin-left:6px;">PERIOD:</span>${periodBtns}
      ${isThr ? `<span class="muted" style="margin-left:6px;">|ρ| ≥</span>
        <input id="net-thr-${idx}" type="number" step="0.05" min="0.1" max="0.95" value="${threshold}" style="border:1px solid var(--border-bright);padding:2px 6px;color:var(--amber);font-size:10.5px;width:60px;">
        <button class="fn-code-btn" onclick="netReloadThreshold(${idx})">APPLY</button>` : ''}
      <input id="net-univ-${idx}" placeholder="custom tickers (≤60)" style="border:1px solid var(--border-bright);padding:2px 6px;color:var(--amber);font-size:10.5px;min-width:220px;flex:1;text-transform:uppercase;">
      <button class="fn-code-btn" onclick="netApplyUniverse(${idx})">APPLY</button>
      <button class="fn-code-btn" onclick="netApplyUniverse(${idx},true)">DEFAULT-30</button>
    </div>`;

  // Cluster legend
  const clusterCards = d.clusters.map(c => {
    const color = clusterColor(c.id);
    return `<div style="border-left:3px solid ${color};padding:4px 8px;background:var(--bg-panel-2);min-width:180px;flex:1;">
      <div style="color:${color};font-weight:700;font-size:10.5px;">CLUSTER ${c.id} · ${c.size} names</div>
      <div class="muted" style="font-size:10px;margin-top:2px;word-break:break-word;">${c.members.join(' · ')}</div>
    </div>`;
  }).join('');

  // Centrality tables
  const centTable = (title, rows, key, valFmt) => `
    <div style="flex:1;min-width:200px;">
      <div class="t-section-title">${title}</div>
      <table class="t-table" style="font-size:10.5px;">
        <thead><tr><th>SYM</th><th class="num">VAL</th><th class="num">DEG</th><th class="num">CL</th></tr></thead>
        <tbody>${rows.slice(0, 8).map(n => `<tr class="clickable" onclick="cmd('${n.id} GIP')">
          <td class="sym">${n.id}</td>
          <td class="num">${valFmt(n[key])}</td>
          <td class="num">${n.degree}</td>
          <td class="num" style="color:${clusterColor(n.cluster)};font-weight:700;">${n.cluster}</td>
        </tr>`).join('')}</tbody>
      </table>
    </div>`;

  setPanelBody(idx, `
    ${banner}
    ${controls}
    <div id="net-host-${idx}" class="network-host" style="height:380px;margin-bottom:8px;"></div>
    <div style="display:flex;gap:14px;flex-wrap:wrap;">
      ${centTable('Top Betweenness (Bridges)', d.top_betweenness, 'betweenness_centrality', v => v.toFixed(3))}
      ${centTable('Top Degree (Hubs)', d.top_degree, 'degree_centrality', v => v.toFixed(3))}
      ${centTable('Top Eigenvector (Influence)', d.top_eigenvector, 'eigenvector_centrality', v => v.toFixed(3))}
    </div>
    <div class="t-section-title">Clusters · Community Detection (Greedy Modularity)</div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;">${clusterCards}</div>
    <div class="muted tiny" style="margin-top:8px;line-height:1.55;">
      <b>Edges:</b> weighted by Mantegna distance <code>d = √(2(1−ρ))</code>. Thicker = more correlated. Green = positive ρ, red = negative.<br>
      <b>MST:</b> minimum spanning tree (n−1 edges, always one connected graph; reveals the strongest correlation backbone).<br>
      <b>Threshold:</b> only pairs with |ρ| ≥ τ (disconnects can occur).<br>
      <b>kNN:</b> each node linked to its k=3 nearest neighbors by distance.<br>
      <b>Centralities:</b> Betweenness = how often the node sits on shortest paths (bridge / systemic risk). Degree = direct connections. Eigenvector = importance weighted by neighbor importance.<br>
      Click any node in the graph (or row in the tables) to drill into its chart.
    </div>
  `);

  // Build the vis-network
  const host = document.getElementById(`net-host-${idx}`);
  if (host) {
    const visNodes = new vis.DataSet(d.nodes.map(n => ({
      id: n.id, label: n.id,
      color: { background: clusterColor(n.cluster), border: '#000', highlight: { background: '#fff', border: clusterColor(n.cluster) } },
      font: { color: '#000', size: 11, face: 'JetBrains Mono', strokeWidth: 0 },
      size: 10 + (n.degree_centrality || 0) * 30 + (n.betweenness_centrality || 0) * 22,
      title: `${n.id}\nCluster ${n.cluster} · deg=${n.degree}\nbetween=${(n.betweenness_centrality || 0).toFixed(3)}\neigen=${(n.eigenvector_centrality || 0).toFixed(3)}`,
    })));
    const visEdges = new vis.DataSet(d.edges.map(e => ({
      from: e.from, to: e.to,
      color: { color: e.corr >= 0 ? 'rgba(0,217,126,0.55)' : 'rgba(255,59,59,0.55)' },
      width: Math.max(0.5, (1 - e.weight / 2) * 2.8),
      title: `${e.from} ↔ ${e.to}  ρ=${e.corr.toFixed(3)}  d=${e.weight.toFixed(3)}`,
      smooth: { type: 'continuous' },
    })));
    panel.network = new vis.Network(host, { nodes: visNodes, edges: visEdges }, {
      nodes: { shape: 'dot', borderWidth: 1 },
      edges: {},
      physics: {
        stabilization: { iterations: 200 },
        barnesHut: { gravitationalConstant: -7000, springLength: 110, springConstant: 0.04, damping: 0.18 },
      },
      interaction: { hover: true, tooltipDelay: 80, zoomView: true, dragView: true },
    });
    panel.network.on('click', (params) => {
      if (params.nodes && params.nodes.length) {
        cmd(`${params.nodes[0]} GIP`);
      }
    });
  }
}

defineFn('GRAPH', 'Asset Correlation Network',
  async (t) => {
    const tickers = t ? `&tickers=${encodeURIComponent(t)}` : '';
    return api(`/api/network?period=1y&method=mst${tickers}`);
  },
  (panel, idx) => {
    panel._netMethod = panel._netMethod || (panel.data && panel.data.method) || 'mst';
    panel._netPeriod = panel._netPeriod || (panel.data && panel.data.period) || '1y';
    panel._netThreshold = panel._netThreshold || 0.5;
    renderNetworkPanel(panel, idx, panel._netMethod, panel._netPeriod, panel._netThreshold);
  }
);

window.netReload = async function(idx, method, period, threshold) {
  const p = STATE.panels[idx];
  if (!p) return;
  setPanelBody(idx, '<div class="loader-inline">LOADING</div>');
  if (p.network) { try { p.network.destroy(); } catch (e) {} p.network = null; }
  try {
    const tickers = p.ticker && p.ticker !== '—' ? `&tickers=${encodeURIComponent(p.ticker)}` : '';
    const thr = method === 'threshold' ? `&threshold=${threshold}` : '';
    const d = await api(`/api/network?period=${period}&method=${method}${thr}${tickers}`);
    p.data = d;
    p._netMethod = method;
    p._netPeriod = period;
    p._netThreshold = threshold;
    renderNetworkPanel(p, idx, method, period, threshold);
  } catch (e) {
    setPanelBody(idx, `<div class="panel-empty"><div class="big" style="color:var(--red);">ERROR</div><div class="hint">${escapeHTML(e.message)}</div></div>`);
  }
};
window.netReloadThreshold = function(idx) {
  const p = STATE.panels[idx];
  if (!p) return;
  const inp = document.getElementById(`net-thr-${idx}`);
  const v = parseFloat(inp && inp.value);
  if (isNaN(v) || v < 0.1 || v > 0.95) return;
  netReload(idx, 'threshold', p._netPeriod || '1y', v);
};
window.netApplyUniverse = function(idx, useDefault) {
  const p = STATE.panels[idx];
  if (!p) return;
  let raw = '';
  if (!useDefault) {
    const inp = document.getElementById(`net-univ-${idx}`);
    raw = (inp && inp.value || '').trim();
    if (!raw) return;
  }
  p.ticker = useDefault ? '—' : raw.toUpperCase();
  netReload(idx, p._netMethod || 'mst', p._netPeriod || '1y', p._netThreshold || 0.5);
};

// Legacy static supply-chain preserved as GRAPHP
defineFn('GRAPHP', 'Pipeline Static Supply-Chain (TSLA/NVDA/PLTR)',
  async () => api('/api/graph-network'),
  (panel, idx) => {
    const d = panel.data;
    setPanelBody(idx, `
      <div class="t-section-title">Supply & Customer Network (static)</div>
      <div id="net-host-${idx}" class="network-host" style="height:340px;"></div>
      <div class="t-section-title">Centrality Ranking</div>
      <table class="t-table"><thead><tr><th>NODE</th><th class="num">DEGREE</th><th class="num">BETWEENNESS</th></tr></thead>
      <tbody>${(d.centrality_metrics ? Object.entries(d.centrality_metrics).slice(0, 12) : []).map(([k, v]) => `<tr><td class="sym">${k}</td><td class="num">${fmt.num(v.degree || 0)}</td><td class="num">${fmt.num(v.betweenness || 0, 3)}</td></tr>`).join('') || '<tr><td colspan="3" class="muted">No data</td></tr>'}</tbody></table>
    `);
    const host = document.getElementById(`net-host-${idx}`);
    if (host && d.nodes && d.edges) {
      const nodes = new vis.DataSet(d.nodes.map(n => ({
        id: n.id || n.label, label: n.label || n.id,
        color: n.type === 'core' ? '#ff9900' : (n.type === 'supplier' ? '#4dafff' : (n.type === 'customer' ? '#00d97e' : '#5a5a5a')),
        font: { color: '#e8e8e8', size: 11, face: 'JetBrains Mono' },
      })));
      const edges = new vis.DataSet(d.edges.map(e => ({ from: e.from || e.source, to: e.to || e.target, color: { color: '#2a2a2a' }, arrows: 'to' })));
      panel.network = new vis.Network(host, { nodes, edges }, {
        nodes: { shape: 'dot', size: 16, borderWidth: 1 },
        edges: { width: 1, smooth: { type: 'continuous' } },
        physics: { stabilization: { iterations: 80 } },
      });
    }
  }
);

// ---- MC — Monte Carlo / Valuation ----
defineFn('MC', 'Monte Carlo Valuation',
  async (t) => {
    const c = (t || 'TSLA').toUpperCase();
    if (!['TSLA', 'NVDA', 'PLTR'].includes(c)) throw new Error('MC available only for TSLA / NVDA / PLTR.');
    return api(`/api/companies/${c}`);
  },
  (panel, idx) => {
    const d = panel.data;
    const v = d.valuation;
    setPanelBody(idx, `
      <div class="t-section-title">${d.company} · Valuation Scenarios</div>
      <div class="kv-list">
        <div class="kv-k">Fair Price (Bull)</div><div class="kv-v pos">${fmt.price(v.fair_price_bull)}</div>
        <div class="kv-k">Fair Price (Base)</div><div class="kv-v amber">${fmt.price(v.fair_price_base)}</div>
        <div class="kv-k">Fair Price (Bear)</div><div class="kv-v neg">${fmt.price(v.fair_price_bear)}</div>
        <div class="kv-k">Growth Rate (Base)</div><div class="kv-v">${fmt.pct(v.growth_rate_base, false)}</div>
        <div class="kv-k">Downside Risk</div><div class="kv-v neg">${fmt.pct(v.downside_risk_pct, false)}</div>
        <div class="kv-k">VaR 95%</div><div class="kv-v neg">${fmt.pct(v.value_at_risk_95, false)}</div>
      </div>
      <div class="t-section-title">Monte Carlo Paths (GBM, 2Y)</div>
      <div class="chart-host" id="mc-chart-${idx}" style="height:240px;"></div>
    `);
    const mc = v.monte_carlo_distribution || {};
    const sample = mc.sample || [];
    if (sample.length) {
      const series = sample.slice(0, 60).map((path, i) => ({ name: `p${i}`, data: path.map((y, j) => ({ x: j, y })) }));
      panel.charts.mc = new ApexCharts(document.getElementById(`mc-chart-${idx}`), {
        series,
        chart: { height: 240, type: 'line', background: 'transparent', toolbar: { show: false }, foreColor: '#8a8a8a', fontFamily: 'JetBrains Mono', animations: { enabled: false } },
        colors: series.map(() => 'rgba(255,153,0,0.18)'),
        stroke: { width: 1, curve: 'straight' },
        grid: { borderColor: '#1a1a1a' },
        xaxis: { type: 'numeric', labels: { style: { fontSize: '9px' } } },
        yaxis: { labels: { style: { fontSize: '9px' }, formatter: vv => fmt.price(vv) } },
        legend: { show: false },
        tooltip: { enabled: false },
      });
      panel.charts.mc.render();
    }
  }
);

// ---- EVTS — Earnings event log ----
defineFn('EVTS', 'Earnings Alerts Log',
  async () => api('/api/alerts'),
  (panel, idx) => {
    const arr = panel.data || [];
    const html = `
      <div class="t-section-title">Earnings Event Log</div>
      <table class="t-table">
        <thead><tr><th>TIME</th><th>SYM</th><th>EVENT</th><th class="num">EXP</th><th class="num">ACT</th><th class="num">DEV</th><th>MSG</th></tr></thead>
        <tbody>${arr.length ? arr.map(a => `
          <tr>
            <td>${(a.timestamp || '').slice(0, 16).replace('T', ' ')}</td>
            <td class="sym">${a.company}</td>
            <td>${escapeHTML(a.event_name || '')}</td>
            <td class="num">${fmt.pct(a.growth_rate_expected, false)}</td>
            <td class="num">${fmt.pct(a.growth_rate_actual, false)}</td>
            <td class="num ${a.deviation_pct >= 0 ? 'pos' : 'neg'}">${a.deviation_pct >= 0 ? '+' : ''}${fmt.num(a.deviation_pct)}%</td>
            <td class="muted">${escapeHTML((a.alert_message || '').slice(0, 80))}</td>
          </tr>`).join('') : '<tr><td colspan="7" class="muted">No events. Type <code>SIM TSLA</code> to simulate.</td></tr>'}
        </tbody>
      </table>
      <div style="margin-top:8px;display:flex;gap:6px;">
        <button class="fn-code-btn" onclick="cmd('SIM TSLA')">▶ SIM TSLA</button>
        <button class="fn-code-btn" onclick="cmd('SIM NVDA')">▶ SIM NVDA</button>
        <button class="fn-code-btn" onclick="cmd('SIM PLTR')">▶ SIM PLTR</button>
      </div>`;
    setPanelBody(idx, html);
  }
);

// ---- SIM — Trigger mock earnings ----
defineFn('SIM', 'Simulate Earnings Event',
  async (t) => {
    if (!t) throw new Error('SIM needs a ticker (TSLA / NVDA / PLTR)');
    const res = await fetch('/api/trigger-earnings', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ company: t }) });
    if (!res.ok) throw new Error('Sim failed');
    return res.json();
  },
  (panel, idx) => {
    const d = panel.data;
    setPanelBody(idx, `
      <div class="t-section-title">Earnings Simulation · ${d.new_alert.company}</div>
      <div class="kv-list">
        <div class="kv-k">Deviation</div><div class="kv-v ${d.new_alert.deviation_pct >= 0 ? 'pos' : 'neg'}">${d.new_alert.deviation_pct >= 0 ? '+' : ''}${fmt.num(d.new_alert.deviation_pct)}%</div>
        <div class="kv-k">Action Taken</div><div class="kv-v">${escapeHTML(d.new_alert.action_taken)}</div>
      </div>
      <div class="t-section-title">Alert Message</div>
      <div style="font-size:11px;color:var(--amber);padding:6px;border:1px solid var(--border-amber);background:var(--amber-bg);">${escapeHTML(d.new_alert.alert_message)}</div>
      <div class="muted" style="margin-top:8px;">Try <code>EVTS</code> to view the full log, or <code>${d.new_alert.company} MC</code> to see updated valuations.</div>
    `);
  }
);

// ---- HELP ----
defineFn('HELP', 'Command Reference',
  async () => ({}),
  (panel, idx) => {
    const codes = Object.entries(FN).map(([k, v]) => `<div class="hg-code">${k}</div><div class="hg-desc">${v.desc}</div>`).join('');
    setPanelBody(idx, `
      <div class="help-block">
        <div class="t-section-title">Command Syntax</div>
        <div style="font-size:11.5px;line-height:1.6;">
          <code>TICKER FN</code> &nbsp;·&nbsp; <code>FN TICKER</code> &nbsp;·&nbsp; <code>FN</code> &nbsp;·&nbsp; trailing <code>GO</code> optional
        </div>
        <div style="font-size:11.5px;margin-top:6px;color:var(--text-dim);">
          Examples: <code>AAPL FA</code> &nbsp; <code>NVDA GIP</code> &nbsp; <code>HEAT</code> &nbsp; <code>N TSLA</code> &nbsp; <code>AAPL,MSFT,GOOG COMP</code> &nbsp; <code>ECO</code>
        </div>
        <div class="t-section-title">Function Codes</div>
        <div class="help-grid">${codes}</div>
        <div class="t-section-title">Keyboard Shortcuts</div>
        <div class="help-grid">
          <div class="hg-code"><span class="kbd">/</span></div><div class="hg-desc">Focus command bar</div>
          <div class="hg-code"><span class="kbd">⏎</span></div><div class="hg-desc">Execute command</div>
          <div class="hg-code"><span class="kbd">Esc</span></div><div class="hg-desc">Blur command bar</div>
          <div class="hg-code"><span class="kbd">↑</span> / <span class="kbd">↓</span></div><div class="hg-desc">Command history</div>
          <div class="hg-code"><span class="kbd">⌘1</span>–<span class="kbd">⌘4</span></div><div class="hg-desc">Focus panel N</div>
          <div class="hg-code"><span class="kbd">⌘L</span></div><div class="hg-desc">Cycle layout (1 → 2h → 2v → 4)</div>
          <div class="hg-code"><span class="kbd">F1</span></div><div class="hg-desc">Help (this screen)</div>
          <div class="hg-code"><span class="kbd">F5</span></div><div class="hg-desc">Reload focused panel</div>
        </div>
        <div class="t-section-title">Tips</div>
        <div style="font-size:11px;line-height:1.6;color:var(--text-dim);">
          • Each panel has its own ticker and function. Focus a panel (click or <span class="kbd">⌘1-4</span>) before executing.<br>
          • Use 4-panel layout to monitor multiple tickers at once: <span class="kbd">⌘L</span>.<br>
          • Click any heatmap cell or screener row to drill into that ticker.<br>
          • <code>STAT</code> / <code>CORR</code> / <code>MACRO</code> / <code>GRAPH</code> / <code>MC</code> use pipeline data (TSLA/NVDA/PLTR).<br>
          • Watchlist persists in browser storage.
        </div>
      </div>
    `);
  }
);

// =================================================================
// FUNCTION BAR — clickable shortcuts at top
// =================================================================
function renderFnBar() {
  const codes = ['HELP', 'HEAT', 'EQS', 'N', 'ECO', 'W', 'GAINERS', 'LOSERS', 'CORR', 'MACRO', 'GRAPH', 'EVTS'];
  document.getElementById('fn-bar-codes').innerHTML = codes.map(c => {
    const e = FN[c];
    return `<button class="fn-code-btn" onclick="cmd('${c}')" title="${e ? escapeHTML(e.desc) : ''}"><span class="code">${c}</span><span>${e ? e.desc : ''}</span></button>`;
  }).join('');
}

// =================================================================
// SUGGESTIONS DROPDOWN
// =================================================================
function updateSuggest(raw) {
  const box = document.getElementById('cmd-suggest');
  const v = raw.trim().toUpperCase();
  if (!v) { box.classList.remove('open'); box.innerHTML = ''; return; }
  const matches = Object.values(FN).filter(f => f.code.startsWith(v.split(' ').pop()) || f.desc.toUpperCase().includes(v)).slice(0, 8);
  if (!matches.length) { box.classList.remove('open'); return; }
  box.innerHTML = matches.map(m => `<div class="cmd-suggest-item" onclick="acceptSuggest('${m.code}')"><span class="cmd-suggest-code">${m.code}</span><span class="cmd-suggest-desc">${m.desc}</span></div>`).join('');
  box.classList.add('open');
}
function closeSuggest() {
  const box = document.getElementById('cmd-suggest');
  if (box) { box.classList.remove('open'); box.innerHTML = ''; }
}
window.acceptSuggest = function(code) {
  const input = document.getElementById('cmd-input');
  const parts = (input.value || '').trim().split(/\s+/);
  parts[parts.length - 1] = code;
  input.value = parts.join(' ') + ' ';
  closeSuggest();
  input.focus();
};

// Convenience for inline onclick handlers
window.cmd = function(raw) {
  document.getElementById('cmd-input').value = raw;
  executeCommand();
};

// =================================================================
// STATUS BAR / CLOCK / SESSION
// =================================================================
async function refreshStatus() {
  try {
    const s = await api('/api/market-status');
    const pill = document.getElementById('status-session');
    pill.textContent = s.session;
    pill.className = 'session-pill ' + (s.session === 'OPEN' ? 'open' : (s.session === 'PRE-MKT' ? 'pre' : (s.session === 'AFTER' ? 'after' : 'closed')));
    document.getElementById('status-et').textContent = s.et_time + ' ' + s.weekday;
  } catch (e) { /* keep last value */ }
}
function tickClock() {
  // Best-effort local clock between server-driven updates
  const el = document.getElementById('status-et');
  if (!el) return;
  const parts = el.textContent.split(' ');
  const t = parts[0];
  if (!/^\d{2}:\d{2}:\d{2}$/.test(t)) return;
  const [h, m, s] = t.split(':').map(Number);
  let ns = s + 1, nm = m, nh = h;
  if (ns >= 60) { ns = 0; nm += 1; if (nm >= 60) { nm = 0; nh = (nh + 1) % 24; } }
  el.textContent = `${String(nh).padStart(2,'0')}:${String(nm).padStart(2,'0')}:${String(ns).padStart(2,'0')} ${parts[1] || ''}`;
}

// =================================================================
// AUTO-REFRESH ACTIVE PANELS
// =================================================================
async function autoRefreshPanels() {
  for (let i = 0; i < STATE.panels.length; i++) {
    const p = STATE.panels[i];
    if (!p.fn || !p.ticker || !['GIP', 'DES', 'FA', 'GO', 'Q'].includes(p.fn)) continue;
    try {
      const q = await api(`/api/live-quote/${p.ticker}`);
      const body = document.getElementById(`panel-body-${i}`);
      if (!body) continue;
      const priceEl = body.querySelector('.quote-price');
      const changeEl = body.querySelector('.quote-change');
      if (!priceEl) continue;
      const prevPrice = p.lastPrice;
      priceEl.textContent = fmt.price(q.price);
      priceEl.classList.remove('pos', 'neg', 'flash-up', 'flash-down');
      priceEl.classList.add(q.change_pct >= 0 ? 'pos' : 'neg');
      if (prevPrice != null && q.price > prevPrice) priceEl.classList.add('flash-up');
      else if (prevPrice != null && q.price < prevPrice) priceEl.classList.add('flash-down');
      if (changeEl) {
        const sign = q.change_pct >= 0 ? '+' : '';
        changeEl.className = 'quote-change ' + (q.change_pct >= 0 ? 'pos' : 'neg');
        changeEl.textContent = `${sign}${fmt.num(q.change)} (${sign}${fmt.num(q.change_pct)}%)`;
      }
      p.lastPrice = q.price;
    } catch (e) { /* ignore */ }
  }
}

// =================================================================
// KEYBOARD
// =================================================================
function bindKeys() {
  const input = document.getElementById('cmd-input');
  input.addEventListener('focus', () => document.getElementById('cmd-bar').classList.add('focused'));
  input.addEventListener('blur', () => { document.getElementById('cmd-bar').classList.remove('focused'); setTimeout(closeSuggest, 200); });
  input.addEventListener('input', () => updateSuggest(input.value));
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); executeCommand(); }
    else if (e.key === 'Escape') { input.blur(); }
    else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (STATE.history.length === 0) return;
      STATE.histIdx = Math.min(STATE.histIdx + 1, STATE.history.length - 1);
      input.value = STATE.history[STATE.histIdx] || '';
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      STATE.histIdx = Math.max(STATE.histIdx - 1, -1);
      input.value = STATE.histIdx === -1 ? '' : (STATE.history[STATE.histIdx] || '');
    }
  });

  document.addEventListener('keydown', (e) => {
    const tag = (e.target.tagName || '').toLowerCase();
    const inField = tag === 'input' || tag === 'textarea';
    if (e.key === '/' && !inField) { e.preventDefault(); input.focus(); }
    else if (e.key === 'F1') { e.preventDefault(); cmd('HELP'); }
    else if (e.key === 'F5') { e.preventDefault(); reloadPanel(STATE.focused); }
    else if ((e.metaKey || e.ctrlKey) && /^[1234]$/.test(e.key)) {
      e.preventDefault();
      const i = parseInt(e.key, 10) - 1;
      if (i < STATE.panels.length) { STATE.focused = i; updateFocusedUI(); }
    } else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'l') {
      e.preventDefault();
      const order = ['1', '2h', '2v', '4'];
      const next = order[(order.indexOf(STATE.layout) + 1) % order.length];
      setLayout(next);
    }
  });
}

// =================================================================
// INIT
// =================================================================
document.addEventListener('DOMContentLoaded', async () => {
  renderFnBar();
  ensurePanels();
  renderWorkspace();
  bindKeys();
  // Initial splash: HELP in panel 0
  loadIntoPanel(0, null, 'HELP');
  refreshStatus();
  setInterval(refreshStatus, 30000);
  setInterval(tickClock, 1000);
  setInterval(autoRefreshPanels, 30000);
});
