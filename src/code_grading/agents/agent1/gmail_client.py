"""Gmail API client with OAuth2 authentication."""

import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GmailClient:
    """Gmail API client wrapper."""

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
    ]

    def __init__(self, credentials_path: Path, token_path: Path):
        """Initialize Gmail client.

        Args:
            credentials_path: Path to OAuth2 credentials JSON
            token_path: Path to store/load access token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None

    def authenticate(self) -> None:
        """Authenticate with Gmail API using OAuth2."""
        creds = None

        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())

        self.service = build("gmail", "v1", credentials=creds)

    def search_messages(
        self,
        folder: str,
        subject_filter: str,
        max_results: int = 100,
    ) -> List[Dict[str, str]]:
        """Search for messages matching criteria.

        Args:
            folder: Gmail folder/label to search
            subject_filter: Subject text to filter by
            max_results: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries with id, date, email, subject, body
        """
        if not self.service:
            self.authenticate()

        # Build query
        query = f'label:{folder} subject:"{subject_filter}"'

        # Search messages
        results = (
            self.service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )

        messages = results.get("messages", [])
        parsed_messages = []

        for msg in messages:
            msg_data = self._get_message_details(msg["id"])
            if msg_data:
                parsed_messages.append(msg_data)

        return parsed_messages

    def _get_message_details(self, msg_id: str) -> Optional[Dict[str, str]]:
        """Get full message details.

        Args:
            msg_id: Message ID

        Returns:
            Dictionary with message details
        """
        msg = self.service.users().messages().get(userId="me", id=msg_id).execute()

        headers = msg["payload"].get("headers", [])
        subject = self._get_header(headers, "Subject")
        from_email = self._get_header(headers, "From")
        date_str = self._get_header(headers, "Date")

        # Parse date
        date = self._parse_date(date_str)

        # Get body
        body = self._get_body(msg["payload"])

        return {
            "id": msg_id,
            "date": date,
            "email": from_email,
            "subject": subject,
            "body": body,
        }

    @staticmethod
    def _get_header(headers: List[Dict], name: str) -> str:
        """Extract header value by name."""
        for header in headers:
            if header["name"].lower() == name.lower():
                return header["value"]
        return ""

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parse email date string."""
        from email.utils import parsedate_to_datetime

        try:
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.now()

    def _get_body(self, payload: Dict) -> str:
        """Extract message body from payload."""
        if "parts" in payload:
            parts = payload["parts"]
            for part in parts:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        elif "body" in payload:
            data = payload["body"].get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        return ""
