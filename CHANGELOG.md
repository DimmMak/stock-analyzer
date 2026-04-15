# CHANGELOG — Stock Analyzer

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
