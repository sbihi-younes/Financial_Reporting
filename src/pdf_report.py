from fpdf import FPDF
from datetime import datetime
import os
import requests

# Optional: Ratio explanations
RATIO_EXPLANATIONS = {
    # Liquidity
    "Current Ratio": "Measures ability to cover short-term liabilities with current assets.",
    "Quick Ratio": "Measures liquidity without relying on inventory.",
    "Cash Ratio": "Measures immediate liquidity using cash and near-cash assets.",
    "Operating Cash Flow Ratio": "Shows ability to cover short-term liabilities using operating cash flow.",
    "Cash Conversion Cycle": "Time (in days) to convert inventory and receivables into cash, after paying suppliers.",

    # Profitability
    "Gross Profit Margin": "Shows how much of revenue is left after direct costs.",
    "Operating Margin": "Shows operational efficiency before interest and tax.",
    "Net Profit Margin": "Shows how much profit is generated from total revenue.",
    "Return on Assets (ROA)": "Shows how effectively the company uses its assets.",
    "Return on Equity (ROE)": "Indicates how well equity capital is used to generate profit.",
    "EBIT Margin": "Shows earnings before interest and taxes as a percentage of revenue.",
    "Return on Capital Employed (ROCE)": "Shows how efficiently capital employed is used to generate EBIT.",

    # Efficiency
    "Inventory Turnover": "Measures how many times inventory is sold per year.",
    "Receivables Turnover": "Shows how efficiently receivables are collected.",
    "Payables Turnover": "Shows how fast the company pays its suppliers.",
    "Asset Turnover": "Measures how efficiently assets generate revenue.",
    "Working Capital Turnover": "Shows how effectively working capital is used to generate sales.",
    "Fixed Asset Turnover": "Measures how efficiently fixed assets (e.g., PPE) generate revenue.",

    # Leverage
    "Debt-to-Equity": "Shows financial leverage via debt vs equity.",
    "Debt Ratio": "Percentage of assets financed by debt.",
    "Interest Coverage": "Shows how easily interest expenses are paid.",
    "Debt-to-Capital": "Debt as a share of total capital (debt + equity).",
    "Equity Multiplier": "Indicates financial leverage via total assets relative to equity.",
    "Capitalization Ratio (LT Debt)": "Long-term debt as a portion of total permanent capital (LT debt + equity).",

    # Return & Valuation
    "Book Value per Share": "Equity value on a per-share basis.",
    "Free Cash Flow Margin": "Shows what portion of revenue is actual free cash.",
    "Return on Invested Capital (ROIC)": "Shows return generated on invested funds.",
    "Earnings Per Share (EPS - Basic)": "Net income divided by basic shares.",
    "Earnings Per Share (EPS - Diluted)": "Net income per share including dilution.",
    "Cash Return on Assets (CROA)": "Shows how effectively assets generate cash from operations."
    # Note: Free Cash Flow Yield can be added here if implemented.
}

