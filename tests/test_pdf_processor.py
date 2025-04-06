# tests/test_pdf_processor.py
import pytest
from pathlib import Path
from pdf_processor import PDFProcessor

@pytest.fixture
def sample_pdf(tmp_path):
    # Use ReportLab to generate a minimal valid PDF
    from reportlab.pdfgen import canvas
    p = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(p))
    c.drawString(100, 750, "Hello, PDFProcessor")
    c.showPage()
    c.save()
    return p

def test_validate_pdf(sample_pdf):
    proc = PDFProcessor()
    # should not raise
    assert proc.validate_pdf(sample_pdf) is True

def test_is_scanned_false(sample_pdf):
    proc = PDFProcessor()
    assert proc.is_scanned(sample_pdf) is False

def test_extract_text(sample_pdf):
    proc = PDFProcessor()
    txt = proc.extract_text(sample_pdf)
    assert "Hello, PDFProcessor" in txt

def test_extract_tables_no_tables(sample_pdf):
    proc = PDFProcessor()
    tables = proc.extract_tables(sample_pdf)
    assert isinstance(tables, list) and tables == []

def test_process_financial_pdf(sample_pdf):
    proc = PDFProcessor()
    data = proc.process_financial_pdf(sample_pdf)
    assert data["path"] == sample_pdf
    assert "text" in data and "Hello, PDFProcessor" in data["text"]
    assert data["tables"] == []
    assert data["type"] in {"unknown", "income_statement", "balance_sheet", "cash_flow"}
    assert data["is_scanned"] is False
