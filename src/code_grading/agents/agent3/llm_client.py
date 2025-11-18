"""Anthropic Claude API client."""

from typing import Optional

import anthropic


class LLMClient:
    """Anthropic Claude API wrapper."""

    def __init__(self, api_key: str, model: str = "claude-3-7-sonnet-20250219"):
        """Initialize LLM client.

        Args:
            api_key: Anthropic API key
            model: Model identifier
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ) -> str:
        """Generate text from prompt.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Generated text
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response
        if message.content and len(message.content) > 0:
            return message.content[0].text

        return ""

    def generate_feedback(
        self,
        style_prompt: str,
        grade: float,
        context: Optional[str] = None,
    ) -> str:
        """Generate personalized feedback.

        Args:
            style_prompt: Style instructions (e.g., Trump, Shachar, Dudi)
            grade: Student's grade (0-100)
            context: Additional context (optional)

        Returns:
            Generated feedback text
        """
        prompt = f"""{style_prompt}

Grade received: {grade}/100

Please write personalized feedback for this grade.
{f'Additional context: {context}' if context else ''}

Keep it concise (2-3 sentences) and encouraging."""

        return self.generate(prompt, max_tokens=300, temperature=0.8)
