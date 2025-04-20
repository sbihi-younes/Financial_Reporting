import yfinance as yf

def get_extended_fundamental_data(ticker_symbol: str) -> dict:
    ticker = yf.Ticker(ticker_symbol)

    def safe_get(func):
        try:
            return func()
        except Exception:
            return None

    return {
        "analyst_price_targets": safe_get(ticker.get_analyst_price_targets),
        "recommendations": safe_get(lambda: ticker.get_recommendations().tail(5)),
        "eps_trend": safe_get(ticker.get_eps_trend),
        "earnings_estimate": safe_get(ticker.get_earnings_estimate),
        "revenue_estimate": safe_get(ticker.get_revenue_estimate),
        "growth_estimates": safe_get(ticker.get_growth_estimates),
    }