class PDFReport(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, "Company Financial Report", ln=True, align="C")
        self.ln(5)

    def add_cover_page(self, ticker: str, company_name: str, name: str, logo_url: str):
        self.add_page()
        self.set_font("Helvetica", "B", 22)
        self.ln(40)
        self.cell(0, 15, f"Financial Report for {company_name} ({ticker})", ln=True, align="C")

        self.set_font("Helvetica", size=14)
        self.ln(10)
        self.cell(0, 10, f"Author: {name}", ln=True, align="C")
        self.cell(0, 10, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=True, align="C")

        if logo_url:
            try:
                img_path = f"{ticker}_logo.png"
                with open(img_path, "wb") as f:
                    f.write(requests.get(logo_url).content)
                self.ln(20)
                self.image(img_path, x=80, w=50)
                os.remove(img_path)
            except Exception as e:
                print("Could not load logo:", e)

        self.add_page()

    def add_section_title(self, title):
        self.ln(5)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 30, 30)
        self.set_x(self.l_margin)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def add_paragraph(self, text):
        self.set_font("Helvetica", size=10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, text)
        self.ln(2)

    def add_key_values(self, data: dict, label_width=50):
        self.set_font("Helvetica", size=10)
        self.set_text_color(0, 0, 0)
        max_width = self.w - self.l_margin - self.r_margin

        for key, value in data.items():
            val = str(value)
            self.set_x(self.l_margin)
            if self.get_string_width(val) > max_width - label_width:
                self.set_font("Helvetica", "B", 10)
                self.cell(label_width, 8, f"{key}:", ln=True)
                self.set_font("Helvetica", "", 10)
                self.multi_cell(0, 8, val)
            else:
                self.set_font("Helvetica", "B", 10)
                self.cell(label_width, 8, f"{key}:", border=0)
                self.set_font("Helvetica", "", 10)
                self.cell(0, 8, val, ln=True)
        self.ln(4)

    def add_table(self, rows: list, col_widths=None):
        self.set_font("Helvetica", size=10)
        self.set_text_color(0, 0, 0)
        if not rows:
            return

        epw = self.w - 2 * self.l_margin
        if not col_widths:
            col_widths = [epw / len(rows[0])] * len(rows[0])

        self.set_fill_color(230, 230, 230)
        self.set_font("Helvetica", "B", 10)
        for header, width in zip(rows[0], col_widths):
            self.cell(width, 8, str(header), border=1, fill=True)
        self.ln()

        self.set_font("Helvetica", size=10)
        for row in rows[1:]:
            for datum, width in zip(row, col_widths):
                self.cell(width, 8, str(datum), border=1)
            self.ln()
        self.ln(4)

    def add_image(self, path, w=180):
        if os.path.exists(path):
            self.image(path, w=w)
            self.ln(5)

    def add_ratio_explanations(self, metrics: dict):
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(90, 90, 90)
        max_width = self.w - self.l_margin - self.r_margin
        for metric in metrics:
            explanation = RATIO_EXPLANATIONS.get(metric)
            if explanation:
                text = f"{metric}: {explanation}"
                self.set_x(self.l_margin)
                if self.get_string_width(text) > max_width:
                    self.multi_cell(0, 6, text)
                else:
                    self.cell(0, 6, text, ln=True)
        self.ln(2)

    def save(self, path):
        self.output(path)

def create_pdf_report(
    ticker: str,
    overview: dict,
    ratios: dict,
    chart_path: str,
    earnings: dict,
    options: dict,
    extended_data: dict,
    save_path="report.pdf",
    name="Analyst",
    logo_url=None
):
    pdf = PDFReport()
    company_name = overview.get("longName") or overview.get("name") or ticker
    pdf.add_cover_page(ticker=ticker, company_name=company_name, name=name, logo_url=logo_url)
    pdf.add_section_title("Company Overview")
    pdf.add_key_values(overview)

    pdf.add_section_title("Stock Price (Last 5 Years)")
    pdf.add_image(chart_path)

    for section, metrics in ratios.items():
        pdf.add_section_title(section)
        rows = [("Metric", "Value")] + [(k, f"{v:.2f}" if isinstance(v, float) else v) for k, v in metrics.items()]
        pdf.add_table(rows)
        pdf.add_ratio_explanations(metrics)

    pdf.add_section_title("Earnings Calendar")
    pdf.add_key_values(earnings)

    pdf.add_section_title("Options Summary")
    pdf.add_key_values({
        "Available Expirations": ", ".join(options['available_expirations'][:5]),
        "Nearest Expiry": options['nearest_expiry']
    })

    pdf.add_section_title("Extended Fundamentals")
    for label, data in extended_data.items():
        if data is None or (hasattr(data, 'empty') and data.empty):
            continue  # Skip None or empty DataFrames
        pdf.add_section_title(label)
        if isinstance(data, dict):
            pdf.add_key_values(data)
        elif hasattr(data, 'to_dict'):
            pdf.add_key_values(data.to_dict())
        else:
            pdf.add_paragraph(str(data))

    pdf.save(save_path)
    return save_path