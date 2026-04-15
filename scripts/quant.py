#!/usr/bin/env python3
"""
quant.py — Quantitative Analysis Engine
Runs DCF, Monte Carlo, factor scoring, and time series analysis

Usage: python3 quant.py AAPL
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import warnings
warnings.filterwarnings('ignore')


def calculate_dcf(fcf, growth_rate_5y, terminal_growth, wacc, shares_outstanding):
    """
    Simple DCF Model
    - fcf: Free Cash Flow (TTM)
    - growth_rate_5y: Expected growth for 5 years
    - terminal_growth: Terminal growth rate (perpetuity)
    - wacc: Weighted Average Cost of Capital
    - shares_outstanding: Shares outstanding
    Returns: intrinsic value per share
    """
    if fcf <= 0 or shares_outstanding <= 0:
        return None

    projected_fcf = []
    for year in range(1, 6):
        projected_fcf.append(fcf * ((1 + growth_rate_5y) ** year))

    # Discount projected FCF
    pv_fcf = sum([cf / ((1 + wacc) ** i) for i, cf in enumerate(projected_fcf, 1)])

    # Terminal value
    terminal_fcf = projected_fcf[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    pv_terminal = terminal_value / ((1 + wacc) ** 5)

    total_value = pv_fcf + pv_terminal
    intrinsic_per_share = total_value / shares_outstanding

    return {
        'intrinsic_value': intrinsic_per_share,
        'pv_fcf': pv_fcf,
        'pv_terminal': pv_terminal,
        'total_value': total_value,
        'projected_fcf': projected_fcf
    }


def run_monte_carlo(hist_prices, simulations=1000, days=252):
    """
    Monte Carlo simulation for price projection (1 year)
    Returns percentile outcomes
    """
    returns = hist_prices['Close'].pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
    current_price = hist_prices['Close'].iloc[-1]

    simulation_results = []
    for _ in range(simulations):
        prices = [current_price]
        for _ in range(days):
            shock = np.random.normal(mu, sigma)
            prices.append(prices[-1] * (1 + shock))
        simulation_results.append(prices[-1])

    results = np.array(simulation_results)
    return {
        'current': current_price,
        'p10': np.percentile(results, 10),
        'p25': np.percentile(results, 25),
        'p50': np.percentile(results, 50),
        'p75': np.percentile(results, 75),
        'p90': np.percentile(results, 90),
        'mean': results.mean(),
        'prob_positive': (results > current_price).mean() * 100,
        'max_loss_10pct': np.percentile(results, 10),
        'best_case': np.percentile(results, 95)
    }


def calculate_factor_scores(info, hist_1y, hist_5y):
    """
    Calculate quant factor scores (0-100):
    - Momentum: price momentum across timeframes
    - Value: how cheap/expensive relative to fundamentals
    - Quality: profitability and balance sheet strength
    - Volatility: lower vol = better score
    """
    scores = {}

    # ── MOMENTUM FACTOR ──
    momentum_points = 0
    try:
        close = hist_1y['Close']
        mom_12m = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100
        mom_6m = ((close.iloc[-1] - close.iloc[-126]) / close.iloc[-126]) * 100 if len(close) > 126 else 0
        mom_3m = ((close.iloc[-1] - close.iloc[-63]) / close.iloc[-63]) * 100 if len(close) > 63 else 0
        mom_1m = ((close.iloc[-1] - close.iloc[-21]) / close.iloc[-21]) * 100 if len(close) > 21 else 0

        if mom_12m > 20: momentum_points += 25
        elif mom_12m > 10: momentum_points += 15
        elif mom_12m > 0: momentum_points += 8
        if mom_6m > 10: momentum_points += 25
        elif mom_6m > 5: momentum_points += 15
        elif mom_6m > 0: momentum_points += 8
        if mom_3m > 5: momentum_points += 25
        elif mom_3m > 0: momentum_points += 15
        if mom_1m > 2: momentum_points += 25
        elif mom_1m > 0: momentum_points += 15
        scores['momentum'] = min(momentum_points, 100)
        scores['momentum_detail'] = f"12m: {mom_12m:+.1f}% | 6m: {mom_6m:+.1f}% | 3m: {mom_3m:+.1f}% | 1m: {mom_1m:+.1f}%"
    except Exception:
        scores['momentum'] = 50
        scores['momentum_detail'] = 'Could not calculate'

    # ── VALUE FACTOR ──
    value_points = 0
    try:
        pe = info.get('trailingPE', None)
        pb = info.get('priceToBook', None)
        ps = info.get('priceToSalesTrailing12Months', None)
        ev_ebitda = info.get('enterpriseToEbitda', None)
        fcf_yield = info.get('freeCashflow', 0) / info.get('marketCap', 1) * 100 if info.get('marketCap', 0) > 0 else 0

        if pe and pe < 15: value_points += 25
        elif pe and pe < 25: value_points += 15
        elif pe and pe < 35: value_points += 8
        if pb and pb < 2: value_points += 25
        elif pb and pb < 4: value_points += 15
        elif pb and pb < 6: value_points += 8
        if ps and ps < 2: value_points += 25
        elif ps and ps < 5: value_points += 15
        elif ps and ps < 10: value_points += 8
        if fcf_yield > 5: value_points += 25
        elif fcf_yield > 3: value_points += 15
        elif fcf_yield > 1: value_points += 8

        scores['value'] = min(value_points, 100)
        scores['value_detail'] = f"P/E: {pe:.1f} | P/B: {pb:.1f} | P/S: {ps:.1f} | FCF Yield: {fcf_yield:.1f}%" if all(x is not None for x in [pe, pb, ps]) else 'Partial data'
    except Exception:
        scores['value'] = 50
        scores['value_detail'] = 'Could not calculate'

    # ── QUALITY FACTOR ──
    quality_points = 0
    try:
        roe = info.get('returnOnEquity', 0) or 0
        roa = info.get('returnOnAssets', 0) or 0
        profit_margin = info.get('profitMargins', 0) or 0
        gross_margin = info.get('grossMargins', 0) or 0
        debt_equity = info.get('debtToEquity', 999) or 999
        current_ratio = info.get('currentRatio', 0) or 0
        revenue_growth = info.get('revenueGrowth', 0) or 0
        earnings_growth = info.get('earningsGrowth', 0) or 0

        if roe > 0.20: quality_points += 15
        elif roe > 0.10: quality_points += 8
        if roa > 0.10: quality_points += 10
        elif roa > 0.05: quality_points += 5
        if profit_margin > 0.20: quality_points += 15
        elif profit_margin > 0.10: quality_points += 8
        if gross_margin > 0.40: quality_points += 15
        elif gross_margin > 0.25: quality_points += 8
        if debt_equity < 50: quality_points += 15
        elif debt_equity < 100: quality_points += 8
        if current_ratio > 1.5: quality_points += 10
        elif current_ratio > 1.0: quality_points += 5
        if revenue_growth > 0.15: quality_points += 10
        elif revenue_growth > 0.05: quality_points += 5
        if earnings_growth > 0.15: quality_points += 10
        elif earnings_growth > 0.05: quality_points += 5

        scores['quality'] = min(quality_points, 100)
        scores['quality_detail'] = f"ROE: {roe*100:.1f}% | Margin: {profit_margin*100:.1f}% | D/E: {debt_equity:.0f} | Rev Growth: {revenue_growth*100:.1f}%"
    except Exception:
        scores['quality'] = 50
        scores['quality_detail'] = 'Could not calculate'

    # ── VOLATILITY FACTOR (lower = better) ──
    try:
        returns = hist_1y['Close'].pct_change().dropna()
        annual_vol = returns.std() * np.sqrt(252) * 100
        if annual_vol < 20: vol_score = 90
        elif annual_vol < 30: vol_score = 75
        elif annual_vol < 40: vol_score = 60
        elif annual_vol < 50: vol_score = 45
        elif annual_vol < 60: vol_score = 30
        else: vol_score = 15
        scores['volatility'] = vol_score
        scores['volatility_detail'] = f"Annual Volatility: {annual_vol:.1f}%"
    except Exception:
        scores['volatility'] = 50
        scores['volatility_detail'] = 'Could not calculate'

    # ── COMPOSITE FACTOR SCORE ──
    composite = (
        scores['momentum'] * 0.30 +
        scores['value'] * 0.25 +
        scores['quality'] * 0.30 +
        scores['volatility'] * 0.15
    )
    scores['composite'] = composite

    return scores


def calculate_sharpe_ratio(hist, risk_free_rate=0.05):
    """Calculate Sharpe Ratio"""
    returns = hist['Close'].pct_change().dropna()
    annual_return = returns.mean() * 252
    annual_vol = returns.std() * np.sqrt(252)
    sharpe = (annual_return - risk_free_rate) / annual_vol
    return sharpe, annual_return * 100, annual_vol * 100


def calculate_beta(hist_stock, hist_market):
    """Calculate Beta vs S&P 500"""
    try:
        stock_returns = hist_stock['Close'].pct_change().dropna()
        market_returns = hist_market['Close'].pct_change().dropna()
        aligned = pd.concat([stock_returns, market_returns], axis=1).dropna()
        aligned.columns = ['stock', 'market']
        covariance = aligned.cov().iloc[0, 1]
        market_variance = aligned['market'].var()
        beta = covariance / market_variance
        return beta
    except Exception:
        return None


def run_quant_analysis(ticker_symbol):
    ticker_symbol = ticker_symbol.upper().strip()
    print(f"\n🔢 Running quant analysis for {ticker_symbol}...")

    ticker = yf.Ticker(ticker_symbol)
    spy = yf.Ticker('SPY')

    print("  → Fetching data...")
    try:
        info = ticker.info
        hist_1y = ticker.history(period='1y')
        hist_5y = ticker.history(period='5y')
        hist_spy = spy.history(period='1y')
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return None

    current_price = hist_1y['Close'].iloc[-1] if not hist_1y.empty else None
    if current_price is None:
        print("  ⚠️  No price data")
        return None

    # ── SBC-ADJUSTED FCF ──
    print("  → Calculating SBC-adjusted FCF...")
    fcf_raw = info.get('freeCashflow', 0) or 0
    sbc = 0
    try:
        cashflow = ticker.cashflow
        if cashflow is not None and not cashflow.empty:
            sbc_keys = ['Stock Based Compensation', 'StockBasedCompensation',
                        'Share Based Compensation', 'ShareBasedCompensation']
            for key in sbc_keys:
                if key in cashflow.index:
                    sbc_val = cashflow.loc[key].iloc[0]
                    if pd.notna(sbc_val):
                        sbc = abs(float(sbc_val))
                        break
    except Exception:
        sbc = 0

    fcf = max(fcf_raw - sbc, 0) if fcf_raw > 0 else fcf_raw
    sbc_pct_fcf = (sbc / fcf_raw * 100) if fcf_raw > 0 else 0

    shares = info.get('sharesOutstanding', 0) or 0
    revenue_growth = info.get('revenueGrowth', 0.10) or 0.10
    earnings_growth = info.get('earningsGrowth', 0.10) or 0.10
    avg_growth = (revenue_growth + earnings_growth) / 2

    # Conservative / Base / Optimistic scenarios (using SBC-adjusted FCF)
    dcf_bear = calculate_dcf(fcf, max(avg_growth * 0.5, 0.02), 0.02, 0.12, shares) if fcf > 0 else None
    dcf_base = calculate_dcf(fcf, max(avg_growth, 0.05), 0.025, 0.10, shares) if fcf > 0 else None
    dcf_bull = calculate_dcf(fcf, min(avg_growth * 1.5, 0.30), 0.03, 0.09, shares) if fcf > 0 else None

    # ── Monte Carlo ──
    print("  → Monte Carlo simulation (1,000 runs)...")
    mc_results = run_monte_carlo(hist_1y) if not hist_1y.empty else None

    # ── Factor Scores ──
    print("  → Factor analysis...")
    factors = calculate_factor_scores(info, hist_1y, hist_5y)

    # ── Sharpe / Beta ──
    print("  → Risk metrics...")
    sharpe, annual_return, annual_vol = calculate_sharpe_ratio(hist_1y) if not hist_1y.empty else (None, None, None)
    beta = calculate_beta(hist_1y, hist_spy) if not hist_1y.empty and not hist_spy.empty else None

    # ── Max Drawdown ──
    try:
        rolling_max = hist_1y['Close'].cummax()
        drawdown = (hist_1y['Close'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        max_drawdown_5y = None
        if not hist_5y.empty:
            rm5 = hist_5y['Close'].cummax()
            dd5 = (hist_5y['Close'] - rm5) / rm5
            max_drawdown_5y = dd5.min() * 100
    except Exception:
        max_drawdown = None
        max_drawdown_5y = None

    # ── VaR ──
    try:
        returns_1y = hist_1y['Close'].pct_change().dropna()
        var_95 = np.percentile(returns_1y, 5) * 100
        var_99 = np.percentile(returns_1y, 1) * 100
    except Exception:
        var_95 = var_99 = None

    # ── Build Output ──
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f"\n\n---\n# QUANTITATIVE ANALYSIS — {ticker_symbol} — {now}")

    # Factor Scores
    lines.append("\n## 📊 FACTOR SCORES")
    lines.append(f"| Factor | Score | Grade | Detail |")
    lines.append(f"|---|---|---|---|")

    def grade(score):
        if score >= 80: return "A"
        elif score >= 70: return "B"
        elif score >= 60: return "C"
        elif score >= 50: return "D"
        else: return "F"

    lines.append(f"| Momentum | {factors['momentum']:.0f}/100 | {grade(factors['momentum'])} | {factors['momentum_detail']} |")
    lines.append(f"| Value | {factors['value']:.0f}/100 | {grade(factors['value'])} | {factors['value_detail']} |")
    lines.append(f"| Quality | {factors['quality']:.0f}/100 | {grade(factors['quality'])} | {factors['quality_detail']} |")
    lines.append(f"| Low Volatility | {factors['volatility']:.0f}/100 | {grade(factors['volatility'])} | {factors['volatility_detail']} |")
    lines.append(f"| **COMPOSITE** | **{factors['composite']:.0f}/100** | **{grade(factors['composite'])}** | Weighted: Mom 30% / Val 25% / Qual 30% / Vol 15% |")

    # DCF
    lines.append("\n---\n## 💰 DCF VALUATION")
    if dcf_base:
        lines.append(f"| Scenario | Growth Rate | Intrinsic Value | vs Current (${current_price:.2f}) | Upside/Downside |")
        lines.append(f"|---|---|---|---|---|")
        if dcf_bear:
            upside_bear = ((dcf_bear['intrinsic_value'] - current_price) / current_price) * 100
            lines.append(f"| 🐻 Bear Case | {max(avg_growth * 0.5, 0.02)*100:.1f}% | ${dcf_bear['intrinsic_value']:.2f} | {'Over' if upside_bear < 0 else 'Under'}valued | {upside_bear:+.1f}% |")
        if dcf_base:
            upside_base = ((dcf_base['intrinsic_value'] - current_price) / current_price) * 100
            lines.append(f"| 📊 Base Case | {max(avg_growth, 0.05)*100:.1f}% | ${dcf_base['intrinsic_value']:.2f} | {'Over' if upside_base < 0 else 'Under'}valued | {upside_base:+.1f}% |")
        if dcf_bull:
            upside_bull = ((dcf_bull['intrinsic_value'] - current_price) / current_price) * 100
            lines.append(f"| 🐂 Bull Case | {min(avg_growth * 1.5, 0.30)*100:.1f}% | ${dcf_bull['intrinsic_value']:.2f} | {'Over' if upside_bull < 0 else 'Under'}valued | {upside_bull:+.1f}% |")
        lines.append(f"\n*DCF Assumptions: WACC Bear 12% / Base 10% / Bull 9% | Terminal Growth 2-3% | Based on SBC-Adjusted FCF*")
        lines.append(f"*FCF (raw): ${fcf_raw/1e9:.2f}B | SBC: ${sbc/1e9:.2f}B | FCF (adj): ${fcf/1e9:.2f}B | SBC as % of raw FCF: {sbc_pct_fcf:.1f}% | Shares: {shares/1e9:.2f}B*")
    else:
        lines.append("⚠️ DCF not available — negative or zero Free Cash Flow")

    # Monte Carlo
    if mc_results:
        lines.append("\n---\n## 🎲 MONTE CARLO SIMULATION (1,000 runs | 1 Year)")
        lines.append(f"| Percentile | Price Target | Return |")
        lines.append(f"|---|---|---|")
        lines.append(f"| 90th (Best 10%) | ${mc_results['p90']:.2f} | {((mc_results['p90']-mc_results['current'])/mc_results['current']*100):+.1f}% |")
        lines.append(f"| 75th | ${mc_results['p75']:.2f} | {((mc_results['p75']-mc_results['current'])/mc_results['current']*100):+.1f}% |")
        lines.append(f"| 50th (Median) | ${mc_results['p50']:.2f} | {((mc_results['p50']-mc_results['current'])/mc_results['current']*100):+.1f}% |")
        lines.append(f"| 25th | ${mc_results['p25']:.2f} | {((mc_results['p25']-mc_results['current'])/mc_results['current']*100):+.1f}% |")
        lines.append(f"| 10th (Worst 10%) | ${mc_results['p10']:.2f} | {((mc_results['p10']-mc_results['current'])/mc_results['current']*100):+.1f}% |")
        lines.append(f"\n- **Probability of Positive Return (1Y):** {mc_results['prob_positive']:.1f}%")
        lines.append(f"- **Expected Value:** ${mc_results['mean']:.2f}")

    # Earnings Quality
    lines.append("\n---\n## 🔬 EARNINGS QUALITY")
    if fcf_raw > 0:
        if sbc_pct_fcf < 15:
            sbc_flag = "🟢 Clean — SBC not distorting FCF"
        elif sbc_pct_fcf < 30:
            sbc_flag = "🟡 Moderate — monitor SBC dilution"
        else:
            sbc_flag = "🔴 High — real FCF significantly lower than reported"
        lines.append(f"- **Reported FCF:** ${fcf_raw/1e9:.2f}B")
        lines.append(f"- **Stock-Based Compensation (SBC):** ${sbc/1e9:.2f}B")
        lines.append(f"- **SBC-Adjusted FCF:** ${fcf/1e9:.2f}B")
        lines.append(f"- **SBC as % of FCF:** {sbc_pct_fcf:.1f}% — {sbc_flag}")
    else:
        lines.append("- FCF data not available for earnings quality analysis")

    # Operating CF vs Net Income (accruals quality)
    try:
        op_cf = info.get('operatingCashflow', 0) or 0
        net_income = info.get('netIncomeToCommon', 0) or 0
        total_assets = info.get('totalAssets', 1) or 1
        if op_cf and net_income and total_assets:
            accruals_ratio = (net_income - op_cf) / total_assets
            if accruals_ratio < -0.05:
                accruals_flag = "🟢 High quality — cash earnings exceed accruals"
            elif accruals_ratio < 0.05:
                accruals_flag = "🟡 Neutral — normal accruals level"
            else:
                accruals_flag = "🔴 Low quality — accruals exceeding cash earnings"
            lines.append(f"- **Accruals Ratio:** {accruals_ratio:.3f} — {accruals_flag}")
    except Exception:
        pass

    # Risk Metrics
    lines.append("\n---\n## ⚠️ RISK METRICS")
    if sharpe is not None:
        lines.append(f"- **Sharpe Ratio (1Y):** {sharpe:.2f} {'🟢 Good' if sharpe > 1 else '🟡 Acceptable' if sharpe > 0.5 else '🔴 Poor'}")
        lines.append(f"- **Annual Return (1Y):** {annual_return:+.1f}%")
        lines.append(f"- **Annual Volatility:** {annual_vol:.1f}%")
    if beta is not None:
        lines.append(f"- **Beta vs S&P 500:** {beta:.2f} {'🟢 Low risk' if beta < 0.8 else '🟡 Market risk' if beta < 1.2 else '🔴 High risk'}")
    if max_drawdown is not None:
        lines.append(f"- **Max Drawdown (1Y):** {max_drawdown:.1f}%")
    if max_drawdown_5y is not None:
        lines.append(f"- **Max Drawdown (5Y):** {max_drawdown_5y:.1f}%")
    if var_95 is not None:
        lines.append(f"- **Value at Risk (95%):** {var_95:.2f}% daily | Meaning: on worst 5% of days, expect >{abs(var_95):.2f}% loss")
    if var_99 is not None:
        lines.append(f"- **Value at Risk (99%):** {var_99:.2f}% daily | Meaning: on worst 1% of days, expect >{abs(var_99):.2f}% loss")

    lines.append(f"\n*Quant analysis completed: {now}*")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 quant.py TICKER")
        sys.exit(1)

    ticker_symbol = sys.argv[1].upper().strip()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    data_file = os.path.join(data_dir, f"{ticker_symbol}_data.md")

    quant_output = run_quant_analysis(ticker_symbol)

    if quant_output:
        if os.path.exists(data_file):
            with open(data_file, 'a') as f:
                f.write(quant_output)
            print(f"\n✅ Quant analysis appended to: data/{ticker_symbol}_data.md")
        else:
            quant_file = os.path.join(data_dir, f"{ticker_symbol}_quant.md")
            with open(quant_file, 'w') as f:
                f.write(quant_output)
            print(f"\n✅ Quant analysis saved to: data/{ticker_symbol}_quant.md")

        print(f"\n🎯 Full data file ready. Open Claude Code and type:")
        print(f"   /stock-analyzer  →  .intake  →  paste ticker: {ticker_symbol}")


if __name__ == '__main__':
    main()
