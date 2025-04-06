# setup.py
from setuptools import setup

setup(
    name="financial-analyzer",
    version="0.1.0",
    description="AI-powered financial PDF extractor",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Brian Rwabwogo",
    author_email="brianrwabogo@example.com",
    url="https://github.com/yourusername/financial-analyzer",
    py_modules=[
        "main",
        "pdf_processor",
        "analyzer",
        "verify_file",
    ],
    python_requires=">=3.10",
    install_requires=[
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
    ],
    entry_points={
        "console_scripts": [
            "financial-analyzer=main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
