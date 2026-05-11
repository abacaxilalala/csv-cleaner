# CSV Cleaner

A professional Python pipeline for cleaning messy CSV files — handles duplicates, inconsistent formatting, invalid values, and missing data, then produces a cleaned file alongside a clear before/after summary report.

---

## What it does

Real-world CSV files are rarely clean. This tool handles the most common data quality problems in a single, auditable pipeline:

| Problem | How it's handled |
|---|---|
| Duplicate rows | Detected and removed (first occurrence kept) |
| Inconsistent text casing | Normalised to title case |
| Country name variations (`"spain"`, `"SPAIN"`, `"España"`) | Resolved to canonical form |
| Currency symbols in numeric fields (`"$29.99"`) | Stripped and parsed to float |
| Negative or impossible numeric values | Rows removed with explanation |
| Mixed date formats (`"01/01/2024"`, `"January 1, 2024"`) | All standardised to `YYYY-MM-DD` |
| Invalid email addresses | Flagged in a new `email_valid` column |
| Rows missing required fields | Dropped and counted |

Every step is logged so you always know exactly what changed and why.

---

## Project structure

```
project-01-csv-cleaner/
├── main.py                  # Entry point — run this
├── generate_sample_data.py  # Generates a realistic messy dataset for demo
├── requirements.txt
├── cleaner/
│   ├── __init__.py
│   ├── cleaner.py           # CSVCleaner class — chainable pipeline
│   ├── loader.py            # CSV loading with validation
│   ├── reporter.py          # Generates the summary report
│   └── exceptions.py        # Custom exception types
└── data/
    ├── raw/                 # Drop your input CSV here
    └── cleaned/             # Cleaned CSV and report appear here
```

---

## Quickstart

**1. Clone and install dependencies**

```bash
git clone https://github.com/danieldobos/csv-cleaner.git
cd csv-cleaner
pip install -r requirements.txt
```

**2. Generate the sample messy dataset (optional)**

```bash
python generate_sample_data.py
```

This creates `data/raw/sales_data_raw.csv` — 210 rows of intentionally messy sales data, including duplicates, mixed date formats, currency symbols in price fields, and invalid emails.

**3. Run the pipeline**

```bash
python main.py
```

**4. Check the output**

- `data/cleaned/sales_data_cleaned.csv` — your clean data
- `data/cleaned/cleaning_report.txt` — full before/after summary

---

## Sample output

```
============================================================
  CSV CLEANER — Starting Pipeline
============================================================

Loading: data/raw/sales_data_raw.csv
  Loaded 210 rows × 9 columns

Cleaning...
  [~] Removed 10 duplicate rows (10 affected)
  [~] Standardised text casing and resolved country aliases (397 affected)
  [✓] Parsed numeric columns, stripped currency symbols (0 affected)
  [~] Removed 16 rows with out-of-range numeric values (16 affected)
  [~] Standardised date formats to YYYY-MM-DD (134 affected)
  [~] Validated emails — 23 flagged as invalid (23 affected)
  [~] Dropped 17 rows missing required fields (17 affected)

  Pipeline complete → 210 rows in, 167 rows out (43 removed)
```

The generated report shows per-column null counts before and after, a full log of every step, and a numeric summary of the cleaned data.

---

## Using it on your own data

Drop your CSV into `data/raw/` and update the `INPUT_FILE` path in `main.py`. To adapt the cleaning rules to your dataset:

- Edit `NUMERIC_COLUMNS` and `NUMERIC_RANGES` in `cleaner/cleaner.py` to match your numeric columns and valid ranges.
- Edit `TEXT_TITLE_COLUMNS` for the columns you want title-cased.
- Add entries to `COUNTRY_ALIASES` for any country name variations in your data.
- Edit `REQUIRED_COLUMNS` to define which columns are mandatory.

---

## Tech stack

- **Python 3.10+**
- **pandas** — data loading, cleaning, and transformation
- **re** (stdlib) — email and pattern validation
- **datetime** (stdlib) — multi-format date parsing

---

## Skills demonstrated

- **OOP with method chaining** — `CSVCleaner` uses the same chainable pipeline pattern as production-grade libraries
- **Custom exceptions** — precise error types for loading, validation, and missing columns
- **Separation of concerns** — loading, cleaning, and reporting are fully independent modules
- **Type hints and docstrings** — NumPy-style, throughout
- **Defensive programming** — invalid inputs produce clear messages, not raw tracebacks

---

## Author

**Daniel Dobos** — Python student based in Seville, Spain.  
Open to entry-level freelance projects in data cleaning, web scraping, and automation.
