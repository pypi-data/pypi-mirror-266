import numpy as np
import pandas as pd
import stock_loader
from mfoci.response_vars.stock_return_vars import load_stock_returns


def load_volatility_index(
    ticker="^VIX", source_db="yfinance", start_date="2004-01-01", end_date="2024-01-01"
):
    """
    Load VIX index data

    :return: pd.DataFrame
    """
    if source_db == "eikon":
        conf = stock_loader.Conf("other")
        loader = stock_loader.DataLoader(conf)
        df = loader.load(file_pattern=ticker)[ticker]
        col_dict = {"DATE": "Date", "CLOSE": "Close"}
        df = df[[*col_dict]].rename(columns=col_dict).copy()
        df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
        df.set_index("Date", inplace=True)
        df.rename({"Close": ticker}, axis=1, inplace=True)
    else:
        df = load_stock_returns([ticker], start_date=start_date)
    df[ticker] = df[ticker].apply(np.log).diff()
    df.dropna(inplace=True)
    return df
