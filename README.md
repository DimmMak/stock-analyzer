# Stock Analyzer — Hedge Fund Level Analysis System

A self-improving 12-agent stock analysis system that runs Everything Money fundamentals, technical analysis, quantitative models (DCF, Monte Carlo, factor scoring), sentiment analysis, options strategies, and watchlist monitoring — and gets smarter with every analysis.

---

## Quick Start

```bash
# 1. Analyze a stock (automated)
python3 scripts/fetch_data.py AAPL
python3 scripts/technicals.py AAPL
python3 scripts/quant.py AAPL

# 2. Open Claude Code
/stock-analyzer → .intake → type: AAPL

# 3. Follow the agent chain
.fundamentals → .quant → .technicals → .sentiment → .valuation → .risk → .options → .verdict
```

---

## The 12 Agents

| Agent | Role |
|---|---|
| `.intake` | Pulls data automatically or guides manual paste. Structures everything for agents. |
| `.fundamentals` | Everything Money 8-Pillar framework. Pass/Fail per pillar. Letter grade. |
| `.quant` | DCF (3 scenarios), Monte Carlo, factor scores, Sharpe, Beta, VaR. |
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
User types ticker
      ↓
  .intake ──── AUTO: runs Python scripts
           └── MANUAL: guides paste from stockanalysis.com + finviz
      ↓
.fundamentals ──────────────────────── 8 Pillar scorecard
      ↓
  .quant ─────────────────────────────  DCF + Monte Carlo + Factors
      ↓
.technicals ────────────────────────── Traffic lights + signals + levels
      ↓
.sentiment ─────────────────────────── Insider + institutional + options flow
      ↓
.valuation ─────────────────────────── Fair value + price target + margin of safety
      ↓
  .risk ──────────────────────────────  Bear case + position sizing
      ↓
.options ───────────────────────────── Options plays for your position
      ↓
.verdict ───────────────────────────── Final stock card + composite score
      ↓
  .meta ──────────────────────────────  (every 10 analyses) agents debate + improve
```

---

## Python Scripts

| Script | What it does |
|---|---|
| `scripts/fetch_data.py TICKER` | Pulls fundamentals, price, analysts, options from Yahoo Finance |
| `scripts/technicals.py TICKER` | Calculates all technical indicators, appends to data file |
| `scripts/quant.py TICKER` | Runs DCF, Monte Carlo, factor scores, risk metrics |
| `scripts/watchlist_check.py` | Checks all watchlist tickers for major signals |

**Requirements:** Python 3.8+, yfinance, pandas, numpy (all pre-installed with Anaconda)

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
| `notes/stock-notes.md` | Full analysis history. Every agent reads and writes here. |
| `notes/watchlist.md` | Active watchlist with entry targets and alert thresholds. |
| `notes/outcome-tracker.md` | Actual results — the ground truth for .meta. |
| `notes/portfolio.md` | Your positions — used by .options and .risk. |
| `notes/agent-debates.md` | Full audit trail of every .meta debate. |
| `notes/alert-log.md` | History of every watchlist alert triggered. |

---

## Output — The Verdict Card

Every analysis ends with this:

```
╔══════════════════════════════════════════════════╗
║          STOCK VERDICT — AAPL                   ║
║          Apple Inc.                             ║
╠══════════════════════════════════════════════════╣
║  Fundamental Score:  7/8 pillars    A           ║
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
│   ├── fetch_data.py             ← fundamentals + price data
│   ├── technicals.py             ← technical indicators
│   ├── quant.py                  ← DCF, Monte Carlo, factors
│   └── watchlist_check.py        ← daily signal monitor
├── data/
│   └── {TICKER}_data.md          ← auto-generated per analysis
├── notes/
│   ├── stock-notes.md            ← shared agent memory
│   ├── watchlist.md              ← active watchlist
│   ├── outcome-tracker.md        ← actual results
│   ├── portfolio.md              ← your positions
│   ├── agent-debates.md          ← .meta debate log
│   └── alert-log.md              ← watchlist alert history
└── skills/
    ├── intake/SKILL.md
    ├── fundamentals/SKILL.md
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
