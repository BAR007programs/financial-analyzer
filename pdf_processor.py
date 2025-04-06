import logging
from pathlib import Path
from typing import List, Dict, Union, Optional

import pandas as pd
import pdfplumber

# Optional imports
try:
    import camelot
except ImportError:
    camelot = None

try:
    from pdf2image import convert_from_path
    import pytesseract
    import cv2
    import numpy as np
except ImportError:
    convert_from_path = pytesseract = cv2 = np = None

logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Processes a financial PDF:
      - Validates file
      - Detects scanned vs digital
      - Extracts text and tables
      - Detects statement type
    """

    def __init__(self, table_flavor: str = "lattice", ocr_dpi: int = 300, poppler_path: Optional[str] = None):
        self.table_flavor = table_flavor
        self.ocr_dpi = ocr_dpi
        self.poppler_path = poppler_path
        self.statement_type: Optional[str] = None

    def validate_pdf(self, pdf_path: Path) -> bool:
        if not pdf_path.exists():
            raise FileNotFoundError(f"File not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF: {pdf_path}")
        return True

    def is_scanned(self, pdf_path: Path) -> bool:
        """Public method: True if first page has no digital text."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = pdf.pages[0].extract_text() or ""
            return not bool(text.strip())
        except Exception as e:
            logger.warning(f"Could not determine scanned status: {e}")
            return False

    def detect_statement_type(self, text: str) -> str:
        t = text.lower()
        if "balance sheet" in t:
            return "balance_sheet"
        if "income statement" in t or "profit and loss" in t:
            return "income_statement"
        if "cash flow" in t:
            return "cash_flow"
        return "unknown"

    def extract_text(self, pdf_path: Path) -> str:
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
        return "\n".join(pages)

    def extract_tables(self, pdf_path: Path) -> List[pd.DataFrame]:
        if camelot is None:
            logger.debug("Camelot not installed; skipping table extraction")
            return []
        try:
            tables = camelot.read_pdf(
                str(pdf_path),
                flavor=self.table_flavor,
                pages="all",
                strip_text="\n",
                suppress_stdout=True,
            )
            return [t.df for t in tables]
        except Exception as e:
            logger.warning(f"Table extraction failed: {e}")
            return []

    def _pdf_to_images(self, pdf_path: Path) -> List[np.ndarray]:
        if convert_from_path is None:
            raise RuntimeError("pdf2image not installed; cannot OCR")
        images = convert_from_path(str(pdf_path), dpi=self.ocr_dpi, poppler_path=self.poppler_path)
        return [cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR) for img in images]

    def process_scanned(self, pdf_path: Path) -> str:
        if pytesseract is None:
            raise RuntimeError("pytesseract not installed; cannot OCR")
        images = self._pdf_to_images(pdf_path)
        return "\n".join(pytesseract.image_to_string(img) for img in images)

    def process_financial_pdf(self, pdf_path: Union[str, Path]) -> Dict:
        path = Path(pdf_path)
        self.validate_pdf(path)

        # 1) Digital text
        text = self.extract_text(path)
        scanned = not bool(text.strip())
        if scanned:
            logger.info(f"No digital text in {path.name}; performing OCR")
            text = self.process_scanned(path)
            tables: List[pd.DataFrame] = []
        else:
            tables = self.extract_tables(path)

        self.statement_type = self.detect_statement_type(text)

        return {
            "path": path,
            "type": self.statement_type,
            "is_scanned": scanned,
            "text": text,
            "tables": tables,
        }
