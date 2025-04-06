# tests/test_cli.py
import subprocess
import sys
from pathlib import Path

def test_cli_end_to_end(tmp_path):
    # Generate a minimal PDF
    from reportlab.pdfgen import canvas
    pdf = tmp_path / "doc.pdf"
    c = canvas.Canvas(str(pdf))
    c.drawString(100, 750, "Revenue: 1234")
    c.showPage(); c.save()

    csv = tmp_path / "out.csv"
    cmd = [
        sys.executable, "main.py",
        str(pdf), str(csv),
        "--metrics", "revenue"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    content = Path(csv).read_text()
    assert "revenue" in content
    assert "1234" in content
