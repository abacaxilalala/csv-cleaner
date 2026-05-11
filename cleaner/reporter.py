"""
reporter.py
-----------
Generates a before/after cleaning summary report.

The reporter is intentionally kept separate from the cleaner — its only
job is to take the original DataFrame, the cleaned DataFrame, and the
cleaning log, and produce a human-readable report. This separation means
the report format can change without touching any cleaning logic.

Output is a plain-text .txt file that any client can open immediately.
"""

from datetime import datetime

import pandas as pd


def generate_report(
    original_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    cleaning_log: list[dict],
    output_path: str,
    input_file: str,
) -> None:
    """
    Write a cleaning summary report to a text file.

    The report contains three sections:
      1. Overview — file names, timestamp, row/column counts.
      2. Cleaning steps — each step with a description and count.
      3. Column summary — per-column null counts before and after.

    Parameters
    ----------
    original_df : pd.DataFrame
        The raw DataFrame before any cleaning.
    cleaned_df : pd.DataFrame
        The DataFrame after the full cleaning pipeline.
    cleaning_log : list[dict]
        The log produced by CSVCleaner, where each entry has keys
        'step', 'description', and 'affected'.
    output_path : str
        Full path where the report .txt file should be saved.
    input_file : str
        The original filename, used for display in the report header.
    """
    lines = []
    sep = "=" * 60

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    lines += [
        sep,
        "  CSV CLEANER — DATA CLEANING REPORT",
        sep,
        f"  Input file   : {input_file}",
        f"  Generated at : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------
    rows_removed = len(original_df) - len(cleaned_df)
    pct_kept = (len(cleaned_df) / len(original_df) * 100) if len(original_df) else 0

    lines += [
        "  OVERVIEW",
        "-" * 60,
        f"  Rows before cleaning  : {len(original_df):>6}",
        f"  Rows after cleaning   : {len(cleaned_df):>6}",
        f"  Rows removed          : {rows_removed:>6}",
        f"  Data retained         : {pct_kept:>5.1f}%",
        f"  Columns before        : {original_df.shape[1]:>6}",
        f"  Columns after         : {cleaned_df.shape[1]:>6}",
        "",
    ]

    # ------------------------------------------------------------------
    # Cleaning steps
    # ------------------------------------------------------------------
    lines += [
        "  CLEANING STEPS PERFORMED",
        "-" * 60,
    ]

    for i, entry in enumerate(cleaning_log, 1):
        affected_str = f"({entry['affected']} affected)"
        lines.append(f"  {i:>2}. {entry['description']:<45} {affected_str}")

    lines.append("")

    # ------------------------------------------------------------------
    # Missing values — before vs after
    # ------------------------------------------------------------------
    lines += [
        "  MISSING VALUES — BEFORE vs AFTER",
        "-" * 60,
        f"  {'Column':<20} {'Before':>8}  {'After':>8}  {'Resolved':>10}",
        f"  {'-'*20} {'-'*8}  {'-'*8}  {'-'*10}",
    ]

    for col in original_df.columns:
        before_null = int(original_df[col].isna().sum())
        if col in cleaned_df.columns:
            after_null = int(cleaned_df[col].isna().sum())
        else:
            after_null = 0
        resolved = before_null - after_null
        lines.append(
            f"  {col:<20} {before_null:>8}  {after_null:>8}  {resolved:>+10}"
        )

    # New columns added during cleaning
    new_cols = set(cleaned_df.columns) - set(original_df.columns)
    for col in sorted(new_cols):
        lines.append(f"  {col:<20} {'(new)':>8}  {int(cleaned_df[col].isna().sum()):>8}  {'—':>10}")

    lines.append("")

    # ------------------------------------------------------------------
    # Numeric summary (cleaned data)
    # ------------------------------------------------------------------
    numeric_cols = cleaned_df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        lines += [
            "  NUMERIC SUMMARY (CLEANED DATA)",
            "-" * 60,
            f"  {'Column':<20} {'Min':>10}  {'Max':>10}  {'Mean':>10}  {'Nulls':>6}",
            f"  {'-'*20} {'-'*10}  {'-'*10}  {'-'*10}  {'-'*6}",
        ]
        for col in numeric_cols:
            series = cleaned_df[col]
            lines.append(
                f"  {col:<20} "
                f"{series.min():>10.2f}  "
                f"{series.max():>10.2f}  "
                f"{series.mean():>10.2f}  "
                f"{int(series.isna().sum()):>6}"
            )
        lines.append("")

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    lines += [
        sep,
        "  END OF REPORT",
        sep,
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"  Report saved → {output_path}")
