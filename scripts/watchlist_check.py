#!/usr/bin/env python3
"""
watchlist_check.py — Daily Watchlist Monitor
Checks all tickers in watchlist.md for major signals
Sends Gmail alert if triggered (requires Gmail MCP or SMTP setup)

Usage: python3 watchlist_check.py
       python3 watchlist_check.py --email your@email.com
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
import re
import smtplib
import warnings
warnings.filterwarnings('ignore')


def read_watchlist(watchlist_path):
    """Parse tickers from watchlist.md"""
    tickers = []
    try:
        with open(watchlist_path, 'r') as f:
            content = f.read()
        # Find lines with ticker symbols (all caps, 1-5 chars)
        for line in content.split('\n'):
            matches = re.findall(r'\b([A-Z]{1,5})\b', line)
            for m in matches:
                if m not in ['N/A', 'MA', 'EMA', 'SMA', 'RSI', 'MACD', 'ATR', 'FCF', 'DCF', 'PE', 'PB', 'PS', 'ROE', 'ROA']:
                    if m not in tickers:
                        tickers.append(m)
    except Exception as e:
        print(f"⚠️  Could not read watchlist: {e}")
    return tickers


def check_signals(ticker_symbol):
    """Check for major buy/sell signals on a ticker"""
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period='3mo')
        info = ticker.info

        if hist.empty:
            return None

        close = hist['Close']
        volume = hist['Volume']
        current_price = close.iloc[-1]

        # Moving averages
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean()
        sma_200_hist = ticker.history(period='1y')['Close'].rolling(200).mean()
        sma_200 = sma_200_hist.iloc[-1] if not sma_200_hist.empty else None

        # RSI
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]

        # MACD
        ema12 = close.ewm(span=12).mean()
        ema26 = close.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal

        # Volume
        vol_avg = volume.rolling(20).mean().iloc[-1]
        vol_current = volume.iloc[-1]
        vol_ratio = vol_current / vol_avg

        # Signals detected
        alerts = []
        signal_strength = 0

        # Golden Cross
        if len(sma_50) > 1 and sma_200 is not None:
            sma_50_today = sma_50.iloc[-1]
            sma_50_yesterday = sma_50.iloc[-2]
            sma_200_yesterday = sma_200_hist.rolling(200).mean().iloc[-2] if len(sma_200_hist) > 1 else None
            if sma_200_yesterday and sma_50_today > sma_200 and sma_50_yesterday <= sma_200_yesterday:
                alerts.append("🚨 GOLDEN CROSS — 50MA crossed above 200MA")
                signal_strength += 3

        # RSI Oversold bounce
        if rsi < 30:
            alerts.append(f"📉 RSI OVERSOLD — {rsi:.1f} (potential bounce)")
            signal_strength += 2
        elif rsi > 75:
            alerts.append(f"📈 RSI OVERBOUGHT — {rsi:.1f} (potential pullback)")
            signal_strength += 1

        # MACD crossover
        if len(histogram) > 2:
            if histogram.iloc[-1] > 0 and histogram.iloc[-2] < 0:
                alerts.append("🟢 MACD BULLISH CROSSOVER")
                signal_strength += 2
            elif histogram.iloc[-1] < 0 and histogram.iloc[-2] > 0:
                alerts.append("🔴 MACD BEARISH CROSSOVER")
                signal_strength += 2

        # High volume breakout
        if vol_ratio > 2.0:
            direction = "UP" if current_price > close.iloc[-2] else "DOWN"
            alerts.append(f"🔥 HIGH VOLUME MOVE {direction} — {vol_ratio:.1f}x average volume")
            signal_strength += 2

        # Price crosses 200MA
        if sma_200 is not None:
            prev_close = close.iloc[-2]
            if current_price > sma_200 and prev_close <= sma_200:
                alerts.append(f"🟢 PRICE CROSSED ABOVE 200MA (${sma_200:.2f})")
                signal_strength += 2
            elif current_price < sma_200 and prev_close >= sma_200:
                alerts.append(f"🔴 PRICE CROSSED BELOW 200MA (${sma_200:.2f})")
                signal_strength += 2

        # 52-week high/low
        hist_1y = ticker.history(period='1y')
        if not hist_1y.empty:
            high_52wk = hist_1y['High'].max()
            low_52wk = hist_1y['Low'].min()
            if current_price >= high_52wk * 0.99:
                alerts.append(f"🏆 NEAR 52-WEEK HIGH (${high_52wk:.2f})")
                signal_strength += 1
            elif current_price <= low_52wk * 1.01:
                alerts.append(f"⚠️  NEAR 52-WEEK LOW (${low_52wk:.2f})")
                signal_strength += 1

        if not alerts:
            return None

        return {
            'ticker': ticker_symbol,
            'price': current_price,
            'rsi': rsi,
            'alerts': alerts,
            'signal_strength': signal_strength,
            'name': info.get('longName', ticker_symbol)
        }

    except Exception as e:
        print(f"  ⚠️  Error checking {ticker_symbol}: {e}")
        return None


def format_alert_email(results):
    """Format alerts for email"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []
    lines.append(f"STOCK ANALYZER — WATCHLIST ALERT")
    lines.append(f"Generated: {now}")
    lines.append("=" * 50)

    for r in results:
        lines.append(f"\n{r['ticker']} — {r['name']}")
        lines.append(f"Price: ${r['price']:.2f} | RSI: {r['rsi']:.1f} | Signal Strength: {r['signal_strength']}/10")
        for alert in r['alerts']:
            lines.append(f"  {alert}")
        lines.append("-" * 40)

    lines.append("\nGenerated by Stock Analyzer | stock-analyzer")
    return "\n".join(lines)


