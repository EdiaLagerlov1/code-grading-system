"""Feedback generation strategies using Strategy Pattern."""

from abc import ABC, abstractmethod
from typing import Protocol

from .llm_client import LLMClient
from .template_loader import TemplateLoader


class FeedbackStrategy(Protocol):
    """Protocol for feedback generation strategies."""

    def generate(self, grade: float) -> str:
        """Generate feedback for given grade."""
        ...


class BaseFeedbackStrategy(ABC):
    """Base class for feedback strategies."""

    def __init__(self, llm_client: LLMClient, template_loader: TemplateLoader):
        """Initialize strategy.

        Args:
            llm_client: LLM client instance
            template_loader: Template loader instance
        """
        self.llm_client = llm_client
        self.template_loader = template_loader

    @abstractmethod
    def generate(self, grade: float) -> str:
        """Generate feedback for given grade."""
        pass


class TrumpFeedback(BaseFeedbackStrategy):
    """Donald Trump style feedback (90-100)."""

    def generate(self, grade: float) -> str:
        template = self.template_loader.load_template("trump")
        return self.llm_client.generate_feedback(template, grade)


class ShacharFeedback(BaseFeedbackStrategy):
    """Shachar Hason style feedback (70-90)."""

    def generate(self, grade: float) -> str:
        template = self.template_loader.load_template("shachar")
        return self.llm_client.generate_feedback(template, grade)


class StandardFeedback(BaseFeedbackStrategy):
    """Standard improvement feedback (55-70)."""

    def generate(self, grade: float) -> str:
        template = self.template_loader.load_template("standard")
        context = "Focus on improving code organization and following the 150-line rule."
        return self.llm_client.generate_feedback(template, grade, context)


class DudiFeedback(BaseFeedbackStrategy):
    """Dudi Amsalem style feedback (0-55)."""

    def generate(self, grade: float) -> str:
        template = self.template_loader.load_template("dudi")
        return self.llm_client.generate_feedback(template, grade)


class FeedbackStrategyFactory:
    """Factory for creating appropriate feedback strategy based on grade."""

    def __init__(self, llm_client: LLMClient, template_loader: TemplateLoader):
        """Initialize factory.

        Args:
            llm_client: LLM client instance
            template_loader: Template loader instance
        """
        self.llm_client = llm_client
        self.template_loader = template_loader

    def create(self, grade: float) -> FeedbackStrategy:
        """Create appropriate feedback strategy for grade.

        Args:
            grade: Student grade (0-100)

        Returns:
            Feedback strategy instance
        """
        if grade >= 90:
            return TrumpFeedback(self.llm_client, self.template_loader)
        elif grade >= 70:
            return ShacharFeedback(self.llm_client, self.template_loader)
        elif grade >= 55:
            return StandardFeedback(self.llm_client, self.template_loader)
        else:
            return DudiFeedback(self.llm_client, self.template_loader)
