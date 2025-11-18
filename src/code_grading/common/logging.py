"""Cyclic logging with line-based rotation."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


class LineCountRotatingFileHandler(RotatingFileHandler):
    """Rotating file handler that rotates based on line count instead of bytes."""

    def __init__(
        self,
        filename: Path,
        max_lines: int = 2000,
        backup_count: int = 1,
        encoding: Optional[str] = "utf-8",
    ):
        """Initialize handler.

        Args:
            filename: Log file path
            max_lines: Maximum lines before rotation
            backup_count: Number of backup files to keep
            encoding: File encoding
        """
        self.max_lines = max_lines
        self.line_count = 0
        super().__init__(
            filename=str(filename),
            maxBytes=0,  # Disable byte-based rotation
            backupCount=backup_count,
            encoding=encoding,
        )
        self._count_existing_lines()

    def _count_existing_lines(self) -> None:
        """Count lines in existing log file."""
        if Path(self.baseFilename).exists():
            with open(self.baseFilename, "r", encoding=self.encoding) as f:
                self.line_count = sum(1 for _ in f)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record and check if rotation is needed."""
        super().emit(record)
        self.line_count += 1
        if self.line_count >= self.max_lines:
            self.doRollover()
            self.line_count = 0


def setup_cyclic_logger(
    name: str,
    log_file: Path,
    max_lines: int = 2000,
    level: str = "INFO",
) -> logging.Logger:
    """Setup logger with cyclic line-based rotation.

    Args:
        name: Logger name
        log_file: Path to log file
        max_lines: Maximum lines before rotation
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # File handler with line-based rotation
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = LineCountRotatingFileHandler(
        filename=log_file,
        max_lines=max_lines,
        backup_count=1,
    )

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
