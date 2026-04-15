#!/usr/bin/env python3
"""
technicals.py — Technical Analysis Calculator
Calculates all technical indicators and appends to the data file

Usage: python3 technicals.py AAPL
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import warnings
warnings.filterwarnings('ignore')


def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, sma, lower


def calculate_atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def find_support_resistance(hist, lookback=90):
    """Find key support and resistance levels"""
    recent = hist.tail(lookback)
    highs = recent['High'].values
    lows = recent['Low'].values
    closes = recent['Close'].values

    # Find local peaks and troughs
    resistance_levels = []
    support_levels = []

    for i in range(2, len(highs) - 2):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            resistance_levels.append(highs[i])
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            support_levels.append(lows[i])

    # Get top 3 levels, sorted
    resistance_levels = sorted(set([round(r, 2) for r in resistance_levels]), reverse=True)[:3]
    support_levels = sorted(set([round(s, 2) for s in support_levels]))[:3]

    return support_levels, resistance_levels


def signal_label(condition_bull, condition_bear=None):
    if condition_bull:
        return "🟢 Bullish"
    elif condition_bear is not None and condition_bear:
        return "🔴 Bearish"
    else:
        return "🟡 Neutral"


def calculate_technicals(ticker_symbol):
    ticker_symbol = ticker_symbol.upper().strip()
    print(f"\n📈 Calculating technicals for {ticker_symbol}...")

    ticker = yf.Ticker(ticker_symbol)

    # Get price history
    hist_1y = ticker.history(period='1y')
    hist_6m = ticker.history(period='6mo')
    hist_3m = ticker.history(period='3mo')
    hist_weekly = ticker.history(period='2y', interval='1wk')

    if hist_1y.empty:
        print("  ⚠️  No price history available")
        return None

    close = hist_1y['Close']
    high = hist_1y['High']
    low = hist_1y['Low']
    volume = hist_1y['Volume']
    current_price = close.iloc[-1]

    # ── Moving Averages ──
    sma_20 = close.rolling(20).mean().iloc[-1]
    sma_50 = close.rolling(50).mean().iloc[-1]
    sma_200 = close.rolling(200).mean().iloc[-1]
    ema_12 = close.ewm(span=12).mean().iloc[-1]
    ema_26 = close.ewm(span=26).mean().iloc[-1]

    # ── RSI ──
    rsi_14 = calculate_rsi(close, 14).iloc[-1]
    rsi_weekly = calculate_rsi(hist_weekly['Close'], 14).iloc[-1] if not hist_weekly.empty else None

    # ── MACD ──
    macd_line, signal_line, histogram = calculate_macd(close)
    macd_val = macd_line.iloc[-1]
    signal_val = signal_line.iloc[-1]
    hist_val = histogram.iloc[-1]
    hist_prev = histogram.iloc[-2]

    # ── Bollinger Bands ──
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(close)
    bb_upper_val = bb_upper.iloc[-1]
    bb_lower_val = bb_lower.iloc[-1]
    bb_width = ((bb_upper_val - bb_lower_val) / bb_mid.iloc[-1]) * 100

    # ── ATR ──
    atr = calculate_atr(high, low, close)
    atr_val = atr.iloc[-1]
    atr_pct = (atr_val / current_price) * 100

    # ── Volume Analysis ──
    vol_sma_20 = volume.rolling(20).mean().iloc[-1]
    vol_current = volume.iloc[-1]
    vol_ratio = vol_current / vol_sma_20
    vol_trend_5d = volume.tail(5).mean() / volume.tail(20).mean()

    # ── Trend Analysis ──
    above_sma20 = current_price > sma_20
    above_sma50 = current_price > sma_50
    above_sma200 = current_price > sma_200
    sma50_above_sma200 = sma_50 > sma_200  # Golden/Death cross

    # Price vs 52wk
    high_52wk = high.max()
    low_52wk = low.min()
    pct_from_high = ((current_price - high_52wk) / high_52wk) * 100
    pct_from_low = ((current_price - low_52wk) / low_52wk) * 100

    # ── Momentum ──
    mom_1m = ((current_price - close.iloc[-21]) / close.iloc[-21]) * 100 if len(close) > 21 else None
    mom_3m = ((current_price - close.iloc[-63]) / close.iloc[-63]) * 100 if len(close) > 63 else None
    mom_6m = ((current_price - close.iloc[-126]) / close.iloc[-126]) * 100 if len(close) > 126 else None

    # ── Support & Resistance ──
    support_levels, resistance_levels = find_support_resistance(hist_1y)

    # ── Trend Signal ──
    trend_score = sum([above_sma20, above_sma50, above_sma200, sma50_above_sma200])
    if trend_score >= 3:
        trend_signal = "🟢 Bullish"
        trend_desc = "Price above key MAs, uptrend intact"
    elif trend_score >= 2:
        trend_signal = "🟡 Neutral"
        trend_desc = "Mixed signals across moving averages"
    else:
        trend_signal = "🔴 Bearish"
        trend_desc = "Price below key MAs, downtrend"

    # ── RSI Signal ──
    if rsi_14 > 70:
        rsi_signal = "🔴 Overbought"
        rsi_desc = f"RSI {rsi_14:.1f} — extended, potential pullback"
    elif rsi_14 < 30:
        rsi_signal = "🟢 Oversold"
        rsi_desc = f"RSI {rsi_14:.1f} — deeply oversold, potential bounce"
    elif rsi_14 > 55:
        rsi_signal = "🟢 Bullish"
        rsi_desc = f"RSI {rsi_14:.1f} — bullish momentum, room to run"
    elif rsi_14 < 45:
        rsi_signal = "🔴 Bearish"
        rsi_desc = f"RSI {rsi_14:.1f} — weak momentum"
    else:
        rsi_signal = "🟡 Neutral"
        rsi_desc = f"RSI {rsi_14:.1f} — neutral zone"

    # ── MACD Signal ──
    macd_bullish = macd_val > signal_val
    macd_crossover = hist_val > 0 and hist_prev < 0
    macd_crossunder = hist_val < 0 and hist_prev > 0
    if macd_crossover:
        macd_signal = "🟢 Bullish Crossover"
        macd_desc = "MACD just crossed above signal — buy signal"
    elif macd_crossunder:
        macd_signal = "🔴 Bearish Crossover"
        macd_desc = "MACD just crossed below signal — sell signal"
    elif macd_bullish:
        macd_signal = "🟢 Bullish"
        macd_desc = "MACD above signal line"
    else:
        macd_signal = "🔴 Bearish"
        macd_desc = "MACD below signal line"

    # ── Volume Signal ──
    if vol_ratio > 1.5 and above_sma20:
        vol_signal = "🟢 Accumulation"
        vol_desc = f"Volume {vol_ratio:.1f}x avg — strong buying pressure"
    elif vol_ratio > 1.5 and not above_sma20:
        vol_signal = "🔴 Distribution"
        vol_desc = f"Volume {vol_ratio:.1f}x avg on down day — selling pressure"
    elif vol_ratio < 0.5:
        vol_signal = "🟡 Low Volume"
        vol_desc = f"Volume {vol_ratio:.1f}x avg — weak conviction"
    else:
        vol_signal = "🟡 Normal"
        vol_desc = f"Volume {vol_ratio:.1f}x avg — normal activity"

    # ── BB Signal ──
    if current_price > bb_upper_val:
        bb_signal = "🔴 Above Upper Band"
        bb_desc = "Overbought — potential mean reversion"
    elif current_price < bb_lower_val:
        bb_signal = "🟢 Below Lower Band"
        bb_desc = "Oversold — potential bounce"
    else:
        bb_pos = (current_price - bb_lower_val) / (bb_upper_val - bb_lower_val) * 100
        bb_signal = "🟡 Inside Bands"
        bb_desc = f"At {bb_pos:.0f}% of band width"

    # ── Overall Technical Verdict ──
    bull_signals = sum([
        trend_score >= 3,
        rsi_14 > 50 and rsi_14 < 70,
        macd_val > signal_val,
        vol_ratio > 1.0 and above_sma20,
        current_price > bb_mid.iloc[-1]
    ])

    if bull_signals >= 4:
        overall = "🟢 STRONG BUY SIGNAL"
    elif bull_signals == 3:
        overall = "🟢 BUY SIGNAL"
    elif bull_signals == 2:
        overall = "🟡 NEUTRAL — WAIT"
    elif bull_signals == 1:
        overall = "🔴 WEAK — CAUTION"
    else:
        overall = "🔴 SELL SIGNAL"

    # ── Timeframe Analysis ──
    # Weekly
    if not hist_weekly.empty:
        weekly_close = hist_weekly['Close']
        weekly_sma20 = weekly_close.rolling(20).mean().iloc[-1]
        weekly_rsi = calculate_rsi(weekly_close, 14).iloc[-1]
        weekly_trend = "Uptrend" if weekly_close.iloc[-1] > weekly_sma20 else "Downtrend"
        weekly_momentum = "Strong" if weekly_rsi > 55 else "Weak" if weekly_rsi < 45 else "Neutral"
    else:
        weekly_trend = "N/A"
        weekly_momentum = "N/A"
        weekly_rsi = None

    # Daily (from 3m)
    if not hist_3m.empty:
        daily_close = hist_3m['Close']
        daily_trend = "Uptrend" if daily_close.iloc[-1] > daily_close.rolling(20).mean().iloc[-1] else "Downtrend"
        daily_rsi = calculate_rsi(daily_close, 14).iloc[-1]
        daily_momentum = "Building" if daily_rsi > 55 else "Fading" if daily_rsi < 45 else "Neutral"
    else:
        daily_trend = "N/A"
        daily_momentum = "N/A"
        daily_rsi = None

    # ── Build Output ──
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f"\n\n---\n# TECHNICAL ANALYSIS — {ticker_symbol} — {now}")
    lines.append("\n## ⚡ QUICK READ (Traffic Lights)")
    lines.append(f"| Signal | Status | Detail |")
    lines.append(f"|---|---|---|")
    lines.append(f"| Trend | {trend_signal} | {trend_desc} |")
    lines.append(f"| Momentum (RSI) | {rsi_signal} | {rsi_desc} |")
    lines.append(f"| MACD | {macd_signal} | {macd_desc} |")
    lines.append(f"| Volume | {vol_signal} | {vol_desc} |")
    lines.append(f"| Bollinger Bands | {bb_signal} | {bb_desc} |")
    lines.append(f"\n**OVERALL TECHNICAL VERDICT: {overall}**")

    lines.append("\n---\n## 📊 SIGNAL TABLE (Detail)")
    lines.append(f"| Indicator | Value | Signal |")
    lines.append(f"|---|---|---|")
    lines.append(f"| Current Price | ${current_price:.2f} | — |")
    lines.append(f"| SMA 20 | ${sma_20:.2f} | {'🟢 Above' if above_sma20 else '🔴 Below'} |")
    lines.append(f"| SMA 50 | ${sma_50:.2f} | {'🟢 Above' if above_sma50 else '🔴 Below'} |")
    lines.append(f"| SMA 200 | ${sma_200:.2f} | {'🟢 Above' if above_sma200 else '🔴 Below'} |")
    lines.append(f"| EMA 12 | ${ema_12:.2f} | — |")
    lines.append(f"| EMA 26 | ${ema_26:.2f} | {'🟢 EMA12>EMA26' if ema_12>ema_26 else '🔴 EMA12<EMA26'} |")
    lines.append(f"| 50/200 Cross | {'Golden Cross ✅' if sma50_above_sma200 else 'Death Cross ❌'} | {'🟢' if sma50_above_sma200 else '🔴'} |")
    lines.append(f"| RSI (14) | {rsi_14:.1f} | {rsi_signal} |")
    lines.append(f"| RSI Weekly | {f'{rsi_weekly:.1f}' if rsi_weekly else 'N/A'} | — |")
    lines.append(f"| MACD Line | {macd_val:.3f} | — |")
    lines.append(f"| MACD Signal | {signal_val:.3f} | {macd_signal} |")
    lines.append(f"| MACD Histogram | {hist_val:.3f} | {'Expanding 🟢' if abs(hist_val)>abs(hist_prev) else 'Contracting 🟡'} |")
    lines.append(f"| BB Upper | ${bb_upper_val:.2f} | — |")
    lines.append(f"| BB Lower | ${bb_lower_val:.2f} | — |")
    lines.append(f"| BB Width | {bb_width:.1f}% | {'Wide 🔴' if bb_width>20 else 'Narrow 🟡' if bb_width<10 else 'Normal 🟢'} |")
    lines.append(f"| ATR (14) | ${atr_val:.2f} ({atr_pct:.1f}%) | Daily volatility range |")
    lines.append(f"| Volume vs Avg | {vol_ratio:.1f}x | {vol_signal} |")
    lines.append(f"| 52wk High | ${high_52wk:.2f} ({pct_from_high:.1f}% from here) | — |")
    lines.append(f"| 52wk Low | ${low_52wk:.2f} (+{pct_from_low:.1f}% from there) | — |")

    lines.append("\n### Momentum")
    if mom_1m: lines.append(f"- **1 Month:** {mom_1m:+.1f}%")
    if mom_3m: lines.append(f"- **3 Month:** {mom_3m:+.1f}%")
    if mom_6m: lines.append(f"- **6 Month:** {mom_6m:+.1f}%")

    lines.append("\n### Key Levels")
    lines.append(f"- **Resistance:** {' | '.join([f'${r:.2f}' for r in resistance_levels]) if resistance_levels else 'None identified'}")
    lines.append(f"- **Support:** {' | '.join([f'${s:.2f}' for s in support_levels]) if support_levels else 'None identified'}")
    lines.append(f"- **Entry Zone (ATR-based):** ${current_price - atr_val:.2f} — ${current_price + atr_val:.2f}")

    lines.append("\n---\n## 🕐 TIMEFRAME STACK (Multi-Timeframe View)")
    lines.append(f"| Timeframe | Trend | Momentum | RSI | Notes |")
    lines.append(f"|---|---|---|---|---|")
    lines.append(f"| Weekly | {weekly_trend} | {weekly_momentum} | {f'{weekly_rsi:.1f}' if weekly_rsi else 'N/A'} | Macro direction |")
    lines.append(f"| Daily | {daily_trend} | {daily_momentum} | {f'{daily_rsi:.1f}' if daily_rsi else 'N/A'} | Medium term setup |")
    lines.append(f"| Current | {'Above SMA20' if above_sma20 else 'Below SMA20'} | {'RSI '+str(round(rsi_14,1))} | {rsi_14:.1f} | Entry timing |")

    lines.append(f"\n*Technicals calculated: {now}*")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 technicals.py TICKER")
        sys.exit(1)

    ticker_symbol = sys.argv[1].upper().strip()

    # Check if data file exists
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    data_file = os.path.join(data_dir, f"{ticker_symbol}_data.md")

    technicals_output = calculate_technicals(ticker_symbol)

    if technicals_output:
        if os.path.exists(data_file):
            with open(data_file, 'a') as f:
                f.write(technicals_output)
            print(f"✅ Technicals appended to: data/{ticker_symbol}_data.md")
        else:
            tech_file = os.path.join(data_dir, f"{ticker_symbol}_technicals.md")
            with open(tech_file, 'w') as f:
                f.write(technicals_output)
            print(f"✅ Technicals saved to: data/{ticker_symbol}_technicals.md")

        print(f"   Next: python3 scripts/quant.py {ticker_symbol}")


if __name__ == '__main__':
    main()
