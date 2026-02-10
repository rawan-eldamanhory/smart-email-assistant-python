"""
Email Templates for Smart Email Assistant.
Uses Jinja2 templating for dynamic email generation.

Template format:
  First line:  Subject: <subject text here>
  Blank line
  Everything below is the body (HTML supported)
"""

# ── Welcome ───────────────────────────────────────────────────────────────────

WELCOME_TEMPLATE = """Subject: Welcome to {{ company_name }}!

<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: #4CAF50; color: white; padding: 24px; text-align: center; border-radius: 8px 8px 0 0; }
    .content { padding: 24px; background: #f9f9f9; }
    .footer { text-align: center; padding: 16px; color: #888; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Welcome, {{ name }}! 🎉</h1>
    </div>
    <div class="content">
      <p>Hi {{ name }},</p>
      <p>Thank you for joining <strong>{{ company_name }}</strong>!
         We're excited to have you on board.</p>
      <h3>What's Next?</h3>
      <ul>
        <li>Complete your profile</li>
        <li>Explore our features</li>
        <li>Connect with your team</li>
      </ul>
      <p>If you have any questions, reach out to our support team anytime.</p>
      <p>Best regards,<br>The {{ company_name }} Team</p>
    </div>
    <div class="footer">
      <p>&copy; {{ year }} {{ company_name }}. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
"""

# ── Meeting confirmation ───────────────────────────────────────────────────────

MEETING_TEMPLATE = """Subject: Meeting Confirmed - {{ meeting_title }}

<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: #2196F3; color: white; padding: 20px; border-radius: 8px 8px 0 0; }
    .info-box { background: #e3f2fd; padding: 16px; margin: 16px 0; border-left: 4px solid #2196F3; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>📅 Meeting Confirmed</h2>
    </div>
    <div style="padding: 20px; background: #f9f9f9;">
      <p>Hi {{ attendee_name }},</p>
      <p>Your meeting has been confirmed!</p>
      <div class="info-box">
        <h3>{{ meeting_title }}</h3>
        <p><strong>📅 Date:</strong> {{ date }}</p>
        <p><strong>🕐 Time:</strong> {{ time }}</p>
        <p><strong>📍 Location:</strong> {{ location }}</p>
        {% if agenda %}
        <p><strong>📋 Agenda:</strong><br>{{ agenda }}</p>
        {% endif %}
      </div>
      <p>Looking forward to seeing you there!</p>
      <p>Best regards,<br>{{ organizer_name }}</p>
    </div>
  </div>
</body>
</html>
"""

# ── Thank you ─────────────────────────────────────────────────────────────────

THANK_YOU_TEMPLATE = """Subject: Thank You, {{ name }}!

<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: #FF9800; color: white; padding: 24px; text-align: center; border-radius: 8px 8px 0 0; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2>Thank You! 🙏</h2>
    </div>
    <div style="padding: 24px; background: #f9f9f9;">
      <p>Dear {{ name }},</p>
      <p>{{ message }}</p>
      <p>We truly appreciate your <strong>{{ reason }}</strong>.</p>
      <p>Warm regards,<br>{{ sender_name }}</p>
    </div>
  </div>
</body>
</html>
"""

# ── Auto-reply ────────────────────────────────────────────────────────────────

AUTO_REPLY_TEMPLATE = """Subject: Re: {{ original_subject }}

<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <p>Hi,</p>
  <p>Thank you for your email. This is an automated response to confirm
     that your message has been received.</p>
  {% if availability_date %}
  <p>I will be available to respond starting <strong>{{ availability_date }}</strong>.</p>
  {% else %}
  <p>I will respond as soon as possible.</p>
  {% endif %}
  {% if urgent_contact %}
  <p>For urgent matters, please contact:
     <a href="mailto:{{ urgent_contact }}">{{ urgent_contact }}</a></p>
  {% endif %}
  <p>Best regards,<br>{{ sender_name }}</p>
</body>
</html>
"""

# ── Newsletter ────────────────────────────────────────────────────────────────

NEWSLETTER_TEMPLATE = """Subject: {{ newsletter_title }} - {{ date }}

<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
    .container { max-width: 700px; margin: 0 auto; }
    .header { background: #673AB7; color: white; padding: 30px; text-align: center; }
    .article { padding: 20px; border-bottom: 1px solid #eee; }
    .article h3 { color: #673AB7; margin: 0 0 8px; }
    .footer { text-align: center; padding: 20px; color: #888; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{{ newsletter_title }}</h1>
      <p>{{ date }}</p>
    </div>
    {% for article in articles %}
    <div class="article">
      <h3>{{ article.title }}</h3>
      <p>{{ article.content }}</p>
      {% if article.link %}
      <p><a href="{{ article.link }}">Read more →</a></p>
      {% endif %}
    </div>
    {% endfor %}
    <div class="footer">
      <p>You're receiving this because you subscribed to our newsletter.</p>
      <p><a href="#">Unsubscribe</a></p>
    </div>
  </div>
</body>
</html>
"""


def get_template(name: str) -> str:
    """Return a template string by name."""
    mapping = {
        "welcome":    WELCOME_TEMPLATE,
        "meeting":    MEETING_TEMPLATE,
        "thank_you":  THANK_YOU_TEMPLATE,
        "auto_reply": AUTO_REPLY_TEMPLATE,
        "newsletter": NEWSLETTER_TEMPLATE,
    }
    result = mapping.get(name, "")
    if not result:
        available = ", ".join(mapping.keys())
        raise ValueError(f"Unknown template '{name}'. Available: {available}")
    return result


if __name__ == "__main__":
    print("Available templates: welcome, meeting, thank_you, auto_reply, newsletter")
