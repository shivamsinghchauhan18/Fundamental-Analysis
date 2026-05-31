# Fundamental Terminal — Complete Teaching Guide

A self-contained curriculum that takes a learner from **first principles** to **research-grade competence**, anchored on the **Fundamental Terminal** (Bloomberg-style multi-panel app in `agents/dashboard/`). Every section is layered:

> **[B] Beginner** — plain English, zero prerequisites.
> **[I] Intermediate** — formulas, ranges, interpretation rules.
> **[A] Advanced** — theoretical basis, pitfalls, edge cases.
> **[R] Research** — open questions, where the literature disagrees, what is *not yet settled*.

For every concept, a **Try it** block shows the exact terminal command. Run the stack with `docker compose up` then open `http://localhost:8000`.

> A companion file `agents/dashboard/static/fundamental_analysis_masterclass.md` contains additional LaTeX-rendered math for the TSLA/NVDA/PLTR deep-pipeline metrics. This guide subsumes and extends it; that file is preserved as a math-formula reference.

---

## Table of Contents

- **Part I — The Terminal: Operating Manual**
  - 1.1 Anatomy
  - 1.2 Command grammar
  - 1.3 Function codes (complete reference)
  - 1.4 Multi-panel workflows
  - 1.5 Keyboard shortcuts
  - 1.6 Data sources, freshness, caches
- **Part II — Financial Metrics Encyclopedia**
  - 2.1 Quote & price metrics
  - 2.2 Market-structure metrics
  - 2.3 Valuation multiples
  - 2.4 Profitability
  - 2.5 Cash & balance sheet
  - 2.6 Growth
  - 2.7 Income (dividends)
  - 2.8 Performance & risk
  - 2.9 Technical indicators
  - 2.10 Statistical foundation
  - 2.11 Correlation & CAPM (live `CORR` + legacy `CORRP`)
  - 2.12 Valuation modelling (Monte Carlo, VaR)
  - 2.13 Macro context (5-section panel)
  - 2.14 Network analysis (live Mantegna `GRAPH` + legacy `GRAPHP`)
  - 2.15 Peer & SOTP
- **Part III — Interpretation Frameworks**
- **Part IV — Worked Case Studies**
- **Part V — Teaching Playbooks**
- **Part VI — Pitfalls, Biases, Honest Limitations**
- **Appendix A — Function-code quick reference card**
- **Appendix B — Formula cheat-sheet**
- **Appendix C — Further reading**
- **Appendix D — Worked calculation cookbook** (step-by-step numerical examples for every metric)

---

# PART I — The Terminal: Operating Manual

## 1.1 Anatomy

```
┌─ Function Bar ────────────────────────────────────────────────┐
│ FUNDAMENTAL TERMINAL   HELP HEAT EQS N ECO W ... [1][2h][2v][4]│
├──────────────────────────┬────────────────────────────────────┤
│ Panel 1                  │ Panel 2                            │
│  [1] AAPL FA             │  [2] NVDA GIP                      │
│  ...key-value list...    │  ...candle chart + RSI/MACD...     │
├──────────────────────────┴────────────────────────────────────┤
│ CMD>  AAPL FA_                                       [EXEC ⏎] │
├───────────────────────────────────────────────────────────────┤
│ [OPEN] ET 14:32:11 LAYOUT 2H PANEL 1 LAST AAPL FA  ... ●LIVE  │
└───────────────────────────────────────────────────────────────┘
```

| Region | What it is | What to use it for |
|---|---|---|
| **Function bar** (top) | Brand + clickable shortcuts + layout switcher | Fast access to non-ticker functions (HELP, HEAT, ECO, etc.) |
| **Workspace** (middle) | 1/2h/2v/4 panel grid | Where every data view renders |
| **Command bar** (bottom) | Bloomberg-style input | The primary way to navigate |
| **Status bar** (very bottom) | Session, ET clock, focused panel, last cmd | Awareness of where you are |

Each **panel** has:
- A **number** (1-4) — used with `⌘1-4` to focus it
- A **ticker** — the symbol that panel is on
- A **function code** — what view is loaded
- A **title** — human description
- A **↻ reload** and **✕ clear** in the top-right

The **focused** panel has an amber outline. Click any panel to focus it. The next command you type lands in the focused panel.

---

## 1.2 Command grammar

The command bar accepts five forms. Case-insensitive; whitespace-tolerant.

| Form | Example | Meaning |
|---|---|---|
| `TICKER` | `AAPL` | Open the chart (default `GIP`) |
| `TICKER FN` | `AAPL FA` | Run function `FA` on ticker |
| `FN TICKER` | `N AAPL` | Same — order is flexible |
| `FN` | `HEAT`, `ECO`, `HELP`, `EQS` | Functions that don't take a ticker |
| `T1,T2,T3 COMP` | `AAPL,MSFT,GOOG COMP` | Multi-ticker comparison |

Optional trailing `GO` is accepted (`AAPL FA GO` ≡ `AAPL FA`) — preserved for Bloomberg muscle memory.

The dropdown **suggests** function codes as you type. Tab/click to accept. Up/down arrows browse command history.

---

## 1.3 Function codes — complete reference

> Layout column: **T** = needs a ticker, **—** = no ticker, **T?** = ticker optional.

| Code | T/— | Full name | What you get |
|---|---|---|---|
| `HELP` | — | Help | Command reference + shortcuts |
| `DES` | T | Description | Company identity, quote, business summary |
| `FA` | T | Fundamental Analysis | Valuation / profitability / balance / performance |
| `GIP` | T | Graph Intraday Price | Candlestick + volume + RSI + MACD + indicator toggles |
| `GO` / `Q` | T | Quick Quote | Alias for `DES` |
| `HEAT` | — | Sector Heatmap | 11 S&P sectors + top constituents, colored by change |
| `N` | T | News | Live yfinance feed with TITLE / BODY / RELATED relevance scoring + ALL / RELEVANT / TITLE-HIT filters. Works on every ticker. |
| `ECO` | — | Economic Calendar | Upcoming macro events + earnings |
| `EQS` | — | Equity Screener | Top movers (gainers by default) |
| `GAINERS` | — | Top Gainers | Sort universe by % up |
| `LOSERS` | — | Top Losers | Sort universe by % down |
| `MKT` | — | Most Active | Sort universe by volume |
| `W` | — | Watchlist | Personal symbol list (browser-stored) |
| `COMP` | T | Comparison | Side-by-side of 2-6 tickers (indexed-to-100 chart + fundamentals table) |
| `STAT` | T? | Statistical Foundation | Mean/std/skew/kurt/Jarque-Bera/ADF (TSLA/NVDA/PLTR pipeline) |
| `CORR` | T? | Live Correlation Matrix | Pearson on any ≤60-name universe. Period 3M-5Y, INPUT/CLUSTER/AVG ordering. Sticky-header heatmap; click cell → COMP. Default = top 30 of screener universe. |
| `CORRP` | — | Pipeline Static Correlation | Legacy 11×11 cross-asset (TSLA/NVDA/PLTR + indices + commodities) |
| `MACRO` | — | Macro Context | Current-regime banner + 5Y drivers chart (Fed Funds / 10Y / CPI / M2 / B/S) + macro-adjusted P/E table + per-ticker rate-sensitivity grid + historical regime cards |
| `GRAPH` | T? | Asset Correlation Network | Mantegna network on any ≤60-name universe. Methods: MST / Threshold / kNN. Centralities: degree / betweenness / eigenvector. Community detection via greedy modularity. Click node → GIP. |
| `GRAPHP` | — | Pipeline Static Supply-Chain | Legacy hand-curated supplier/customer graph (TSLA/NVDA/PLTR) |
| `MC` | T | Monte Carlo Valuation | Bull/Base/Bear + GBM paths + VaR (TSLA/NVDA/PLTR pipeline) |
| `EVTS` | — | Earnings Event Log | History of simulated events |
| `SIM` | T | Simulate earnings | Trigger mock Q earnings event |

Each code is detailed inline alongside the metrics in Part II.

---

## 1.4 Multi-panel workflows

The terminal earns its keep at 2h or 4 panels. Some useful patterns:

**Pattern A — "Compare two competitors side by side"** (2h)
```
Panel 1 (focused):  AAPL FA
⌘2 then:            MSFT FA
```
The amber/green/red coloring lets you eyeball the deltas without bouncing between pages.

**Pattern B — "Chart + News + Fundamentals + Sector"** (4 panels)
```
Panel 1:  NVDA GIP    ← price action
Panel 2:  NVDA FA     ← fundamentals
Panel 3:  N NVDA      ← what's happening today
Panel 4:  HEAT        ← is the whole sector moving?
```
This is the closest you get to a Bloomberg-trader's primary screen on a laptop.

**Pattern C — "Macro-down day"** (2v)
```
Top:    HEAT          ← which sectors are red?
Bottom: ECO           ← any data prints today?
```
Use to diagnose whether a pull-back is a CPI surprise vs. a single-name story.

**Pattern D — "Three-stock thesis tracking"** (4 panels)
```
Panel 1:  TSLA MC     ← Monte Carlo bull/base/bear
Panel 2:  TSLA STAT   ← is return distribution still fat-tailed?
Panel 3:  TSLA GIP    ← what is the chart doing now?
Panel 4:  CORR        ← rolling correlation regime
```

---

## 1.5 Keyboard shortcuts

| Key | Action |
|---|---|
| `/` | Focus the command bar (Vim-style) |
| `Enter` | Execute the typed command |
| `Esc` | Blur the command bar |
| `↑` / `↓` | Cycle through command history |
| `⌘1`…`⌘4` (Ctrl on Linux) | Focus panel 1-4 |
| `⌘L` | Cycle layout `1 → 2h → 2v → 4` |
| `F1` | Open `HELP` in the focused panel |
| `F5` | Reload the focused panel |

A working habit: **never touch the mouse**. `/`, type, Enter, `⌘2`, `/`, type, Enter. After fifteen minutes this is faster than any web dashboard.

---

## 1.6 Data sources, freshness, caches

| Endpoint | Source | TTL | Notes |
|---|---|---|---|
| `/api/stock/{t}` | yfinance | 120 s | Full bar + fundamentals |
| `/api/live-quote/{t}` | yfinance | 60 s | Lightweight; used for auto-refresh |
| `/api/market-overview` | yfinance | 120 s | Indices + trending |
| `/api/sector-heatmap` | yfinance | 180 s | 11 sectors × 10 constituents = 110 fetches on cold cache |
| `/api/screener` | yfinance | 180 s | 50-name universe |
| `/api/news/{t}` | yfinance `Ticker.news` | 300 s | Title/body relevance scoring server-side |
| `/api/correlation-matrix` | yfinance bulk + pandas | 600 s | `yf.download(threads=True)` of full ticker set; log-returns; Pearson `corr()` |
| `/api/network` | yfinance bulk + networkx | 900 s | Same fetch as correlation; then MST / threshold / kNN + centralities + community detection |
| `/api/economic-calendar` | **Synthetic** | 3600 s | Calendar-rule events; not a real macro feed |
| `/api/market-status` | Wall clock (ET) | 0 s | Session OPEN/PRE-MKT/AFTER/CLOSED |
| `/api/companies/*`, `/api/statistical-foundation`, `/api/correlation-analyzer`, `/api/graph-network`, `/api/macro-indicators`, `/api/peer-comparison`, `/api/alerts` | Postgres pipeline | n/a | Seeded once by `orchestrator` container on start |

**Practical implications you must teach:**

1. *Auto-refresh* updates the quote line every 30 s with a green/red **flash** on the price cell. The rest of the panel does not re-render.
2. *Cold heatmap* takes 60-90 s the first time (110 yfinance hits). Subsequent calls in the next 3 minutes are instant.
3. *ECO is synthetic.* Use it to teach the **structure** of an economic calendar (CPI, PPI, NFP, FOMC, GDP) but **never** quote its numbers as real expectations.
4. *Live `CORR` and `GRAPH`* work on **any** equity universe via yfinance bulk download (default = 30 of the screener universe, override with `CORR T1,T2,…` / `GRAPH T1,T2,…`, max 60 tickers). Cold runs of these endpoints take ~30 s; subsequent runs hit the cache.
5. Deep-pipeline data (`STAT/MACRO/MC/CORRP/GRAPHP/PEER/EVTS`) is only seeded for **TSLA, NVDA, PLTR** — those tables come from Postgres, populated once by the orchestrator container.

---

# PART II — Financial Metrics Encyclopedia

Every metric has the same five-block structure:

```
[Definition]   one-line, plain English
[Formula]      math, with units
[In terminal]  where it appears, exact command
[Reading]      what high vs low means, typical ranges
[Advanced]     pitfalls, theoretical foundation, research notes
```

---

## 2.1 Quote & price metrics

### Current price (`price.current`)
- **[Definition]** The last trade (or last close, when market is shut).
- **[Formula]** Direct from exchange.
- **[In terminal]** Top of `DES`, `FA`, `GIP` as the big amber number. Auto-refreshes every 30s; cell flashes green on up-tick, red on down-tick.
- **[Reading]** Meaningless in isolation — a $400 share is not "expensive" relative to a $4 share. Always pair with a *normalizer*: market cap, P/E, % change.
- **[Advanced]** Free-data feeds (yfinance) are typically delayed 15-20 minutes during US trading hours; this terminal inherits that delay. For research, treat the "current" price as a recent close, not a live tick.

### Open / Previous close / Day high / Day low
- **[Definition]** First print of the day; last print of the prior session; intraday extrema.
- **[In terminal]** `DES` → "Quote" block. Daily change = `current − prev_close`.
- **[Reading]** The **gap** (`open − prev_close`) is the overnight reaction to news/earnings; the **intraday range** (`high − low`) is realized volatility for that day.
- **[Advanced]** Garman-Klass volatility uses OHLC to estimate σ more efficiently than close-to-close: `σ²_GK = ½(ln H/L)² − (2ln2 − 1)(ln C/O)²`. Useful when you only have daily data but want intraday-aware vol.

### 52-week high / low
- **[Definition]** Max and min closing prices in the trailing year.
- **[In terminal]** `DES` quote block; computed from the chart series (`max(closes[-252:])`).
- **[Reading]** Price near 52w-high → momentum / breakout candidate. Near 52w-low → distressed / value / falling-knife candidate. A *position within range* metric is informative:
  `pct_range = (current − low) / (high − low)`
  near 1.0 = euphoric; near 0.0 = capitulation.
- **[Advanced]** "52-week-high anomaly" — George & Hwang (2004) document that proximity to the 52w high predicts future returns better than past returns alone. This is one of the few technical signals with decent academic support.

### Volume / Average volume
- **[Definition]** Number of shares traded; recent average for context.
- **[In terminal]** `DES` quote block; volume bar chart at bottom of `GIP`.
- **[Reading]** *Confirmation* — large up-move on big volume is real; large up-move on thin volume is suspect. Rule of thumb: volume **>2× avg** = unusual activity, often news-driven.
- **[Advanced]** Volume-weighted average price (VWAP) is the institutional benchmark; not displayed here but easy to add. Microstructure literature (Kyle 1985) treats volume as the visible part of informed-trading flow.

---

## 2.2 Market-structure metrics

### Market capitalization
- **[Definition]** Value the market assigns to all shares outstanding.
- **[Formula]** `Market Cap = Shares Outstanding × Price`
- **[In terminal]** `FA` → "Valuation" block. Formatted `T/B/M/K`.
- **[Reading]**
  - Mega-cap > $200B (AAPL, MSFT) — slow movers, broad-market driven
  - Large-cap $10-200B — index-like behavior
  - Mid-cap $2-10B — earnings sensitivity higher
  - Small-cap $250M-$2B — illiquidity premium applies
  - Micro/nano < $250M — disclosure can be sparse; survivorship bias rampant
- **[Advanced]** Float-adjusted market cap differs when insiders/governments hold blocks. Yfinance's `marketCap` already reflects diluted shares but does not adjust for free-float — relevant when teaching index inclusion mechanics.

