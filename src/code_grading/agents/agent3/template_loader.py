"""Template loading for feedback prompts."""

from pathlib import Path
from typing import Dict


class TemplateLoader:
    """Load prompt templates from files."""

    def __init__(self, template_dir: Path):
        """Initialize template loader.

        Args:
            template_dir: Directory containing template files
        """
        self.template_dir = template_dir
        self.prompts_dir = template_dir / "prompts"

    def load_template(self, name: str) -> str:
        """Load template by name.

        Args:
            name: Template name (without extension)

        Returns:
            Template content
        """
        template_file = self.prompts_dir / f"{name}.txt"

        if template_file.exists():
            with open(template_file, "r", encoding="utf-8") as f:
                return f.read()

        # Fallback to default templates
        return self._get_default_template(name)

    def _get_default_template(self, name: str) -> str:
        """Get default template if file doesn't exist.

        Args:
            name: Template name

        Returns:
            Default template content
        """
        defaults: Dict[str, str] = {
            "trump": """You are writing feedback in Donald Trump's style.
Use superlatives, be confident, use simple words, and be enthusiastic!
Examples: "Tremendous work!", "The best code I've seen!", "Fantastic!".""",
            "shachar": """You are writing feedback in Shachar Hason's satirical comedy style.
Use Israeli humor, observational comedy, be witty and relatable.
Mix Hebrew expressions naturally. Be energetic and real.""",
            "dudi": """You are writing feedback in Dudi Amsalem's warm comedic style.
Be friendly, relatable, use family-oriented humor, and be authentic.
Honest reactions with that Israeli everyman perspective.""",
            "standard": """Write constructive feedback focused on improvement.
Be specific about what can be enhanced and provide encouragement.""",
        }

        return defaults.get(name, defaults["standard"])
