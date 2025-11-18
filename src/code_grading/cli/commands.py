"""CLI commands using Click."""

import sys
from pathlib import Path

import click

from ..config import Config
from ..agents.agent1 import Agent1
from ..agents.agent2 import Agent2
from ..agents.agent3 import Agent3
from ..agents.agent4 import Agent4
from ..orchestrator import Pipeline


@click.group()
@click.version_option(version="1.0.0")
def cli() -> None:
    """Code Grading System - Multi-agent automated grading platform."""
    pass


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to custom config file")
def agent1(config: str) -> None:
    """Run Agent 1: Email Collector."""
    cfg = _load_config(config)
    try:
        agent = Agent1(cfg)
        agent.run()
        click.echo("✓ Agent 1 completed successfully")
    except Exception as e:
        click.echo(f"✗ Agent 1 failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to custom config file")
def agent2(config: str) -> None:
    """Run Agent 2: Code Analyzer."""
    cfg = _load_config(config)
    try:
        agent = Agent2(cfg)
        agent.run()
        click.echo("✓ Agent 2 completed successfully")
    except Exception as e:
        click.echo(f"✗ Agent 2 failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to custom config file")
def agent3(config: str) -> None:
    """Run Agent 3: AI Feedback Generator."""
    cfg = _load_config(config)
    try:
        agent = Agent3(cfg)
        agent.run()
        click.echo("✓ Agent 3 completed successfully")
    except Exception as e:
        click.echo(f"✗ Agent 3 failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to custom config file")
def agent4(config: str) -> None:
    """Run Agent 4: Email Drafter."""
    cfg = _load_config(config)
    try:
        agent = Agent4(cfg)
        agent.run()
        click.echo("✓ Agent 4 completed successfully")
    except Exception as e:
        click.echo(f"✗ Agent 4 failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--config", type=click.Path(exists=True), help="Path to custom config file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run_all(config: str, verbose: bool) -> None:
    """Run all agents in sequence."""
    cfg = _load_config(config)

    if verbose:
        cfg.log_level = "DEBUG"

    try:
        pipeline = Pipeline(cfg)
        pipeline.run_all()
        click.echo("✓ All agents completed successfully")
    except Exception as e:
        click.echo(f"✗ Pipeline failed: {e}", err=True)
        sys.exit(1)


def _load_config(config_path: str = None) -> Config:
    """Load configuration from environment or file.

    Args:
        config_path: Optional path to config file

    Returns:
        Config instance
    """
    if config_path:
        env_file = Path(config_path)
    else:
        env_file = Path(".env")

    cfg = Config.from_env(env_file if env_file.exists() else None)
    cfg.ensure_directories()
    return cfg


if __name__ == "__main__":
    cli()
