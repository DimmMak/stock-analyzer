# How to Use the Stock Analyzer — Full Walkthrough

---

## First Analysis — AAPL

**Step 1:** Open terminal, run the data scripts:
```
python3 scripts/fetch_data.py AAPL
python3 scripts/technicals.py AAPL
python3 scripts/quant.py AAPL
```
Takes ~30 seconds. Outputs `data/AAPL_data.md`

**Step 2:** Open Claude Code, type `/stock-analyzer`

The hub shows current status and available agents.

**Step 3:** Type `.intake`

> "Auto-fetch complete. AAPL data loaded — 5 years price history, full financials, options chain, analyst data. Data quality: Complete. Handing to .fundamentals"

**Step 4:** Type `.fundamentals`

Runs the 8 pillars. AAPL scores 7/8:

```
P1 Revenue Growth      PASS ✅ — 8% CAGR over 5 years
P2 EPS Growth          PASS ✅ — EPS up 15% YoY
P3 Free Cash Flow      PASS ✅ — $90B FCF, 24% FCF margin
P4 Net Cash/Debt       PASS ✅ — Net cash positive
P5 Share Dilution      PASS ✅ — Shares declining (buybacks)
P6 ROIC                PASS ✅ — 28% ROIC, excellent
P7 Valuation           FAIL ❌ — P/E 28x, PEG 2.1, stretched
P8 Capital Return      PASS ✅ — $90B buybacks + dividend

SCORE: 7/8 — Grade: A
```

**Step 5:** Type `.quant`

> "Factor composite: 71/100 — Grade B. DCF base case: $198, 3.7% upside. Monte Carlo: 64% probability positive return in 12 months. Sharpe 1.2 — good risk-adjusted return. Handing to .sentiment"

**Step 6:** Type `.technicals`

```
⚡ TECHNICAL QUICK READ — AAPL @ $191.00
─────────────────────────────────────────
Trend     │ 🟢 Bullish │ Above all 3 MAs
Momentum  │ 🟡 Neutral │ RSI 54 — room to run
MACD      │ 🟢 Bullish │ Above signal line
Volume    │ 🟡 Normal  │ 0.9x average
Bollinger │ 🟡 Inside  │ 62% of band width
─────────────────────────────────────────
OVERALL: 🟡 WAIT — Strong stock, slightly overextended
Entry zone: $178–$184 | Resistance: $199
```

**Step 7:** Type `.sentiment`

> "Insider activity neutral — no recent buys or sells. Institutional ownership 61% — normal. Analyst consensus: BUY, mean target $205. Short interest 0.8% — minimal. Options P/C ratio 0.82 — mildly bullish. Overall: 🟢 Bullish sentiment."

**Step 8:** Type `.valuation`

```
VALUATION — AAPL @ $191.00
DCF Bear:    $168 — 12% overvalued
DCF Base:    $198 — 3.7% undervalued
DCF Bull:    $245 — 28% undervalued
PEG (2.1):   Fairly valued for growth rate
FCF Yield:   3.2% — fair
────────────────────────────
FAIR VALUE RANGE: $168 — $245
PRICE TARGET: $198 (base case)
MARGIN OF SAFETY: 3.7%
VERDICT: 🟡 FAIRLY VALUED
```

**Step 9:** Type `.risk`

> "Risk level: Medium. Key risks: 1) China revenue exposure (19% of revenue) — geopolitical risk HIGH. 2) Services growth deceleration — probability MEDIUM. 3) Multiple compression if rates stay high — probability MEDIUM. Bear case: $155 (-19%). Position sizing: 3-5% of portfolio for this conviction level."

**Step 10:** Type `.options`

> "You own 100 shares at $182.50. Current price $191.00 (+4.7% from avg).
>
> COVERED CALL: Sell $200 strike, 30 DTE — collect ~$280 premium. If assigned, you sell at $200 (+9.6% from avg). If not assigned, keep $280 and repeat.
>
> BULL CALL SPREAD: Buy $195/$205 spread — costs $320, max profit $680 if AAPL > $205 at expiry. Risk/reward 2.1:1."

**Step 11:** Type `.verdict`

```
╔══════════════════════════════════════════════════╗
║          STOCK VERDICT — AAPL                   ║
╠══════════════════════════════════════════════════╣
║  Fundamental:  7/8 pillars     A                ║
║  Quant:        71/100          B                ║
║  Technical:    🟡 Wait                          ║
║  Sentiment:    🟢 Bullish                       ║
║  Risk:         MEDIUM                           ║
║  COMPOSITE:    74/100  Grade: B                 ║
╠══════════════════════════════════════════════════╣
║  VERDICT: BUY — WAIT FOR ENTRY                  ║
╠══════════════════════════════════════════════════╣
║  Fair Value:    $168 — $245                     ║
║  Price Target:  $198                            ║
║  Current:       $191                            ║
║  Entry Zone:    $178 — $185                     ║
║  Stop Loss:     $168 (-12%)                     ║
║  Position Size: 3-5% of portfolio               ║
║                                                 ║
║  THE CALL: Apple is a fundamentally excellent   ║
║  business fairly priced at current levels.      ║
║  Wait for a pullback to $178-$185 for a         ║
║  better margin of safety before adding.         ║
╚══════════════════════════════════════════════════╝
```

---

## Adding to Watchlist

Type `.watchlist` → `add AAPL`

> "AAPL added to watchlist. Alert triggers set: price below $185 (entry zone), RSI below 35 (oversold), golden cross (momentum confirmation). Run watchlist_check.py daily to monitor."

---

## Daily Monitoring

In terminal:
```
python3 scripts/watchlist_check.py
```

If AAPL drops to $183:
```
🚨 AAPL — ENTRY ZONE REACHED
Price: $183.20 | RSI: 41 | Volume: 1.2x average
→ Review analysis and consider entry
```

Gmail alert sent automatically.

---

## 10 Analyses Later — .meta Runs

Type `.meta` (or it triggers automatically):

```
.meta reads outcome-tracker.md — 8 of 10 verdicts were correct.
Debate runs. Agents argue.

.quant says: "FCF yield has been the most predictive factor. Weight it higher."
.technicals says: "RSI oversold bounces have been reliable entry points."
.fundamentals says: "P7 valuation keeps failing on growth stocks — need context."

.meta VERDICT:
- .quant: increase FCF yield weight in value factor
- .technicals: flag RSI < 35 as high-priority entry signal
- .fundamentals: add growth-rate context to P7 valuation pillar

All DYNAMIC sections updated.
System accuracy: 80%. Agents are smarter.
```

---

## The System After 6 Months

Every DYNAMIC section has been updated multiple times.
The system knows:
- Which sectors you analyze most
- Which factors have been predictive for your stocks
- Which technical signals have led to correct entries
- Your preferred position sizes and options strategies

It's not the same system you started with.
It's been tuned to you specifically.
