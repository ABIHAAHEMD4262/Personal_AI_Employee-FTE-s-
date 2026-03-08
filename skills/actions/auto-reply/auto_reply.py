#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Email Reply - Automatically reply to approved emails.

Workflow:
1. Gmail Watcher creates file in /Needs_Action/
2. User moves file to /Approved/
3. This script generates reply and sends email
4. Moves file to /Done/

Usage:
    python auto_reply.py /path/to/vault
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class AutoEmailReply:
    """Automatically reply to approved emails."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.pending_folder = self.vault_path / 'Pending_Approval'
        
        # Ensure folders exist
        for folder in [self.approved_folder, self.done_folder, self.pending_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Email signature
        self.signature = "\n\nBest regards,\nAI Employee\nAutomated Email System"
    
    def log(self, message: str, level: str = "INFO"):
        print(f"[{level}] {message}")
    
    def parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter."""
        frontmatter = {}
        in_frontmatter = False
        
        for line in content.split('\n'):
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"')
        
        return frontmatter
    
    def extract_email_content(self, content: str) -> str:
        """Extract email body from action file."""
        # Find content after ## Content header
        match = re.search(r'## Content\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def generate_reply(self, original_email: Dict[str, Any], content: str) -> str:
        """Generate an appropriate reply based on email content."""
        subject = original_email.get('subject', 'No Subject')
        from_email = original_email.get('from', 'Unknown')
        email_body = self.extract_email_content(content)
        
        # Analyze email type and generate appropriate reply
        email_lower = email_body.lower()
        subject_lower = subject.lower()
        
        # Determine reply type
        if any(word in email_lower for word in ['invoice', 'payment', 'bill']):
            reply = self._invoice_reply(from_email, subject, email_body)
        elif any(word in email_lower for word in ['meeting', 'schedule', 'call']):
            reply = self._meeting_reply(from_email, subject, email_body)
        elif any(word in email_lower for word in ['question', 'help', 'support']):
            reply = self._support_reply(from_email, subject, email_body)
        elif any(word in email_lower for word in ['urgent', 'asap', 'emergency']):
            reply = self._urgent_reply(from_email, subject, email_body)
        else:
            reply = self._general_reply(from_email, subject, email_body)
        
        return reply
    
    def _general_reply(self, from_email: str, subject: str, body: str) -> str:
        """General purpose reply."""
        return f"""Dear {from_email.split('<')[0].strip()},

Thank you for your email regarding "{subject}".

I have received your message and will review it shortly. You can expect a detailed response within 24 hours.

If this is urgent, please reply with "URGENT" in the subject line.

Best regards,
AI Employee
Automated Email System"""
    
    def _invoice_reply(self, from_email: str, subject: str, body: str) -> str:
        """Invoice/payment related reply."""
        return f"""Dear {from_email.split('<')[0].strip()},

Thank you for your email regarding "{subject}".

I have received your invoice/payment request and it has been forwarded to our accounting system for processing.

You will receive a confirmation once the payment has been processed.

If you have any questions, please don't hesitate to reach out.

Best regards,
AI Employee
Automated Email System"""
    
    def _meeting_reply(self, from_email: str, subject: str, body: str) -> str:
        """Meeting/scheduling reply."""
        return f"""Dear {from_email.split('<')[0].strip()},

Thank you for reaching out regarding "{subject}".

I would be happy to schedule a meeting. Please share your availability for the coming week, and I will coordinate accordingly.

Looking forward to connecting.

Best regards,
AI Employee
Automated Email System"""
    
    def _support_reply(self, from_email: str, subject: str, body: str) -> str:
        """Support/question reply."""
        return f"""Dear {from_email.split('<')[0].strip()},

Thank you for contacting support regarding "{subject}".

I have received your inquiry and am reviewing the details. You will receive a comprehensive response with a solution within 24 hours.

If this is urgent, please reply with "URGENT" in the subject line.

Best regards,
AI Employee
Automated Email System"""
    
    def _urgent_reply(self, from_email: str, subject: str, body: str) -> str:
        """Urgent email reply."""
        return f"""Dear {from_email.split('<')[0].strip()},

I have received your URGENT email regarding "{subject}".

This has been flagged for immediate attention. You will receive a priority response within 2 hours.

Thank you for your patience.

Best regards,
AI Employee
Automated Email System"""
    
    def create_send_approval(self, to_email: str, subject: str, content: str, 
                              original_file: Path) -> Path:
        """Create approval request for sending email."""
        now = datetime.now()
        filename = f"EMAIL_SEND_{now.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.pending_folder / filename
        
        file_content = f"""---
type: approval_request
action: email_send
to: {to_email}
subject: Re: {subject}
content_preview: {content[:100]}...
created: {now.isoformat()}
status: auto_generated
original_file: {original_file.name}
---

# Auto-Generated Email Reply

## To
{to_email}

## Subject
Re: {subject}

## Content
{content}

---
*Generated by Auto Email Reply Skill*
*Auto-approved - ready to send*
"""
        filepath.write_text(file_content)
        return filepath
    
    def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """Send email via send-email skill."""
        try:
            # Use send-email skill
            import subprocess
            
            # Create the email directly (bypass approval since user already approved by moving file)
            result = subprocess.run([
                'python',
                'skills/actions/send-email/send_email.py',
                str(self.vault_path),
                '--send',
                '--to', to_email,
                '--subject', f'Re: {subject}',
                '--content', content,
                '--no-approval'  # Skip approval since user already approved
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log(f"  → Email sent successfully")
                return True
            else:
                self.log(f"  → Send failed: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"  → Error sending email: {e}", "ERROR")
            return False
    
    def move_to_done(self, source_file: Path):
        """Move processed file to Done folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        done_today = self.done_folder / today
        done_today.mkdir(parents=True, exist_ok=True)
        
        dest = done_today / source_file.name
        source_file.rename(dest)
        self.log(f"  → Moved to Done/{today}/")
    
    def process_approved_emails(self) -> int:
        """Process all approved email files."""
        processed = 0
        
        if not self.approved_folder.exists():
            self.log("No Approved folder found")
            return 0
        
        # Find email action files in Approved folder
        email_files = list(self.approved_folder.glob('EMAIL_*.md'))
        
        if not email_files:
            self.log("No email files in Approved folder")
            return 0
        
        self.log(f"Found {len(email_files)} email(s) to process")
        
        for email_file in email_files:
            try:
                self.log(f"\nProcessing: {email_file.name}")
                
                # Read email content
                content = email_file.read_text()
                frontmatter = self.parse_frontmatter(content)
                
                # Extract email details
                from_email = frontmatter.get('from', '')
                subject = frontmatter.get('subject', 'No Subject')
                to_email = frontmatter.get('to', '')
                
                # Extract sender email address
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_email)
                if email_match:
                    sender_email = email_match.group()
                else:
                    self.log("  → Could not extract sender email", "ERROR")
                    continue
                
                # Generate reply
                self.log("  → Generating reply...")
                reply_content = self.generate_reply(frontmatter, content)
                
                # Send email
                self.log("  → Sending email...")
                if self.send_email(sender_email, subject, reply_content):
                    # Move to Done
                    self.move_to_done(email_file)
                    processed += 1
                else:
                    self.log("  → Failed to send email", "ERROR")
                    
            except Exception as e:
                self.log(f"Error processing {email_file.name}: {e}", "ERROR")
        
        return processed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Auto Email Reply - Automatically reply to approved emails"
    )
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch for new approved files continuously"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Check interval in seconds (default: 30)"
    )
    
    args = parser.parse_args()
    
    auto_reply = AutoEmailReply(args.vault_path)
    
    if args.watch:
        import time
        auto_reply.log(f"Watching for approved emails (interval: {args.interval}s)")
        try:
            while True:
                processed = auto_reply.process_approved_emails()
                if processed > 0:
                    auto_reply.log(f"Processed {processed} email(s)")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            auto_reply.log("\nStopped by user")
    else:
        processed = auto_reply.process_approved_emails()
        auto_reply.log(f"\n✅ Processed {processed} email(s)")


if __name__ == "__main__":
    main()
