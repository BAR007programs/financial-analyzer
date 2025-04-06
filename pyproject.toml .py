[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "financial-analyzer"
version = "0.1.0"
description = "AI‑powered financial PDF extractor"
readme = "README.md"
authors = [
  { name="Brian Rwabwogo", email="brianrwabogo@example.com" }
]
license = { file="LICENSE" }
requires-python = ">=3.10"

dependencies = [
  "pandas",
  "pdfplumber",
  "camelot-py[cv]",
  "pytesseract",
  "pdf2image",
  "pikepdf",
  "numpy",
  "opencv-python",
  "pillow",
  "reportlab",
]

[project.scripts]
financial-analyzer = "main:main"
