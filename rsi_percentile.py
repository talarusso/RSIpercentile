"""
Calculates 14-day RSI (sciclaw)

Version 20260307

@author: talarusso
"""

import sys
import yfinance as yf
import pandas as pd
from curl_cffi import requests as curl_requests
import ta


def get_rsi_percentiles(symbol):
    session = curl_requests.Session(impersonate="chrome124")

    tickerdata = yf.download(
        symbol,
        period="max",
        interval="1d",
        auto_adjust=False,
        progress=False,
        timeout=10,
        session=session,
    )

    if tickerdata.empty:
        raise ValueError(f"No data returned for symbol: {symbol}")

    # Remove multiindex if present
    if isinstance(tickerdata.columns, pd.MultiIndex):
        tickerdata.columns = tickerdata.columns.droplevel(1)

    close = tickerdata["Close"].squeeze()

    # Calculate RSI
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().dropna()

    current_percentile = int(round(rsi.iloc[-1]))

    percentiles = {
        "0.5th": rsi.quantile(0.005).round().astype(int),
        "2.5th": rsi.quantile(0.025).round().astype(int),
        "5th": rsi.quantile(0.05).round().astype(int),
        "95th": rsi.quantile(0.95).round().astype(int),
        "97.5th": rsi.quantile(0.975).round().astype(int),
    }

    return current_percentile, percentiles


def _parse_symbol_from_argv(argv):
    # Usage:
    #   rsi-percentile LMT
    # or:
    #   python rsi_percentile.py LMT
    if len(argv) >= 2 and argv[1].strip():
        return argv[1].upper().strip()
    return None


def main(argv=None):
    if argv is None:
        argv = sys.argv

    symbol = _parse_symbol_from_argv(argv)
    if symbol is None:
        symbol = input("Enter stock ticker: ").upper().strip()

    current_percentile, percentiles = get_rsi_percentiles(symbol)