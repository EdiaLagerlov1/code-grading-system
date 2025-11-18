"""Pipeline orchestrator to run all agents in sequence."""

import logging
from typing import List, Callable

from ..agents.agent1 import Agent1
from ..agents.agent2 import Agent2
from ..agents.agent3 import Agent3
from ..agents.agent4 import Agent4
from ..config import Config


class Pipeline:
    """Orchestrate execution of all agents."""

    def __init__(self, config: Config):
        """Initialize pipeline.

        Args:
            config: System configuration
        """
        self.config = config
        self.logger = logging.getLogger("pipeline")

        # Initialize all agents
        self.agents = [
            Agent1(config),
            Agent2(config),
            Agent3(config),
            Agent4(config),
        ]

    def run_all(self) -> None:
        """Run all agents in sequence."""
        self.logger.info("Starting pipeline execution")

        for agent in self.agents:
            try:
                agent.run()
            except Exception as e:
                self.logger.error(f"Agent {agent.agent_name} failed: {e}")
                raise

        self.logger.info("Pipeline completed successfully")

    def run_agents(self, agent_numbers: List[int]) -> None:
        """Run specific agents by number.

        Args:
            agent_numbers: List of agent numbers (1-4)
        """
        for num in agent_numbers:
            if 1 <= num <= 4:
                agent = self.agents[num - 1]
                try:
                    agent.run()
                except Exception as e:
                    self.logger.error(f"Agent {agent.agent_name} failed: {e}")
                    raise
            else:
                self.logger.warning(f"Invalid agent number: {num}")