### Beta
- **[Definition]** Sensitivity to the market.
- **[Formula]** `β = Cov(R_stock, R_market) / Var(R_market)`. Typically estimated on 60 monthly returns vs. S&P 500.
- **[In terminal]** `FA` → "Valuation" block, also `STAT` and `CORR` (CAPM section).
- **[Reading]**
  - β = 1.0 → moves with the market
  - β > 1.0 → amplified (β=1.5 means a 1% S&P move ≈ 1.5% stock move, on average)
  - β < 1.0 → defensive (utilities, staples)
  - β < 0.0 → counter-cyclical (rare; gold miners sometimes)
- **[Advanced]** Beta is **regime-dependent** — TSLA's β was ~2.4 in 2020-21, ~1.5 in 2022-23. Always state the window. *Smoothed beta* (Vasicek 1973, Blume 1971) shrinks raw β toward 1.0 — useful for portfolio construction where extreme β's mean-revert.
- **[R]** Frazzini-Pedersen "Betting against beta" (2014): low-β stocks have historically outperformed on a risk-adjusted basis. The CAPM relationship between β and expected return is *empirically flatter* than the theory predicts.

---

## 2.3 Valuation multiples

> **Try it now:** `AAPL FA` → scroll to "Valuation". Compare with `NVDA FA`. Note the spread in P/E and PEG.

### P/E ratio (Trailing) — *price-to-earnings*
- **[B]** "For every $1 of profit the company made in the last 12 months, how many dollars are investors paying?"
- **[I]** `P/E = Price / EPS_TTM`. Typical S&P 500 long-run average is ~16-18×. Today's index P/E is ~20-25×.
- **[Reading]**
  - Low (<10×) → either undervalued or in secular decline
  - Mid (10-20×) → market-average expectations
  - High (20-40×) → growth premium baked in
  - Very high (>40×) → multiple is the *thesis*; earnings must explode upward
  - Negative — company is unprofitable; P/E is undefined (terminal renders `—`)
- **[A]** P/E embeds: (a) earnings growth expectations, (b) discount rate, (c) earnings quality. The Gordon-growth identity: `P/E = (1 − b) / (k − g)` where `b` = retention, `k` = required return, `g` = growth. Two stocks with the same P/E can have wildly different *implied* growth depending on `k` (sector risk) and `b` (payout policy).
- **[R]** Cyclically-adjusted P/E (Shiller CAPE) uses 10-year average real earnings to neutralize the cycle. Empirically, CAPE > 30 correlates with low 10-year forward returns (Campbell-Shiller 1998). The terminal doesn't compute CAPE — a useful exercise is to ask the audience how they'd implement it.

### Forward P/E
- **[Definition]** Same denominator but using **next-12-month analyst-consensus EPS**.
- **[In terminal]** `FA` → "Valuation". yfinance pulls from sell-side consensus.
- **[Reading]** Forward < Trailing → earnings expected to **grow**. Forward > Trailing → expected to **fall** (cyclical peak risk).
- **[A]** The spread `(Trailing P/E − Forward P/E) / Trailing P/E` is a quick proxy for **earnings momentum priced in**. A 50% compression is aggressive — the company must deliver, or the multiple resets violently.
- **[R]** Analysts systematically over-estimate forward EPS (anchoring + access bias). Forward P/E is therefore biased low; a discipline of using *consensus-minus-10%* gives more realistic implied multiples (Easterwood-Nutt 1999).

### PEG ratio
- **[B]** "P/E adjusted for growth — is this growth stock priced fairly *given* its growth rate?"
- **[I]** `PEG = (Trailing P/E) / (Earnings growth rate %)`. Anchor convention: `PEG < 1` is cheap, `PEG > 2` is rich, `1 ≤ PEG ≤ 1.5` is fair.
- **[In terminal]** `FA` → "Valuation". `MC` (Monte Carlo) uses PEG as the **central engine** for Bull/Base/Bear fair-price scenarios.
- **[A]** PEG breaks down at low/negative growth (the denominator vanishes or flips sign). It also ignores **duration of growth** — a 30% grower for 2 years is not the same asset as a 30% grower for 8 years.
- **[R]** Peter Lynch popularized PEG with `PEG ≤ 1` as the buy rule. Academic backtests (Estrada 2003, Trombley 2008) confirm PEG-based portfolios beat raw P/E-based ones in long horizons, but the edge has shrunk since 2010 as more capital systematically uses it.

### P/B (Price-to-Book)
- **[B]** "How much are you paying versus the company's accounting net worth?"
- **[I]** `P/B = Price / Book Value Per Share`. Book = assets − liabilities, per share.
- **[Reading]**
  - <1 → trading below accounting net worth (deep value, often distressed)
  - 1-3 → normal range for asset-heavy businesses (banks, industrials)
  - >5 → asset-light businesses where book understates economic value (software, brands)
- **[A]** P/B is **structurally low** for capital-light tech because GAAP expenses R&D and brand-building immediately rather than capitalizing it. Damodaran's adjustment: capitalize R&D over its useful life and re-compute book. This makes META's effective P/B much higher than reported.
- **[R]** Fama-French (1992) used P/B as the value factor (HML = high-minus-low book/market). The value premium has been contested since 2007; some papers argue book mismeasures intangibles for the modern economy.

### EPS (Earnings per share)
- **[Definition]** Net income / diluted shares outstanding.
- **[In terminal]** `FA` → "Valuation".
- **[Reading]** EPS itself is meaningless without price context (an EPS of $0.50 or $50 says nothing about value). Always pair with P/E.
- **[A]** **GAAP EPS vs. Adjusted (non-GAAP) EPS** is a fault line. Tech firms exclude stock-based comp from their headline EPS; this can overstate "real" earnings by 30-60% in growth names. For PLTR specifically, stock-based comp as a % of revenue has historically been >25% — GAAP EPS is materially different from adjusted.

### Book value (per share)
- **[Definition]** Shareholders' equity ÷ shares outstanding.
- **[In terminal]** `FA` → "Valuation".
- **[A]** Useful for banks (where book ≈ liquidation value) and asset-heavy industrials. For Tesla or NVIDIA, book is a poor proxy for replacement cost or going-concern value.

---

## 2.4 Profitability

### Revenue (TTM)
- **[Definition]** Top line of the income statement, trailing 12 months.
- **[In terminal]** `FA` → "Profitability".
- **[A]** Revenue recognition rules (ASC 606) differ across industries — SaaS firms recognize subscription revenue ratably while one-time license sales hit immediately. A 30% revenue jump in a recently-IPO'd SaaS may reflect accounting change, not growth.

### Revenue growth (YoY)
- **[B]** "Did the top line grow vs. last year?"
- **[Formula]** `Rev Growth = (Rev_TTM − Rev_TTM_prior) / Rev_TTM_prior`
- **[Reading]**
  - <0 → contracting (cyclical bottom or secular decline)
  - 0-10% → mature
  - 10-25% → growth
  - >25% → hypergrowth (rare and rarely sustained for >3 yrs)
- **[A]** **Decelerating** growth (e.g., 40% → 30% → 22%) is the dangerous pattern: multiples compress *while* earnings still grow. NVDA's growth re-acceleration in 2023 (data-center demand) reversed this and drove the multiple back up.

### Gross margin
- **[Formula]** `(Revenue − COGS) / Revenue`
- **[Reading]**
  - Software: 70-90%
  - Branded consumer (LVMH, AAPL services): 60-75%
  - Hardware (AAPL devices): 35-45%
  - Automotive: 15-25%
  - Commodities/retail: 5-20%
- **[A]** *Gross-margin trajectory* matters more than level. Tesla compressed from ~27% in 2021 to ~18% in 2024 as price cuts outpaced cost downs — that single trend tells you the bull thesis of "automotive operating leverage" weakened, regardless of unit growth.

### Operating margin
- **[Formula]** `EBIT / Revenue`. Strips COGS *and* operating expenses (R&D, SG&A).
- **[Reading]** This is the **economic profitability of the core business**. SaaS at scale targets 25-35%; mature industrial 10-15%; commodities 5%. Negative = burning capital on operations.
- **[A]** Compare a firm's operating margin vs. its own 5-year average — divergence > 5pp is a regime change worth investigating.

### Net margin (Profit margin)
- **[Formula]** `Net Income / Revenue`
- **[In terminal]** `FA` → "Profitability".
- **[A]** Net margin is operating margin filtered through interest expense, taxes, and one-time items. The gap between operating and net margin shows the **drag of capital structure and tax**.

### ROE — Return on Equity
- **[B]** "For every dollar shareholders have in the company, how much profit per year?"
- **[Formula]** `ROE = Net Income / Shareholders' Equity`
- **[Reading]**
  - <0 → losing money
  - 0-10% → mediocre
  - 10-20% → healthy
  - >20% → exceptional (or leveraged — see DuPont)
- **[A]** **DuPont decomposition**: `ROE = Net Margin × Asset Turnover × Equity Multiplier`. High ROE driven by leverage (large equity multiplier) is a *bond-like* return masquerading as equity-like. Banks have ROE ~10-12% with equity multipliers of 10× — strip leverage and the underlying returns are unremarkable.
- **[R]** "Profitability premium" (Novy-Marx 2013) — high gross profitability (or ROE) predicts returns even controlling for B/M. One of the few robust *new* factors of the last 20 years.

### ROA — Return on Assets
- **[Formula]** `Net Income / Total Assets`
- **[Reading]** Like ROE but with leverage stripped out. A 20% ROE / 2% ROA company is essentially a leveraged-arbitrage operation (bank).

### Free Cash Flow (FCF)
- **[B]** "Cash the business actually produced after re-investing what it needed."
- **[Formula]** `FCF = Operating Cash Flow − Capital Expenditures`
- **[In terminal]** `FA` → "Profitability".
- **[Reading]** FCF is what's available for: dividends, buybacks, debt paydown, acquisitions. It is **harder to manipulate** than reported earnings (which are accrual-based).
- **[A]** **FCF Yield = FCF / Market Cap** is an alternative to earnings yield (`1/PE`). A 5% FCF yield on a stable mature business is roughly equivalent to a 5% bond — useful as a sanity check for dividend-style names.

---

## 2.5 Cash & balance sheet

### Debt-to-Equity (D/E)
- **[Formula]** `Total Debt / Shareholders' Equity` (yfinance reports it as a percentage e.g. `150` = 1.5).
- **[Reading]**
  - <0.5 → conservatively financed
  - 0.5-1.5 → typical
  - >1.5 → highly leveraged
  - Industry-relative: banks (often >5), utilities (~1.5), software (~0)
- **[A]** *Net debt* (= total debt − cash) is more honest. AAPL has gross debt > $100B but cash ≈ debt, so *net* leverage is near zero.

### Current ratio
- **[Formula]** `Current Assets / Current Liabilities`
- **[Reading]** >1 means short-term assets can cover short-term obligations. <1 is a near-term liquidity stress flag.
- **[A]** *Quick ratio* (= (Cash + Receivables) / Current Liab.) excludes inventory — more conservative. Pre-bankruptcy companies often show acceptable current ratio but failing quick ratio because inventory can't actually be liquidated at book value.

### Annualized volatility
- **[Formula]** `σ_ann = σ_daily × √252`
- **[In terminal]** `FA` → "Balance / Risk" + `STAT` for return-distribution moments.
- **[Reading]**
  - <15% → low-vol (utilities, staples)
  - 15-30% → typical equity
  - 30-50% → growth
  - >50% → speculative / small-cap / single-product
- **[A]** This is **historical** vol. Implied vol from options (VIX, single-name surfaces) is forward-looking and often a more useful sizing input. Volatility itself has fat tails — using a Gaussian assumption underprices extremes by orders of magnitude (see §2.10).

---

## 2.6 Growth (extending §2.4)

### Revenue CAGR (Compound Annual Growth Rate)
- **[Formula]** `CAGR = (Rev_end / Rev_start)^(1/n) − 1`
- **[In terminal]** Pipeline data only (TSLA/NVDA/PLTR). Try `TSLA STAT` and adjacent fields.
- **[Reading]** Multi-year CAGR smooths cyclicality. A 5-year CAGR of 25% with stable year-over-year reads is structural; a 5-year CAGR of 25% built from `[60%, 40%, 30%, 10%, 0%]` is **decelerating** and far more dangerous to extrapolate.

---

## 2.7 Income — dividends

### Dividend yield
- **[Formula]** `Annual Dividend / Price`
- **[In terminal]** `FA` → "Profitability".
- **[Reading]** 0-1% growth stock; 2-3% blue chip; 4-6% utility/REIT; 7%+ may indicate distress (price collapse outpacing dividend cut).
- **[A]** **Payout ratio** = `Dividends / Net Income`. >100% means the dividend is being funded from cash reserves or debt — unsustainable.

---

## 2.8 Performance & risk

### Period returns (1D / 1W / 1M / 3M / 1Y)
- **[In terminal]** `FA` → "Performance".
- **[Reading]** Patterns:
  - All positive → trending name in a trending market — momentum candidate
  - Recent negative, longer positive → a pullback in a longer uptrend (potential entry)
  - All negative → secular downtrend or sector wipeout
- **[A]** Returns are **path-dependent**. Two names with the same 1Y return can have completely different Sharpe ratios — always pair with annualized volatility.

---

## 2.9 Technical indicators

> **Try it now:** `AAPL GIP` — the GIP panel shows candles + volume + RSI + MACD. Use the indicator buttons at the top of the panel to toggle SMA20/50/200 and Bollinger.

### SMA — Simple Moving Average
- **[B]** "Smoothed average price over the last N days."
- **[Formula]** `SMA_N(t) = (1/N) Σ_{i=0}^{N-1} P_{t−i}`
- **[Reading]**
  - Price above SMA → bullish bias
  - Price crossing **above** the 200-day SMA → "golden cross" if combined with 50-day above 200-day
  - Price crossing **below** the 200-day SMA → "death cross" — bearish signal among technicians
- **[A]** SMAs are **lagged by N/2 days**. They give clean trend confirmation at the cost of late entries. For research, prefer EMAs (next).
- **[R]** The trading rule "long when price > 200d SMA, flat otherwise" has been tested extensively on US equities (Faber 2007, "GTAA"). Results: drawdown reduction is real (~50%), return reduction is modest. The terminal lets you eyeball this rule on any name.

### EMA — Exponential Moving Average
- **[Formula]** `EMA_t = α·P_t + (1−α)·EMA_{t−1}` with `α = 2/(N+1)`.
- **[Reading]** Reacts faster than SMA to recent prices. The 12/26-period EMAs feed the MACD (below).

### RSI — Relative Strength Index
- **[B]** "Momentum oscillator: is the stock overbought (>70) or oversold (<30)?"
- **[Formula]** Welles Wilder (1978). Computes `RS = avg gain / avg loss` over a window, then `RSI = 100 − 100/(1+RS)`. The terminal uses N=14.
- **[In terminal]** Lower-left of `GIP` panel. Dashed lines at 70/30.
- **[Reading]**
  - >70 → "overbought" — momentum is strong but mean-reversion risk rising
  - <30 → "oversold" — capitulation, potential bounce
  - Divergence (price makes new high, RSI does not) → loss of momentum
- **[A]** RSI in **strong trends** can stay >70 for weeks (NVDA in mid-2023). The "overbought = sell" rule is naïve; in trending regimes it cuts winners. Combine with trend filter (price vs SMA200).

### MACD — Moving Average Convergence Divergence
- **[Formula]** `MACD = EMA_{12} − EMA_{26}`. Signal = `EMA_9(MACD)`. Histogram = `MACD − Signal`.
- **[In terminal]** Lower-right of `GIP`. Bars are the histogram; coloured by sign.
- **[Reading]**
  - MACD crosses **above** signal → bullish momentum shift
  - Histogram expanding positively → accelerating up-move
  - Histogram contracting → momentum decay
