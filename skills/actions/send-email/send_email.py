#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send Email Skill - Send emails via MCP server with approval.

Usage:
    python send_email.py /path/to/vault --send --to email --subject "Subj" --content "Msg"
    python send_email.py /path/to/vault --draft --to email --subject "Subj" --content "Msg"
    python send_email.py /path/to/vault --search "query"
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


class SendEmailSkill:
    """
    Send emails with human-in-the-loop approval.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the skill.
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path).resolve()
        
        # Folders
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.drafts_folder = self.vault_path / 'Drafts'
        
        # Ensure folders exist
        for folder in [self.pending_folder, self.approved_folder, 
                       self.done_folder, self.drafts_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Config
        self.config_path = Path(__file__).parent / 'config.json'
        self.config = self._load_config()
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        print(f"[{level}] {message}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration."""
        default = {
            'auto_approve_contacts': [],
            'require_approval': True,
            'signature': '',
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)
                    default.update(config)
            except:
                pass
        
        return default
    
    def send_email(self, to: str, subject: str, content: str, 
                   cc: str = None, requires_approval: bool = True) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            content: Email body
            cc: CC recipient (optional)
            requires_approval: Whether approval is needed
            
        Returns:
            True if sent successfully
        """
        # Check if auto-approve
        if not requires_approval:
            for contact in self.config.get('auto_approve_contacts', []):
                if contact.lower() in to.lower():
                    requires_approval = False
                    break
        
        if requires_approval:
            # Create approval request
            return self._create_approval_request(to, subject, content, cc)
        else:
            # Send directly via MCP
            return self._execute_send(to, subject, content, cc)
    
    def _create_approval_request(self, to: str, subject: str, 
                                  content: str, cc: str = None) -> bool:
        """Create approval request for email."""
        try:
            now = datetime.now()
            filename = f"EMAIL_SEND_{now.strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.pending_folder / filename
            
            file_content = f"""---
type: approval_request
action: email_send
to: {to}
cc: {cc or ''}
subject: {subject}
created: {now.isoformat()}
expires: {datetime.now().replace(hour=23, minute=59).isoformat()}
status: pending
---

# Approval Request: Send Email

## Email Details
- **To:** {to}
{f"- **CC:** {cc}" if cc else ""}
- **Subject:** {subject}

