"""
cleaner.py
----------
Core cleaning pipeline for the CSV Cleaner package.

The CSVCleaner class implements a chainable cleaning pipeline — each
method fixes one specific data quality problem and returns self, so
calls can be composed in a readable sequence:

    cleaned_df = (
        CSVCleaner(df)
        .remove_duplicates()
        .standardise_text()
        .parse_numeric_columns()
        .validate_numeric_ranges()
        .standardise_dates()
        .validate_emails()
        .drop_rows_missing_required()
        .get_dataframe()
    )

Each step logs what it changed so the reporter can produce a clear
before/after summary.
"""

import re
from datetime import datetime

import pandas as pd

from .exceptions import MissingColumnError


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Columns that must contain a valid number after cleaning.
NUMERIC_COLUMNS = ["quantity", "unit_price"]

# Known valid ranges per column. Rows outside these are flagged/removed.
NUMERIC_RANGES = {
    "quantity": (1, 10_000),
    "unit_price": (0.01, 100_000),
}

# Columns where at least one value is mandatory — rows missing all of
# these become unworkable and are dropped.
REQUIRED_COLUMNS = ["product", "quantity", "unit_price"]

# Text columns normalised to title case.
TEXT_TITLE_COLUMNS = ["product", "category", "country", "sales_rep"]

# A simple email validation pattern — not RFC 5321 complete, but
# sufficient to catch obvious junk like "not-an-email".
EMAIL_PATTERN = re.compile(r"^[\w\.\-\+]+@[\w\-]+\.[a-zA-Z]{2,}$")

# Country name aliases → canonical form.
COUNTRY_ALIASES: dict[str, str] = {
    "spain": "Spain",
    "españa": "Spain",
    "germany": "Germany",
    "deutschland": "Germany",
    "france": "France",
    "italia": "Italy",
    "italy": "Italy",
    "netherlands": "Netherlands",
    "nederland": "Netherlands",
}

# Date formats we try to parse, in order of specificity.
DATE_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%B %d, %Y",
    "%Y/%m/%d",
]


