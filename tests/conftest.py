"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from code_grading.config import Config
from code_grading.common.status import Status


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_config(temp_dir):
    """Create test configuration."""
    config = Config(
        project_root=temp_dir,
        data_dir=temp_dir / "data",
        log_dir=temp_dir / "logs",
        template_dir=temp_dir / "templates",
        gmail_credentials_path=temp_dir / "credentials.json",
        gmail_token_path=temp_dir / "token.json",
        gmail_account="test@example.com",
        gmail_folder="TestFolder",
        subject_filter="test subject",
        anthropic_api_key="test-key",
        worker_threads=2,
        temp_dir=temp_dir / "temp",
        excel_agent1=temp_dir / "data" / "agent1.xlsx",
        excel_agent2=temp_dir / "data" / "agent2.xlsx",
        excel_agent3=temp_dir / "data" / "agent3.xlsx",
        log_max_lines=100,
        log_level="DEBUG",
    )
    config.ensure_directories()
    return config


@pytest.fixture
def sample_excel_agent1(test_config):
    """Create sample Excel file for Agent 1 output."""
    df = pd.DataFrame({
        "ID": [1, 2, 3],
        "Date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        "email": ["user1@test.com", "user2@test.com", "user3@test.com"],
        "subject": ["Test 1", "Test 2", "Test 3"],
        "Repo": [
            "https://github.com/user/repo1",
            "https://github.com/user/repo2",
            "https://github.com/user/repo3",
        ],
        "Status": [str(Status.READY), str(Status.READY), str(Status.PENDING)],
    })
    df.to_excel(test_config.excel_agent1, index=False, engine="openpyxl")
    return test_config.excel_agent1


@pytest.fixture
def sample_excel_agent2(test_config):
    """Create sample Excel file for Agent 2 output."""
    df = pd.DataFrame({
        "ID": [1, 2],
        "grade": [85.5, 92.3],
        "Status": [str(Status.READY), str(Status.READY)],
    })
    df.to_excel(test_config.excel_agent2, index=False, engine="openpyxl")
    return test_config.excel_agent2
