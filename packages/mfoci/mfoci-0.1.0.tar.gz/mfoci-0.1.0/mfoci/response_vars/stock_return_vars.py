import pandas as pd
import yfinance as yf


def load_stock_returns(tickers, start_date="2013-01-01", end_date="2024-01-01"):
    """
    Load stock returns for a list of tickers from Yahoo Finance.
    """
    data = {}
    for ticker in tickers:
        data[ticker] = yf.download(ticker, start=start_date, end=end_date)["Close"]
    return pd.DataFrame(data)
