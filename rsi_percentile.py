"""
Calculates 14-day RSI

Version 20260307

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
    
    current_percentile = int(round(rsi.iloc[-1]))

    percentiles = {
        "0.5th":  rsi.quantile(0.005).round().astype(int),
        "2.5th":  rsi.quantile(0.025).round().astype(int),
        "5th":    rsi.quantile(0.05).round().astype(int),
        "95th":   rsi.quantile(0.95).round().astype(int),
        "97.5th": rsi.quantile(0.975).round().astype(int)
    }

    return current_percentile, percentiles


def main():
    symbol = input("Enter stock ticker: ").upper().strip()

    current_percentile, percentiles = get_rsi_percentiles(symbol)

    print(f"\nRSI percentile thresholds for {symbol}\n")
    print(f"Current 14-day RSI for {symbol}: {current_percentile}\n")
    
    for key, value in percentiles.items():
        print(f"{key} percentile: {value}")

    print()


if __name__ == "__main__":
    main()
