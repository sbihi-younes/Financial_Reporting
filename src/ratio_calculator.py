# src/ratio_calculator.py
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import Optional

def safe_divide(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator in (None, 0):
        return None
    return round(numerator / denominator, 4)

def average(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None:
        return None
    return (a + b) / 2

def extract(df: DataFrame, item: str, date: datetime) -> Optional[float]:
    if item not in df.index or date not in df.columns:
        return None
    value = df.at[item, date]
    return None if pd.isna(value) else float(value)

def calculate_ratios(financials: dict, current_date: datetime, previous_date: datetime) -> dict:
    bs = financials["balance_sheet"]
    is_ = financials["income_statement"]
    cf = financials["cash_flow"]

    # Extract required values
    CA1 = extract(bs, "Current Assets", current_date)
    CL1 = extract(bs, "Current Liabilities", current_date)
    INV1 = extract(bs, "Inventory", current_date)
    CCE1 = extract(bs, "Cash And Cash Equivalents", current_date)
    OI1 = extract(bs, "Other Short Term Investments", current_date)

    GP1 = extract(is_, "Gross Profit", current_date)
    OI = extract(is_, "Operating Income", current_date)
    NI1 = extract(is_, "Net Income", current_date)
    TR1 = extract(is_, "Total Revenue", current_date)
    TA1 = extract(bs, "Total Assets", current_date)
    TA0 = extract(bs, "Total Assets", previous_date)
    SE1 = extract(bs, "Stockholders Equity", current_date)
    SE0 = extract(bs, "Stockholders Equity", previous_date)

    COGS1 = extract(is_, "Cost Of Revenue", current_date)
    INV0 = extract(bs, "Inventory", previous_date)
    REC1 = extract(bs, "Receivables", current_date)
    REC0 = extract(bs, "Receivables", previous_date)
    PAY1 = extract(bs, "Accounts Payable", current_date)
    PAY0 = extract(bs, "Accounts Payable", previous_date)

    TD1 = extract(bs, "Total Debt", current_date)
    LT_DEBT = extract(bs, "Long Term Debt", current_date)
    IE1 = extract(is_, "Interest Expense", current_date)
    TC1 = extract(bs, "Total Capitalization", current_date)
    OSO1 = extract(bs, "Ordinary Shares Number", current_date)

    FCF1 = extract(cf, "Free Cash Flow", current_date)
    OCF1 = extract(cf, "Operating Cash Flow", current_date) or extract(cf, "Cash Flow From Continuing Operating Activities", current_date)
    EBIT1 = extract(is_, "EBIT", current_date)
    IC1 = extract(bs, "Invested Capital", current_date)
    WC1 = (CA1 - CL1) if CA1 is not None and CL1 is not None else None
    NPPE1 = extract(bs, "Net PPE", current_date)

    # Turnovers for CCC
    inv_turnover = safe_divide(COGS1, average(INV1, INV0))
    rec_turnover = safe_divide(TR1, average(REC1, REC0))
    pay_turnover = safe_divide(COGS1, average(PAY1, PAY0))

    DIO = safe_divide(365, inv_turnover)
    DSO = safe_divide(365, rec_turnover)
    DPO = safe_divide(365, pay_turnover)
    CCC = DSO + DIO - DPO if all([DSO, DIO, DPO]) else None

    return {
        "Liquidity": {
            "Current Ratio": safe_divide(CA1, CL1),
            "Quick Ratio": safe_divide(CA1 - INV1 if CA1 and INV1 else None, CL1),
            "Cash Ratio": safe_divide((CCE1 or 0) + (OI1 or 0), CL1),
            "Operating Cash Flow Ratio": safe_divide(OCF1, CL1),
            "Cash Conversion Cycle": round(CCC, 2) if CCC is not None else None
        },
        "Profitability": {
            "Gross Profit Margin": safe_divide(GP1, TR1),
            "Operating Margin": safe_divide(OI, TR1),
            "Net Profit Margin": safe_divide(NI1, TR1),
            "Return on Assets (ROA)": safe_divide(NI1, average(TA1, TA0)),
            "Return on Equity (ROE)": safe_divide(NI1, average(SE1, SE0)),
            "EBIT Margin": safe_divide(EBIT1, TR1),
            "Return on Capital Employed (ROCE)": safe_divide(EBIT1, TA1 - CL1 if TA1 is not None and CL1 is not None else None)
        },
        "Efficiency": {
            "Inventory Turnover": inv_turnover,
            "Receivables Turnover": rec_turnover,
            "Payables Turnover": pay_turnover,
            "Asset Turnover": safe_divide(TR1, average(TA1, TA0)),
            "Working Capital Turnover": safe_divide(TR1, WC1),
            "Fixed Asset Turnover": safe_divide(TR1, NPPE1)
        },
        "Leverage": {
            "Debt-to-Equity": safe_divide(TD1, SE1),
            "Debt Ratio": safe_divide(TD1, TA1),
            "Interest Coverage": safe_divide(EBIT1, IE1),
            "Debt-to-Capital": safe_divide(TD1, TC1),
            "Equity Multiplier": safe_divide(TA1, SE1),
            "Capitalization Ratio (LT Debt)": safe_divide(LT_DEBT, LT_DEBT + SE1 if LT_DEBT is not None and SE1 is not None else None)
        },
        "Return & Valuation": {
            "Book Value per Share": safe_divide(SE1, OSO1),
            "Free Cash Flow Margin": safe_divide(FCF1, TR1),
            "Return on Invested Capital (ROIC)": safe_divide(EBIT1, IC1),
            "Earnings Per Share (EPS - Basic)": extract(is_, "Basic EPS", current_date),
            "Earnings Per Share (EPS - Diluted)": extract(is_, "Diluted EPS", current_date),
            "Cash Return on Assets (CROA)": safe_divide(OCF1, average(TA1, TA0)),
            # You can optionally add Free Cash Flow Yield with market cap passed externally
        }
    }