# src/data_loader.py

import yfinance as yf
import pandas as pd

def get_ticker_data(ticker: str) -> yf.Ticker:
    """Return a yfinance Ticker object."""
    return yf.Ticker(ticker)

def get_balance_sheet(ticker: str) -> pd.DataFrame:
    """Return the most recent annual balance sheet as a DataFrame."""
    ticker_obj = get_ticker_data(ticker)
    bs = ticker_obj.balance_sheet
    return bs if not bs.empty else pd.DataFrame()

def get_income_statement(ticker: str) -> pd.DataFrame:
    """Return the most recent annual income statement as a DataFrame."""
    ticker_obj = get_ticker_data(ticker)
    is_df = ticker_obj.financials
    return is_df if not is_df.empty else pd.DataFrame()

def get_cash_flow(ticker: str) -> pd.DataFrame:
    """Return the most recent annual cash flow statement as a DataFrame."""
    ticker_obj = get_ticker_data(ticker)
    cf = ticker_obj.cashflow
    return cf if not cf.empty else pd.DataFrame()

def get_all_financials(ticker: str) -> dict:
    """Return all financials as a dictionary of DataFrames."""
    return {
        "balance_sheet": get_balance_sheet(ticker),
        "income_statement": get_income_statement(ticker),
        "cash_flow": get_cash_flow(ticker),
    }