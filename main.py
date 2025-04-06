#!/usr/bin/env python3
import argparse
import datetime
import logging
import os
import sys
from pathlib import Path

import pandas as pd

from verify_file import FileVerifier
from pdf_processor import PDFProcessor
from analyzer import FinancialAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Financial PDF → CSV extractor",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input_pdf", type=Path, help="Input PDF file")
    parser.add_argument("output_csv", type=Path, help="Output CSV file")
    parser.add_argument(
        "-i", "--interactive", action="store_true",
        help="Choose PDF interactively from ./test_files"
    )
    parser.add_argument(
        "-m", "--metrics", nargs="+", required=True,
        help="Metrics to extract (e.g. revenue expenses profit)"
    )
    parser.add_argument(
        "-p", "--period",
        help="Period to filter (e.g. '2023' or 'Q1'); auto‑detected if omitted"
    )
    parser.add_argument(
        "-s", "--statement-type",
        choices=["income_statement","balance_sheet","cash_flow"],
        help="Override detected statement type"
    )
    parser.add_argument("--poppler-path", help="Path to poppler binaries (for pdf2image)")
    parser.add_argument("--tesseract-cmd", help="Full path to tesseract executable")
    return parser.parse_args()

def find_pdfs(folder=Path("test_files")):
    return list(folder.glob("*.pdf"))

def select_pdf_interactive(pdfs):
    print("\nAvailable PDFs:")
    for i, p in enumerate(pdfs, 1):
        print(f"{i}. {p.name}")
    while True:
        choice = input("Number (0 to exit): ").strip()
        if choice == "0":
            sys.exit(0)
        if choice.isdigit() and 1 <= int(choice) <= len(pdfs):
            return pdfs[int(choice)-1]
        print("Invalid selection")

def main():
    args = parse_args()

    if args.interactive:
        pdfs = find_pdfs()
        if not pdfs:
            logger.error("No PDFs in test_files/")
            sys.exit(1)
        args.input_pdf = select_pdf_interactive(pdfs)

    # Verify
    try:
        FileVerifier.verify_pdf(args.input_pdf)
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        sys.exit(1)

    # Configure external binaries
    if args.tesseract_cmd:
        os.environ["TESSERACT_CMD"] = args.tesseract_cmd
    poppler_path = args.poppler_path or None

    # Ensure output dir
    if args.output_csv.parent:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing '{args.input_pdf.name}'")
    processor = PDFProcessor(poppler_path=poppler_path)
    try:
        pdf_data = processor.process_financial_pdf(args.input_pdf)
    except Exception as e:
        logger.error(f"PDF processing failed: {e}")
        sys.exit(1)

    # Statement type override or inference
    if args.statement_type:
        stype = args.statement_type
    else:
        stype = None

    analyzer = FinancialAnalyzer(pdf_data["tables"] or pdf_data["text"])
    df = analyzer.extract_metrics(args.metrics, args.period)

    # Auto‑infer statement type if not overridden
    if not stype:
        if df.get("revenue", pd.NA).notna().any():
            stype = "income_statement"
        elif df.get("assets", pd.NA).notna().any() or df.get("liabilities", pd.NA).notna().any():
            stype = "balance_sheet"
        elif df.get("profit", pd.NA).notna().any():
            stype = "income_statement"
        else:
            stype = "unknown"
    logger.info(f"Statement type: {stype}")

    # Determine period: CLI > detected > current year
    detected = analyzer.detect_period(pdf_data["text"] or "")
    period = args.period or detected or str(datetime.datetime.now().year)

    # Attach metadata
    df["statement_type"] = stype
    df["period"] = period

    # Save
    try:
        df.to_csv(args.output_csv, index=False)
    except Exception as e:
        logger.error(f"Failed to write CSV: {e}")
        sys.exit(1)

    logger.info(f"Results saved to {args.output_csv}")
    print(df.head().to_markdown(tablefmt="grid"))

if __name__ == "__main__":
    main()
