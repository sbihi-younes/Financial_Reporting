# src/report_builder.py

import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os


def get_company_overview(ticker: str) -> dict:
    """Fetch basic metadata and company profile info."""
    info = yf.Ticker(ticker).info
    return {
        "name": info.get("longName", "N/A"),
        "summary": info.get("longBusinessSummary", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "website": info.get("website", "N/A"),
        "marketCap": info.get("marketCap", "N/A"),
    }


def plot_stock_price(ticker: str, reference_date: datetime, save_path: str = "stock_chart.png") -> str:
    """Plot the stock price for the past 5 years and save as an image."""
    end_date = reference_date
    start_date = end_date - timedelta(days=5 * 365)

    ticker_obj = yf.Ticker(ticker)
    hist = ticker_obj.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

    if hist.empty:
        raise ValueError("No historical price data available for the given range.")

    plt.figure(figsize=(10, 4))
    plt.plot(hist.index, hist['Close'], label="Close Price")
    plt.title(f"{ticker} Stock Price (Last 5 Years)")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    return save_path


def get_dividends_and_splits(ticker: str) -> dict:
    """Retrieve historical dividends and stock splits."""
    ticker_obj = yf.Ticker(ticker)
    return {
        "dividends": ticker_obj.dividends,
        "splits": ticker_obj.splits
    }


def get_news(ticker: str, max_items: int = 5) -> list:
    """Get recent news headlines."""
    ticker_obj = yf.Ticker(ticker)
    return ticker_obj.news[:max_items] if ticker_obj.news else []


def get_earnings_calendar(ticker: str) -> dict:
    """Return earnings calendar data: next earnings date, EPS estimate, last reported EPS."""
    ticker_obj = yf.Ticker(ticker)
    calendar = ticker_obj.calendar

    next_earnings_date = "N/A"
    eps_estimate = "N/A"

    if isinstance(calendar, dict):
        if "Earnings Date" in calendar:
            next_earnings_date = calendar["Earnings Date"][0]
        if "EPS Estimate" in calendar:
            eps_estimate = calendar["EPS Estimate"][0]

    # We drop last_reported_eps (deprecated)
    return {
        "next_earnings_date": next_earnings_date,
        "eps_estimate": eps_estimate,
        "last_reported_eps": "N/A"  # deprecated, optional to remove from UI
    }


def get_options_summary(ticker: str) -> dict:
    """Return available option expiry dates and option chain data for the nearest expiry."""
    ticker_obj = yf.Ticker(ticker)
    options = ticker_obj.options

    if not options:
        return {"available_expirations": [], "calls": None, "puts": None}

    expiry = options[0]
    chain = ticker_obj.option_chain(expiry)

    return {
        "available_expirations": options,
        "nearest_expiry": expiry,
        "calls": chain.calls,
        "puts": chain.puts
    }
