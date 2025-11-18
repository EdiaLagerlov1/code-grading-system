"""Thread worker for repository analysis."""

import logging
from pathlib import Path
from typing import Dict, Optional

from .code_analyzer import CodeAnalyzer
from .git_client import GitClient


class RepoWorker:
    """Worker for analyzing a single repository."""

    def __init__(self, logger: logging.Logger, temp_dir: Path):
        """Initialize worker.

        Args:
            logger: Logger instance
            temp_dir: Base temporary directory for cloning
        """
        self.logger = logger
        self.temp_dir = temp_dir
        self.git_client = GitClient()
        self.analyzer = CodeAnalyzer()

    def process(self, record: Dict) -> Optional[Dict]:
        """Process a single repository.

        Args:
            record: Record with ID and Repo URL

        Returns:
            Result dictionary with ID, grade, Status, or None on failure
        """
        repo_id = record["ID"]
        repo_url = record["Repo"]

        self.logger.info(f"Worker processing repo {repo_id}: {repo_url}")

        repo_dir = None
        try:
            # Clone repository
            repo_dir = self.git_client.clone_repo(repo_url)
            self.logger.debug(f"Cloned {repo_url} to {repo_dir}")

            # Analyze code
            analysis = self.analyzer.analyze_repository(repo_dir)
            grade = self.analyzer.calculate_grade(analysis)

            self.logger.info(
                f"Repo {repo_id} analyzed: {analysis['total_files']} files, "
                f"{analysis['total_lines']} lines, grade: {grade}"
            )

            return {
                "ID": repo_id,
                "grade": grade,
                "Status": "ready",
            }

        except Exception as e:
            self.logger.error(f"Failed to process repo {repo_id}: {e}")
            return {
                "ID": repo_id,
                "grade": 0.0,
                "Status": "error",
            }

        finally:
            # Cleanup cloned repository
            if repo_dir:
                self.git_client.cleanup_repo(repo_dir)
                self.logger.debug(f"Cleaned up {repo_dir}")
