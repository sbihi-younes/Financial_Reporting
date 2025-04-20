# src/utils.py

from datetime import datetime
from pandas import DataFrame
from typing import Optional, Tuple

def format_currency(value: float) -> str:
    """Formats numeric values as currency with M/B suffix."""
    if value is None:
        return "N/A"
    if value >= 1e9:
        return f"${value / 1e9:.2f}B"
    elif value >= 1e6:
        return f"${value / 1e6:.2f}M"
    else:
        return f"${value:,.0f}"

def get_two_closest_columns(df: DataFrame, reference_date: datetime) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Find the two closest reporting dates in the DataFrame:
    - The most recent column before or on the reference_date
    - The closest column about one year earlier
    """
    if df.empty or not hasattr(df, "columns"):
        return None, None

    dates = sorted(df.columns, reverse=True)
    latest = next((d for d in dates if d <= reference_date), None)

    if not latest:
        return None, None

    one_year_back = latest.replace(year=latest.year - 1)
    prev = min(
        (d for d in dates if d < latest),
        key=lambda d: abs((d - one_year_back).days),
        default=None
    )

    return latest, prev

def print_statement_by_date(df: DataFrame, title: str, reference_date: datetime) -> None:
    """Print statement values for the closest two dates around the reference date."""
    latest, prev = get_two_closest_columns(df, reference_date)

    if latest is None or prev is None:
        print(f"\n{title} — Not enough data around {reference_date.date()}")
        return

    print(f"\n📄 {title} (Reporting dates: {latest.date()} vs {prev.date()})")
    subset = df[[latest, prev]].dropna(how="all")

    for item, row in subset.iterrows():
        val_latest = format_currency(row[latest])
        val_prev = format_currency(row[prev])
        print(f"- {item}: {val_latest} (prev: {val_prev})")