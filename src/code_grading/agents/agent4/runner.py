"""Agent 4 runner: Gmail draft creation."""

from typing import List, Dict

import pandas as pd

from ...common.excel_handler import ExcelHandler
from ...common.status import Status
from ...config import Config
from ..base import AbstractAgent
from .email_builder import EmailBuilder
from .gmail_drafter import GmailDrafter


class Agent4(AbstractAgent):
    """Agent 4: Email Drafter."""

    def __init__(self, config: Config):
        """Initialize Agent 4.

        Args:
            config: System configuration
        """
        super().__init__(config, "agent4")
        self.gmail_drafter = GmailDrafter(
            credentials_path=config.gmail_credentials_path,
            token_path=config.gmail_token_path,
        )
        self.email_builder = EmailBuilder(template_dir=config.template_dir)

    def run(self) -> None:
        """Execute draft email creation."""
        self.log_start()

        try:
            # Authenticate with Gmail
            self.logger.info("Authenticating with Gmail...")
            self.gmail_drafter.authenticate()

            # Read feedback, email, and grade data
            df_feedback = ExcelHandler.read_with_status(
                self.config.excel_agent3,
                status=Status.READY,
            )

            df_emails = ExcelHandler.read_all(
                self.config.excel_agent1,
                columns=["ID", "email", "subject"],
            )

            df_grades = ExcelHandler.read_all(
                self.config.excel_agent2,
                columns=["ID", "grade"],
            )

            if df_feedback.empty:
                self.logger.warning("No feedback to send")
                return

            # Merge data
            df_merged = df_feedback.merge(df_emails, on="ID", how="inner")
            df_merged = df_merged.merge(df_grades, on="ID", how="inner")

            drafts_data = df_merged[["ID", "Feedback", "email", "subject", "grade"]].to_dict("records")
            self.logger.info(f"Creating {len(drafts_data)} draft emails")

            # Create drafts
            self._create_drafts(drafts_data)

            self.log_complete(len(drafts_data))

        except Exception as e:
            self.log_error(e, "draft creation")
            raise

    def _create_drafts(self, drafts_data: List[Dict]) -> None:
        """Create draft emails in Gmail.

        Args:
            drafts_data: List of draft data dictionaries
        """
        for draft_info in drafts_data:
            try:
                draft_id = draft_info["ID"]
                feedback = draft_info["Feedback"]
                recipient = draft_info["email"]
                subject = draft_info["subject"]
                grade = draft_info["grade"]

                self.logger.info(f"Creating draft for ID {draft_id}, recipient: {recipient}")

                # Build email content
                email_data = self.email_builder.build_email(feedback, recipient, subject, grade)

                # Create draft
                draft_gmail_id = self.gmail_drafter.create_draft(email_data)

                self.logger.info(f"Draft created: {draft_gmail_id} for ID {draft_id}")

            except Exception as e:
                self.logger.error(f"Failed to create draft for ID {draft_id}: {e}")
