# tests/test_financial_analyzer.py
import pytest
import pandas as pd
from analyzer import FinancialAnalyzer

@pytest.fixture
def sample_table():
    # Create a DataFrame mimicking a simple income statement
    df = pd.DataFrame({
        "Period": ["2023", "2022"],
        "Revenue": ["1,000", "900"],
        "Expenses": ["400", "350"],
        "Net Profit": ["600", "550"]
    })
    return [df]

def test_extract_revenue_from_table(sample_table):
    fa = FinancialAnalyzer(sample_table)
    df = fa.extract_metrics(["revenue"], period="2023")
    assert df.loc[0, "revenue"] == 1000.0

def test_extract_expenses_from_table(sample_table):
    fa = FinancialAnalyzer(sample_table)
    df = fa.extract_metrics(["expenses"], period="2022")
    assert df.loc[0, "expenses"] == 350.0

def test_extract_profit_from_table(sample_table):
    fa = FinancialAnalyzer(sample_table)
    df = fa.extract_metrics(["profit"], period="2023")
    # “Net Profit” column maps to “profit”
    assert df.loc[0, "profit"] == 600.0

def test_text_fallback():
    text = "Total Revenue: 2,500\nTotal Expenses: 1,000\nNet Income: 1,500"
    fa = FinancialAnalyzer(text)
    df = fa.extract_metrics(["revenue", "expenses", "profit"])
    assert df.loc[0, "revenue"] == 2500.0
    assert df.loc[0, "expenses"] == 1000.0
    assert df.loc[0, "profit"] == 1500.0

def test_unknown_metric():
    fa = FinancialAnalyzer("some random text")
    df = fa.extract_metrics(["foobar"])
    # unknown metric yields NA
    assert pd.isna(df.loc[0, "foobar"])