def save_alert_log(results, log_path):
    """Append alerts to a log file"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(log_path, 'a') as f:
        f.write(f"\n\n## Watchlist Check — {now}\n")
        if not results:
            f.write("No major signals detected.\n")
        else:
            for r in results:
                f.write(f"\n### {r['ticker']} — {r['name']}\n")
                f.write(f"- Price: ${r['price']:.2f} | RSI: {r['rsi']:.1f}\n")
                for alert in r['alerts']:
                    f.write(f"- {alert}\n")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, '..')
    watchlist_path = os.path.join(base_dir, 'notes', 'watchlist.md')
    log_path = os.path.join(base_dir, 'notes', 'alert-log.md')

    print(f"\n👁️  Watchlist Monitor — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    # Read watchlist
    tickers = read_watchlist(watchlist_path)
    if not tickers:
        print("⚠️  No tickers found in watchlist.md")
        print("   Add tickers to notes/watchlist.md first")
        sys.exit(0)

    print(f"Checking {len(tickers)} tickers: {', '.join(tickers)}\n")

    # Check each ticker
    results = []
    for ticker in tickers:
        print(f"  Checking {ticker}...", end=' ', flush=True)
        result = check_signals(ticker)
        if result:
            print(f"⚠️  {len(result['alerts'])} signal(s) found!")
            results.append(result)
        else:
            print("✓ No major signals")

    print(f"\n{'='*50}")
    print(f"Results: {len(results)} tickers with signals out of {len(tickers)} checked")

    if results:
        # Sort by signal strength
        results.sort(key=lambda x: x['signal_strength'], reverse=True)

        print("\n🚨 SIGNALS DETECTED:")
        for r in results:
            print(f"\n  {r['ticker']} (${r['price']:.2f})")
            for alert in r['alerts']:
                print(f"    {alert}")

        # Save to log
        save_alert_log(results, log_path)
        print(f"\n✅ Alert log updated: notes/alert-log.md")

        # Email alert if requested
        email = None
        for i, arg in enumerate(sys.argv):
            if arg == '--email' and i + 1 < len(sys.argv):
                email = sys.argv[i + 1]

        if email:
            print(f"\n📧 Sending email to {email}...")
            print("   (Configure SMTP in watchlist_check.py for real email alerts)")
            print("   Alternatively use Gmail MCP via .watchlist skill")

        # Print summary for Claude
        alert_text = format_alert_email(results)
        print(f"\n--- ALERT SUMMARY FOR CLAUDE ---")
        print(alert_text)

    else:
        save_alert_log([], log_path)
        print("\n✅ No major signals. Watchlist is quiet.")

    print(f"\nNext check: run python3 scripts/watchlist_check.py again")
    print("To automate: set up a cron job or use /schedule in Claude Code")


if __name__ == '__main__':
    main()
