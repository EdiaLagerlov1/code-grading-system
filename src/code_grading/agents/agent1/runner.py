"""Agent 1 runner: Email collection and repository extraction."""

from datetime import datetime
from typing import List, Dict

import pandas as pd

from ...common.excel_handler import ExcelHandler
from ...common.status import Status
from ...config import Config
from ..base import AbstractAgent
from .email_parser import EmailParser
from .gmail_client import GmailClient


class Agent1(AbstractAgent):
    """Agent 1: Collect emails and extract repository links."""

    def __init__(self, config: Config):
        """Initialize Agent 1.

        Args:
            config: System configuration
        """
        super().__init__(config, "agent1")
        self.gmail_client = GmailClient(
            credentials_path=config.gmail_credentials_path,
            token_path=config.gmail_token_path,
        )
        self.parser = EmailParser()

    def run(self) -> None:
        """Execute email collection and extraction."""
        self.log_start()

        try:
            # Authenticate with Gmail
            self.logger.info("Authenticating with Gmail...")
            self.gmail_client.authenticate()

            # Search for messages
            self.logger.info(
                f"Searching folder '{self.config.gmail_folder}' "
                f"for subject '{self.config.subject_filter}'..."
            )
            messages = self.gmail_client.search_messages(
                folder=self.config.gmail_folder,
                subject_filter=self.config.subject_filter,
            )

            self.logger.info(f"Found {len(messages)} messages")

            # Process messages
            results = self._process_messages(messages)

            # Save to Excel
            self._save_results(results)

            self.log_complete(len(results))

        except Exception as e:
            self.log_error(e, "email collection")
            raise

    def _process_messages(self, messages: List[Dict[str, str]]) -> List[Dict]:
        """Process messages and extract repository information.

        Args:
            messages: List of message dictionaries

        Returns:
            List of processed records
        """
        results = []

        for idx, msg in enumerate(messages, start=1):
            try:
                # Extract repository URL from body
                repo_url = self.parser.extract_repo_url(msg["body"])

                if not repo_url:
                    self.logger.warning(
                        f"No repository URL found in message from {msg['email']}"
                    )
                    repo_url = ""

                # Extract clean email address
                email = self.parser.extract_email_address(msg["email"])

                # Convert timezone-aware datetime to naive for Excel compatibility
                date = msg["date"]
                if hasattr(date, "tzinfo") and date.tzinfo is not None:
                    date = date.replace(tzinfo=None)

                # Create record
                record = {
                    "ID": idx,
                    "Date": date,
                    "email": email,
                    "subject": msg["subject"],
                    "Repo": repo_url,
                    "Status": str(Status.READY) if repo_url else str(Status.ERROR),
                }

                results.append(record)
                self.logger.debug(f"Processed message {idx}: {email}")

            except Exception as e:
                self.logger.error(f"Error processing message {idx}: {e}")

        return results

    def _save_results(self, results: List[Dict]) -> None:
        """Save results to Excel file.

        Args:
            results: List of result dictionaries
        """
        if not results:
            self.logger.warning("No results to save")
            return

        df = pd.DataFrame(results)

        # Ensure data directory exists
        self.config.ensure_directories()

        # Save to Excel
        ExcelHandler.atomic_write(df, self.config.excel_agent1)
        self.logger.info(f"Results saved to {self.config.excel_agent1}")
