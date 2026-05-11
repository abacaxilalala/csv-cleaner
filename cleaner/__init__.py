"""
CSV Cleaner — a professional data cleaning pipeline for messy CSV files.
"""

from .cleaner import CSVCleaner
from .loader import load_csv
from .reporter import generate_report
from .exceptions import CSVCleanerError, EmptyFileError, MissingColumnError

__version__ = "1.0.0"
__author__ = "Daniel Dobos"

__all__ = [
    "CSVCleaner",
    "load_csv",
    "generate_report",
    "CSVCleanerError",
    "EmptyFileError",
    "MissingColumnError",
]
