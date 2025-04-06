# tests/test_verify_file.py
import pytest
from pathlib import Path
from verify_file import FileVerifier

@pytest.fixture
def non_pdf(tmp_path):
    p = tmp_path / "not_a_pdf.txt"
    p.write_text("just some text")
    return p

@pytest.fixture
def bad_header_pdf(tmp_path):
    p = tmp_path / "bad_header.pdf"
    # Wrong PDF header
    p.write_bytes(b"%PFD- garbage\n%%EOF")
    return p

@pytest.fixture
def minimal_pdf(tmp_path):
    p = tmp_path / "valid.pdf"
    # Minimal valid PDF
    p.write_bytes(
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog >>\nendobj\n"
        b"xref\n0 1\n0000000000 65535 f \n"
        b"trailer\n<< /Root 1 0 R >>\n"
        b"startxref\n9\n%%EOF"
    )
    return p

@pytest.fixture
def encrypted_pdf(minimal_pdf, tmp_path):
    out = tmp_path / "encrypted.pdf"
    import pikepdf
    pdf = pikepdf.open(str(minimal_pdf))
    pdf.save(
        str(out),
        encryption=pikepdf.Encryption(user="userpw", owner="ownpw", R=4)
    )
    return out

def test_missing_file(tmp_path):
    missing = tmp_path / "no.pdf"
    with pytest.raises(FileNotFoundError):
        FileVerifier.verify_pdf(missing)

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
