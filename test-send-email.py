#!/usr/bin/env python3
"""Quick test email script"""

import sys
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).parent

sys.path.insert(0, str(BASE_DIR / 'skills' / 'actions' / 'send-email'))

from send_email import SendEmailSkill

# Initialize
skill = SendEmailSkill(BASE_DIR / 'AI_Employee_Vault')

# Send test email
print("📧 Sending test email...")
success = skill.send_email(
    to='syedaabihaahmed194@gmail.com',
    subject='Test from AI Employee',
    content='This is a test email to verify the system is working!',
    requires_approval=False
)

if success:
    print("✅ Email sent successfully!")
    print("📬 Check Gmail Sent folder: https://mail.google.com/mail/u/0/#sent")
else:
    print("❌ Failed to send email")
