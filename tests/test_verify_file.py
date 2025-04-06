import pytest
from pathlib import Path
from verify_file import FileVerifier

# Generate a valid PDF using ReportLab
@pytest.fixture
def minimal_pdf(tmp_path):
    from reportlab.pdfgen import canvas

    p = tmp_path / "valid.pdf"
    c = canvas.Canvas(str(p))
    c.drawString(100, 750, "Test PDF")
    c.showPage()
    c.save()
    return p

@pytest.fixture
def non_pdf(tmp_path):
    p = tmp_path / "not_a_pdf.txt"
    p.write_text("just some text")
    return p

@pytest.fixture
def bad_header_pdf(tmp_path):
    p = tmp_path / "bad_header.pdf"
    p.write_bytes(b"%PFD- garbage\n%%EOF")
    return p

@pytest.fixture
def encrypted_pdf(minimal_pdf, tmp_path):
    import pikepdf
    out = tmp_path / "encrypted.pdf"
    pdf = pikepdf.open(str(minimal_pdf))
    pdf.save(
        str(out),
        encryption=pikepdf.Encryption(user="userpw", owner="ownpw", R=4)
    )
    return out

def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        FileVerifier.verify_pdf(tmp_path / "no.pdf")

def test_not_pdf(non_pdf):
    with pytest.raises(ValueError):
        FileVerifier.verify_pdf(non_pdf)

def test_bad_header(bad_header_pdf):
    with pytest.raises(ValueError):
        FileVerifier.verify_pdf(bad_header_pdf)

def test_encrypted_pdf(encrypted_pdf):
    with pytest.raises(ValueError):
        FileVerifier.verify_pdf(encrypted_pdf)

def test_valid_pdf(minimal_pdf):
    # Should not raise
    FileVerifier.verify_pdf(minimal_pdf)
