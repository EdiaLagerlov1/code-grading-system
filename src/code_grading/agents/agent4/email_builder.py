"""Email content builder from templates."""

import re
from pathlib import Path
from typing import Dict, Optional


class EmailBuilder:
    """Build email content from templates."""

    def __init__(self, template_dir: Path):
        """Initialize email builder.

        Args:
            template_dir: Directory containing email templates
        """
        self.template_dir = template_dir

    def build_email(
        self,
        feedback: str,
        recipient: str,
        original_subject: Optional[str] = None,
        grade: float = 0.0,
    ) -> Dict[str, str]:
        """Build email content.

        Args:
            feedback: Feedback text
            recipient: Recipient email address
            original_subject: Original email subject to extract exercise number
            grade: Student's grade (0-100)

        Returns:
            Dictionary with 'subject', 'body', 'to' keys
        """
        # Extract exercise number from original subject
        exercise_num = self._extract_exercise_number(original_subject)

        if exercise_num:
            subject = f"תוצאות בדיקה עצמית - תרגיל {exercise_num}"
        else:
            subject = "תוצאות בדיקה עצמית - תרגיל"

        # Load template or use default
        template_file = self.template_dir / "email_template.html"

        if template_file.exists():
            with open(template_file, "r", encoding="utf-8") as f:
                body_template = f.read()
        else:
            body_template = self._get_default_template()

        # Generate recommendations only if grade < 100
        recommendations = self._get_recommendations(grade)

        # Replace placeholders
        body = body_template.replace("{feedback}", feedback)
        body = body.replace("{recommendations}", recommendations)

        return {
            "to": recipient,
            "subject": subject,
            "body": body,
        }

    @staticmethod
    def _get_recommendations(grade: float) -> str:
        """Get recommendations HTML based on grade.

        Args:
            grade: Student's grade (0-100)

        Returns:
            HTML string with recommendations, or empty string for perfect scores
        """
        if grade >= 100:
            return ""

        return """<p>אנו ממליצים לשפר את הקוד לפי ההנחיות:</p>
        <ul>
            <li>שמירה על אורך קובץ עד 150 שורות</li>
            <li>הפרדת קוד לפונקציות קטנות וממוקדות</li>
            <li>שימוש בעקרונות SOLID</li>
        </ul>"""

    @staticmethod
    def _extract_exercise_number(subject: Optional[str]) -> Optional[str]:
        """Extract exercise number from email subject.

        Args:
            subject: Email subject line

        Returns:
            Exercise number as string, or None if not found
        """
        if not subject:
            return None

        # Look for pattern like "תרגיל 15" or "תרגיל15"
        match = re.search(r"תרגיל\s*(\d+)", subject)
        if match:
            return match.group(1)

        return None

    @staticmethod
    def _get_default_template() -> str:
        """Get default email template.

        Returns:
            Default HTML template
        """
        return """<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .feedback {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>שלום,</h2>
        <p>להלן המשוב על התרגיל שלך:</p>
        <div class="feedback">
            {feedback}
        </div>
        <p>בברכה,<br>המערכת</p>
    </div>
</body>
</html>"""