class CSVCleaner:
    """
    Cleans a raw sales CSV DataFrame through a chainable pipeline.

    Each public method addresses one type of data quality issue and
    returns ``self`` so methods can be chained together. A private
    log records every change made — this feeds the CleaningReporter.

    Attributes
    ----------
    _df : pd.DataFrame
        The DataFrame being cleaned (private — access via `.dataframe`).
    _log : list[dict]
        Each entry records a cleaning step: its name, a description,
        and the number of rows or values affected.

    Examples
    --------
    >>> from cleaner.loader import load_csv
    >>> from cleaner.cleaner import CSVCleaner
    >>> df = load_csv("data/raw/sales_data_raw.csv")
    >>> cleaned = (
    ...     CSVCleaner(df)
    ...     .remove_duplicates()
    ...     .standardise_text()
    ...     .parse_numeric_columns()
    ...     .validate_numeric_ranges()
    ...     .standardise_dates()
    ...     .validate_emails()
    ...     .drop_rows_missing_required()
    ...     .get_dataframe()
    ... )
    """

    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialise the CSVCleaner with a raw DataFrame.

        Parameters
        ----------
        dataframe : pd.DataFrame
            Raw data as loaded by the loader module. A copy is stored
            so the original is never modified.
        """
        self._df = dataframe.copy()
        self._original_shape = dataframe.shape
        self._log: list[dict] = []

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def dataframe(self) -> pd.DataFrame:
        """The current state of the DataFrame (read-only)."""
        return self._df

    @property
    def log(self) -> list[dict]:
        """The cleaning log (read-only)."""
        return self._log

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _record(self, step: str, description: str, affected: int) -> None:
        """
        Append an entry to the internal cleaning log.

        Parameters
        ----------
        step : str
            Short identifier for the cleaning step (e.g. "duplicates").
        description : str
            Human-readable description of what was fixed.
        affected : int
            Number of rows or values changed by this step.
        """
        entry = {"step": step, "description": description, "affected": affected}
        self._log.append(entry)
        flag = "✓" if affected == 0 else "~"
        print(f"  [{flag}] {description} ({affected} affected)")

    # ------------------------------------------------------------------
    # Public cleaning methods
    # ------------------------------------------------------------------

    def remove_duplicates(self) -> "CSVCleaner":
        """
        Drop fully duplicate rows from the DataFrame.

        A row is considered a duplicate if every column value matches
        another row exactly. The first occurrence is kept.

        Returns
        -------
        CSVCleaner
            Returns self for method chaining.
        """
        before = len(self._df)
        self._df = self._df.drop_duplicates()
        removed = before - len(self._df)
        self._record(
            "duplicates",
            f"Removed {removed} duplicate rows",
            removed,
        )
        return self

    def standardise_text(self) -> "CSVCleaner":
        """
        Normalise text columns: strip whitespace, fix case, resolve
        country aliases.

        - Name/label columns receive title case.
        - Country values are resolved to a canonical English name via
          the COUNTRY_ALIASES lookup.

        Returns
        -------
        CSVCleaner
            Returns self for method chaining.
        """
        affected = 0

        for col in TEXT_TITLE_COLUMNS:
            if col not in self._df.columns:
                continue
            original = self._df[col].copy()
            self._df[col] = self._df[col].astype(str).str.strip().str.title()
            self._df[col] = self._df[col].replace("Nan", "")
            affected += (self._df[col] != original).sum()

        if "country" in self._df.columns:
            self._df["country"] = (
                self._df["country"]
                .astype(str)
                .str.strip()
                .str.lower()
                .map(lambda v: COUNTRY_ALIASES.get(v, v.title()))
            )

        self._record(
            "text",
            "Standardised text casing and resolved country aliases",
            int(affected),
        )
        return self

    def parse_numeric_columns(self) -> "CSVCleaner":
        """
        Convert numeric columns to float, stripping stray characters.

        Handles values like ``"$29.99"``, ``"€ 14.50"``, or ``" 5 "``
        by removing any non-numeric characters except ``.`` and ``-``
        before conversion. Values that cannot be parsed become NaN.

        Returns
        -------
        CSVCleaner
            Returns self for method chaining.
        """
        affected = 0

        for col in NUMERIC_COLUMNS:
            if col not in self._df.columns:
                continue
            cleaned = (
                self._df[col]
                .astype(str)
                .str.strip()
                .str.replace(r"[^\d\.\-]", "", regex=True)
            )
            numeric = pd.to_numeric(cleaned, errors="coerce")
            was_nan = self._df[col].isna() | (self._df[col].astype(str).str.strip() == "")
            now_nan = numeric.isna()
            affected += int((now_nan & ~was_nan).sum())
            self._df[col] = numeric

        self._record(
            "numeric_parse",
            "Parsed numeric columns, stripped currency symbols",
            affected,
        )
        return self

    def validate_numeric_ranges(self) -> "CSVCleaner":
        """
        Remove rows with numeric values outside acceptable ranges.

        Uses the ``NUMERIC_RANGES`` constant to define valid bounds per
        column. Rows with out-of-range values are dropped rather than
        corrected, because they indicate data entry errors (e.g. a
        negative quantity) that cannot be safely inferred.

        Returns
        -------
        CSVCleaner
            Returns self for method chaining.
        """
        before = len(self._df)

        for col, (lo, hi) in NUMERIC_RANGES.items():
            if col not in self._df.columns:
                continue
            self._df = self._df[
                self._df[col].isna() | self._df[col].between(lo, hi)
            ]

        removed = before - len(self._df)
        self._record(
            "numeric_range",
            f"Removed {removed} rows with out-of-range numeric values",
            removed,
        )
        return self

    def standardise_dates(self) -> "CSVCleaner":
        """
        Parse and reformat all date values to ISO 8601 (YYYY-MM-DD).

        Tries each format in ``DATE_FORMATS`` in order. Values that
        cannot be parsed by any format are set to NaN and flagged.

        Returns
        -------
        CSVCleaner
            Returns self for method chaining.
        """
        if "order_date" not in self._df.columns:
            return self

        def parse_date(value) -> str:
            value = str(value) if value is not None else ""
            if not value or value.strip() in ("", "nan", "NaN"):
                return ""
            for fmt in DATE_FORMATS:
                try:
                    return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
                except ValueError:
                    continue
            return ""  # Could not parse

        original = self._df["order_date"].copy()
        self._df["order_date"] = self._df["order_date"].astype(str).apply(parse_date)
        affected = int((self._df["order_date"] != original).sum())

        self._record(
            "dates",
            "Standardised date formats to YYYY-MM-DD",
            affected,
        )
        return self

    def validate_emails(self) -> "CSVCleaner":
        """
        Flag invalid email addresses in a new ``email_valid`` column.

        Rather than dropping rows with bad emails (the rest of the row
        may be perfectly usable), a boolean flag column is added so the
        client can decide how to handle them downstream.

        Returns
        -------
        CSVCleaner
            Returns self for method chaining.
        """
        if "email" not in self._df.columns:
            return self

        self._df["email_valid"] = (
            self._df["email"]
            .fillna("")
            .astype(str)
            .str.strip()
            .apply(lambda v: bool(EMAIL_PATTERN.match(v)) if v and v != "nan" else False)
        )

        invalid_count = int((~self._df["email_valid"]).sum())
        self._record(
            "emails",
            f"Validated emails — {invalid_count} flagged as invalid in 'email_valid' column",
            invalid_count,
        )
        return self

    def drop_rows_missing_required(self) -> "CSVCleaner":
        """
        Drop rows that are missing values in required columns.

        Rows missing any value in ``REQUIRED_COLUMNS`` are not
        salvageable for analysis and are removed. The count dropped
        is logged so the client knows how much data was lost.

        Returns
        -------
        CSVCleaner
            Returns self for method chaining.
        """
        before = len(self._df)
        existing = [c for c in REQUIRED_COLUMNS if c in self._df.columns]
        self._df = self._df.dropna(subset=existing)

        # Also drop rows where required text fields are empty strings
        for col in existing:
            if self._df[col].dtype == object:
                self._df = self._df[self._df[col].str.strip() != ""]

        removed = before - len(self._df)
        self._record(
            "required",
            f"Dropped {removed} rows missing required fields {existing}",
            removed,
        )
        return self

    def get_dataframe(self) -> pd.DataFrame:
        """
        Return the cleaned DataFrame.

        Intended as the final call in a pipeline chain. Prints a
        one-line summary of the final dataset shape.

        Returns
        -------
        pd.DataFrame
            The fully cleaned DataFrame.
        """
        print(
            f"\n  Pipeline complete → "
            f"{self._original_shape[0]} rows in, "
            f"{len(self._df)} rows out "
            f"({self._original_shape[0] - len(self._df)} removed)"
        )
        return self._df
