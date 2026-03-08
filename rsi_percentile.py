"""
Calculates 14-day RSI

Version 20260308

@author: talarusso
"""

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
        session=session
    )

    if tickerdata.empty:
        raise ValueError(f"No data returned for symbol: {symbol}")

    # Remove multiindex if present
    if isinstance(tickerdata.columns, pd.MultiIndex):
        tickerdata.columns = tickerdata.columns.droplevel(1)

    close = tickerdata["Close"].squeeze()

    # Calculate RSI
    rsi = ta.momentum.RSIIndicator(close, window=14).rsi().dropna()
    
    current_rsi = float(rsi.iloc[-1])
    current_percentile = float((rsi <= current_rsi).mean() * 100)

    percentiles = {
        "0.5th": rsi.quantile(0.005).round().astype(int),
        "2.5th": rsi.quantile(0.025).round().astype(int),
        "5th": rsi.quantile(0.05).round().astype(int),
        "95th": rsi.quantile(0.95).round().astype(int),
        "97.5th": rsi.quantile(0.975).round().astype(int),
    }

    return current_rsi, current_percentile, percentiles


def _parse_symbol_from_argv(argv):
    # Usage:
    #   rsi-percentile LMT
    # or:
    #   python -m rsi_percentile LMT
    if len(argv) >= 2 and str(argv[1]).strip():
        return str(argv[1]).upper().strip()
    return None


def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv

    symbol = _parse_symbol_from_argv(argv)
    if symbol is None:
        symbol = input("Enter stock ticker: ").upper().strip()

    current_rsi, current_percentile, percentiles = get_rsi_percentiles(symbol)

    print(f"{symbol} RSI (14d): {current_rsi:.2f}")
    print(f"{symbol} RSI (14d) percentile: {current_percentile:.2f}\n")
    print(
        "Percentile cutoffs (historical RSI): "
        + ", ".join([f"{k}={v}" for k, v in percentiles.items()])
    )


if __name__ == "__main__":
    main()
