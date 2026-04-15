# Stock Analyzer — Hedge Fund Level Analysis System

A self-improving 14-agent stock analysis system with macro environment scanning, token-optimized routing, SBC-adjusted DCF valuation, and earnings quality analysis. Runs Everything Money fundamentals, technical analysis, quantitative models, sentiment analysis, options strategies, and watchlist monitoring — and gets smarter with every analysis.

---

## Quick Start

```bash
# 0. (Optional but recommended) Get macro context first
python3 scripts/macro.py

# 1. Analyze a stock
python3 scripts/fetch_data.py AAPL
python3 scripts/technicals.py AAPL
python3 scripts/quant.py AAPL

# 2. Open Claude Code — just talk naturally
/stock-analyzer
"is AAPL a buy right now?"
"full analysis NVDA"
"top 5 AI stocks"
"quick take on META"
```

The `.router` agent automatically picks the right analysis path. No commands needed.

---

## The 14 Agents

| Agent | Role |
|---|---|
| `.router` | **NEW** — Classifies query type, routes to minimum agents needed. Saves 55-90% tokens. |
| `.macro` | **NEW** — Market regime, VIX, rates, sector rotation. Frames every analysis with context. |
| `.intake` | Pulls data automatically or guides manual paste. Structures everything for agents. |
| `.fundamentals` | Everything Money 8-Pillar + P9 Earnings Quality. Pass/Fail per pillar. Letter grade. |
| `.quant` | DCF (SBC-adjusted, 3 scenarios), Monte Carlo, factor scores, Sharpe, Beta, VaR. |
| `.technicals` | Traffic light + signal table + timeframe stack. Entry zones, key levels. |
| `.sentiment` | Insider activity, institutional flow, analyst ratings, short interest, options flow. |
| `.valuation` | Fair value range, price target, margin of safety. Multiple methods. |
| `.risk` | Bear case, key risks, position sizing, stop loss reference. |
| `.options` | Position plays (covered calls, protective puts) + standalone plays (spreads). |
| `.verdict` | Final stock card: rating, composite score, price target, entry zone, position size. |
| `.watchlist` | Adds/monitors stocks. Gmail alerts on major signals. |
| `.meta` | Self-improvement engine. Reads outcome data, runs agent debate, updates instructions. |
| `.manager` | System admin: health, backup, history, outcome logging, portfolio. |

---

## The Full Analysis Flow

```
User types anything naturally
          ↓
      .router ─────────────────── Classifies intent, picks minimum skill set
          ↓
      .macro ──────────────────── Market regime, VIX, rates, sector rotation
          ↓
      .intake ──── AUTO: runs Python scripts
               └── MANUAL: guides paste from stockanalysis.com + finviz
          ↓
  .fundamentals ───────────────── 8 Pillar + P9 Earnings Quality scorecard
          ↓
      .quant ──────────────────── SBC-adjusted DCF + Monte Carlo + Factors
          ↓
  .technicals ─────────────────── Traffic lights + signals + levels
          ↓
  .sentiment ──────────────────── Insider + institutional + options flow
          ↓
  .valuation ──────────────────── Fair value + price target + margin of safety
          ↓
      .risk ───────────────────── Bear case + position sizing
          ↓
  .options ────────────────────── Options plays for your position
          ↓
  .verdict ────────────────────── Final stock card + composite score
          ↓
      .meta ───────────────────── (every 10 analyses) agents debate + improve
```

---

## Query Types & Token Savings

The `.router` automatically classifies every request:

| Query Type | Example | Token Savings |
|---|---|---|
| Macro only | "what's the market doing" | ~95% |
| Quick take | "should I buy NVDA?" | ~55% |
| Full analysis | "deep dive AAPL" | 0% (intentional) |
| Specific question | "technical setup for META" | ~80% |
| Comparison | "top 5 AI stocks" | ~65% |
| Watchlist | "check my watchlist" | ~90% |
| Options play | "covered call for TSLA" | ~70% |
| Risk check | "bear case for AVGO" | ~65% |

---

## Python Scripts

| Script | What it does |
|---|---|
| `scripts/macro.py` | **NEW** — Pulls VIX, 10Y yield, S&P, dollar, sector ETF rotation. Outputs `data/MACRO_data.md` |
| `scripts/fetch_data.py TICKER` | Pulls fundamentals, price, analysts, options from Yahoo Finance |
| `scripts/technicals.py TICKER` | Calculates all technical indicators, appends to data file |
| `scripts/quant.py TICKER` | **UPGRADED** — SBC-adjusted DCF + earnings quality metrics + risk |
| `scripts/watchlist_check.py` | Checks all watchlist tickers for major signals |

**Requirements:** Python 3.8+, yfinance, pandas, numpy (all pre-installed with Anaconda)

---

## What's New — v1.1

### `.macro` Agent
Runs `macro.py` to pull live market data then outputs a 1-page macro brief:
- Market regime (risk-on / mixed / risk-off)
- VIX level + interpretation
- 10Y yield + impact on high-multiple stocks
- All 11 sector ETF 1M and 3M performance (ranked)
- Growth vs Value rotation signal (QQQ vs IWD)
- Dollar strength impact on multinationals
- Macro flags passed downstream to adjust analysis context

