"""
Smart Email Assistant 
"""

import base64
import os
import pickle
import re
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from jinja2 import Template


OAUTH_PORT = 8080

TOKEN_FILE   = "token.pickle"
CREDS_FILE   = "credentials.json"
SCOPES       = ["https://www.googleapis.com/auth/gmail.modify"]

# Email category rules
CATEGORIES = {
    "work": {
        "keywords":     ["meeting", "project", "deadline", "invoice", "urgent"],
        "from_domains": ["company.com", "work.com", "enterprise.com"],
        "label":        "Work",
    },
    "personal": {
        "keywords": ["family", "friend", "birthday", "dinner", "vacation"],
        "label":    "Personal",
    },
    "newsletter": {
        "keywords":         ["unsubscribe", "newsletter", "weekly digest"],
        "subject_patterns": [r"newsletter", r"digest", r"updates?"],
        "label":            "Newsletters",
    },
    "promotion": {
        "keywords":         ["sale", "discount", "offer", "deal", "promo"],
        "subject_patterns": [r"\d+%\s*off", r"\bsale\b", r"\bdiscount\b"],
        "label":            "Promotions",
    },
    "important": {
        "keywords": ["important", "critical", "action required", "asap"],
        "label":    "Important",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Authentication  
# ─────────────────────────────────────────────────────────────────────────────


class EmailAssistant:
    """Smart Email Assistant — reads, categorises, labels and sends emails."""

    def __init__(self, credentials_path: str = CREDS_FILE):
        self.credentials_path = credentials_path
        self.service: Any = None
        self.user_email: str = ""

    # ── Auth ──────────────────────────────────────────────────────────────────

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail via OAuth2.
        """
        if not os.path.exists(self.credentials_path):
            print(f"\n'{self.credentials_path}' not found!\n")
            print("How to get it:")
            print("  1. https://console.cloud.google.com")
            print("  2. APIs & Services → Credentials")
            print("  3. Click your OAuth 2.0 Client ID → Download JSON")
            print("  4. Rename the file to credentials.json")
            print("  5. Place it next to email_assistant.py\n")
            return False

        creds = self._load_token()

        # Try to refresh an expired token
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._save_token(creds)
                print("Token refreshed")
            except RefreshError:
                print(" Saved token is invalid — re-authenticating...")
                self._delete_token()
                creds = None

        # Full browser login when no valid token exists
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, SCOPES
            )
            creds = flow.run_local_server(
                port=OAUTH_PORT,
                open_browser=True,
                authorization_prompt_message=(
                    "\nOpening browser for Google sign-in...\n"
                    "   If the browser doesn't open, visit:\n{url}\n"
                ),
                success_message="Authenticated! You can close this tab.",
            )
            self._save_token(creds)

        self.service = build("gmail", "v1", credentials=creds)

        # Cache the user's own email address (useful for sending)
        profile = self.service.users().getProfile(userId="me").execute()
        self.user_email = profile.get("emailAddress", "")

        print(f"Authenticated as: {self.user_email}")
        return True

    def _load_token(self):
        """Load token.pickle; return None if missing or corrupted."""
        if not os.path.exists(TOKEN_FILE):
            return None
        try:
            with open(TOKEN_FILE, "rb") as f:
                return pickle.load(f)
        except Exception:
            self._delete_token()
            return None

    def _save_token(self, creds) -> None:
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    def _delete_token(self) -> None:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)

    # ── Fetch emails ──────────────────────────────────────────────────────────

    def get_emails(
        self, max_results: int = 10, query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail.
        """
        try:
            resp = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
            emails = []
            for msg in resp.get("messages", []):
                details = self._get_email_details(msg["id"])
                if details:
                    emails.append(details)
            return emails
        except HttpError as err:
            print(f"Fetch error: {err}")
            return []

    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Return a structured dict for one message."""
        try:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
            headers = msg["payload"]["headers"]

            def h(name: str) -> str:
                return next(
                    (v["value"] for v in headers
                     if v["name"].lower() == name.lower()), ""
                )

            return {
                "id":      message_id,
                "subject": h("Subject") or "(no subject)",
                "from":    h("From"),
                "to":      h("To"),
                "date":    h("Date"),
                "body":    self._extract_body(msg["payload"]),
                "snippet": msg.get("snippet", ""),
                "labels":  msg.get("labelIds", []),
            }
        except HttpError as err:
            print(f"Could not read message {message_id}: {err}")
            return None

    def _extract_body(self, payload: Dict) -> str:
        """
        Recursively extract plain-text from any MIME structure.
        """
        def decode(data: str) -> str:
            try:
                return base64.urlsafe_b64decode(data + "==").decode(
                    "utf-8", errors="replace"
                )
            except Exception:
                return ""

        if "parts" in payload:
            # Prefer plain text over HTML
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        return decode(data)
            # recurse into nested parts / use HTML
            for part in payload["parts"]:
                if "parts" in part:
                    result = self._extract_body(part)
                    if result:
                        return result
                if part.get("mimeType") == "text/html":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        return decode(data)

        # Simple (non-multipart) message
        data = payload.get("body", {}).get("data", "")
        return decode(data) if data else ""

    # ── Categorise ────────────────────────────────────────────────────────────

    def categorize_email(self, email: Dict[str, Any]) -> str:
        """
        Categorise one email using keyword + regex rules.
        """
        subject   = email.get("subject", "").lower()
        sender    = email.get("from",    "").lower()
        body_text = (email.get("body", "") or email.get("snippet", "")).lower()
        full_text = f"{subject} {sender} {body_text}"

        for category, rules in CATEGORIES.items():
            if any(kw in full_text for kw in rules.get("keywords", [])):
                return category
            if any(d in sender for d in rules.get("from_domains", [])):
                return category
            if any(re.search(p, subject)
                   for p in rules.get("subject_patterns", [])):
                return category

        return "uncategorized"

    # ── Labels ────────────────────────────────────────────────────────────────

    def apply_label(self, message_id: str, category: str) -> bool:
        """Apply the category label to an email in Gmail."""
        label_name = CATEGORIES.get(category, {}).get(
            "label", category.capitalize()
        )
        label_id = self._get_or_create_label(label_name)
        if not label_id:
            return False
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"addLabelIds": [label_id]},
            ).execute()
            return True
        except HttpError as err:
            print(f"Label error: {err}")
            return False

    def _get_or_create_label(self, name: str) -> Optional[str]:
        """Return label ID """
        try:
            labels = (
                self.service.users().labels().list(userId="me").execute()
            ).get("labels", [])
            for lbl in labels:
                if lbl["name"].lower() == name.lower():
                    return lbl["id"]
            created = (
                self.service.users()
                .labels()
                .create(
                    userId="me",
                    body={
                        "name": name,
                        "labelListVisibility":   "labelShow",
                        "messageListVisibility": "show",
                    },
                )
                .execute()
            )
            return created["id"]
        except HttpError as err:
            print(f"Label lookup/create error: {err}")
            return None

    # ── Send email ────────────────────────────────────────────────────────────

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> bool:
        """
        Send an email.
        """
        try:
            if html:
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(body, "html", "utf-8"))   
            else:
                msg = MIMEText(body, "plain", "utf-8")       

            msg["To"]      = to
            msg["Subject"] = subject
            if self.user_email:
                msg["From"] = self.user_email

            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
            self.service.users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()
            print(f"Email sent to {to}")
            return True
        except HttpError as err:
            print(f"Send failed: {err}")
            return False

    def send_templated_email(
        self,
        to: str,
        template: str,
        context: Dict[str, Any],
    ) -> bool:
        """
        Render a Jinja2 template and send it.
        """
        rendered = Template(template).render(**context)
        lines    = rendered.strip().splitlines()

        subject  = ""
        body_lines: List[str] = []
        in_body  = False

        for line in lines:
            if not in_body and line.lower().startswith("subject:"):
                subject = line[len("subject:"):].strip()  # BUG 5 FIX
            elif subject and not in_body and line.strip() == "":
                in_body = True
            elif in_body:
                body_lines.append(line)

        body    = "\n".join(body_lines).strip()
        is_html = body.lstrip().startswith("<")
        return self.send_email(to, subject, body, html=is_html)

    # ── Attachments ───────────────────────────────────────────────────────────

    def get_attachments(self, message_id: str) -> List[Dict[str, Any]]:
        """
        List all attachments in an email.
        """
        try:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
            attachments: List[Dict[str, Any]] = []

            def _scan(parts: List[Dict]) -> None:
                for part in parts:
                    if part.get("filename"):
                        attachments.append({
                            "filename":     part["filename"],
                            "mimeType":     part.get("mimeType", ""),
                            "attachmentId": part["body"].get("attachmentId"),
                            "size":         part["body"].get("size", 0),
                        })
                    if "parts" in part:       
                        _scan(part["parts"])

            if "parts" in msg.get("payload", {}):
                _scan(msg["payload"]["parts"])
            return attachments
        except HttpError as err:
            print(f"Attachment list error: {err}")
            return []

    def download_attachment(
        self,
        message_id: str,
        attachment_id: str,
        filename: str,
        output_dir: str = "attachments",
    ) -> bool:
        """Download one attachment to disk."""
        os.makedirs(output_dir, exist_ok=True)
        try:
            data = (
                self.service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )
            raw = base64.urlsafe_b64decode(data["data"] + "==")
            path = os.path.join(output_dir, filename)
            with open(path, "wb") as f:
                f.write(raw)
            print(f"Saved → {path}")
            return True
        except HttpError as err:
            print(f"Download error: {err}")
            return False


# ─────────────────────────────────────────────────────────────────────────────
# Main demo
# ─────────────────────────────────────────────────────────────────────────────


def main() -> None:
    print()
    print("=" * 60)
    print("  SMART EMAIL ASSISTANT  ")
    print("=" * 60)
    print()

    assistant = EmailAssistant()

    # ── Authenticate ─────────────────────────────────────────────────────────
    print("Step 1: Authenticating...")
    if not assistant.authenticate():
        return
    print()

    # ── Fetch ─────────────────────────────────────────────────────────────────
    print("Step 2: Fetching 10 recent emails...")
    emails = assistant.get_emails(max_results=10)
    print(f"   Found {len(emails)} emails")

    if not emails:
        print("   Inbox appears empty — nothing to process.")
        return

    # ── Categorise + label ────────────────────────────────────────────────────
    print()
    print("Step 3: Categorising & applying Gmail labels...")
    print()
    print("  {:<50}  {:<15}  {}".format("Subject", "Category", "From"))
    print("  " + "─" * 80)

    labeled = 0
    for email in emails:
        cat = assistant.categorize_email(email)
        subj = email["subject"][:48]
        frm  = email["from"][:30]
        print(f"  {subj:<50}  {cat:<15}  {frm}")

        if cat != "uncategorized":
            if assistant.apply_label(email["id"], cat):
                labeled += 1

    print()
    print(f"   Labels applied: {labeled}/{len(emails)}")

    # ── Attachments ───────────────────────────────────────────────────────────
    print()
    print("Step 4: Checking for attachments in first 5 emails...")
    any_found = False
    for email in emails[:5]:
        atts = assistant.get_attachments(email["id"])
        if atts:
            any_found = True
            print(f"   {email['subject'][:50]}")
            for a in atts:
                kb = a["size"] // 1024
                print(f"    {a['filename']}  ({kb} KB)  [{a['mimeType']}]")
    if not any_found:
        print("   No attachments found in recent emails")

    # ── Send templated email ──────────────────────────────────────────────────
    print()
    print("Step 5: Sending a test welcome email to yourself...")
    from email_templates import WELCOME_TEMPLATE

    success = assistant.send_templated_email(
        to=assistant.user_email,
        template=WELCOME_TEMPLATE,
        context={
            "name":         "Developer",
            "company_name": "Email Assistant",
            "year":         datetime.now().year,
        },
    )
    if success:
        print(f"   Check your inbox at {assistant.user_email}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  All steps complete!")
    print("=" * 60)
    print()
    print("  Authenticated with OAuth")
    print("  Fetched and displayed emails")
    print("  Categorised by keyword/domain/regex rules")
    print("  Applied Gmail labels automatically")
    print("  Scanned attachments (recursive MIME)")
    print("  Sent a Jinja2-templated HTML email")
    print()


if __name__ == "__main__":
    main()