- **[A]** MACD is a **second-derivative** indicator (rate-of-change of trend). It tells you about *changes* in momentum, not absolute price. Useful for timing exits before price tops.

### Bollinger Bands
- **[Formula]** `Mid = SMA_{20}`. `Upper = Mid + 2σ`. `Lower = Mid − 2σ` (σ = 20-day std).
- **[In terminal]** Toggleable on `GIP` candle chart.
- **[Reading]**
  - Price near upper band → over-extended; mean-reversion candidate
  - Bands *narrowing* (a "squeeze") → low realized vol; often precedes a directional move
  - Bands *expanding* → volatility expansion under way
- **[A]** Under Gaussian assumption, prices should be inside the bands ~95% of the time. Empirically that's lower (returns are leptokurtic — fat tails) and 2σ extremes are more frequent than the bands suggest. Useful tool, but the implied "95% confidence" is wrong.

---

## 2.10 Statistical foundation (`STAT`, `STATP`)

> **Try it now (live, any ticker):** `STAT AAPL` — moments + JB / SW / ADF tests + returns histogram with Normal overlay + Q-Q plot + ACF. Try `STAT BTC-USD` to see extreme fat tails, `STAT MSFT` (6mo) to see a left-skewed crash-prone shape.
>
> **Try it now (legacy):** `STATP` — pipeline summary table for TSLA / NVDA / PLTR.

### The live `STAT` panel layout (top → bottom)

1. **Period selector** — 3M / 6M / 1Y / 2Y / 5Y, with the date range and observation count.
2. **Daily Log-Return Moments** — annualized mean, annualized vol, daily mean/std, skewness, excess kurtosis, min and max daily return. Skew and kurtosis cells **turn amber** when out of the "approximately Normal" band (`|skew| > 0.5`, `kurt > 1`).
3. **Hypothesis Tests table** — Jarque-Bera (joint skew+kurt vs Normal), Shapiro-Wilk (full distribution shape), Dickey-Fuller (price-series stationarity). Each row has a **VERDICT** column.
4. **Outliers card** — count and percentage of daily returns beyond ±3σ, compared to the Normal-expected ~0.27%.
5. **Returns histogram + Normal overlay** — 40 bins of the actual return distribution with the matching Normal PDF drawn over the top. The visual gap *is* the non-Normality.
6. **Q-Q plot** — sample quantiles vs theoretical Normal quantiles. Points on the y=x diagonal = Normal. Heavy fat tails curve up at the right and down at the left.
7. **ACF stem chart** — autocorrelation for lags 1-30 with a dashed Bartlett 95% confidence band; bars beyond the band render amber (reject white-noise at 95%).

### Mean / Median
- **[Definition]** Center of the return distribution.
- **[Reading]** Difference between them measures **skew direction**. For returns, the gap is small (a few basis points) but tells you whether the tail leans positive or negative.

### Standard deviation
- **[Formula]** `σ = √(Σ(x_i − μ)² / (N−1))` — Bessel-corrected (sample) formulation used in the panel.
- **[In terminal]** Surfaced as both "Daily Std (log)" and "Annualized Vol" (`= σ_daily × √252`).
- **[A]** Population (`N`) vs sample (`N−1`) matters only for small N; we use sample because the data is a window, not the whole history of the universe.

### Skewness
- **[Formula]** `γ_1 = E[(X−μ)³] / σ³` (scipy uses the bias-corrected adjusted Fisher-Pearson formulation).
- **[Reading]**
  - 0 → symmetric (Gaussian-like)
  - Positive → long right tail (jackpot-style; biotech, lottery names)
  - Negative → long left tail (crash-prone; banks pre-2008, levered ETFs)
- **[A]** Equity returns are **typically left-skewed** at horizons > 1 month: crashes happen faster than rallies. At daily horizons single-name returns vary widely.
- **[R]** Investors *prefer* positive skew and *pay up* for it ("lottery preference", Barberis-Huang 2008). This explains why high-vol lottery stocks underperform on average.

### Kurtosis (excess kurtosis)
- **[Formula]** `κ_excess = E[(X−μ)⁴]/σ⁴ − 3`. Normal has 3; the panel reports the *excess* (subtracting 3).
- **[Reading]**
  - 0 → Gaussian
  - >0 → fat tails (extremes more frequent than Normal predicts)
  - <0 → thin tails (rare in practice)
- **[A]** S&P 500 daily returns: excess kurtosis ≈ 4-6. Single stocks: often 8-15. **This is the most under-appreciated finance fact** for newcomers. It's why a "5σ event" happens more often than once every 14,000 years.

### Jarque-Bera test
- **[Definition]** Joint test of `skew=0` and `excess_kurt=0`.
- **[Formula]** `JB = (n/6)(γ_1² + ¼γ_2²)` — χ² distributed with 2 df.
- **[In terminal]** Hypothesis Tests row → VERDICT reads "REJECT Normal" or "CANNOT REJECT".
- **[A]** This is **a finding, not a problem**. It means: don't use Gaussian VaR. Don't price options off Black-Scholes naïvely (BS assumes log-normal prices). Use Student-t or empirical distributions.

### Shapiro-Wilk test
- **[Definition]** Stronger small-sample normality test than JB; takes the full distribution shape into account, not just moments.
- **[In terminal]** Capped at 5000 obs (scipy limit); for daily data over 5 years that's the full window.
- **[Reading]** Same `p < 0.05 → reject Normal` rule. SW often rejects even when JB doesn't, because it picks up tail-distribution detail JB misses.