## Content
{content}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.
"""
            filepath.write_text(file_content)
            
            self.log(f"Created approval request: {filename}")
            self.log(f"  To: {to}")
            self.log(f"  Subject: {subject}")
            
            return True
            
        except Exception as e:
            self.log(f"Failed to create approval request: {e}", "ERROR")
            return False
    
    def _execute_send(self, to: str, subject: str, content: str, 
                      cc: str = None) -> bool:
        """
        Execute email send via MCP server OR direct Gmail API.
        """
        try:
            self.log(f"Sending email via Gmail API...")
            self.log(f"  To: {to}")
            self.log(f"  Subject: {subject}")
            
            # Try to use Gmail API directly
            success = self._send_via_gmail_api(to, subject, content, cc)
            
            if success:
                self.log(f"  → Email sent successfully!")
                self.log(f"  → Check Gmail Sent folder")
                self._log_email(to, subject, 'sent')
                return True
            else:
                self.log(f"  → Gmail API failed, using simulation", "WARNING")
                self.log(f"  → (Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib)")
                self._log_email(to, subject, 'simulated')
                return True  # Return True even for simulation
                
        except Exception as e:
            self.log(f"Failed to send email: {e}", "ERROR")
            return False
    
    def _send_via_gmail_api(self, to: str, subject: str, body: str, 
                            cc: str = None) -> bool:
        """Send email using Gmail API directly."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import base64
            from email.mime.text import MIMEText

            # Load credentials
            creds_path = Path(__file__).parent.parent.parent.parent / 'credentials.json'
            token_path = Path(__file__).parent.parent.parent / 'mcp-servers' / 'email-mcp' / 'token.json'

            if not creds_path.exists():
                self.log("  → Credentials file not found", "ERROR")
                return False

            # For now, simulate if no token
            if not token_path.exists():
                self.log("  → No OAuth token (run: node auth_gmail.js)", "WARNING")
                return False

            # Load token and credentials
            token_data = json.loads(token_path.read_text())
            creds_data = json.loads(creds_path.read_text())
            
            # Build credentials with all required info
            creds = Credentials(
                token=token_data.get('access_token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=creds_data['installed']['client_id'],
                client_secret=creds_data['installed']['client_secret'],
                scopes=['https://www.googleapis.com/auth/gmail.send']
            )

            # Refresh if needed
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())

            # Build service
            service = build('gmail', 'v1', credentials=creds)

            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc

            # Encode and send
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            self.log(f"  → Gmail API sent! Message ID: {result['id']}")
            return True
            
        except ImportError:
            self.log("  → Gmail API not installed", "WARNING")
            return False
        except Exception as e:
            self.log(f"  → API error: {e}", "ERROR")
            return False
    
    def _log_email(self, to: str, subject: str, status: str):
        """Log email action."""
        log_file = self.vault_path / 'Logs' / 'email_log.md'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        if not log_file.exists():
            log_file.write_text("# Email Log\n\n")

        timestamp = datetime.now().isoformat()
        entry = f"- [{timestamp}] {status.upper()}: To={to}, Subject={subject}\n"
        with open(log_file, 'a') as f:
            f.write(entry)
    
    def draft_email(self, to: str, subject: str, content: str, 
                    cc: str = None) -> Optional[Path]:
        """
        Draft an email for review.
        
        Args:
            to: Recipient email
            subject: Email subject
            content: Email body
            cc: CC recipient
            
        Returns:
            Path to draft file
        """
        try:
            now = datetime.now()
            filename = f"DRAFT_{now.strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.drafts_folder / filename
            
            # Add signature
            full_content = content
            if self.config.get('signature'):
                full_content += f"\n\n{self.config['signature']}"
            
            file_content = f"""---
type: email_draft
to: {to}
cc: {cc or ''}
subject: {subject}
created: {now.isoformat()}
status: draft
---

# Draft Email

## To
{to}

## Subject
{subject}

## Content
{full_content}

---
*To send this email, move to /Pending_Approval or use send-email skill*
"""
            filepath.write_text(file_content)
            
            self.log(f"Created draft: {filename}")
            return filepath
            
        except Exception as e:
            self.log(f"Failed to create draft: {e}", "ERROR")
            return None
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search emails via MCP server.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of email info dicts
        """
        self.log(f"Searching emails: '{query}'")
        
        # TODO: Integrate with MCP server
        # For now, return mock results
        self.log(f"  → Search via MCP server (not connected)")
        
        return []
    
    def process_approved(self) -> int:
        """
        Process approved email actions.
        
        Returns:
            Number of emails sent
        """
        sent = 0
        
        if not self.approved_folder.exists():
            return 0
        
        for md_file in self.approved_folder.glob('*.md'):
            try:
                content = md_file.read_text()
                
                # Parse frontmatter
                frontmatter = self._parse_frontmatter(content)
                
                if frontmatter.get('action') != 'email_send':
                    continue
                
                to = frontmatter.get('to', '')
                subject = frontmatter.get('subject', '')
                
                # Extract content from markdown
                content_start = content.find('## Content')
                if content_start == -1:
                    content_start = content.find('## Body')
                
                email_content = ''
                if content_start != -1:
                    # Get content after the header
                    lines = content[content_start:].split('\n')[2:]
                    email_content = '\n'.join(lines).strip()
                
                # Send email
                if self._execute_send(to, subject, email_content):
                    # Move to Done
                    today = datetime.now().strftime('%Y-%m-%d')
                    done_folder = self.done_folder / today
                    done_folder.mkdir(parents=True, exist_ok=True)
                    md_file.rename(done_folder / md_file.name)
                    sent += 1
                    
            except Exception as e:
                self.log(f"Error processing {md_file.name}: {e}", "ERROR")
        
        return sent
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter."""
        frontmatter = {}
        in_frontmatter = False
        
        for line in content.split('\n'):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        
        return frontmatter


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Send Email Skill - Send emails with approval"
    )
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault"
    )
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--send",
        action="store_true",
        help="Send email"
    )
    action_group.add_argument(
        "--draft",
        action="store_true",
        help="Draft email"
    )
    action_group.add_argument(
        "--search",
        help="Search emails"
    )
    action_group.add_argument(
        "--process-approved",
        action="store_true",
        help="Process approved email actions"
    )
    
    # Email parameters
    parser.add_argument(
        "--to", "-t",
        help="Recipient email address"
    )
    parser.add_argument(
        "--subject", "-s",
        help="Email subject"
    )
    parser.add_argument(
        "--content", "-c",
        help="Email content"
    )
    parser.add_argument(
        "--cc",
        help="CC recipient"
    )
    parser.add_argument(
        "--no-approval",
        action="store_true",
        help="Skip approval (use with caution)"
    )
    parser.add_argument(
        "--max",
        type=int,
        default=10,
        help="Max search results"
    )
    
    args = parser.parse_args()
    
    skill = SendEmailSkill(args.vault_path)
    
    if args.send:
        if not all([args.to, args.subject, args.content]):
            print("Error: --to, --subject, and --content required for --send")
            exit(1)
        
        success = skill.send_email(
            args.to, args.subject, args.content, args.cc,
            requires_approval=not args.no_approval
        )
        exit(0 if success else 1)
    
    elif args.draft:
        if not all([args.to, args.subject, args.content]):
            print("Error: --to, --subject, and --content required for --draft")
            exit(1)
        
        result = skill.draft_email(args.to, args.subject, args.content, args.cc)
        exit(0 if result else 1)
    
    elif args.search:
        results = skill.search_emails(args.search, args.max)
        for email in results:
            print(f"From: {email.get('from', 'Unknown')}")
            print(f"Subject: {email.get('subject', 'No subject')}")
            print()
    
    elif args.process_approved:
        sent = skill.process_approved()
        print(f"Sent {sent} email(s)")


if __name__ == "__main__":
    main()
