"""
main.py
-------
Entry point for the CSV Cleaner pipeline.

Run from the project root:
    python main.py

Reads the raw CSV from data/raw/, runs the full cleaning pipeline,
saves the cleaned CSV to data/cleaned/, and writes a summary report
alongside it.
"""

import os
import sys

import pandas as pd

from cleaner.loader import load_csv
from cleaner.cleaner import CSVCleaner
from cleaner.reporter import generate_report
from cleaner.exceptions import CSVCleanerError


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "data", "raw", "sales_data_raw.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "cleaned", "sales_data_cleaned.csv")
REPORT_FILE = os.path.join(BASE_DIR, "data", "cleaned", "cleaning_report.txt")


def run() -> None:
    """
    Execute the full CSV cleaning pipeline.

    Loads the raw CSV, runs each cleaning step in sequence, saves
    the cleaned file, and produces a human-readable summary report.
    All errors are caught and reported with clear messages rather
    than raw tracebacks.
    """
    print("=" * 60)
    print("  CSV CLEANER — Starting Pipeline")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Load
    # ------------------------------------------------------------------
    print(f"\nLoading: {INPUT_FILE}")
    try:
        raw_df = load_csv(INPUT_FILE)
    except CSVCleanerError as e:
        print(f"\n  ERROR: {e.message}")
        sys.exit(1)

    print(f"  Loaded {len(raw_df)} rows × {raw_df.shape[1]} columns")

    # ------------------------------------------------------------------
    # 2. Clean
    # ------------------------------------------------------------------
    print("\nCleaning...")
    try:
        pipeline = CSVCleaner(raw_df)
        cleaned_df = (
            pipeline
            .remove_duplicates()
            .standardise_text()
            .parse_numeric_columns()
            .validate_numeric_ranges()
            .standardise_dates()
            .validate_emails()
            .drop_rows_missing_required()
            .get_dataframe()
        )
    except CSVCleanerError as e:
        print(f"\n  ERROR during cleaning: {e.message}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # 3. Save cleaned CSV
    # ------------------------------------------------------------------
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    cleaned_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n  Cleaned data saved → {OUTPUT_FILE}")

    # ------------------------------------------------------------------
    # 4. Generate report
    # ------------------------------------------------------------------
    print("\nGenerating report...")
    generate_report(
        original_df=raw_df,
        cleaned_df=cleaned_df,
        cleaning_log=pipeline.log,
        output_path=REPORT_FILE,
        input_file=os.path.basename(INPUT_FILE),
    )

    # ------------------------------------------------------------------
    # 5. Final summary to console
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Input rows      : {len(raw_df)}")
    print(f"  Output rows     : {len(cleaned_df)}")
    print(f"  Rows removed    : {len(raw_df) - len(cleaned_df)}")
    print(f"  Cleaned file    : {OUTPUT_FILE}")
    print(f"  Report file     : {REPORT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    run()