### SBC-Adjusted DCF (`quant.py`)
Stock-Based Compensation is a real cost that inflates reported FCF. Now fixed:
- Pulls SBC from cashflow statement automatically
- Calculates `FCF_adjusted = FCF_reported - SBC`
- Uses adjusted FCF for all DCF scenarios
- Reports: raw FCF, SBC amount, adjusted FCF, SBC as % of FCF

### P9 Earnings Quality (`fundamentals`)
Three new checks that reveal whether profits are real:
1. **SBC % of FCF** — < 15% clean, 15-30% moderate, > 30% red flag
2. **Accruals Ratio** — cash earnings vs accrual earnings quality signal
3. **Gross Profit Dollar Growth** — pricing power and scale leverage check

### `.router` Agent
Intercepts every natural language request and routes to the minimum agents needed. No more running 9 agents when 2 will answer the question.

---

## The Self-Improving Loop

Every 10 analyses, `.meta` activates:
1. Reads outcome-tracker.md — actual results vs predictions
2. Runs agent debate — each agent argues what needs to change
3. Writes debate to `notes/agent-debates.md` (full audit trail)
4. Updates `## DYNAMIC` section of every skill file

After 10 analyses: the system knows which factors are predictive **for the stocks you analyze specifically.**

---

## Shared Memory Files

| File | Purpose |
|---|---|
| `data/MACRO_data.md` | Latest macro environment scan |
| `notes/stock-notes.md` | Full analysis history. Every agent reads and writes here. |
| `notes/watchlist.md` | Active watchlist with entry targets and alert thresholds. |
| `notes/outcome-tracker.md` | Actual results — the ground truth for .meta. |
| `notes/portfolio.md` | Your positions — used by .options and .risk. |
| `notes/agent-debates.md` | Full audit trail of every .meta debate. |
| `notes/alert-log.md` | History of every watchlist alert triggered. |

---

## Output — The Verdict Card

Every full analysis ends with this:

```
╔══════════════════════════════════════════════════╗
║          STOCK VERDICT — AAPL                   ║
║          Apple Inc.                             ║
╠══════════════════════════════════════════════════╣
║  Macro Regime:       🟢 Risk-On                 ║
║  Fundamental Score:  7/8 pillars    A           ║
║  Earnings Quality:   P9 — Clean ✅              ║
║  Quant Score:        73/100         B           ║
║  Technical Signal:   🟡 Wait                    ║
║  Sentiment:          🟢 Bullish                 ║
║  Risk Level:         MEDIUM                     ║
║  COMPOSITE SCORE:    76/100  Grade: B           ║
╠══════════════════════════════════════════════════╣
║  VERDICT: BUY                                   ║
╠══════════════════════════════════════════════════╣
║  Fair Value Range:   $185 — $210                ║
║  Price Target (12m): $200                       ║
║  Current Price:      $191                       ║
║  Upside:             +4.7%                      ║
║  Entry Zone:         $178 — $185                ║
║  Stop Loss:          $168 (-12%)                ║
║  Position Size:      3-5% of portfolio          ║
╠══════════════════════════════════════════════════╣
║  BULL CASE: AI integration drives margin        ║
║             expansion and services growth       ║
║  BEAR CASE: Multiple compression in rising      ║
║             rate environment                    ║
╚══════════════════════════════════════════════════╝
```

---

## File Structure

```
stock-analyzer/
├── README.md
├── CHANGELOG.md
├── WALKTHROUGH.md
├── stock-analyzer.skill          ← master orchestrator
├── stock-manager.skill           ← system admin
├── scripts/
│   ├── macro.py                  ← NEW: macro environment scanner
│   ├── fetch_data.py             ← fundamentals + price data
│   ├── technicals.py             ← technical indicators
│   ├── quant.py                  ← UPGRADED: SBC-adjusted DCF + earnings quality
│   └── watchlist_check.py        ← daily signal monitor
├── data/
│   ├── MACRO_data.md             ← auto-generated by macro.py
│   └── {TICKER}_data.md          ← auto-generated per analysis
├── notes/
│   ├── stock-notes.md            ← shared agent memory
│   ├── watchlist.md              ← active watchlist
│   ├── outcome-tracker.md        ← actual results
│   ├── portfolio.md              ← your positions
│   ├── agent-debates.md          ← .meta debate log
│   └── alert-log.md              ← watchlist alert history
└── skills/
    ├── router/SKILL.md           ← NEW: token optimizer + query classifier
    ├── macro/SKILL.md            ← NEW: macro environment agent
    ├── intake/SKILL.md
    ├── fundamentals/SKILL.md     ← UPGRADED: P9 earnings quality
    ├── quant/SKILL.md
    ├── technicals/SKILL.md
    ├── sentiment/SKILL.md
    ├── valuation/SKILL.md
    ├── risk/SKILL.md
    ├── options/SKILL.md
    ├── verdict/SKILL.md
    ├── watchlist/SKILL.md
    ├── meta/SKILL.md
    └── manager/SKILL.md
```
