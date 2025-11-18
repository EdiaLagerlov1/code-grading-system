"""Base class for all agents."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from ..common.logging import setup_cyclic_logger
from ..config import Config


class AbstractAgent(ABC):
    """Base class for all agents with common functionality."""

    def __init__(self, config: Config, agent_name: str):
        """Initialize agent.

        Args:
            config: System configuration
            agent_name: Name of the agent (e.g., 'agent1')
        """
        self.config = config
        self.agent_name = agent_name
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup cyclic logger for this agent.

        Returns:
            Configured logger instance
        """
        log_file = self.config.log_dir / f"{self.agent_name}.log"
        return setup_cyclic_logger(
            name=self.agent_name,
            log_file=log_file,
            max_lines=self.config.log_max_lines,
            level=self.config.log_level,
        )

    @abstractmethod
    def run(self) -> None:
        """Execute agent's main task.

        Must be implemented by subclasses.
        """
        pass

    def log_start(self) -> None:
        """Log agent start."""
        self.logger.info(f"{self.agent_name.upper()} started")

    def log_complete(self, processed_count: int = 0) -> None:
        """Log agent completion.

        Args:
            processed_count: Number of items processed
        """
        self.logger.info(
            f"{self.agent_name.upper()} completed - Processed {processed_count} items"
        )

    def log_error(self, error: Exception, context: str = "") -> None:
        """Log error with context.

        Args:
            error: Exception that occurred
            context: Additional context information
        """
        msg = f"Error in {self.agent_name}"
        if context:
            msg += f" ({context})"
        msg += f": {str(error)}"
        self.logger.error(msg, exc_info=True)
