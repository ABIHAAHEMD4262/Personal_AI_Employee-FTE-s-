#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitor Gmail for important/unread emails.

Uses Gmail API to fetch emails and creates action files in /Needs_Action.

Usage:
    python gmail_watcher.py /path/to/vault [--interval 120] [--once] [--auth]
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Import base watcher from parent directory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'watchers'))
from base_watcher import BaseWatcher

# Gmail dependencies - check at runtime
GMAIL_AVAILABLE = False
Credentials = None
Request = None
build = None
HttpError = None
flow = None

def _check_gmail_dependencies():
    """Check if Gmail dependencies are available."""
    global GMAIL_AVAILABLE, Credentials, Request, build, HttpError, flow
    try:
        from google.oauth2.credentials import Credentials as Creds
        from google_auth_oauthlib.flow import InstalledAppFlow as Fl
        from google.auth.transport.requests import Request as Req
        from googleapiclient.discovery import build as bld
        from googleapiclient.errors import HttpError as HttpErr
        
        GMAIL_AVAILABLE = True
        Credentials = Creds
        Request = Req
        build = bld
        HttpError = HttpErr
        flow = Fl
        return True
    except ImportError:
        GMAIL_AVAILABLE = False
        return False

# Initial check
_check_gmail_dependencies()


class EmailItem:
    """Represents a Gmail message."""

    def __init__(self, message_data: Dict[str, Any]):
        self.id = message_data.get('id', '')
        self.thread_id = message_data.get('threadId', '')
        self.internal_data = message_data.get('internalDate', '')
        
        # Handle labels - can be list of dicts or list of strings
        label_data = message_data.get('labelIds', [])
        if label_data and isinstance(label_data[0], dict):
            self.labels = [l.get('name', '') for l in label_data]
        else:
            self.labels = label_data
        
        # Parse headers
        self.headers = {}
        self.payload = message_data.get('payload', {})
        
        # Headers can be in payload or in a separate headers field
        headers_list = []
        if self.payload and isinstance(self.payload, dict):
            headers_list = self.payload.get('headers', [])
        
        if headers_list and isinstance(headers_list, list):
            for h in headers_list:
                if isinstance(h, dict):
                    name = h.get('name', '')
                    value = h.get('value', '')
                    if name:
                        self.headers[name] = value
        
        # Extract common fields
        self.from_email = self.headers.get('From', 'Unknown')
        self.to_email = self.headers.get('To', '')
        self.subject = self.headers.get('Subject', 'No Subject')
        self.date = self.headers.get('Date', '')

        # Extract body
        self.body = self._extract_body()
        self.snippet = message_data.get('snippet', '')
    
    def _extract_body(self) -> str:
        """Extract email body from payload."""
        def decode_part(part):
            if not isinstance(part, dict):
                return ''
            body = part.get('body', {})
            if not isinstance(body, dict):
                return ''
            data = body.get('data', '')
            if data:
                try:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='replace')
                except:
                    return ''
            return ''

        if not self.payload or not isinstance(self.payload, dict):
            return ''

        # Try multipart first
        parts = self.payload.get('parts', [])
        if parts and isinstance(parts, list):
            # Look for plain text part
            for part in parts:
                if isinstance(part, dict) and part.get('mimeType') == 'text/plain':
                    result = decode_part(part)
                    if result:
                        return result
            # Fallback to html
            for part in parts:
                if isinstance(part, dict) and part.get('mimeType') == 'text/html':
                    result = decode_part(part)
                    if result:
                        return result

        # Try single part
        return decode_part(self.payload)
    
    def is_important(self) -> bool:
        """Check if email is marked important."""
        return 'IMPORTANT' in self.labels
    
    def is_unread(self) -> bool:
        """Check if email is unread."""
        return 'UNREAD' in self.labels


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new important/unread emails.
    """
    
    def __init__(self, vault_path: str, credentials_path: str = None, 
                 check_interval: int = 120):
        """
        Initialize the Gmail Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail OAuth credentials
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        # Credentials
        self.credentials_path = credentials_path or os.environ.get(
            'GMAIL_CREDENTIALS', 
            str(Path(__file__).parent / 'credentials.json')
        )
        self.token_path = Path(__file__).parent / 'token.json'
        
        # Configuration
        self.config_path = Path(__file__).parent / 'config.json'
        self.config = self._load_config()
        
        # Processed message IDs
        self.processed_ids: set = set()
        self._load_processed_ids()
        
        # Gmail service
        self.service = None
        
        # Check dependencies
        if not GMAIL_AVAILABLE:
            self.logger.warning(
                "Gmail dependencies not installed. "
                "Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
    
    def _load_config(self) -> Dict[str, Any]:
        """Load watcher configuration."""
        default_config = {
            'query': 'is:unread is:important',
            'max_results': 10,
            'keywords': ['urgent', 'asap', 'invoice', 'payment', 'help'],
            'exclude_senders': ['noreply@', 'notifications@', 'donotreply@'],
            'labels': ['INBOX'],
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def _load_processed_ids(self):
        """Load previously processed message IDs."""
        cache_file = self.vault_path / '.gmail_processed.cache'
        if cache_file.exists():
            try:
                self.processed_ids = set(
                    cache_file.read_text().strip().split('\n')
                )
                self.processed_ids.discard('')  # Remove empty strings
                self.logger.info(
                    f"Loaded {len(self.processed_ids)} processed message IDs"
                )
            except Exception as e:
                self.logger.warning(f"Could not load cache: {e}")
                self.processed_ids = set()
    
    def _save_processed_ids(self):
        """Save processed message IDs to cache."""
        cache_file = self.vault_path / '.gmail_processed.cache'
        try:
            # Keep only last 1000 IDs to prevent unbounded growth
            ids_list = list(self.processed_ids)[-1000:]
            cache_file.write_text('\n'.join(ids_list))
        except Exception as e:
            self.logger.warning(f"Could not save cache: {e}")
    
    def authenticate(self, no_browser: bool = False):
        """Run OAuth authentication flow.

        Set no_browser=True (or pass --no-browser) when running in WSL/SSH
        where a browser cannot be opened automatically. A URL will be printed
        instead — paste it into any browser, complete the login, then paste
        the resulting code back into the terminal.
        """
        if not GMAIL_AVAILABLE:
            print("Gmail dependencies not installed.")
            print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return False

        try:
            flow_instance = flow.from_client_secrets_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
            )

            if no_browser:
                flow_instance.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                auth_url, _ = flow_instance.authorization_url(prompt='consent')
                print("\n" + "=" * 60)
                print("WSL/headless mode: cannot open browser automatically.")
                print("1. Copy this URL and open it in your Windows browser:")
                print(f"\n   {auth_url}\n")
                print("2. Sign in with Google and click Allow.")
                print("3. Copy the authorization code shown on the page.")
                print("=" * 60)
                code = input("Paste the authorization code here: ").strip()
                flow_instance.fetch_token(code=code)
                creds = flow_instance.credentials
            else:
                creds = flow_instance.run_local_server(port=0)

            # Save credentials
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())

            print("Authentication successful!")
            print(f"Credentials saved to: {self.token_path}")
            return True

        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def _get_credentials(self) -> Optional[Credentials]:
        """Get valid Gmail credentials."""
        creds = None
        
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path,
                    scopes=['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
                )
            except Exception as e:
                self.logger.warning(f"Could not load token: {e}")
                self.token_path.unlink()
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Token refresh failed: {e}")
                    return None
            else:
                self.logger.error("No valid credentials. Run with --auth first.")
                return None
            
            # Save refreshed credentials
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())
        
        return creds
    
    def _connect(self) -> bool:
        """Connect to Gmail API."""
        if self.service is not None:
            return True
        
        creds = self._get_credentials()
        if not creds:
            return False
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Connected to Gmail API")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Gmail API: {e}")
            return False
    
    def check_for_updates(self) -> List[EmailItem]:
        """
        Check Gmail for new messages.
        
        Returns:
            List of new EmailItem objects
        """
        if not self._connect():
            return []
        
        try:
            # Fetch messages
            results = self.service.users().messages().list(
                userId='me',
                q=self.config['query'],
                maxResults=self.config['max_results']
            ).execute()
            
            messages = results.get('messages', [])
            self.logger.debug(f"Found {len(messages)} messages matching query")
            
            # Process messages
            items = []
            for msg in messages:
                if msg['id'] in self.processed_ids:
                    continue
                
                # Fetch full message
                try:
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()
                    
                    email = EmailItem(full_msg)
                    
                    # Check exclusions
                    if self._should_exclude(email):
                        self.processed_ids.add(msg['id'])
                        continue
                    
                    items.append(email)
                    self.processed_ids.add(msg['id'])
                    
                except Exception as e:
                    self.logger.error(f"Error fetching message {msg['id']}: {e}")
            
            # Save updated cache
            if items:
                self._save_processed_ids()
            
            return items
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []
    
    def _should_exclude(self, email: EmailItem) -> bool:
        """Check if email should be excluded."""
        # Check excluded senders
        for excluded in self.config.get('exclude_senders', []):
            if excluded.lower() in email.from_email.lower():
                return True
        
        return False
    
    def create_action_file(self, item: EmailItem) -> Optional[Path]:
        """
        Create action file for email.
        
        Args:
            item: EmailItem to process
            
        Returns:
            Path to created .md file
        """
        try:
            # Generate filename
            safe_subject = "".join(
                c for c in item.subject 
                if c.isalnum() or c in ' -_'
            )[:50]
            filename = f"EMAIL_{safe_subject}_{item.id}.md"
            filepath = self.needs_action / filename
            
            # Determine priority
            priority = 'high' if item.is_important() else 'normal'
            
            # Generate suggested actions
            actions = self._get_suggested_actions(item)
            
            # Create content
            content = f"""---
type: email
from: {item.from_email}
to: {item.to_email}
subject: {item.subject}
received: {datetime.now().isoformat()}
message_id: {item.id}
priority: {priority}
status: pending
labels: {json.dumps(item.labels)}
---

# Email: {item.subject}

## From
{item.from_email}

## Received
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content
{item.body if item.body else item.snippet}

## Suggested Actions
{actions}
"""
            filepath.write_text(content)
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to create action file: {e}")
            return None
    
    def _get_suggested_actions(self, email: EmailItem) -> str:
        """Get suggested actions based on email content."""
        actions = ['- [ ] Read and understand email content']
        
        content_lower = (email.subject + ' ' + email.body).lower()
        
        # Check for keywords
        if any(kw in content_lower for kw in ['invoice', 'payment', 'bill']):
            actions.extend([
                '- [ ] Identify amount and due date',
                '- [ ] Create approval request for payment',
                '- [ ] Forward to accounting if needed',
            ])
        elif any(kw in content_lower for kw in ['urgent', 'asap', 'emergency']):
            actions.extend([
                '- [ ] Respond promptly (high priority)',
                '- [ ] Take required action',
            ])
        elif any(kw in content_lower for kw in ['meeting', 'schedule', 'calendar']):
            actions.extend([
                '- [ ] Check availability',
                '- [ ] Respond with available times',
                '- [ ] Add to calendar',
            ])
        else:
            actions.extend([
                '- [ ] Draft appropriate reply',
                '- [ ] Send reply (requires approval for new contacts)',
            ])
        
        actions.append('- [ ] Archive email after processing')
        
        return '\n'.join(actions)
    
    def check_config(self) -> bool:
        """Check if configuration is valid."""
        issues = []
        
        # Check credentials file
        if not Path(self.credentials_path).exists():
            issues.append(f"Credentials file not found: {self.credentials_path}")
        
        # Check dependencies
        if not GMAIL_AVAILABLE:
            issues.append("Gmail dependencies not installed")
        
        # Report
        if issues:
            print("Configuration Issues:")
            for issue in issues:
                print(f"  ❌ {issue}")
            return False
        else:
            print("✅ Configuration OK")
            print(f"  Credentials: {self.credentials_path}")
            print(f"  Token: {self.token_path}")
            print(f"  Query: {self.config['query']}")
            return True


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gmail Watcher - Monitor Gmail for important emails"
    )
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=120,
        help="Check interval in seconds (default: 120)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for cron)"
    )
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Run OAuth authentication"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="WSL/SSH mode: print auth URL instead of opening a browser"
    )
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check configuration"
    )
    parser.add_argument(
        "--credentials",
        help="Path to Gmail credentials.json"
    )
    
    args = parser.parse_args()
    
    watcher = GmailWatcher(
        args.vault_path,
        credentials_path=args.credentials,
        check_interval=args.interval
    )
    
    if args.auth:
        success = watcher.authenticate(no_browser=args.no_browser)
        exit(0 if success else 1)
    
    if args.check_config:
        success = watcher.check_config()
        exit(0 if success else 1)
    
    if args.once:
        count = watcher.run_once()
        print(f"Processed {count} email(s)")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
