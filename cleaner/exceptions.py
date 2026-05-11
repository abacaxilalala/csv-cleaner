"""
exceptions.py
-------------
Custom exception classes for the CSV Cleaner package.

Defining specific exception types (rather than using generic ValueError
or RuntimeError) makes error handling precise — callers can catch exactly
the kind of failure they know how to recover from.
"""


class CSVCleanerError(Exception):
    """Base exception for all CSV Cleaner errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class FileNotFoundError(CSVCleanerError):
    """Raised when the input CSV file does not exist."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"Input file not found: '{file_path}'")


class EmptyFileError(CSVCleanerError):
    """Raised when the input CSV is empty or has no data rows."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        super().__init__(f"Input file is empty or contains no data: '{file_path}'")


class MissingColumnError(CSVCleanerError):
    """Raised when a required column is absent from the dataset."""

    def __init__(self, column: str):
        self.column = column
        super().__init__(f"Required column not found in dataset: '{column}'")
