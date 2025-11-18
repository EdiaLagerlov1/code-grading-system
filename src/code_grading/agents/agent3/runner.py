"""Agent 3 runner: AI-powered feedback generation."""

from typing import List, Dict

import pandas as pd

from ...common.excel_handler import ExcelHandler
from ...common.status import Status
from ...config import Config
from ..base import AbstractAgent
from .feedback_strategy import FeedbackStrategyFactory
from .llm_client import LLMClient
from .template_loader import TemplateLoader


class Agent3(AbstractAgent):
    """Agent 3: AI Feedback Generator."""

    def __init__(self, config: Config):
        """Initialize Agent 3.

        Args:
            config: System configuration
        """
        super().__init__(config, "agent3")

        # Initialize LLM client
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        self.llm_client = LLMClient(api_key=config.anthropic_api_key)
        self.template_loader = TemplateLoader(config.template_dir)
        self.factory = FeedbackStrategyFactory(self.llm_client, self.template_loader)

    def run(self) -> None:
        """Execute feedback generation."""
        self.log_start()

        try:
            # Read grades
            df_grades = ExcelHandler.read_with_status(
                self.config.excel_agent2,
                status=Status.READY,
            )

            if df_grades.empty:
                self.logger.warning("No grades to process")
                return

            grades = df_grades[["ID", "grade"]].to_dict("records")
            self.logger.info(f"Generating feedback for {len(grades)} submissions")

            # Generate feedback
            results = self._generate_feedback(grades)

            # Save results
            self._save_results(results)

            self.log_complete(len(results))

        except Exception as e:
            self.log_error(e, "feedback generation")
            raise

    def _generate_feedback(self, grades: List[Dict]) -> List[Dict]:
        """Generate personalized feedback for each grade.

        Args:
            grades: List of grade records

        Returns:
            List of feedback records
        """
        results = []

        for record in grades:
            try:
                grade_id = record["ID"]
                grade_value = record["grade"]

                self.logger.info(f"Generating feedback for ID {grade_id}, grade: {grade_value}")

                # Get appropriate strategy
                strategy = self.factory.create(grade_value)

                # Generate feedback
                feedback = strategy.generate(grade_value)

                results.append({
                    "ID": grade_id,
                    "Feedback": feedback,
                    "Status": str(Status.READY),
                })

                self.logger.debug(f"Feedback generated for ID {grade_id}")

            except Exception as e:
                self.logger.error(f"Failed to generate feedback for ID {grade_id}: {e}")
                results.append({
                    "ID": grade_id,
                    "Feedback": "Error generating feedback",
                    "Status": "error",
                })

        return results

    def _save_results(self, results: List[Dict]) -> None:
        """Save feedback results to Excel.

        Args:
            results: List of feedback records
        """
        if not results:
            self.logger.warning("No results to save")
            return

        df = pd.DataFrame(results)
        ExcelHandler.atomic_write(df, self.config.excel_agent3)
        self.logger.info(f"Results saved to {self.config.excel_agent3}")
