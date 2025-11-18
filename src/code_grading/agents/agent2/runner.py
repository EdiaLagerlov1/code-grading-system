"""Agent 2 runner: Multi-threaded code analysis."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

import pandas as pd

from ...common.excel_handler import ExcelHandler
from ...common.status import Status
from ...config import Config
from ..base import AbstractAgent
from .worker import RepoWorker


class Agent2(AbstractAgent):
    """Agent 2: Multi-threaded code analyzer."""

    def __init__(self, config: Config):
        """Initialize Agent 2.

        Args:
            config: System configuration
        """
        super().__init__(config, "agent2")
        self.max_workers = config.worker_threads

    def run(self) -> None:
        """Execute multi-threaded code analysis."""
        self.log_start()

        try:
            # Read input data
            df_input = ExcelHandler.read_with_status(
                self.config.excel_agent1,
                status=Status.READY,
            )

            if df_input.empty:
                self.logger.warning("No repositories to process")
                return

            repos = df_input[["ID", "Repo"]].to_dict("records")
            self.logger.info(f"Processing {len(repos)} repositories with {self.max_workers} workers")

            # Process repositories in parallel
            results = self._process_parallel(repos)

            # Save results
            self._save_results(results)

            self.log_complete(len(results))

        except Exception as e:
            self.log_error(e, "code analysis")
            raise

    def _process_parallel(self, repos: List[Dict]) -> List[Dict]:
        """Process repositories in parallel using thread pool.

        Args:
            repos: List of repository records

        Returns:
            List of result dictionaries
        """
        results = []

        # Ensure temp directory exists
        self.config.ensure_directories()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create worker for each repository
            futures = {}
            for repo in repos:
                worker = RepoWorker(self.logger, self.config.temp_dir)
                future = executor.submit(worker.process, repo)
                futures[future] = repo["ID"]

            # Collect results as they complete
            for future in as_completed(futures):
                repo_id = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Worker exception for repo {repo_id}: {e}")
                    results.append({
                        "ID": repo_id,
                        "grade": 0.0,
                        "Status": "error",
                    })

        return results

    def _save_results(self, results: List[Dict]) -> None:
        """Save analysis results to Excel.

        Args:
            results: List of result dictionaries
        """
        if not results:
            self.logger.warning("No results to save")
            return

        df = pd.DataFrame(results)
        ExcelHandler.atomic_write(df, self.config.excel_agent2)
        self.logger.info(f"Results saved to {self.config.excel_agent2}")
