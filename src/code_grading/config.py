"""Configuration management with environment variable support."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """System-wide configuration."""

    # Project paths (relative)
    project_root: Path
    data_dir: Path
    log_dir: Path
    template_dir: Path

    # Gmail configuration
    gmail_credentials_path: Path
    gmail_token_path: Path
    gmail_account: str
    gmail_folder: str
    subject_filter: str

    # Anthropic AI configuration
    anthropic_api_key: str

    # Agent 2 configuration
    worker_threads: int
    temp_dir: Path

    # File paths
    excel_agent1: Path
    excel_agent2: Path
    excel_agent3: Path

    # Logging
    log_max_lines: int
    log_level: str

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Config":
        """Load configuration from environment variables.

        Args:
            env_file: Path to .env file (defaults to .env in current directory)

        Returns:
            Config instance
        """
        # Load .env file
        if env_file is None:
            env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)

        # Determine project root (where .env is located or current dir)
        project_root = Path.cwd()

        # Helper to resolve relative paths
        def resolve_path(env_var: str, default: str) -> Path:
            path_str = os.getenv(env_var, default)
            path = Path(path_str)
            if not path.is_absolute():
                path = project_root / path
            return path

        return cls(
            project_root=project_root,
            data_dir=resolve_path("DATA_DIR", "./data"),
            log_dir=resolve_path("LOG_DIR", "./data/logs"),
            template_dir=resolve_path("TEMPLATE_DIR", "./templates"),
            gmail_credentials_path=resolve_path("GMAIL_CREDENTIALS_PATH", "./credentials.json"),
            gmail_token_path=resolve_path("GMAIL_TOKEN_PATH", "./token.json"),
            gmail_account=os.getenv("GMAIL_ACCOUNT", "edialagerlov1@gmail.com"),
            gmail_folder=os.getenv("GMAIL_FOLDER", "AICourse2025"),
            subject_filter=os.getenv("SUBJECT_FILTER", "בדיקה עצמית של תרגיל"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            worker_threads=int(os.getenv("WORKER_THREADS", "4")),
            temp_dir=resolve_path("TEMP_DIR", "./data/temp"),
            excel_agent1=resolve_path("EXCEL_AGENT1", "./data/ExcelBK_byAgent1.xlsx"),
            excel_agent2=resolve_path("EXCEL_AGENT2", "./data/Grade_byAgent2.xlsx"),
            excel_agent3=resolve_path("EXCEL_AGENT3", "./data/Feedback_ByAgent3.xlsx"),
            log_max_lines=int(os.getenv("LOG_MAX_LINES", "2000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
