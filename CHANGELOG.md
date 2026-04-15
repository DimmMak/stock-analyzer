# CHANGELOG — Stock Analyzer

---

## [2026-04-15] — v1.1 — Hedge Fund Upgrades

### 4 upgrades for professional-grade analysis

**1. `.macro` Agent + `scripts/macro.py`**
New agent that scans the macro environment before any stock analysis. Pulls live data: VIX, 10Y yield, S&P 500, dollar index (DXY), all 11 sector ETFs (1M + 3M performance), growth vs value rotation (QQQ vs IWD). Outputs a 1-page macro brief with regime flags passed to downstream agents. Real hedge funds always frame stock picks inside macro context — now this system does too.

**2. SBC-Adjusted DCF (`quant.py` upgrade)**
Stock-Based Compensation is a real cash cost that inflates reported Free Cash Flow. Previous DCF used raw FCF, which overstated intrinsic value for high-SBC companies (NVDA, META, etc.). Now: `FCF_adjusted = FCF_reported - SBC`. All DCF scenarios use adjusted FCF. Output shows raw FCF, SBC amount, adjusted FCF, and SBC as % of FCF so you can see the distortion clearly.

**3. P9 Earnings Quality Pillar (`fundamentals` upgrade)**
Three new checks on whether reported profits are real:
- SBC % of FCF: < 15% clean, > 30% red flag
- Accruals Ratio: (Net Income - Operating CF) / Total Assets — negative is good
- Gross Profit Dollar Growth: pricing power and scale leverage signal

**4. `.router` Agent (token optimizer)**
Classifies every natural language request into 1 of 7 query types and routes to the minimum agents needed. Saves 55-90% tokens vs running the full pipeline every time. Full analysis still available on demand — router just makes sure you're not burning 50k tokens to answer a 5k-token question.

**Architecture insight:** These 4 upgrades close the gap between "good retail analysis" and "how hedge funds actually think." Macro context + earnings quality + real FCF = fewer blind spots.

**Files added/modified:**
- `scripts/macro.py` (new)
- `skills/macro/SKILL.md` (new)
- `skills/router/SKILL.md` (updated with macro type)
- `scripts/quant.py` (SBC adjustment + earnings quality section)
- `skills/fundamentals/SKILL.md` (P9 pillar added)
- `README.md` (updated — now updated with every release)
- `stock-analyzer.skill` (routing table updated)

---

## [2026-04-15] — v1.0 — Initial Build

### Built in collaboration with Claude Code

**Concept origin:**
Started from the Everything Money 8-Pillar fundamental analysis framework. Evolved into a full hedge fund-level analysis system with technical analysis, quantitative models, sentiment analysis, options strategies, and self-improving agents.

**Architecture decisions:**

1. **Two-layer design:** Python scripts handle data fetching and calculation. Claude skill agents handle reasoning and interpretation. Clean separation — Python doesn't think, Claude doesn't fetch.

2. **AUTO + MANUAL intake:** Automated yfinance pull with graceful fallback to guided manual paste if auto fails. Minimizes errors, maximizes reliability.

3. **12 specialized agents** — each owns one analysis domain. Better than one agent doing everything.

4. **PERMANENT + DYNAMIC section architecture** — core agent identity never changes. Personalization layer updated by .meta after every 10 analyses.

5. **Outcome tracking as ground truth** — .meta only improves based on actual results (outcome-tracker.md), not feelings about how the analysis went.

6. **Everything Money 8 Pillars as foundation** — extended with: gross margin trend, management quality signals, and additional quant extensions.

7. **Three-layer technical output** — Traffic lights (instant) → Signal table (detail) → Timeframe stack (deep dive). Designed for efficiency.

8. **Gmail alerts via MCP** — real email alerts when watchlist signals trigger. No third-party services needed.

**Files created:**
- 4 Python scripts (fetch_data.py, technicals.py, quant.py, watchlist_check.py)
- 12 skill files (intake, fundamentals, quant, technicals, sentiment, valuation, risk, options, verdict, watchlist, meta, manager)
- 6 notes files (stock-notes, watchlist, outcome-tracker, portfolio, agent-debates, alert-log)
- Master orchestrator skill: stock-analyzer.skill
- System admin skill: stock-manager.skill

**Quant models implemented:**
- DCF: 3 scenarios (bear/base/bull) with variable WACC and growth rates
- Monte Carlo: 1,000 simulations, 1-year horizon, percentile outcomes
- Factor scores: Momentum (30%), Value (25%), Quality (30%), Low Volatility (15%)
- Risk: Sharpe ratio, Beta vs SPY, Max Drawdown, VaR 95%/99%

---

<!-- New entries go above this line -->
