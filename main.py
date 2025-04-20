from datetime import datetime
from src.data_loader import get_all_financials
from src.utils import get_two_closest_columns
from src.ratio_calculator import calculate_ratios
from src.report_builder import (
    get_company_overview,
    plot_stock_price,
    get_dividends_and_splits,
    get_earnings_calendar,
    get_options_summary
)
from src.extended_data import get_extended_fundamental_data
from src.pdf_report import create_pdf_report

# Get input from user
ticker = input("Enter a stock ticker (e.g. AAPL): ").strip().upper()
date_input = input("Enter a reference date (YYYY-MM-DD): ").strip()

try:
    reference_date = datetime.strptime(date_input, "%Y-%m-%d")
except ValueError:
    print("Invalid date format. Please use YYYY-MM-DD.")
    exit(1)

# Load financial data
financials = get_all_financials(ticker)
bs = financials["balance_sheet"]
current_date, previous_date = get_two_closest_columns(bs, reference_date)

if not current_date or not previous_date:
    print("Not enough financial data around the selected date.")
    exit(1)

# Collect all sections
ratios = calculate_ratios(financials, current_date, previous_date)
info = get_company_overview(ticker)
chart_path = plot_stock_price(ticker, reference_date)
divs_splits = get_dividends_and_splits(ticker)
earnings = get_earnings_calendar(ticker)
options = get_options_summary(ticker)
extended_data = get_extended_fundamental_data(ticker)

# Enhance overview with dividend and split history
info["Latest Dividends"] = ", ".join([
    f"{d.date().isoformat()}: {v}" for d, v in divs_splits['dividends'].tail().items()
])
info["Stock Splits"] = ", ".join([
    f"{d.date().isoformat()}: {v}" for d, v in divs_splits['splits'].tail().items()
])

# Optional: Generate logo URL
domain = info.get("website", "").replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
logo_url = f"https://logo.clearbit.com/{domain}" if domain else None

# Generate the final PDF report
pdf_path = create_pdf_report(
    ticker=ticker,
    overview=info,
    ratios=ratios,
    chart_path=chart_path,
    earnings=earnings,
    options=options,
    extended_data=extended_data,
    save_path=f"{ticker}_report.pdf",
    name="Younes Sbihi",
    logo_url=logo_url
)

print(f"PDF report saved to: {pdf_path}")