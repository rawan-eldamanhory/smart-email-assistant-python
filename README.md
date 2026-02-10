# Smart Email Assistant (Python + Gmail API)

A Smart Email Assistant built with Python and the Gmail API that automatically reads emails, categorizes them, applies labels, extracts attachments, and sends templated replies using Jinja2.

This project demonstrates real-world API integration, OAuth2 authentication, email processing, rule-based classification, and template-based email generation.

---

## Features

* Gmail API OAuth2 authentication
* Fetch recent emails
* Extract subject, sender, body, snippet
* Rule-based email categorization
* Auto label creation & assignment
* Attachment detection & download
* Send emails via Gmail API
* Send templated HTML emails (Jinja2)
* Clean, modular Python design

---

## Project Structure

```
smart_email_assistant/
├── email_assistant.py      # Main application
├── email_templates.py      # Email templates
├── requirements.txt        # Dependencies
```

---

## Email Categories

Emails are categorized using:

* Keywords
* Sender domains
* Subject regex patterns

Example categories:

* Work
* Personal
* Newsletters
* Promotions
* Important
* Uncategorized

---

## Tech Stack

* Python 3.10+
* Gmail API
* Google OAuth2
* google-api-python-client
* Jinja2 templates
* pytest (testing)

---

## Installation

```bash
git clone https://github.com/rawan-eldamanhory/smart-email-assistant-python.git
cd smart-email-assistant

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

---

## Gmail API Setup

1. Go to Google Cloud Console
2. Create a new project
3. Enable **Gmail API**
4. Configure **OAuth Consent Screen**

   * Choose **External**
5. Create OAuth Client ID

   * Application type: Desktop App
6. Download credentials file
7. Rename to:

```
credentials.json
```

8. Place it in the project root folder

---

## Run

```bash
python email_assistant.py
```

First run will:

* Open browser for Gmail authorization
* Create `token.pickle`
* Store your OAuth access token

---

## Email Templates

The project includes Jinja2 templates:

* Welcome emails
* Meeting confirmations
* Thank you emails
* Auto replies
* Newsletters

Located in:

```
email_templates.py
```

---

## Future Improvements

* ML-based email classification
* Auto reply rules
* Background scheduler
* Web dashboard
* Vector search for email content
* AI summarization

---
