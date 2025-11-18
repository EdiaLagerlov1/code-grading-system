"""Excel file operations with pandas."""

import tempfile
from pathlib import Path
from typing import List, Optional

import pandas as pd

from .status import Status


class ExcelHandler:
    """Handle Excel file read/write operations."""

    @staticmethod
    def read_with_status(
        file_path: Path,
        status: Status = Status.READY,
        columns: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Read Excel file and filter by status.

        Args:
            file_path: Path to Excel file
            status: Status to filter by
            columns: Specific columns to read (None = all)

        Returns:
            Filtered DataFrame
        """
        if not file_path.exists():
            return pd.DataFrame()

        df = pd.read_excel(
            file_path,
            engine="openpyxl",
            usecols=columns,
        )

        if "Status" in df.columns:
            return df[df["Status"] == str(status)].copy()

        return df

    @staticmethod
    def read_all(file_path: Path, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Read entire Excel file.

        Args:
            file_path: Path to Excel file
            columns: Specific columns to read (None = all)

        Returns:
            DataFrame
        """
        if not file_path.exists():
            return pd.DataFrame()

        return pd.read_excel(
            file_path,
            engine="openpyxl",
            usecols=columns,
        )

    @staticmethod
    def atomic_write(df: pd.DataFrame, file_path: Path) -> None:
        """Write DataFrame to Excel atomically (temp file + rename).

        Args:
            df: DataFrame to write
            file_path: Destination file path
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file first
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".xlsx",
            dir=file_path.parent,
            delete=False,
        ) as tmp_file:
            temp_path = Path(tmp_file.name)

        try:
            df.to_excel(
                temp_path,
                engine="openpyxl",
                index=False,
            )
            # Atomic rename
            temp_path.replace(file_path)
        except Exception:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise

    @staticmethod
    def append_or_create(df: pd.DataFrame, file_path: Path) -> None:
        """Append to existing Excel or create new one.

        Args:
            df: DataFrame to append
            file_path: Target file path
        """
        if file_path.exists():
            existing = pd.read_excel(file_path, engine="openpyxl")
            combined = pd.concat([existing, df], ignore_index=True)
            ExcelHandler.atomic_write(combined, file_path)
        else:
            ExcelHandler.atomic_write(df, file_path)
