"""Email parsing and repository link extraction."""

import re
from typing import Optional


class EmailParser:
    """Parse emails and extract repository information."""

    # Common git repository URL patterns
    REPO_PATTERNS = [
        r"https?://github\.com/[\w\-]+/[\w\-\.]+",
        r"https?://gitlab\.com/[\w\-]+/[\w\-\.]+",
        r"https?://bitbucket\.org/[\w\-]+/[\w\-\.]+",
        r"git@github\.com:[\w\-]+/[\w\-\.]+\.git",
        r"git@gitlab\.com:[\w\-]+/[\w\-\.]+\.git",
    ]

    @classmethod
    def extract_repo_url(cls, text: str) -> Optional[str]:
        """Extract repository URL from text.

        Args:
            text: Email body or subject text

        Returns:
            First repository URL found, or None
        """
        for pattern in cls.REPO_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(0)
                # Normalize URL (remove .git suffix, ensure https)
                return cls._normalize_url(url)

        return None

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize git URL to https format.

        Args:
            url: Git URL (https or ssh format)

        Returns:
            Normalized https URL
        """
        # Remove .git suffix
        url = re.sub(r"\.git$", "", url)

        # Convert SSH to HTTPS
        if url.startswith("git@github.com:"):
            url = url.replace("git@github.com:", "https://github.com/")
        elif url.startswith("git@gitlab.com:"):
            url = url.replace("git@gitlab.com:", "https://gitlab.com/")

        return url

    @staticmethod
    def extract_email_address(from_field: str) -> str:
        """Extract clean email address from 'From' header.

        Args:
            from_field: Email 'From' header (e.g., 'Name <email@example.com>')

        Returns:
            Clean email address
        """
        # Extract email from "Name <email@example.com>" format
        match = re.search(r"<(.+?)>", from_field)
        if match:
            return match.group(1)

        # If no brackets, assume it's just the email
        match = re.search(r"[\w\.\-]+@[\w\.\-]+", from_field)
        if match:
            return match.group(0)

        return from_field