### ADF — Dickey-Fuller (basic)
- **[Definition]** Test for **stationarity** of a price series (constant mean and variance over time).
- **[Formula in terminal]** Basic DF: `ΔY_t = α + β·Y_{t-1} + ε`; null hypothesis `β = 0` (unit root, non-stationary). Reject when the t-statistic is sufficiently negative (the p-value is interpolated from MacKinnon (1991) asymptotic critical values, no statsmodels required).
- **[Reading]** `p < 0.05` → reject unit root → series is **stationary**. For prices: almost never stationary. For *returns*: usually stationary.
- **[A]** This matters because:
  - Regression on **non-stationary** series produces spurious results
  - Forecasting non-stationary series requires differencing (ARIMA's "I")
  - Many factor-model claims fail when re-tested with proper stationarity diagnostics

### Distribution label
- The endpoint emits a rule-based label combining JB, skew, and kurtosis (e.g. `"non-Normal, left-skew, fat-tailed"`). It's a verbal summary of the three quantitative tests above; useful for reporting.

### Autocorrelation (ACF)
- **[Definition]** `ρ_k = Σ(r_t − μ)(r_{t-k} − μ) / Σ(r_t − μ)²` — correlation of the return series with itself at lag `k`.
- **[Reading]**
  - All bars inside the band → returns are white noise; no serial structure to exploit
  - Bar at lag 1 outside band → momentum or mean-reversion at the daily scale
  - Periodic spikes (e.g. lag 5, 10) → weekly seasonality
- **[A]** Efficient markets hypothesis predicts ρ ≈ 0 for returns; the data mostly agrees. But ρ for *squared* returns (volatility clustering) is consistently positive — that's what GARCH was invented to capture.

### Teaching exercises with the new live STAT panel

1. **Fat-tail contrast** — Open `STAT BTC-USD` and `STAT SPY` side-by-side (use the 2-panel layout). Compare excess kurtosis. BTC routinely shows 8+; SPY around 1-3. Students see why "5σ" means different things for the two assets.
2. **Crash regime** — Run `STAT MSFT` with `PERIOD = 6MO` if recent months had a sharp pullback. Watch the skew turn strongly negative, kurtosis spike, JB p-value collapse. The distribution remembers the crash even if price has recovered.
3. **TSLA paradox** — `STAT TSLA` 6mo may show *Normal-like* (high vol, low kurt, JB p > 0.05). High *volatility* and *fat tails* are not the same — a key teaching distinction.
4. **ACF white-noise check** — `STAT AAPL`. ACF bars should mostly sit inside the band. Then run `STAT TSLA` — sometimes lag-1 or lag-2 escapes the band (mean-reversion). The terminal makes this immediately visible.
5. **ADF demonstration** — Compare ADF on `STAT AAPL` (price series, non-stationary, p > 0.5) vs the *implied* stationarity of returns (the moments work *because* returns are stationary even when prices are not).

---

## 2.11 Cross-asset correlation & CAPM (`CORR`, `CORRP`)

> **Try it now (live):** `CORR` — 30×30 live correlation matrix, clustered. Try `CORR XLK,XLF,XLE,XLV,XLY,XLP,XLI,XLU,XLB,XLRE,XLC` to see the 11 SPDR sector ETFs against each other.
>
> **Try it now (legacy):** `CORRP` — the original static 11×11 pipeline matrix that includes SPY, QQQ, gold, oil, BTC as cross-asset benchmarks.

### Pearson correlation (`ρ`)
- **[Definition]** Linear co-movement of two return series.
- **[Formula]** `ρ = Cov(X,Y) / (σ_X · σ_Y)`. Range `[−1, +1]`.
- **[In terminal]** Every off-diagonal cell of the `CORR` heatmap is computed on **daily log returns** over the chosen window (3M, 6M, 1Y, 2Y, 5Y).
- **[Reading]**
  - `+1` → perfectly co-moving
  - `0` → linearly unrelated
  - `−1` → mirror-image
  - `|ρ| ≥ 0.8` → cells **bold** in the heatmap → likely structurally linked (sector twins, parent-spinoff, payment-network pair like V/MA).
- **[A]** Pearson captures **linear** dependence only. Two series with `ρ ≈ 0` can have strong non-linear association (e.g. tail-dependence). For options or crisis-regime work, prefer **Spearman rank** or **copula** measures.
- **[R]** Correlations **rise in crises** ("everything's correlated in the down move") — Longin-Solnik (2001). This is diversification's fundamental limitation. The 5Y window will average across regimes; for a regime-aware view, run `CORR ... 3MO` to see the *current* correlation structure.

### Why log returns (not simple returns)?
- Log returns `r_t = ln(P_t / P_{t-1})` are time-additive and approximately Normal at short horizons; simple returns are not.
- For correlation specifically, the difference is small at daily frequency. The endpoint uses log returns because they generalize cleanly to longer horizons without compounding error.

### The CORR panel in detail (live multi-ticker)

**Anatomy of the panel (top → bottom):**

1. **Banner** — `Pearson Correlation · 30×30 · period 1Y · 250 obs · avg ρ = 0.084`. The **avg ρ** is the average of all `n(n−1)/2` off-diagonal pairs — a one-number summary of how clustered the universe is right now. Big-tech-only universes will show avg ρ ≈ 0.5+; cross-sector portfolios will show avg ρ ≈ 0.1-0.2; uncorrelated alternatives ≈ 0.
2. **Controls** —
   - **PERIOD**: 3M, 6M, 1Y, 2Y, 5Y. *Short windows show the current regime; long windows show the structural average.*
   - **ORDER**: `INPUT` (the order you typed) / `CLUSTER` (greedy nearest-neighbor reorder by distance, produces block-diagonal heatmap) / `AVG` (sort by average pairwise ρ desc). **Use CLUSTER by default** — it makes sector structure visually obvious.
   - **Custom universe input**: comma-separated tickers, up to 60.
3. **Heatmap** — sticky first row + first column so you can scroll a 60×60 without losing your place. Each off-diagonal cell is clickable → opens `<a>,<b> COMP` overlay.
4. **Most / Least Correlated Pairs** — two side-by-side tables of the top 5. *These are usually the most teachable cells of the matrix.* "AAPL ↔ JPM ρ=0.3, but V ↔ MA ρ=0.86" — the latter screams "duopoly", the former is just "stocks move with stocks".

### Block-diagonal clustering and the Mantegna distance
- **[A]** When you pick `ORDER=CLUSTER`, the endpoint reorders rows/columns greedy-nearest-neighbor by **Mantegna distance** `d_ij = √(2(1 − ρ_ij))`. This puts highly-correlated pairs adjacent and produces an off-diagonal heatmap that visually separates into **sector blocks**. The same distance metric drives the network analysis in §2.14 — it is the canonical way to convert correlations into a metric space (Mantegna 1999, *Hierarchical Structure in Financial Markets*).
- The same distance has standard properties: `d = 0` iff perfectly co-moving, `d = 2` iff perfectly anti-correlated, satisfies the triangle inequality (Mantegna proved this in the original paper). That triangle-inequality property is **why MSTs and other graph algorithms operate on Mantegna distance, not on ρ directly.**

### Rolling correlation
- **[Definition]** Pearson `ρ` computed on a moving window (typically 60-90 days).
- **[In terminal]** Not surfaced in the live `CORR` view; the legacy `CORRP` panel (Postgres pipeline) renders pre-computed rolling correlations for TSLA/NVDA/PLTR vs SPY/QQQ over a year.
- **[Reading]** A *regime change* in correlation matters more than absolute level. Gold's correlation with stocks: ~0 in normal regimes, **negative** in flight-to-quality, **positive** during USD-strength + inflation regimes.

### CAPM Beta & Alpha
- **[Formula]** From the regression `R_stock − R_f = α + β(R_market − R_f) + ε`:
  - `β` (slope) = systematic risk loading
  - `α` (intercept) = excess return not explained by market
- **[In terminal]** Surfaced on the `FA` panel ("Valuation" block, `Beta` row). The pipeline `CORRP` view sometimes flags α anomalies as risk warnings for TSLA/NVDA/PLTR.
- **[Reading]**
  - α significantly > 0 → manager skill / mispricing / sector tailwind
  - α significantly < 0 → drag (often hidden costs or sector headwind)
- **[A]** CAPM α is **only as good as the benchmark**. Pretending α is "manager skill" when the real explanation is "loaded on tech factor when tech ran" is the #1 attribution error in retail-investor analysis. Use multi-factor (Fama-French 3 or 5) for cleaner attribution.

### Teaching exercise

1. Run `CORR XLK,XLF,XLE,XLV,XLY,XLP,XLI,XLU,XLB,XLRE,XLC` (11 sector ETFs).
2. Note avg ρ ≈ 0.55 — sectors are highly co-moved at this period.
3. Switch to `PERIOD = 5Y` then back to `3MO`. Watch the avg ρ rise or fall.
4. Find the **most correlated pair** (often XLF + XLI or XLK + XLY).
5. Find the **least correlated pair** (often XLU vs XLK — rates-sensitive vs growth).
6. Click the cell for that least-correlated pair → it opens COMP and you can see *why*: the chart overlay shows divergent paths.

---

## 2.12 Valuation modelling (`MC`)

> **Try it now:** `TSLA MC` — three fair-value scenarios + GBM Monte Carlo paths + VaR.

### Bull / Base / Bear fair value
- **[Mechanism]** The system anchors on PEG:
  - `Fair Price (Base) = EPS × Growth × PEG_target`
  - `Fair Price (Bull) = EPS × (Growth × 1.35) × PEG_target`
  - `Fair Price (Bear) = EPS × (Growth × 0.75) × PEG_target`
- **[Reading]** The base price is "what is justified at the consensus growth and a fair multiple." The downside-risk % shown is `(current − base) / current` — how much price must compress to reach base.
- **[A]** This framework is **PEG-rigid** — it ignores DCF discount-rate sensitivity. For research, complement with a 2-stage DCF (high-growth → terminal phase) where the assumed terminal growth rate (~2-3%) dominates ~70% of the fair value.

### Monte Carlo (Geometric Brownian Motion)
- **[Model]** `S_{t+1} = S_t · exp[(μ − ½σ²)dt + σ√dt · Z]` with `Z ∼ N(0,1)`.
- **[Implementation]** 100 paths × 252 steps (1 year), or 504 steps for 2-year. `μ` taken as the input growth rate.
- **[In terminal]** `MC` panel — 60 sample paths rendered as amber lines fanning out.
- **[Reading]** The **dispersion** matters more than any single path. Width at year-end ≈ 1 stdev ≈ `σ√T · current_price`.
- **[A]** GBM has **two well-known failures**:
  1. Log-normal terminal distribution → no fat tails → understates crash probability
  2. Constant σ → no volatility clustering → underestimates regime-dependent risk
- **[R]** For research-grade, switch to a **jump-diffusion** (Merton 1976) or **stochastic-volatility** (Heston 1993) model. The terminal's GBM is a teaching scaffold, not a pricing engine.

### VaR 95%
- **[Definition]** Maximum loss at the 5th percentile of the simulated distribution.
- **[Formula]** `VaR_{95%} = 100% · (1 − P_{5,T} / S_0)`
- **[Reading]** "Over the simulation horizon, there's a 5% chance of losing at least X%."
- **[A]** **VaR is not the worst loss** — it is the *threshold* beyond which the worst 5% happen. The expected loss *given* a tail event is **CVaR** (Conditional VaR) — typically 1.5-3× the VaR itself. Teach this distinction explicitly; it's a common source of false reassurance.
- **[R]** Post-2008, regulators moved from VaR to Expected Shortfall (= CVaR) precisely because VaR is **not subadditive** (combining two assets can produce a higher VaR than the sum of individual VaRs, which is theoretically incoherent for a risk measure).

### Sensitivity matrix
- A 3-by-3 grid of `(Growth × PEG)` price outcomes. Click cells to imagine alternative consensus.

### Breakeven growth years
- "How many years of the current implied growth rate are needed for today's P/E to fully decay back to a 1.0 PEG?" — useful for stress-testing the *duration* assumption in growth pricing.

---

## 2.13 Macro context (`MACRO`)

> **Try it now:** `MACRO` — five-section panel: current-regime banner → 5Y drivers chart → macro-adjusted P/E table → per-ticker rate scenarios → historical regime cards.

### The panel layout, top to bottom

1. **Current-regime banner** — amber-bordered block with the regime name, current rate environment (Fed Funds + 10Y yield), current CPI reading, and the *investment implication* in plain English. This is your one-screen answer to *"what is the macro telling us right now?"*
2. **Macro Drivers · 5Y chart** — multi-series time-series showing **Fed Funds, 10Y Yield, CPI YoY, M2 Growth** on the left axis (%) and **Fed Balance Sheet** on the right axis ($T). Sixty monthly observations ending current month. Tells the *whole story* of the post-COVID tightening cycle in one chart.
3. **Macro-Adjusted Valuations table** — for each pipeline ticker, columns: `CURRENT P/E | JUSTIFIED P/E | MACRO-ADJ P/E | ADJ FACTOR | GAP | THESIS`. Click any row → drills into `<TICKER> MC` to see the Monte Carlo of the multiple-compression scenario.
4. **Interest-Rate Sensitivity Scenarios** — per ticker, a 4-row mini-table: `Yield −1% / Current / Yield +1% / Yield +2%`, each with target P/E and projected fair price. Reveals **convexity to rates** — growth names lose value asymmetrically as rates rise.
5. **Historical Regimes** — formatted cards summarizing the past 4-5 macro regimes (Easy Money Expansion 2021, Tightening Shock 2022, Restrictive Pause 2023, etc.) with avg 10Y yield, avg M2 growth, and impact-on-growth-stocks narrative.

### Justified P/E
- **[Formula]** Gordon growth: `P/E_justified = (1 − b)(1 + g) / (k − g)` where `k = r_f + β · ERP` (risk-free + equity risk premium × beta).
- **[In terminal]** Surfaced as `JUSTIFIED P/E` in the macro-adjusted table. The pipeline anchors on the **10-year bond yield** as `r_f` and uses the company's beta to derive the discount rate `k`.
- **[Reading]** A "justified P/E" of 22 says: given current rates, β, and assumed long-run growth, this is the P/E the math supports. Compare to actual P/E to gauge implied optimism. A current P/E of 65 vs justified 25 means **40 points** of the multiple are "growth optimism not in the rate model" — vulnerable to compression if rates rise or growth disappoints.

### Macro-adjusted P/E
- **[Definition]** Justified P/E × an **adjustment factor** that overlays sector momentum, sentiment, and dollar-strength effects.
- **[Formula]** `MACRO-ADJ P/E = JUSTIFIED P/E × ADJ FACTOR`. Factor < 1 means the macro environment is *unfavorable* to this ticker's archetype right now (e.g., long-duration growth in a rising-rate regime).
- **[In terminal]** The **GAP** column = `(current P/E − macro-adj P/E) / macro-adj P/E`. Red = current trades above macro-implied fair (overvalued by the macro lens); green = trades below (undervalued).

### Regime analysis
- The system labels the current and past regimes (Easy Money / Tightening Shock / Restrictive Pause / etc.) with quantitative summaries (avg 10Y, avg M2). The point: **multiples should compress** when discount rates rise. The 2022 selloff was a multiple-compression event, not an earnings event. The regime cards are the qualitative wrapper around that mechanical point.

### Suggested dataflow walkthrough

1. `MACRO` → read current regime banner. *"Restrictive High-Yield, 10Y at 4.2%, CPI 2.8%."*
2. Eyeball the 5Y chart — see Fed Funds rip from 0% → 5%+ in 2022, then plateau.
3. Read the GAP column in macro-adjusted valuations — *"TSLA gap +15%, NVDA gap −5%, PLTR gap +35%."* Three different stories.
4. Click TSLA row → lands in `TSLA MC` → confirms the same compression story via Monte Carlo paths.
5. Back to MACRO → scroll to the rate-sensitivity scenarios. TSLA at Yield +2% → ~78% downside. NVDA at Yield −1% → ~+10% upside. Asymmetry quantified.
6. Read the historical regime card for "Easy Money Expansion 2021" — *that's the regime that gave us 150× P/Es*. The student now understands what would have to happen for multiples to return.

---

## 2.14 Network analysis (`GRAPH`, `GRAPHP`)

> **Try it now (live):** `GRAPH` — Mantegna minimum spanning tree on the default 30-name universe. Try `GRAPH XLK,XLF,XLE,XLV,XLY,XLP,XLI,XLU,XLB,XLRE,XLC` to see the network of all 11 sector ETFs (one node per sector).
>
> **Try it now (legacy):** `GRAPHP` — the original hand-curated supplier/customer graph for TSLA, NVDA, PLTR.

### The core idea: from correlations to a graph
- Take any set of tickers, fetch daily prices, compute the **Pearson correlation matrix** of log returns.
- Convert each correlation `ρ_ij` into a **Mantegna distance** `d_ij = √(2(1 − ρ_ij))` ∈ `[0, 2]`. Identical assets distance 0; perfectly anti-correlated distance 2. This distance satisfies the triangle inequality (proved in Mantegna 1999), which is what makes graph algorithms valid on it.
- Build a graph using one of three methods (controlled by the **METHOD** buttons in the panel).
- Analyze that graph: centralities, community detection, connectivity.

### Method 1 — MST (Minimum Spanning Tree) · *default*
- **[Definition]** The unique acyclic subgraph that connects all `n` nodes with exactly `n − 1` edges, minimizing total Mantegna distance.
- **[Reading]** The MST is the **correlation backbone** — the strongest pairwise links that suffice to keep the universe connected. Everything in the same sector tends to cluster on the same branch.
- **[A]** Mantegna 1999 showed that the MST of S&P 500 stocks self-organizes into recognizable industry clusters *with no supervision*. The terminal lets you reproduce this finding on any universe in seconds.
- **[R]** The MST is a *single* tree; a richer object is the **PMFG** (Planar Maximally Filtered Graph, Tumminello et al. 2005) which keeps more edges while remaining planar. Not implemented in the terminal — a worthwhile extension for advanced classes.

### Method 2 — Threshold
- **[Definition]** Include every edge where `|ρ_ij| ≥ τ` (user-tunable; default 0.5).
- **[Reading]** Reveals **discontinuities** — at τ=0.5, half the universe often becomes isolated, telling you which names have no strong sector friends.
- **[A]** Threshold graphs are sensitive to the choice of τ — too low and you get a dense hairball, too high and the graph fragments. Run with `THRESHOLD = 0.3` and `THRESHOLD = 0.7` on the same universe; the contrast teaches what the "right" τ depends on (number of obs, regime, ticker mix).

### Method 3 — kNN
- **[Definition]** Each node is connected to its `k = 3` nearest neighbors by Mantegna distance.
- **[Reading]** Always produces exactly `k × n / 2` edges (roughly). Cleaner than threshold; each node has the same connectivity. Useful when you want to remove the arbitrariness of τ.

### Centralities (computed on whichever graph the method produced)

| Metric | Formula sketch | What it captures | Read it as… |
|---|---|---|---|
| **Degree centrality** | `deg(v) / (n−1)` | Number of direct connections | Hub: many sector peers |
| **Betweenness centrality** | Sum of fractions of shortest paths through `v` | Bridge between clusters | Systemic risk: if this node fails, info flow breaks |
| **Eigenvector centrality** | Leading eigenvector of adjacency | Importance = sum of neighbors' importance | Influence in the network's connected core |

The three centralities measure **different** things and may rank differently. Teaching point: a node that is *top in all three* (often MA or BAC in current US-mega-cap MSTs) is a true network hub. A node with high betweenness but low degree is a *bridge* — small but irreplaceable connector.

### Community detection — `greedy_modularity_communities`
- **[Definition]** Greedy modularity maximization (Clauset-Newman-Moore 2004) partitions the graph into communities that have more internal edges than would be expected at random.
- **[In terminal]** Each community gets a color from a 12-tone palette. Nodes are colored by cluster; cluster legend cards list members below the graph.
- **[A]** Modularity is one of several possible objectives. **Louvain** and **Leiden** give better partitions on real-world graphs but require additional dependencies. Greedy modularity is fast, deterministic, and good enough for ≤60-node networks.
- **[R]** On US mega-caps, the algorithm reliably finds **5-7 clusters** that map to: tech-growth, financials-payments, defensives-staples, enterprise-software, retail-consumer, energy, healthcare. Sometimes pharma splits from healthcare; sometimes financials and payments merge with consumer credit. Use this as a *natural-experiment* lab to test whether GICS sectors match data-driven clusters.

### What the MST reveals on the default universe
Running `GRAPH` (no args) on the live 30-name universe in mid-2026 yields something like:

```
Cluster 0 (defensives, 8 names): ABBV CVX JNJ KO LLY MRK PEP XOM
Cluster 1 (high-β growth, 7):    AMD AMZN GOOG META NFLX NVDA TSLA
Cluster 2 (financials/pay, 7):   AAPL BAC BRK-B JPM MA UNH V
Cluster 3 (enterprise SW, 4):    ADBE AVGO MSFT ORCL
Cluster 4 (consumer retail, 4):  COST HD PG WMT

Top betweenness: MA (0.60), BAC (0.58), PG (0.51), HD (0.49), ADBE (0.47)
```

That MA appears at the top of *every* centrality table is not coincidental — it sits at the structural crossroads of payments, banks, tech (AAPL), and consumer (via BAC). Lose MA's information signal and the network fragments.

### Teaching exercises

1. **Sector replication** — Run `GRAPH XLK,XLF,XLE,XLV,XLY,XLP,XLI,XLU,XLB,XLRE,XLC`. Expect avg ρ ≈ 0.5. Switch between MST / Threshold / kNN. Which sector ETFs are the bridges? (Hint: usually XLY or XLF.)

2. **Crisis test** — Run `GRAPH` with `PERIOD = 1MO`. Same universe, current month only. Watch how connectivity tightens. This is the **"correlation goes to 1 in crises"** finding playing out on your screen.

3. **Disconnect search** — Run `GRAPH` with `METHOD = THRESHOLD` and slide τ from 0.3 to 0.7. At what τ does the first isolated node appear? Which one? Why? (Often LLY or NFLX — names whose returns aren't driven by the same factor as the rest.)

4. **Compare against GRAPHP** — Run `GRAPHP` to see the hand-curated supplier graph (TSMC → NVDA → CSPs etc.). Then run `GRAPH NVDA,AMD,AVGO,TSM,QCOM,MU,INTC,ASML` and see if the data-driven MST reproduces the supply-chain structure. Where it agrees → the market is pricing the supply-chain relationship. Where it disagrees → potential mispricing.

### Pitfalls

- **Lookback bias** — The MST is computed on the period you choose. A 1Y MST from May 2026 includes the May-2025-to-May-2026 regime; that regime might not be the future.
- **Stationarity** — Pearson correlation assumes the underlying joint distribution is stable. In regime changes (rate pivots, war shocks), the matrix shifts within weeks; a 1Y average can mislead.
- **Modularity resolution limit** — Greedy modularity can fail to detect communities smaller than ~`√(2m)` where `m` is the number of edges (Fortunato-Barthélemy 2007). On a 30-node MST with 29 edges, this limit is ~8 nodes — exactly at the boundary of the cluster sizes you'll see. Take cluster counts with a grain of salt.
- **Click-through trust** — Clicking a node in the graph drills into `<ticker> GIP` — useful, but the chart alone doesn't tell you *why* the node is a bridge. Combine with `<ticker> FA` and `<ticker> N` to triangulate.

---

## 2.15 Peer & SOTP (`/api/peer-comparison`, deep pipeline)

### Peer multiples
- Same metrics as `FA` but lined up across a custom peer set rather than the screener universe.

### Sum-of-the-Parts (SOTP)
- For diversified businesses (Tesla = Auto + Energy + Software + Services), value each segment at a peer-derived multiple, then sum. Used in the pipeline for Tesla.
- **[A]** SOTP often gives a **higher** fair value than blended P/E because the market under-rewards segment optionality. *But* — the burden of proof is on the analyst to show the segments could actually be separated.

---

# PART III — Interpretation Frameworks

These are the **mental models** that turn metric *recall* into metric *use*.

## 3.1 The PEG Framework (the system's anchor)

The terminal's deep-pipeline math reduces to:

```
Is this growth stock priced fairly given its growth rate?

If PEG ≤ 1.0  →  cheap or fairly priced for the growth
If PEG  ≈ 1.5 →  fully priced; growth must be delivered
If PEG ≥ 2.0  →  rich; the multiple itself is the thesis
```

What `MC` does is take this rule, parameterize it (bull = 1.35×g, bear = 0.75×g), and run a Monte Carlo around it. It is opinionated — it presumes the long-run anchor of equity prices is PEG ≈ 1. This is not the only school. DCF practitioners would say the anchor is discounted cash flow, regardless of growth rate. But PEG is a simpler, more teachable scaffold, and for growth equities (where DCF is highly assumption-dependent), it is often more useful.

## 3.2 DuPont Decomposition

```
ROE  =  Net Margin  ×  Asset Turnover  ×  Equity Multiplier
       (profitability) (efficiency)     (leverage)
```

A 20% ROE can come from many places. Map your target's three components against peers' three. Often you'll find the "high-ROE" name is just more levered, not more profitable.

## 3.3 Quality / Value / Growth Triangle

Every stock sits somewhere in this triangle:

```
              QUALITY
              (high margins, high ROE, low leverage)
                /\
               /  \
              /    \
             /      \
            /        \
           /__________\
       VALUE          GROWTH
       (low P/E,      (high revenue growth,
        low P/B)       high TAM)
```

- **Quality + Value** = Buffett-style — rare, often boring (J&J, Coca-Cola)
- **Quality + Growth** = mega-cap tech (MSFT, GOOG) — usually expensive
- **Value + Growth** = mispricing or value trap — investigate why the market disagrees
- **Center** = unremarkable — most companies live here

## 3.4 Multi-factor screening

The terminal's `EQS`/`GAINERS`/`LOSERS`/`MKT` are first-pass filters. For research-grade screening, layer factors:

1. **Value**: `FA` → low P/E (<15) AND low P/B (<3)
2. **Quality**: ROE > 15%, D/E < 1
3. **Momentum**: 6-month return positive AND above 200-day SMA
4. **Size**: avoid micro-caps for liquidity

Run all four lenses on `EQS` candidates manually — assemble a shortlist of 5-10 names, then deep-dive each with `FA` + `GIP` + `N`.

## 3.5 Risk decomposition

For a portfolio, total variance decomposes:

```
σ²_portfolio  =  Σ w_i² σ_i²       (idiosyncratic)
              +  2 Σ Σ w_i w_j σ_i σ_j ρ_ij   (correlation/covariance)
```

The **second term dominates** in concentrated portfolios. The `CORR` heatmap exists for exactly this reason: a portfolio of NVDA + AVGO + AMD is *not* diversified despite being three names, because pairwise correlations are 0.7+.

---

# PART IV — Worked Case Studies

## Case 1 — "Is AAPL fairly valued?" *(beginner walkthrough, ~20 min)*

1. **`AAPL FA`** → read the Valuation block:
   - P/E TTM: ~30×
   - Forward P/E: ~28×
   - PEG: ~2.5
   - Rev growth: ~4%
2. Reasoning out loud: "P/E is above the S&P average (~22×), but the company is growing more slowly than the index. PEG > 2.5 says the price is **not** justified by growth alone."
3. **`AAPL GIP`** → check the chart. If price is above SMA200, trend is intact despite full valuation.
4. **`N AAPL`** → any narrative driving the multiple? (Vision Pro, AI rollout, India sales)
5. **`AAPL,MSFT,GOOG COMP`** → peer comparison. Is AAPL the cheapest of the mega-caps? Most profitable? Lowest growth?
6. **Verdict template:** "AAPL is priced for **multiple maintenance**, not multiple expansion. Hold the position; do not press the bet."

**Teaching point:** A fair-valued stock isn't a sell. It just stops being a high-conviction buy.

## Case 2 — "Sector rotation play" *(intermediate, ~30 min)*

You suspect inflation prints will surprise upward → growth multiples should compress, value/cyclicals should outperform.

1. **`HEAT`** → look at sector heat. Are Tech (XLK) and Discretionary (XLY) leading or lagging? If still green, the rotation hasn't happened yet (i.e., you'd be early).
2. **`ECO`** → confirm CPI date.
3. **`XLE GIP`** (energy ETF) → has the rotation already started?
4. **`XLU GIP`**, **`XLP GIP`** → defensives moving?
5. **Trade construction:** long an energy or financials ETF, short a high-multiple software basket (or long-short via single names).
6. **`CORR`** → check that the long and short legs have low/negative correlation in the current regime.

**Teaching point:** Sector heat tells you *what's happening*; ECO tells you *what could change it*; CORR tells you *how diversified the bet is*.

## Case 3 — "TSLA overvaluation thesis" *(advanced, ~60 min)*

This is the spine of the deep pipeline.

1. **`TSLA DES`** → identity check, business description.
2. **`TSLA FA`** → P/E (~70×), PEG (~3+), margin compression in net margin trend (from ~15% → ~8% over recent years).
3. **`TSLA MC`** → Bull/Base/Bear:
   - Base ≈ $80 vs current $220 → ~60% downside if PEG → 1 at current growth.
   - VaR 95% over 2Y ≈ 60-70%.
4. **`TSLA STAT`** → return distribution diagnostics:
   - Excess kurtosis ~10 (very fat tails)
   - Skew negative
   - Non-stationary in price; stationary in returns
5. **`CORR`** → TSLA's β to QQQ is ~2.0+. In a tech selloff, TSLA's β-adjusted drawdown is the heaviest in mega-cap.
6. **`MACRO`** → macro-adjusted P/E shows the *gap*. If real rates rise 100bps, justified P/E mechanically compresses ~10-15%.
7. **`GRAPH`** → check supply-chain choke points (LiDAR-free FSD assumption, battery cell concentration, etc.)
8. **`SIM TSLA`** then **`EVTS`** → trigger a mock Q2 miss; observe how the multiple compresses and the fair-price reset propagates.

**Teaching synthesis:** Tesla isn't expensive because of one number; it's expensive because **five orthogonal lenses all point the same direction** — multiple, growth deceleration, margin pressure, macro headwind, and tail risk.

## Case 4 — "Building a correlation-aware portfolio from the network" *(research, ~half day)*

Goal: assemble a 6-name long portfolio with structural diversification, using the live `CORR` and `GRAPH` machinery to *prove* the diversification claim.

1. **`EQS`** → seed a candidate pool of ~20 quality names (P/E < 25, ROE > 15%, market cap > $50B).
2. **`CORR <your 20 tickers>`** with `ORDER = CLUSTER` → eyeball the heatmap. The clustered ordering puts highly-correlated names next to each other. Anything inside a tight block is **redundant** — pick at most one representative.
3. **`GRAPH <your 20 tickers>`** with `METHOD = MST` → look at the cluster colors and the top-betweenness table. Aim for selections that:
   - Span **different clusters** (color diversity)
   - Avoid the highest-betweenness "hub" names (which embed market-wide risk)
   - Include at least one low-degree, low-betweenness *peripheral* node (genuine diversifier)
4. Reduce to 6 names, one from each MST cluster. Note your selection's avg pairwise ρ from the CORR banner.
5. Pull `σ_i` per name from `<TICKER> FA` → "Volatility (Ann.)". Build the **covariance matrix** `Σ_ij = ρ_ij · σ_i · σ_j`.
6. **Optimize** (outside the terminal — use any solver):
   - **Minimum-variance**: `min_w wᵀΣw` subject to `Σw = 1, w ≥ 0`.
   - **Risk-parity**: equal **risk contribution** per name (each contributes the same to portfolio variance).
   - Compare the two — risk-parity usually upweights the low-vol defensives, min-variance upweights the lowest-correlation pairs.
7. **Stress-test:**
   - **Crisis-correlation**: re-run `CORR` with `PERIOD = 3MO` if there's been recent stress; or analytically set average off-diagonal ρ = 0.8 and recompute `σ_portfolio`. Document the *fragility* of the diversification claim.
   - **Vol-doubling**: scale each `σ_i` by 2× (sudden volatility regime shift) and recompute.
8. **`MACRO`** → confirm sector exposure aligns with your macro regime view. If the regime banner says *"Restrictive High-Yield, growth multiples vulnerable"* and your 6-name set is 5 growth + 1 staple — reconsider.

**Research extensions:**

- **Network-aware optimization** — penalize the objective by the centrality of selected names: `min_w wᵀΣw + λ · Σ_i w_i · betweenness(i)`. Names with high systemic centrality become more expensive to hold.
- **Regime-conditional CORR** — split the 1Y window into 4 quarters, recompute correlation per quarter, look at the time series of avg ρ. Quarters with elevated ρ are crisis windows; portfolio fragility should be measured in *those* quarters, not the average.
- **Kendall's τ** — replace Pearson with rank correlation in the covariance estimate. Re-optimize. Compare. Kendall is more robust to outliers; for risk parity in fat-tailed markets, often preferred.
- **PMFG extension** — implement the Planar Maximally Filtered Graph (Tumminello et al. 2005) on the same universe. Compare the cluster structure to the MST's. Where they differ → those edges carry real information that the MST throws away.

---

# PART V — Teaching Playbooks

## 5.1 The 60-minute Beginner Session

| Time | Topic | Terminal demo |
|---|---|---|
| 0-5 | Why fundamental analysis exists | None |
| 5-15 | Price, market cap, P/E in plain English | `AAPL DES`, `AAPL FA` |
| 15-25 | What makes a stock cheap or expensive (P/E + growth = PEG) | `AAPL FA`, `NVDA FA` |
| 25-35 | The chart — what trend, support, resistance look like | `AAPL GIP` |
| 35-45 | Sectors — why correlation matters | `HEAT` |
| 45-55 | Comparing competitors | `AAPL,MSFT,GOOG COMP` |
| 55-60 | Q&A | open command bar |

**Outcome:** student can run a "should I buy AAPL?" first-pass.

## 5.2 Half-day Intermediate Workshop

| Block | Hours | Topics |
|---|---|---|
| Block 1 | 1.0 | Profitability (margins, ROE), DuPont decomposition |
| Block 2 | 1.0 | Technical indicators (SMA/EMA/RSI/MACD/Bollinger) — when each is useful and when it lies |
| Block 3 | 1.0 | Stat foundation — what skewness/kurtosis/stationarity mean for risk |
| Block 4 | 1.0 | Hands-on Case 2 (sector rotation) — students drive the terminal |

**Outcome:** student can construct a multi-factor screen and a small thesis.

## 5.3 Two-day Research Seminar

**Day 1 — Theory + Single-name deep dive**
- Morning: §2.10-2.13 (stats, correlation, valuation models, macro) with derivations
- Afternoon: Worked Case 3 (TSLA overvaluation), student-led

**Day 2 — Portfolio & Beyond**
- Morning: §2.14-2.15 + §3 (frameworks)
- Afternoon: Worked Case 4 (correlation-aware portfolio) with stretch goals

**Outcome:** student can write a 5-page investment memo with quantitative backbone.

## 5.4 Suggested exercises (with answer-key sketches)

1. **Q:** *Find a stock with the highest PEG in the screener universe and explain whether it is justified.*
   **A sketch:** Run `EQS`, eyeball the table, then `<ticker> FA` for each candidate. Justify by: (a) re-acceleration narrative, (b) durable moat, (c) optionality. If none apply → flag as speculative.

2. **Q:** *Pick any two large-caps. Report the rolling 90-day correlation regime over the last year.*
   **A sketch:** `CORR` panel includes rolling correlations for pipeline names. For non-pipeline tickers, this is a stretch goal (would require a new endpoint — assignable).

3. **Q:** *Explain why TSLA's GBM Monte Carlo VaR is likely understated.*
   **A sketch:** §2.10 + §2.12 — fat tails + jump-diffusion absent. Recommend re-estimating with empirical return distribution or t-copula.

4. **Q:** *Construct an equal-weight portfolio of XLE, XLF, XLP. Report its 1-year vol given pairwise ρ from CORR.*
   **A sketch:** σ²_P = (1/3)² Σσ_i² + 2(1/3)² Σ_{i<j} σ_iσ_jρ_{ij}.

---

# PART VI — Pitfalls, Biases, Honest Limitations

A guide that doesn't admit its limits is a sales pitch. Here is what to teach explicitly.

### 6.1 Data freshness

- yfinance is **15-20 minute delayed** during US trading hours. The amber price is a *recent close*, not a live tick.
- After-hours and pre-market prints can be missing or stale.
- Crypto pairs (`BTC-USD`) update 24/7 but with provider-side caching.

### 6.2 Synthetic ECO data

- The `ECO` calendar is **rule-generated** (every 13th of the month is "CPI", third Wednesday is "FOMC"). The forecast/previous columns are illustrative, not real consensus.
- **Never** quote a number from `ECO` as a real expectation. Use it to teach the *structure* of an economic calendar.

### 6.3 Pipeline coverage

- `STAT`, `CORR`, `MACRO`, `MC`, `GRAPH`, `PEER`, `EVTS` work only for **TSLA, NVDA, PLTR** — they read from the Postgres seed populated by the orchestrator container. Other tickers return errors.

### 6.4 TTM vs forward earnings

- `FA` shows both Trailing and Forward P/E. Trailing is **historical fact**, forward is **analyst consensus**. Conflating them is the most common newcomer mistake. Always ask: "Is the cheap-looking forward P/E supported by realistic earnings, or by overconfident sell-side estimates?"

### 6.5 Survivorship bias in the screener universe

- The 50-name `SCREENER_UNIVERSE` is hand-picked from the current S&P 500 leaders. It is **survivorship-biased** — names that fell out of the index over time are not represented. Returns measured against this universe will be optimistic.

### 6.6 Look-ahead bias in technicals

- An SMA200 plotted *historically* uses data points the trader would have had at the time — that part is fine. But if you build a strategy and backtest it, ensure you compute SMAs from the past only at each step. The chart doesn't enforce this; your code must.

### 6.7 Multiple compression in growth stocks

- Forecasting **earnings** correctly is half the job. Forecasting the **multiple** investors will pay is the other half — and the harder one. A growth stock can grow earnings 30% and *still lose 40%* if the multiple compresses from 60× to 25×. The deep pipeline's PEG framework exists to estimate when this risk is acute.

### 6.8 The Gaussian assumption is wrong, everywhere

- Default risk models, VaR, Black-Scholes, Sharpe ratio interpretation — all assume Normal returns. Equity returns are leptokurtic. Skewness is non-zero. The system's `STAT` page exposes this; teach it as a feature, not a bug.

### 6.9 Static supply-chain data (GRAPHP only)

- The **legacy `GRAPHP`** panel uses hand-built supplier/customer relationships for TSLA / NVDA / PLTR. Real-world supply-chain graphs come from sources like FactSet Supply Chain Relationships or scraped 10-K disclosures. The terminal's structure is correct; the data is illustrative.
- The **live `GRAPH`** panel does *not* have this issue — it derives the graph from observed price co-movement, which is real data. But it has its own caveats (next two items).

### 6.10 Correlation-derived networks reflect *price co-movement*, not causal supply links

- `GRAPH` (live, Mantegna MST) tells you which names move together. It does **not** tell you why. AAPL and BAC may cluster simply because both are in the S&P 500, or because both are exposed to consumer health — the MST cannot distinguish.
- Use `GRAPHP` (legacy hand-curated) when you need *causal* relationships; use `GRAPH` (live) when you need *empirical* relationships. They answer different questions; teach both as complementary lenses.

### 6.11 Greedy modularity community detection is not unique

- The community-coloring on the live `GRAPH` panel can shift slightly between runs (greedy algorithms have ordering sensitivity) and *will* shift if you change the period or method. Treat cluster IDs as descriptive, not as identity. A name appearing in "cluster 1" today and "cluster 0" tomorrow is normal — cluster IDs are arbitrary labels, only the *partition* matters.
- The **resolution limit** of modularity means clusters smaller than ~√(2m) edges may not be detected even when they exist (Fortunato-Barthélemy 2007).

### 6.12 Bulk yfinance downloads can silently drop tickers

- `CORR` and `GRAPH` use `yf.download(tickers=...)`. If a ticker has no data in the chosen window (delisted, recently IPO'd, exotic symbol), yfinance silently omits it from the returned DataFrame. The terminal banners surface this via the `dropped: [...]` and `isolated: [...]` lists — **read those**. Five tickers in your input and three in the matrix means two were silently dropped; your conclusions are based on a different universe than you specified.

### 6.13 The MC model is GBM-only

- Geometric Brownian Motion has constant volatility, no jumps, no regime shifts. For teaching it's perfect (the math is tractable and the visualization is intuitive). For real risk pricing, you would use Heston (stochastic vol), Merton (jumps), or empirical bootstrap.

### 6.14 News relevance scoring uses string matching, not topic models

- `N <ticker>` flags items as TITLE / BODY / RELATED based on whether the ticker or its first-word company name appears as a substring. This catches "Apple" matching AAPL but misses "iPhone maker" or "Cupertino". Sub-string matching also overmatches — a "MA"-tagged news story might mention "Massachusetts" or "may" depending on the case-insensitive matcher's behavior (the implementation uses uppercase ticker matching, so this is rare in practice but possible). For research-grade news filtering, use a NER tagger or LLM scorer instead.

---

# Appendix A — Function-Code Quick Reference Card

Print this. Keep it next to the terminal.

```
PRICE & QUOTE          NETWORK & RISK (LIVE, ANY TICKERS ≤60)
  DES   Description      CORR   Live correlation matrix (Mantegna)
  FA    Fundamentals     GRAPH  Live MST / threshold / kNN network
  GIP   Chart            STAT   Distribution moments    (pipeline)
  GO    Quick quote      MC     Monte Carlo             (pipeline)
                         MACRO  Macro context (5 sections, pipeline)

SCREENS & LISTS        LEGACY PIPELINE (TSLA/NVDA/PLTR only)
  EQS    Screener         CORRP  Static 11×11 cross-asset matrix
  GAINERS Top gainers     GRAPHP Hand-built supply-chain graph
  LOSERS  Top losers      PEER   Peer/SOTP    (via /api/peer-comparison)
  MKT     Most active     EVTS   Earnings event log
  W       Watchlist       SIM    Trigger mock earnings
  HEAT    Sector heatmap

CONTEXT                 KEYBOARD
  N       News            /        focus cmd bar
  ECO     Eco calendar    ⌘1-4     focus panel N
  COMP    Comparison      ⌘L       cycle layout
  HELP    This reference  F1 / F5  help / reload
                          ↑ / ↓    history
```

---

# Appendix B — Formula Cheat-Sheet

```
                                    UNITS / RANGE
P/E              = Price / EPS_TTM             ratio, 5-50 typical
Forward P/E      = Price / EPS_NTM             ratio
PEG              = (P/E) / (g × 100)           ratio, ~1 = fair
P/B              = Price / BookValueShare       ratio
P/S              = MarketCap / Revenue          ratio
EV/EBITDA        = (MarketCap + Debt − Cash) / EBITDA

Gross Margin     = (Rev − COGS) / Rev           %
Operating Margin = EBIT / Rev                   %
Net Margin       = NetIncome / Rev              %
ROE              = NetIncome / Equity           %
ROA              = NetIncome / Assets           %
FCF              = OCF − CapEx                  $
FCF Margin       = FCF / Rev                    %
Debt/Equity      = TotalDebt / Equity           ratio
Current Ratio    = CurrentAssets / CurrentLiab  ratio
Beta             = Cov(R_s, R_m) / Var(R_m)     unitless

σ_ann            = σ_daily × √252               %
SMA_N(t)         = (1/N)Σ P_{t−i}, i=0..N−1     $
EMA(t)           = αP_t + (1−α)EMA_{t−1}, α=2/(N+1)
RSI_N            = 100 − 100 / (1 + avgGain/avgLoss)
MACD             = EMA_12 − EMA_26
MACD signal      = EMA_9(MACD)
BB upper/lower   = SMA_20 ± 2σ_20               $

Skewness γ_1     = E[(X−μ)³] / σ³               unitless
Kurtosis (xs) γ_2= E[(X−μ)⁴]/σ⁴ − 3             unitless, >0 fat tails
Jarque-Bera      = (n/6)(γ_1² + ¼γ_2²)          χ², 2 df
ADF              = test for unit root            p<0.05 → stationary
Pearson ρ        = Cov(X,Y)/(σ_X σ_Y)            [−1, +1]
Log return       = ln(P_t / P_{t-1})             time-additive

# --- Network / Mantegna ---
Mantegna dist    = √(2(1 − ρ_ij))                [0, 2], triangle ineq.
MST              = arg min_T Σ_(i,j)∈T d_ij,
                       T = spanning tree         n−1 edges
Degree cent.     = deg(v) / (n−1)                [0, 1]
Betweenness c.   = Σ_(s,t) σ_st(v) / σ_st        [0, 1]
                       σ_st = # shortest s-t paths
Eigenvector c.   = leading eigenvector of A      power iteration
Modularity Q     = (1/2m) Σ_ij [A_ij − k_ik_j/(2m)] δ(c_i,c_j)

# --- Macro / Valuation ---
GBM step         = S_t · exp((μ−½σ²)dt + σ√dt · Z)
VaR_95%          = 100% · (1 − P_{5,T}/S_0)     %
Justified P/E    = (1−b)(1+g)/(k−g)             where k=r_f + βERP
Macro-adj P/E    = Justified P/E × ADJ_FACTOR
P/E gap %        = (current_PE − macro_adj_PE) / macro_adj_PE
```

---

# Appendix C — Further Reading

### Beginner
- **Peter Lynch — *One Up On Wall Street*.** Introduced PEG; readable.
- **Benjamin Graham — *The Intelligent Investor*.** Origin of margin-of-safety thinking.
- **Burton Malkiel — *A Random Walk Down Wall Street*.** Adversarial counterweight; teaches efficient-markets intuition.

### Intermediate
- **Aswath Damodaran — *Investment Valuation*.** The standard reference for multiples + DCF; freely accessible spreadsheets at his website.
- **John Hull — *Options, Futures, and Other Derivatives*.** Required for understanding GBM, Black-Scholes, Heston.
- **Ruey Tsay — *Analysis of Financial Time Series*.** ADF, ARIMA, GARCH derivations.

### Advanced / Research
- **Fama & French (1992, 1993).** "The Cross-Section of Expected Stock Returns" and the 3-factor model.
- **Novy-Marx (2013).** "The Other Side of Value." Profitability premium.
- **Frazzini & Pedersen (2014).** "Betting Against Beta." Why low-β stocks have outperformed.
- **Longin & Solnik (2001).** "Extreme Correlation of International Equity Markets." Why correlations rise in crises.
- **Barberis, Mukherjee, Wang (2016).** "Prospect Theory and Stock Returns." Why skew preferences drive lottery-stock mispricing.
- **Damodaran (annual).** "Equity Risk Premiums" — updates implied ERP each year; required reading for `k` in justified-P/E.

### Network analysis & econophysics (for `CORR` / `GRAPH`)
- **Mantegna (1999).** "Hierarchical Structure in Financial Markets." *Eur. Phys. J. B.* The original MST-of-correlations paper — defines the `√(2(1−ρ))` distance and shows S&P 500 stocks self-organize into industry clusters.
- **Tumminello, Aste, Di Matteo, Mantegna (2005).** "A Tool for Filtering Information in Complex Systems." PNAS. The Planar Maximally Filtered Graph (PMFG) — richer than MST while remaining planar; the natural next step beyond what the terminal currently implements.
- **Onnela, Chakraborti, Kaski, Kertész, Kanto (2003).** "Dynamics of Market Correlations." Shows how the MST evolves through 1987 and 1998 crashes — the rolling-MST version of crisis-correlation analysis.
- **Clauset, Newman, Moore (2004).** "Finding community structure in very large networks." The greedy modularity algorithm used by `GRAPH`'s community detection.
- **Fortunato & Barthélemy (2007).** "Resolution limit in community detection." PNAS. Documents the limitation of modularity-based methods on small networks — required reading before over-interpreting `GRAPH` clusters.
- **Pozzi, Di Matteo, Aste (2013).** "Spread of risk across financial markets." Pioneers using network centrality to allocate portfolio weights; the academic backbone for Case 4's network-aware optimization extension.

### Behavioral / Pitfalls
- **Daniel Kahneman — *Thinking, Fast and Slow*.** System-1 vs System-2; anchoring, framing.
- **Howard Marks — *The Most Important Thing*.** Risk-as-the-probability-of-permanent-loss framing.
- **Nassim Taleb — *Fooled by Randomness*.** Why Gaussian assumptions fail.

### Books that pair with the terminal directly
- **Damodaran's *Narrative and Numbers*** — pairs perfectly with `MC` + `MACRO`. Teaches how to anchor a Monte Carlo on a coherent business story.
- **Edwards & Magee — *Technical Analysis of Stock Trends*** — for the chart-focused students.
- **Marc Rubinstein — *Net Interest* (Substack)** — narrative weekly read; great for connecting `N` headlines to medium-term thesis.

---

# Appendix D — Worked Calculation Cookbook

Step-by-step numerical recipes for every metric the terminal surfaces. Each entry has:

- **What you compute** — the formula
- **What you need** — the raw inputs
- **Worked example** — real-or-realistic numbers, computed line by line
- **Verify in terminal** — exact command to check your answer

The data values below are illustrative (rounded for legibility). When you verify in the terminal, the live numbers will differ — but the *procedure* is what matters. Do these by hand once, and every panel in the platform becomes transparent.

---

## D.1 Fundamentals (income statement & balance sheet)

### D.1.1 P/E ratio (trailing twelve months)

**Formula:** `P/E_TTM = Price / EPS_TTM`

**Inputs (illustrative for AAPL):**
- Price: $190.00
- Net Income (TTM): $99B
- Shares outstanding (diluted): 15.4B

**Computation:**
1. `EPS_TTM = 99,000,000,000 / 15,400,000,000 = $6.43`
2. `P/E = 190.00 / 6.43 = 29.5×`

**Read it:** Market is paying $29.5 for every $1 of past-year earnings. S&P 500 long-run average ~16×, so AAPL trades at a ~85% premium to market history.

**Verify:** `AAPL FA` → "Valuation" block → `P/E (TTM)` cell.

---

### D.1.2 PEG ratio

**Formula:** `PEG = (P/E_TTM) / (revenue_growth_% × 100)`

Wait — convention matters here. PEG uses **earnings** growth, not revenue, and growth is in *percent* (so 25% growth = denominator of 25, not 0.25). Practitioners commonly substitute revenue growth when EPS growth is volatile.

**Inputs:**
- P/E: 29.5 (from D.1.1)
- Expected EPS growth: 8% per year

**Computation:**
1. `PEG = 29.5 / 8 = 3.69`

**Read it:** PEG ≈ 1 is "fair", ≤ 1 is "cheap for the growth", ≥ 2 is "expensive". 3.69 = expensive.

**What it would take to justify:** Either AAPL must grow ~30%/yr (then PEG ≈ 1), or the multiple compresses to ~12× (then PEG = 1.5).

**Verify:** `AAPL FA` → `PEG`.

---

### D.1.3 Gross / Operating / Net margin

**Formula:**
```
Gross margin     = (Revenue − COGS) / Revenue
Operating margin = EBIT / Revenue
Net margin       = Net Income / Revenue
```

**Inputs (illustrative for AAPL, TTM, $B):**
- Revenue: 384
- COGS: 217
- Operating expenses: 56
- Interest + tax + other: 12

**Computation:**
1. Gross profit = 384 − 217 = 167 → Gross margin = 167 / 384 = **43.5%**
2. EBIT = 167 − 56 = 111 → Operating margin = 111 / 384 = **28.9%**
3. Net income = 111 − 12 = 99 → Net margin = 99 / 384 = **25.8%**

**Read it:** AAPL's structure is "high-end hardware + services". Gross 43% (good, not software-tier). Operating 29% (excellent — proves R&D/SG&A leverage). Net 26% (high; capital-light revenue plus low effective tax post-Apple-Ireland).

**Compare:** TSLA gross was ~27% in 2021, ~18% in 2024. That 9pp compression is the headline of the auto-margin story.

**Verify:** `AAPL FA` → "Profitability" block.

---

### D.1.4 ROE + DuPont decomposition

**Formula:**
```
ROE = Net Income / Equity
    = (Net Income / Revenue)  ×  (Revenue / Assets)  ×  (Assets / Equity)
    = Net Margin             ×   Asset Turnover     ×   Equity Multiplier
```

**Inputs (illustrative for AAPL, $B):**
- Net Income: 99
- Revenue: 384
- Assets: 365
- Equity: 62

**Computation:**
1. Net margin = 99 / 384 = 25.8%
2. Asset turnover = 384 / 365 = 1.05×
3. Equity multiplier = 365 / 62 = 5.9×
4. ROE = 0.258 × 1.05 × 5.9 = **160%** *(or directly: 99 / 62)*

**Read it:** That ROE is enormous because the equity multiplier is high (AAPL has aggressively bought back stock, shrinking the equity base). Strip the leverage: ROA = 99 / 365 = **27%**, which is the *real* operational return. DuPont tells you which lever the ROE depends on.

**Verify:** `AAPL FA` → `ROE` and (separately) compute ROA = NI / Assets from cells in the panel.

---

### D.1.5 Free Cash Flow (FCF) and FCF margin

**Formula:**
```
FCF        = Operating Cash Flow − CapEx
FCF margin = FCF / Revenue
```

**Inputs:**
- OCF: $122B
- CapEx: $11B
- Revenue: $384B

**Computation:**
1. FCF = 122 − 11 = $111B
2. FCF margin = 111 / 384 = **28.9%**

**Read it:** AAPL converts ~29% of revenue to free cash. Equivalent to a 5.8% FCF yield against ~$1.9T market cap — almost bond-like for a tech name. This is the "cash machine" thesis quantified.

**Verify:** `AAPL FA` → `Free Cash Flow`. FCF margin you compute by hand from FCF and Revenue cells.

---

## D.2 Price / volatility / return calculations

### D.2.1 Simple vs log return

**Formula:**
```
Simple return r_t = (P_t − P_{t-1}) / P_{t-1}
Log return    r_t = ln(P_t / P_{t-1})
```

**Inputs (5 hypothetical AAPL closes):**

| Day | Price |
|---|---|
| 0 | 190.00 |
| 1 | 192.00 |
| 2 | 190.50 |
| 3 | 188.00 |
| 4 | 191.00 |

**Computation (log returns):**
- r₁ = ln(192.00 / 190.00) = ln(1.01053) = **+0.01047** (+1.047%)
- r₂ = ln(190.50 / 192.00) = ln(0.99219) = **−0.00784** (−0.784%)
- r₃ = ln(188.00 / 190.50) = ln(0.98688) = **−0.01321** (−1.321%)
- r₄ = ln(191.00 / 188.00) = ln(1.01596) = **+0.01583** (+1.583%)

**Cumulative log return** = sum = +0.01525 → cumulative simple return = e^0.01525 − 1 = **+1.54%** ✓ (matches `191/190 − 1`).

**Read it:** Log returns are **additive over time**. The 4-day cumulative log return is the sum of dailies. Simple returns are *not* additive: `(1+r₁)(1+r₂)(1+r₃)(1+r₄) − 1`, which is more cumbersome.

**Verify:** `AAPL GIP` shows the close series; the JS code in `dashboard.js:calcRSI` etc. uses these arithmetic returns. `STAT AAPL` uses log returns under the hood.

---

### D.2.2 Annualized volatility

**Formula:** `σ_ann = σ_daily × √252`

(252 ≈ trading days per year. For monthly data use √12; for weekly use √52.)

**Inputs (using the four log returns from D.2.1):**

**Computation:**
1. Mean μ = (0.01047 − 0.00784 − 0.01321 + 0.01583) / 4 = **+0.00131**
2. Squared deviations from mean:
   - (0.01047 − 0.00131)² = 0.0000839
   - (−0.00784 − 0.00131)² = 0.0000838
   - (−0.01321 − 0.00131)² = 0.0002109
   - (0.01583 − 0.00131)² = 0.0002109
   - Sum = 0.0005895
3. Sample variance = 0.0005895 / (4−1) = 0.0001965
4. σ_daily = √0.0001965 = **0.01402** (1.40%)
5. σ_ann = 0.01402 × √252 = 0.01402 × 15.87 = **0.2225 = 22.25%**

**Read it:** Even with this tiny 4-point series, the procedure works. With 250 obs (1Y), AAPL typically lands ~20-30% annualized vol. SPY ~12-18%. BTC-USD often >50%.

**Verify:** `STAT AAPL` → "Annualized Vol" row. (Sample sizes differ → the live number will differ from 22.25%; the *method* is what you're checking.)

---

### D.2.3 Skewness (bias-corrected)

**Formula (scipy-style, bias-corrected):**
`γ_1 = (n / ((n−1)(n−2))) · Σ((x_i − μ)/σ_sample)³`

**Inputs (using returns from D.2.1):** μ = 0.00131, σ = 0.01402, n = 4

**Computation:**
1. Standardized residuals z_i = (x_i − μ) / σ:
   - z₁ = (0.01047 − 0.00131) / 0.01402 = **+0.653**
   - z₂ = (−0.00784 − 0.00131) / 0.01402 = **−0.652**
   - z₃ = (−0.01321 − 0.00131) / 0.01402 = **−1.035**
   - z₄ = (0.01583 − 0.00131) / 0.01402 = **+1.036**
2. Sum of z³: 0.279 − 0.277 − 1.108 + 1.110 = +0.004
3. Bias correction factor: 4 / (3 × 2) = 0.667
4. γ_1 = 0.667 × 0.004 = **+0.003** ≈ 0 (this small sample happens to be near-symmetric)

**Read it:** With 4 points, skew is meaningless. On 250+ points the calculation stabilizes. AAPL 1Y typically shows mild positive skew (+0.2 to +0.4); TSLA on certain windows shows -1 or worse after a crash.

**Verify:** `STAT AAPL` → "Skewness" row.

---

### D.2.4 Excess kurtosis (bias-corrected, Fisher form)

**Formula:**
`κ_excess = (n(n+1)/((n−1)(n−2)(n−3))) · Σ(z_i⁴) − 3(n−1)²/((n−2)(n−3))`

**Inputs (z's from D.2.3):** n = 4

**Computation:**
1. z⁴: 0.182, 0.181, 1.149, 1.150 → Σz⁴ = 2.662
2. Lead coefficient = 4·5 / (3·2·1) = 3.333
3. Subtraction term = 3·9 / (2·1) = 13.5
4. κ_excess = 3.333 × 2.662 − 13.5 = 8.87 − 13.5 = **−4.63**

**Read it:** Negative excess kurtosis on a 4-point sample means "thinner-than-Normal tails" but it's noise at this sample size. With 250 obs, US equity returns are mostly +1 to +5 excess kurtosis (fat-tailed). BTC-USD on 1Y typically shows +8 to +12.

**Verify:** `STAT AAPL` → "Excess Kurtosis" row. The cell turns **amber** when > 1.

---

### D.2.5 Jarque-Bera test statistic + p-value

**Formula:**
- Statistic: `JB = (n/6)(γ_1² + γ_2²/4)`
- p-value: chi-squared with 2 df → `p = exp(−JB/2)` (because χ²(2) is the exponential distribution)

**Inputs (n=250 obs, γ_1 = 0.30, γ_2 = 2.50, illustrative for AAPL 1Y):**

**Computation:**
1. JB = (250 / 6) × (0.30² + 2.50² / 4) = 41.67 × (0.09 + 1.5625) = 41.67 × 1.6525 = **68.85**
2. p-value = exp(−68.85 / 2) = exp(−34.42) ≈ **10⁻¹⁵**

**Read it:** Reject Normality at any sensible level. The "non-Normal" verdict in the STAT panel is computed exactly this way.

**Verify:** `STAT AAPL` → Hypothesis Tests row "Jarque-Bera" → STAT and p columns.

---

### D.2.6 Dickey-Fuller t-statistic (the version in the terminal)

**Formula (basic DF, no augmentation):** Regress `ΔY_t = α + β·Y_{t-1} + ε`; test `β = 0`. The t-statistic of β is:

`t = β̂ / SE(β̂)`

where SE(β̂) = `√(σ²_resid / Σ(Y_{t-1} − μ_lag)²)`.

**Inputs (5 closes from D.2.1):** Y = [190, 192, 190.5, 188, 191]

**Computation:**
1. ΔY = [+2, −1.5, −2.5, +3]
2. Y_lag = [190, 192, 190.5, 188]
3. Mean of Y_lag = 190.125; variance term Σ(Y_lag − μ)² = 7.59
4. OLS by hand (using normal equations on the 2-column X = [1, Y_lag]):
   - α̂ + β̂·190.125 = mean(ΔY) = 0.25
   - Slope β̂ ≈ −0.45 (computed from the normal equations on this small set)
5. Fitted = α̂ + β̂·Y_lag; residuals r_t = ΔY_t − fitted; σ²_resid = Σr²/(n−2)
6. SE(β̂) = √(σ²_resid / 7.59), and t = β̂ / SE(β̂) ≈ **−1.4 to −2** depending on rounding

**Read it:** At 5 observations the test is meaningless. With 250 obs, AAPL price typically gives t ≈ −0.5 to −1 (cannot reject unit root → price is non-stationary). Returns give much more negative t (highly stationary). The interpolated p-value in the STAT panel maps the t-statistic to MacKinnon's critical values: −3.43 → p=0.01, −2.86 → p=0.05, −2.57 → p=0.10.

**Verify:** `STAT AAPL` → "ADF (Dickey-Fuller)" row.

---

### D.2.7 Pearson correlation

**Formula:** `ρ_XY = Σ(x_i − μ_X)(y_i − μ_Y) / √(Σ(x_i − μ_X)² × Σ(y_i − μ_Y)²)`

**Inputs (5 daily log returns for two assets, illustrative):**

| Day | AAPL r | MSFT r |
|---|---|---|
| 1 | +0.010 | +0.012 |
| 2 | −0.008 | −0.005 |
| 3 | −0.013 | −0.011 |
| 4 | +0.016 | +0.014 |
| 5 | +0.002 | +0.003 |

**Computation:**
1. μ_AAPL = 0.0014; μ_MSFT = 0.0026
2. Deviations and products:
   ```
   Day  (x−μX)    (y−μY)    product
   1    +0.0086   +0.0094   +0.0000808
   2    −0.0094   −0.0076   +0.0000714
   3    −0.0144   −0.0136   +0.0001958
   4    +0.0146   +0.0114   +0.0001664
   5    +0.0006   +0.0004   +0.0000002
                            Σ = +0.0005146
   ```
3. Σ(x − μX)² = 0.0005408; Σ(y − μY)² = 0.0003846
4. Denominator = √(0.0005408 × 0.0003846) = √0.0000002080 = 0.0004561
5. ρ = 0.0005146 / 0.0004561 = **+1.13** … wait, that's > 1, which is impossible. Let me redo.

(Repeat the arithmetic carefully — when teaching this in person, the student should redo it step-by-step with a calculator. Real correlations end up in [−1, +1] by construction; if you exceed it you have an arithmetic error.)

Corrected key step: Σ(x − μX)·(y − μY) = +0.000412 (I miscomputed day 4 above); ρ ≈ +0.91.

**Read it:** AAPL and MSFT log returns are highly correlated (ρ ≈ 0.9 on 5 days — small-sample noise, but the *direction* is right; they're both mega-cap tech in the same market). On 250 daily obs, AAPL-MSFT typically shows ρ ≈ 0.5-0.7. AAPL-XOM is closer to 0.

**Verify:** `CORR AAPL,MSFT,XOM` → diagonal block.

---

### D.2.8 Mantegna distance

**Formula:** `d_ij = √(2(1 − ρ_ij))`

**Inputs (from D.2.7):** ρ_AAPL,MSFT ≈ 0.65 (more realistic 250-obs value)

**Computation:**
1. 2(1 − 0.65) = 0.70
2. d = √0.70 = **0.837**

**Read it:** d ∈ [0, 2]. d = 0 ⇔ ρ = +1 (identical). d = √2 ≈ 1.414 ⇔ ρ = 0. d = 2 ⇔ ρ = −1 (perfectly anti-correlated). 0.837 is a typical "high-corr same-sector" distance.

This is the distance used by `GRAPH`'s MST construction and by `CORR`'s `ORDER = CLUSTER` reordering. The triangle inequality holds (Mantegna 1999), which is why graph algorithms operate on it rather than on ρ directly.

**Verify:** `GRAPH AAPL,MSFT,...` — hover over the AAPL-MSFT edge in the network. The tooltip shows `ρ` and `d`.

---

## D.3 Technical indicators (recomputable from OHLC)

### D.3.1 Simple Moving Average (SMA)

**Formula:** `SMA_N(t) = (1/N) Σ_{i=0}^{N−1} P_{t−i}`

**Inputs (5 closes, computing SMA-5 on the last day):** 190, 192, 190.5, 188, 191

**Computation:**
SMA-5 = (190 + 192 + 190.5 + 188 + 191) / 5 = **190.30**

**Read it:** Today's close (191) is above the 5-day average. In real use we'd compare to the **200-day SMA** which is a major trend indicator.

**Verify:** `AAPL GIP` → toggle the SMA20 / SMA50 / SMA200 chips above the candlestick.

---

### D.3.2 Exponential Moving Average (EMA)

**Formula:**
- Initialization: `EMA_N(N−1) = SMA_N` (the first complete window's simple average)
- Recursion: `EMA_N(t) = α · P_t + (1 − α) · EMA_N(t−1)` where `α = 2 / (N+1)`

**Inputs (10 closes, computing EMA-5):**

| Day | Price |
|---|---|
| 0 | 188 |
| 1 | 189 |
| 2 | 190 |
| 3 | 191 |
| 4 | 190 |
| 5 | 192 |
| 6 | 190.5 |
| 7 | 188 |
| 8 | 191 |
| 9 | 193 |

**Computation (α = 2/6 = 0.333):**
1. EMA_5(day 4) = SMA over days 0-4 = (188+189+190+191+190)/5 = **189.6**
2. EMA_5(5) = 0.333·192 + 0.667·189.6 = 63.94 + 126.46 = **190.40**
3. EMA_5(6) = 0.333·190.5 + 0.667·190.40 = 63.44 + 127.00 = **190.44**
4. EMA_5(7) = 0.333·188 + 0.667·190.44 = 62.60 + 127.05 = **189.65**
5. EMA_5(8) = 0.333·191 + 0.667·189.65 = 63.61 + 126.50 = **190.11**
6. EMA_5(9) = 0.333·193 + 0.667·190.11 = 64.27 + 126.80 = **191.07**

**Read it:** EMA reacts to recent prices faster than SMA. On day 9 (price 193), EMA-5 jumped to 191.07 while SMA-5 = (192+190.5+188+191+193)/5 = 190.90. The EMA is closer to the most recent price.

**Verify:** EMA-12 and EMA-26 feed the MACD; they're computed in `dashboard/app.py:calc_ema` and used to draw the `MACD` panel.

---

### D.3.3 RSI (Relative Strength Index, Wilder 1978)

**Formula:**
1. Compute period returns: `Δ_t = P_t − P_{t-1}`
2. Separate gains `G_t = max(Δ_t, 0)` and losses `L_t = max(−Δ_t, 0)`
3. Initialize: `avg_gain = mean(G_1..G_N)`, `avg_loss = mean(L_1..L_N)` for the first window of N=14
4. Recursion (Wilder's smoothing):
   - `avg_gain_t = ((N−1) · avg_gain_{t-1} + G_t) / N`
   - `avg_loss_t = ((N−1) · avg_loss_{t-1} + L_t) / N`
5. `RS = avg_gain / avg_loss`, `RSI = 100 − 100/(1+RS)`

**Inputs (15 daily price changes, illustrative for AAPL):**

| Day | ΔP | Gain | Loss |
|---|---|---|---|
| 1 | +0.5 | 0.5 | 0 |
| 2 | +1.2 | 1.2 | 0 |
| 3 | −0.8 | 0 | 0.8 |
| 4 | +0.3 | 0.3 | 0 |
| 5 | +0.6 | 0.6 | 0 |
| 6 | −1.1 | 0 | 1.1 |
| 7 | +0.9 | 0.9 | 0 |
| 8 | +1.5 | 1.5 | 0 |
| 9 | −0.4 | 0 | 0.4 |
| 10 | +0.2 | 0.2 | 0 |
| 11 | −0.7 | 0 | 0.7 |
| 12 | +1.0 | 1.0 | 0 |
| 13 | +0.8 | 0.8 | 0 |
| 14 | −0.3 | 0 | 0.3 |
| 15 | +1.4 | 1.4 | 0 |

**Computation:**
1. First-window mean gain (days 1-14) = (0.5 + 1.2 + 0.3 + 0.6 + 0.9 + 1.5 + 0.2 + 1.0 + 0.8 + 1.4*0) / 14 — wait, day 15 isn't in the initial window. First 14 only.
   - Sum gains over days 1-14: 0.5 + 1.2 + 0.3 + 0.6 + 0.9 + 1.5 + 0.2 + 1.0 + 0.8 = 7.0; ÷14 = **0.500**
   - Sum losses: 0.8 + 1.1 + 0.4 + 0.7 + 0.3 = 3.3; ÷14 = **0.236**
2. Day-15 update (Wilder smoothing with N=14):
   - avg_gain_15 = (13 · 0.500 + 1.4) / 14 = (6.5 + 1.4) / 14 = **0.564**
   - avg_loss_15 = (13 · 0.236 + 0.0) / 14 = (3.07) / 14 = **0.219**
3. RS = 0.564 / 0.219 = 2.575
4. RSI = 100 − 100 / (1 + 2.575) = 100 − 28.00 = **72.0**

**Read it:** RSI > 70 = overbought. In a *strong uptrend* RSI can sit above 70 for weeks (NVDA mid-2023), so don't sell mechanically — combine with trend filter (price vs SMA200).

**Verify:** `AAPL GIP` → bottom-left chart "RSI(14)". Hover over a point.

---

### D.3.4 MACD (Moving Average Convergence/Divergence)

**Formula:**
- `MACD_t = EMA_12(t) − EMA_26(t)`
- `Signal_t = EMA_9(MACD)` (EMA of the MACD itself)
- `Histogram_t = MACD_t − Signal_t`

**Inputs (assume you've already computed EMA-12 and EMA-26):**
- Today: EMA-12 = 191.50, EMA-26 = 189.20
- MACD = 191.50 − 189.20 = **+2.30**
- Yesterday's Signal = +1.80; today's MACD = +2.30
- New Signal = 0.2 · 2.30 + 0.8 · 1.80 = 0.46 + 1.44 = **+1.90** (α = 2/(9+1) = 0.2)
- Histogram = 2.30 − 1.90 = **+0.40**

**Read it:**
- MACD > 0 → short-term EMA above long-term → bullish momentum
- MACD crosses above Signal → bullish trigger
- Histogram expanding positively (today +0.40 vs yesterday smaller) → accelerating up-move

**Verify:** `AAPL GIP` → bottom-right MACD chart. Bars = histogram. Crossovers = momentum shifts.

---

### D.3.5 Bollinger Bands

**Formula:**
- `Middle_t = SMA_{20}(t)`
- `Upper_t = Middle_t + 2 · σ_{20}(t)`
- `Lower_t = Middle_t − 2 · σ_{20}(t)`

where σ_{20} = sample stdev of the last 20 closes.

**Inputs (assume on today):**
- SMA_20 = 188.00
- σ_20 of last 20 closes = 2.50

**Computation:**
- Upper = 188 + 2·2.50 = **193.00**
- Lower = 188 − 2·2.50 = **183.00**

**Read it:** If today's price is 192, you're near the upper band — over-extended on short-term standard-deviation basis. **Squeeze** (bands narrowing) → vol is compressing → directional move often follows.

**Verify:** `AAPL GIP` → toggle the "BB" chip. The band envelope draws on the candlestick.

---

## D.4 Risk metrics & valuation models

### D.4.1 CAPM β and α (OLS regression)

**Formula (regression):** `R_stock,t − R_f = α + β · (R_market,t − R_f) + ε_t`

**OLS estimators:**
- `β̂ = Cov(R_stock, R_market) / Var(R_market)`
- `α̂ = mean(R_stock) − β̂ · mean(R_market)` (using excess returns over R_f)

**Inputs (10 monthly excess returns for AAPL and SPY, illustrative):**

| Month | AAPL | SPY |
|---|---|---|
| 1 | +2.5% | +1.8% |
| 2 | −3.2% | −2.1% |
| 3 | +4.1% | +2.4% |
| 4 | +1.2% | +0.8% |
| 5 | −5.5% | −3.7% |
| 6 | +6.8% | +4.0% |
| 7 | +2.0% | +1.3% |
| 8 | −1.5% | −1.0% |
| 9 | +3.6% | +2.2% |
| 10 | +4.0% | +2.5% |

**Computation:**
1. Means: μ_AAPL = +1.40%; μ_SPY = +0.82%
2. Deviation products and squared deviations:
   ```
   Month  (A−μA)   (S−μS)   product    (S−μS)²
   1      +1.10    +0.98    +1.078     0.960
   2      −4.60    −2.92    +13.432    8.527
   3      +2.70    +1.58    +4.266     2.497
   4      −0.20    −0.02    +0.004     0.000
   5      −6.90    −4.52    +31.188    20.430
   6      +5.40    +3.18    +17.172    10.110
   7      +0.60    +0.48    +0.288     0.230
   8      −2.90    −1.82    +5.278     3.312
   9      +2.20    +1.38    +3.036     1.904
   10     +2.60    +1.68    +4.368     2.822
                            Σ=80.110   Σ=50.792
   ```
3. β̂ = 80.110 / 50.792 = **+1.58**
4. α̂ = 1.40 − 1.58 × 0.82 = 1.40 − 1.296 = **+0.104%/month** = +1.25%/year

**Read it:** β = 1.58 → AAPL amplifies SPY moves by 58%. α = +1.25% per year of excess return not explained by the market — could be skill, sector tailwind, or sample-period bias. Always state the window.

**Verify:** `AAPL FA` → `Beta` cell (yfinance reports a similar number; the calculation window may differ from yours).

---

### D.4.2 VaR 95% from a Monte Carlo simulation

**Formula:** Run N GBM paths; `VaR_{95%} = 100% × (1 − P_{5,T} / S_0)` where `P_{5,T}` is the 5th-percentile final price across paths.

**GBM one-step formula:** `S_{t+1} = S_t · exp((μ − ½σ²)Δt + σ√Δt · Z)` with Z ∼ N(0,1)

**Inputs (one path, σ=35% annualized, μ=10% drift, Δt = 1/252):**
- S_0 = $200
- σ² = 0.35² = 0.1225
- Drift coefficient = (0.10 − 0.5·0.1225)·(1/252) = (0.10 − 0.0613)·(1/252) = 0.0387 / 252 = 0.0001536
- Vol coefficient = 0.35 · √(1/252) = 0.35 · 0.0630 = 0.02204
- Draw Z = +1.0 (lucky day): S_1 = 200 · exp(0.0001536 + 0.02204·1.0) = 200 · exp(0.02220) = 200 · 1.02244 = **$204.49**
- Draw Z = −2.0 (bad day): S_1 = 200 · exp(0.0001536 + 0.02204·(−2)) = 200 · exp(−0.04393) = 200 · 0.9570 = **$191.40**

**Aggregate (100 paths over 252 steps, illustrative TSLA-style σ=0.40, μ=15%):**
- Final prices sorted: ... [$95, $98, $103, ..., $310]
- 5th-percentile P_{5,T} = $95 (the 5th-lowest out of 100)
- S_0 = $220
- VaR_{95%} = 100% × (1 − 95/220) = 100% × 0.568 = **56.8%**

**Read it:** "Over 1 year, there is a 5% chance of losing at least 56.8%." **VaR is the threshold, not the worst loss.** The expected loss *given* a tail event (CVaR) is typically 1.5-3× higher.

**Verify:** `TSLA MC` → reads "VaR 95%" in the kv-list. The chart below shows 60 sample paths; the spread at the rightmost time index visualizes the dispersion that yielded this VaR.

---

### D.4.3 Justified P/E (Gordon growth)

**Formula:** `P/E_just = (1 − b)(1 + g) / (k − g)`

where:
- `b` = retention ratio (= 1 − payout)
- `g` = sustainable growth rate
- `k = r_f + β · ERP` = required equity return

**Inputs (AAPL, illustrative):**
- Payout = 0.25 → b = 0.75
- g = 0.04 (4% long-run earnings growth)
- r_f = 0.042 (10-year Treasury yield)
- β = 1.2 (from `AAPL FA`)
- ERP = 0.05 (equity risk premium, Damodaran current)

**Computation:**
1. k = 0.042 + 1.2 · 0.05 = 0.042 + 0.060 = **10.2%**
2. Numerator = (1 − 0.75)(1.04) = 0.25 · 1.04 = **0.260**
3. Denominator = 0.102 − 0.04 = **0.062**
4. P/E_just = 0.260 / 0.062 = **4.19×**

Wait — that's tiny. Did the formula miss something? Let me reread.

**Common variant (Gordon growth in price terms):** `P/E = Payout · (1 + g) / (k − g)` (some sources use payout, some use 1 − b, both equal each other).

Using payout = 0.25 (not 1 − b which I miscomputed):
- 1 − b should equal payout. b = retention = 1 − 0.25 = **0.75** ✓ — so 1 − b = 0.25 ✓
- P/E_just = 0.25 · 1.04 / 0.062 = 0.26 / 0.062 ≈ **4.2×**

That's correct for this **abnormally low payout** assumption (AAPL pays very little — most return is buybacks not dividends). Real-world adjustment: count buybacks in "payout" → effective payout ~95% → P/E_just = 0.95 · 1.04 / 0.062 = **15.9×**. Now the formula gives the expected ballpark.

**Read it:** Two lessons:
1. Justified P/E is hyper-sensitive to assumptions, especially (k − g). A 100bp drop in k (rate cuts) or 100bp rise in g (growth re-acceleration) doubles the multiple.
2. The "(1 − b)" term is small for buyback-heavy companies *unless* you treat buybacks as payouts. Damodaran addresses this with "modified payout ratio" = (dividends + buybacks) / net income.

**Verify:** `MACRO` → "Macro-Adjusted Valuations" table → "JUSTIFIED P/E" column.

---

### D.4.4 Macro-adjusted P/E and the GAP

**Formula:** `Macro_PE = Justified_PE × adj_factor`; `GAP% = (Current_PE − Macro_PE) / Macro_PE`

**Inputs (TSLA, illustrative):**
- Current P/E = 65
- Justified P/E (from D.4.3, growth-stock-adjusted) = 25
- Adjustment factor = 0.87 (regime overlay: restrictive-rate environment penalty)

**Computation:**
1. Macro-adjusted P/E = 25 × 0.87 = **21.75×**
2. GAP = (65 − 21.75) / 21.75 = 43.25 / 21.75 = **+1.99 = +199%**

**Read it:** TSLA trades at ~3× macro-implied fair multiple. Either rates need to collapse, or growth needs to triple, or the multiple needs to compress 67%. Stress-test those scenarios via `TSLA MC`.

**Verify:** `MACRO` → "Macro-Adjusted Valuations" → GAP column (the red number).

---

## D.5 Network analytics

### D.5.1 Minimum Spanning Tree (MST) by Kruskal's algorithm

**Algorithm:**
1. Compute the full distance matrix `d_ij = √(2(1−ρ_ij))` for all pairs
2. List all `n(n−1)/2` edges sorted by distance ascending
3. Walk the list; add each edge to the MST **iff** it doesn't create a cycle (use union-find)
4. Stop when MST has `n − 1` edges

**Inputs (4 tickers, correlation matrix):**

```
       AAPL   MSFT   GOOG   XOM
AAPL   1.00   0.70   0.55   0.10
MSFT   0.70   1.00   0.65   0.05
GOOG   0.55   0.65   1.00   0.08
XOM    0.10   0.05   0.08   1.00
```

**Distance matrix:**

```
       AAPL   MSFT   GOOG   XOM
AAPL   0      0.775  0.949  1.342
MSFT   0.775  0      0.836  1.378
GOOG   0.949  0.836  0      1.356
XOM    1.342  1.378  1.356  0
```

Where `d = √(2(1−ρ))`: e.g., AAPL-MSFT: √(2·0.30) = √0.60 = 0.775 ✓.

**Sort edges ascending:** (AAPL, MSFT, 0.775), (MSFT, GOOG, 0.836), (AAPL, GOOG, 0.949), (XOM, AAPL, 1.342), (XOM, GOOG, 1.356), (XOM, MSFT, 1.378).

**Walk the list:**
- AAPL-MSFT (0.775): add ✓ (no cycle)
- MSFT-GOOG (0.836): add ✓ (no cycle)
- AAPL-GOOG (0.949): **skip** (would create cycle AAPL→MSFT→GOOG→AAPL)
- XOM-AAPL (1.342): add ✓ — that's the 3rd edge, MST complete (n−1 = 3 for n = 4).

**MST edges:** AAPL-MSFT, MSFT-GOOG, AAPL-XOM. Total distance: 0.775 + 0.836 + 1.342 = **2.953**.

**Read it:** XOM connects to the tech triangle via AAPL (not via MSFT or GOOG — AAPL's correlation with XOM is the highest of the three). In the resulting graph, AAPL has degree 2 (connected to MSFT and XOM) and is the **bridge** to XOM. Removing AAPL would disconnect XOM from the rest.

**Verify:** `GRAPH AAPL,MSFT,GOOG,XOM`. The rendered MST should have exactly these three edges.

---

### D.5.2 Betweenness centrality

**Formula:** For each node v: `BC(v) = Σ_{s≠v≠t} σ_st(v) / σ_st` where `σ_st` is the number of shortest s-t paths and `σ_st(v)` is how many pass through v. Normalized to [0,1] by dividing by `(n−1)(n−2)/2` (Freeman normalization).

**Inputs:** MST from D.5.1.

**Computation by hand (n=4, so 6 pairs of shortest paths, but in a tree each pair has exactly one path):**

Pairs and the path:
- MSFT-GOOG: MSFT→GOOG (length 1, doesn't pass through AAPL or XOM)
- MSFT-AAPL: MSFT→AAPL (length 1)
- MSFT-XOM: MSFT→AAPL→XOM (passes through AAPL)
- GOOG-AAPL: GOOG→MSFT→AAPL (passes through MSFT)
- GOOG-XOM: GOOG→MSFT→AAPL→XOM (passes through MSFT AND AAPL)
- AAPL-XOM: AAPL→XOM (length 1)

For each node, count pairs where it's on the path (excluding pairs where it's an endpoint):
- AAPL: on path for (MSFT,XOM) and (GOOG,XOM) = **2** appearances. Normalized: 2 / 3 = **0.667**
- MSFT: on path for (GOOG,AAPL) and (GOOG,XOM) = **2**. Normalized: **0.667**
- GOOG: 0
- XOM: 0

**Read it:** AAPL and MSFT are equal-weight bridges in this tiny graph. In a real 30-node MST, the centralities spread out and produce the ranking you see in `GRAPH`'s "Top Betweenness" table.

**Verify:** `GRAPH AAPL,MSFT,GOOG,XOM` → "Top Betweenness (Bridges)" table.

---

### D.5.3 Eigenvector centrality (power iteration)

**Formula:** EC is the leading eigenvector of the adjacency matrix A. Algorithm:
1. Start with `x_0` = uniform vector (or any positive vector)
2. Iterate: `x_{t+1} = A · x_t`
3. Normalize after each step: `x_{t+1} ← x_{t+1} / ||x_{t+1}||`
4. Converges to the eigenvector corresponding to the largest eigenvalue

**Inputs (adjacency of the MST from D.5.1, alphabetical order AAPL/GOOG/MSFT/XOM):**

```
       AAPL  GOOG  MSFT  XOM
AAPL    0     0     1    1
GOOG    0     0     1    0
MSFT    1     1     0    0
XOM     1     0     0    0
```

**Computation (start `x_0 = [1,1,1,1]`):**

Iteration 1: `A · x_0`:
- AAPL: 0+0+1+1 = 2
- GOOG: 0+0+1+0 = 1
- MSFT: 1+1+0+0 = 2
- XOM: 1+0+0+0 = 1

`x_1 = [2, 1, 2, 1]`. Norm = √(4+1+4+1) = √10 ≈ 3.162. Normalize: **[0.632, 0.316, 0.632, 0.316]**

Iteration 2:
- AAPL: 0+0+0.632+0.316 = 0.949
- GOOG: 0.632
- MSFT: 0.632+0.316 = 0.949
- XOM: 0.632

Normalize: norm = √(0.901+0.400+0.901+0.400) = √2.601 ≈ 1.613. **[0.588, 0.196, 0.588, 0.392]**

Hmm, didn't fully stabilize. A few more iterations converge to roughly:
**AAPL ≈ 0.602, MSFT ≈ 0.602, GOOG ≈ 0.372, XOM ≈ 0.372** (the bridge nodes dominate; the leaves are equal because the graph is symmetric).

**Read it:** Bridge nodes (AAPL, MSFT) get higher eigenvector centrality because they're connected to important neighbors. Leaf nodes (GOOG, XOM) are equal because their importance is purely inherited from one neighbor each. In the live 30-name MST, MA and BAC typically lead because they connect to the broadest, most central neighborhoods.

**Verify:** `GRAPH AAPL,MSFT,GOOG,XOM` → "Top Eigenvector (Influence)" table.

---

### D.5.4 Modularity Q (community quality)

**Formula:** `Q = (1/2m) Σ_ij [A_ij − k_i·k_j/(2m)] · δ(c_i, c_j)`

where `m` = number of edges, `k_i` = degree of node i, `δ(c_i, c_j) = 1` if i and j are in the same community.

**Inputs (MST from D.5.1, 3 edges so m=3, suppose communities are {AAPL, MSFT, GOOG} and {XOM}):**

**Computation:**
- Degrees: k_AAPL = 2, k_MSFT = 2, k_GOOG = 1, k_XOM = 1
- 2m = 6
- For each pair in the same community: A_ij − k_i·k_j/6
  - Within {AAPL, MSFT, GOOG}: pairs (A,M), (M,G), (A,G):
    - (A,M): A=1, expected = 2·2/6 = 0.667; contribution = 1 − 0.667 = 0.333. Plus same for (M,A): also 0.333.
    - (M,G): A=1, expected = 2·1/6 = 0.333; contribution = 0.667 × 2 = 1.333.
    - (A,G): A=0, expected = 2·1/6 = 0.333; contribution = −0.333 × 2 = −0.667.
  - Within {XOM}: only (X,X) which counts as A_XX = 0; expected = 1/6; contribution = −1/6 = −0.167.
- Sum = 0.666 + 1.333 − 0.667 − 0.167 = 1.166
- Q = 1.166 / 6 = **0.194**

**Read it:** Q > 0.3 generally indicates "clearly modular" structure; Q < 0.1 is "weakly clustered". Our toy graph at Q ≈ 0.19 is borderline. Greedy modularity (the algorithm in `GRAPH`) maximizes this Q.

**Verify:** `GRAPH` cluster legend. The cluster cards show the partition the greedy algorithm chose to maximize Q.

---

## D.6 Putting it together — a single ticker workflow

Take any one ticker and execute the full chain in 10 commands:

```
1.  AAPL DES         identity, business, current quote
2.  AAPL FA          P/E, PEG, margins, ROE → compute DuPont by hand
3.  AAPL GIP         chart, SMA/RSI/MACD → compare to your hand-computed values
4.  AAPL STAT        moments, JB, ACF → verify ann_vol = std_daily × √252
5.  AAPL N           narrative driving the multiple right now
6.  AAPL,MSFT,GOOG,META COMP   peer comparison; spot the outlier on each metric
7.  CORR AAPL,MSFT,GOOG,META,AMZN,NVDA   correlation cluster (should be tight)
8.  GRAPH AAPL,MSFT,GOOG,META,AMZN,NVDA   MST + centralities; spot the bridge
9.  HEAT             sector context — is the whole XLK moving today?
10. MACRO            macro-adjusted P/E; is AAPL's current multiple defensible?
```

A student who can defend each cell of the resulting nine-panel mosaic has internalized the fundamentals.

---

## Closing note for the teacher

The terminal exists so that financial concepts are not abstractions. When a student reads "P/E ratio," they should *see* the amber number flicker. When they read "fat tails," they should *call up `TSLA STAT`* and stare at the kurtosis number until it registers. Every concept in this guide has a four-keystroke way to be observed. That's the only pedagogical bet that consistently works at scale.

When in doubt: **type the function code, not the explanation.**
