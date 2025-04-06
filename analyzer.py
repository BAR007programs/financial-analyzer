import logging
import re
from typing import List, Union, Optional

import pandas as pd

logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    """
    Extracts financial metrics and auto‑detects period from text if not provided.
    """

    FINANCIAL_TERMS = {
        "revenue": ["revenue", "sales", "income", "turnover"],
        "expenses": ["expense", "cost", "cogs", "operating"],
        "profit": ["profit", "net income", "net profit", "ebitda"],
        "assets": ["asset", "property", "inventory"],
        "liabilities": ["liabilit", "debt", "payable", "loan"],
    }

    METRIC_REGEX = {
        metric: re.compile(
            rf"(?P<term>{'|'.join(re.escape(t) for t in terms)})s?\s*[:\-–]\s*(?P<value>[\d,]+(?:\.\d+)?)",
            re.IGNORECASE,
        )
        for metric, terms in FINANCIAL_TERMS.items()
    }

    PERIOD_REGEX = re.compile(r"\b(20\d{2})\b")

    def __init__(self, extracted_data: Union[List[pd.DataFrame], str]):
        if isinstance(extracted_data, list):
            self.tables = extracted_data
            self.text: Optional[str] = None
        elif isinstance(extracted_data, str):
            self.text = extracted_data
            self.tables: List[pd.DataFrame] = []
        else:
            raise ValueError("extracted_data must be list of DataFrames or raw text")

    def extract_metrics(self, metrics: List[str], period: Optional[str] = None) -> pd.DataFrame:
        results = {}
        for metric in metrics:
            key = metric.lower()
            try:
                results[metric] = self._extract_metric(key, period)
            except ValueError:
                logger.warning(f"Metric '{metric}' not found; using NA")
                results[metric] = pd.NA
        # 'period' column will be added in main.py
        return pd.DataFrame([results])

    def _extract_metric(self, metric: str, period: Optional[str]) -> float:
        # 1) Table-based
        for df in self.tables:
            cols = [str(c).lower() for c in df.columns]
            for idx, col in enumerate(cols):
                if any(term in col for term in self.FINANCIAL_TERMS.get(metric, [metric])):
                    series = df.iloc[:, idx]
                    if period and "period" in cols:
                        mask = df.iloc[:, cols.index("period")].astype(str).str.contains(period, case=False, na=False)
                        series = series[mask]
                    for val in series:
                        num = self._to_number(val)
                        if num is not None:
                            return num

        # 2) Text-based
        if self.text:
            regex = self.METRIC_REGEX.get(metric)
            if regex:
                m = regex.search(self.text)
                if m:
                    num = self._to_number(m.group("value"))
                    if num is not None:
                        return num

        raise ValueError(f"Metric '{metric}' not found")

    def detect_period(self, text: str) -> Optional[str]:
        m = self.PERIOD_REGEX.search(text)
        return m.group(1) if m else None

    @staticmethod
    def _to_number(val) -> Optional[float]:
        if pd.isna(val):
            return None
        s = re.sub(r"[^\d.]", "", str(val))
        try:
            return float(s)
        except ValueError:
            return None
