#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Approval Workflow Skill - Human-in-the-loop for sensitive actions.

Manages approval requests between /Pending_Approval/, /Approved/, and /Rejected/ folders.

Usage:
    python approval_workflow.py /path/to/vault [--check] [--execute] [--create]
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List


class ApprovalWorkflowSkill:
    """
    Manage human-in-the-loop approvals for sensitive actions.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the skill.
        
        Args:
            vault_path: Path to the Obsidian vault root
        """
        self.vault_path = Path(vault_path).resolve()
        
        # Folders
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.pending_folder, self.approved_folder, 
                       self.rejected_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Log file
        self.log_file = self.logs_folder / 'approval_log.md'
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message to console and file."""
        print(f"[{level}] {message}")
        self._write_to_log(message, level)
    
    def _write_to_log(self, message: str, level: str = "INFO"):
        """Append message to approval log."""
        timestamp = datetime.now().isoformat()
        log_entry = f"- [{timestamp}] [{level}] {message}\n"
        
        # Initialize log file if needed
        if not self.log_file.exists():
            self.log_file.write_text(f"# Approval Log\n\n")
        
        self.log_file.append(log_entry)
    
    def parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown content."""
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
    
    def check_pending(self) -> List[Dict[str, Any]]:
        """
        Check all pending approval requests.
        
        Returns:
            List of pending approval info dicts
        """
        pending = []
        
        if not self.pending_folder.exists():
            return pending
        
        for md_file in self.pending_folder.glob('*.md'):
            try:
                content = md_file.read_text()
                frontmatter = self.parse_frontmatter(content)
                
                # Check if expired
                expires = frontmatter.get('expires', '')
                is_expired = False
                if expires:
                    try:
                        expiry_date = datetime.fromisoformat(expires)
                        is_expired = datetime.now() > expiry_date
                    except:
                        pass
                
                pending.append({
                    'file': md_file,
                    'name': md_file.stem,
                    'type': frontmatter.get('type', 'unknown'),
                    'action': frontmatter.get('action', 'unknown'),
                    'amount': frontmatter.get('amount', ''),
                    'recipient': frontmatter.get('recipient', ''),
                    'created': frontmatter.get('created', ''),
                    'expires': expires,
                    'is_expired': is_expired,
                    'priority': frontmatter.get('priority', 'normal'),
                })
            except Exception as e:
                self.log(f"Error reading {md_file.name}: {e}", "ERROR")
        
        return pending
    
    def display_pending(self, pending: List[Dict]):
        """Display pending approvals in a formatted way."""
        if not pending:
            print("\n✅ No pending approvals\n")
            return
        
        print(f"\n📋 Pending Approvals: {len(pending)}\n")
        print("-" * 60)
        
        for item in pending:
            status = "⚠️ EXPIRED" if item['is_expired'] else "⏳ Pending"
            print(f"\n{item['name']}")
            print(f"  Type: {item['action']}")
            if item['amount']:
                print(f"  Amount: {item['amount']}")
            if item['recipient']:
                print(f"  Recipient: {item['recipient']}")
            if item['expires']:
                print(f"  Expires: {item['expires']}")
            print(f"  Status: {status}")
        
        print("\n" + "-" * 60)
        print("\nTo approve: Move file to /Approved folder")
        print("To reject: Move file to /Rejected folder\n")
    
    def execute_approved(self) -> int:
        """
        Execute all approved actions.
        
        Returns:
            Number of actions executed
        """
        executed = 0
        
        if not self.approved_folder.exists():
            self.log("No approved actions to execute")
            return 0
        
        for md_file in self.approved_folder.glob('*.md'):
            try:
                content = md_file.read_text()
                frontmatter = self.parse_frontmatter(content)
                
                action_type = frontmatter.get('action', 'unknown')
                self.log(f"Executing: {md_file.stem}")
                self.log(f"  Action type: {action_type}")
                
                # Execute based on action type
                if action_type == 'payment':
                    self._execute_payment(frontmatter, md_file)
                elif action_type == 'email_send':
                    self._execute_email(frontmatter, md_file)
                elif action_type == 'social_post':
                    self._execute_post(frontmatter, md_file)
                else:
                    self.log(f"  Unknown action type: {action_type}", "WARNING")
                    self._archive_done(md_file)
                
                executed += 1
                
            except Exception as e:
                self.log(f"Failed to execute {md_file.name}: {e}", "ERROR")
        
        return executed
    
    def _execute_payment(self, frontmatter: Dict, md_file: Path):
        """Execute a payment action (placeholder for MCP integration)."""
        amount = frontmatter.get('amount', 'unknown')
        recipient = frontmatter.get('recipient', 'unknown')
        
        self.log(f"  Payment: ${amount} to {recipient}")
        self.log(f"  → Would execute via MCP payment server")
        self.log(f"  → Payment logged for execution")
        
        self._archive_done(md_file)
    
    def _execute_email(self, frontmatter: Dict, md_file: Path):
        """Execute an email send action (placeholder for MCP integration)."""
        recipient = frontmatter.get('to', frontmatter.get('recipient', 'unknown'))
        subject = frontmatter.get('subject', 'No subject')
        
        self.log(f"  Email to: {recipient}")
        self.log(f"  Subject: {subject}")
        self.log(f"  → Would execute via MCP email server")
        
        self._archive_done(md_file)
    
    def _execute_post(self, frontmatter: Dict, md_file: Path):
        """Execute a social media post action (placeholder for MCP integration)."""
        platform = frontmatter.get('platform', 'unknown')
        content = frontmatter.get('content', '')
        
        self.log(f"  Post to: {platform}")
        self.log(f"  Content: {content[:50]}...")
        self.log(f"  → Would execute via MCP social media server")
        
        self._archive_done(md_file)
    
    def _archive_done(self, md_file: Path):
        """Move executed file to Done folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        done_folder = self.done_folder / today
        done_folder.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(md_file), str(done_folder / md_file.name))
        self.log(f"  → Moved to /Done/{today}/")
    
    def create_approval_request(self, action_type: str, **kwargs) -> Optional[Path]:
        """
        Create a new approval request.
        
        Args:
            action_type: Type of action (payment, email_send, social_post, etc.)
            **kwargs: Action-specific parameters
            
        Returns:
            Path to created file, or None if failed
        """
        try:
            now = datetime.now()
            expires = now + timedelta(hours=24)
            
            # Generate filename
            safe_name = f"{action_type.upper()}_{now.strftime('%Y%m%d_%H%M%S')}"
            filename = f"{safe_name}.md"
            filepath = self.pending_folder / filename
            
            # Build content based on action type
            content = self._build_approval_content(action_type, kwargs, now, expires)
            
            filepath.write_text(content)
            
            self.log(f"Created approval request: {filename}")
            self.log(f"  Type: {action_type}")
            self.log(f"  Expires: {expires.isoformat()}")
            
            return filepath
            
        except Exception as e:
            self.log(f"Failed to create approval request: {e}", "ERROR")
            return None
    
    def _build_approval_content(self, action_type: str, kwargs: Dict, 
                                 created: datetime, expires: datetime) -> str:
        """Build approval request content based on action type."""
        
        templates = {
            'payment': self._payment_template,
            'email_send': self._email_template,
            'social_post': self._post_template,
            'file_delete': self._delete_template,
            'api_call': self._api_template,
        }
        
        template = templates.get(action_type, self._generic_template)
        return template(kwargs, created, expires)
    
    def _generic_template(self, kwargs: Dict, created: datetime, 
                          expires: datetime) -> str:
        """Generic approval template."""
        action = kwargs.get('action', 'unknown')
        reason = kwargs.get('reason', 'No reason provided')
        
        return f"""---
type: approval_request
action: {action}
created: {created.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: normal
---

# Approval Request: {action.title()}

## Action Details
- **Type:** {action}
- **Reason:** {reason}

## Context
{kwargs.get('context', 'Additional details about this action.')}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.

## Deadline
This request expires on {expires.strftime('%Y-%m-%d at %H:%M')}
"""
    
    def _payment_template(self, kwargs: Dict, created: datetime, 
                          expires: datetime) -> str:
        """Payment approval template."""
        amount = kwargs.get('amount', '0.00')
        recipient = kwargs.get('recipient', 'Unknown')
        reason = kwargs.get('reason', 'Payment')
        reference = kwargs.get('reference', '')
        
        return f"""---
type: approval_request
action: payment
amount: {amount}
recipient: {recipient}
reason: {reason}
reference: {reference}
created: {created.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: normal
---

# Approval Request: Payment

## Payment Details
- **Amount:** ${amount}
- **Recipient:** {recipient}
- **Reason:** {reason}
{f"- **Reference:** {reference}" if reference else ""}

## Context
This payment requires your approval before processing.

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.

## Deadline
This request expires on {expires.strftime('%Y-%m-%d at %H:%M')}
"""
    
    def _email_template(self, kwargs: Dict, created: datetime, 
                        expires: datetime) -> str:
        """Email send approval template."""
        to = kwargs.get('to', 'Unknown')
        subject = kwargs.get('subject', 'No subject')
        content = kwargs.get('content', '')
        
        return f"""---
type: approval_request
action: email_send
to: {to}
subject: {subject}
created: {created.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: normal
---

# Approval Request: Send Email

## Email Details
- **To:** {to}
- **Subject:** {subject}

## Content
{content}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.

## Deadline
This request expires on {expires.strftime('%Y-%m-%d at %H:%M')}
"""
    
    def _post_template(self, kwargs: Dict, created: datetime, 
                       expires: datetime) -> str:
        """Social media post approval template."""
        platform = kwargs.get('platform', 'Unknown')
        content = kwargs.get('content', '')
        
        return f"""---
type: approval_request
action: social_post
platform: {platform}
content: {content[:100]}{'...' if len(content) > 100 else ''}
created: {created.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: normal
---

# Approval Request: Social Media Post

## Post Details
- **Platform:** {platform}
- **Content:** {content}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.

## Deadline
This request expires on {expires.strftime('%Y-%m-%d at %H:%M')}
"""
    
    def _delete_template(self, kwargs: Dict, created: datetime, 
                         expires: datetime) -> str:
        """File delete approval template."""
        filepath = kwargs.get('filepath', 'Unknown')
        reason = kwargs.get('reason', 'Cleanup')
        
        return f"""---
type: approval_request
action: file_delete
filepath: {filepath}
reason: {reason}
created: {created.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: normal
---

# Approval Request: Delete File

## File Details
- **File:** {filepath}
- **Reason:** {reason}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.

## Deadline
This request expires on {expires.strftime('%Y-%m-%d at %H:%M')}
"""
    
    def _api_template(self, kwargs: Dict, created: datetime, 
                      expires: datetime) -> str:
        """API call approval template."""
        endpoint = kwargs.get('endpoint', 'Unknown')
        method = kwargs.get('method', 'GET')
        purpose = kwargs.get('purpose', 'API operation')
        
        return f"""---
type: approval_request
action: api_call
endpoint: {endpoint}
method: {method}
purpose: {purpose}
created: {created.isoformat()}
expires: {expires.isoformat()}
status: pending
priority: normal
---

# Approval Request: API Call

## API Details
- **Endpoint:** {endpoint}
- **Method:** {method}
- **Purpose:** {purpose}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.

## Deadline
This request expires on {expires.strftime('%Y-%m-%d at %H:%M')}
"""
    
    def run(self, mode: str = 'check', **kwargs) -> int:
        """
        Run the skill in specified mode.
        
        Args:
            mode: 'check', 'execute', or 'create'
            **kwargs: Additional arguments for create mode
            
        Returns:
            Result code (0=success, 1=error)
        """
        if mode == 'check':
            pending = self.check_pending()
            self.display_pending(pending)
            
            # Handle expired approvals
            expired = [p for p in pending if p['is_expired']]
            for item in expired:
                self.log(f"Approval expired: {item['name']}", "WARNING")
            
            return len(pending)
        
        elif mode == 'execute':
            executed = self.execute_approved()
            self.log(f"Executed {executed} approved action(s)")
            return executed
        
        elif mode == 'create':
            action_type = kwargs.get('action_type', 'unknown')
            result = self.create_approval_request(action_type, **kwargs)
            return 0 if result else 1
        
        else:
            self.log(f"Unknown mode: {mode}", "ERROR")
            return 1


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Approval Workflow Skill - Human-in-the-loop approvals"
    )
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault"
    )
    
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--check",
        action="store_true",
        help="Check pending approvals"
    )
    mode_group.add_argument(
        "--execute",
        action="store_true",
        help="Execute approved actions"
    )
    mode_group.add_argument(
        "--create",
        action="store_true",
        help="Create new approval request"
    )
    
    # Arguments for create mode
    parser.add_argument(
        "--action", "-a",
        help="Action type (payment, email_send, social_post, etc.)"
    )
    parser.add_argument(
        "--amount",
        help="Amount (for payment actions)"
    )
    parser.add_argument(
        "--recipient", "-r",
        help="Recipient (for payment/email actions)"
    )
    parser.add_argument(
        "--reason",
        help="Reason for the action"
    )
    parser.add_argument(
        "--subject",
        help="Email subject (for email actions)"
    )
    parser.add_argument(
        "--content", "-c",
        help="Content (for email/post actions)"
    )
    parser.add_argument(
        "--platform",
        help="Platform (for social post actions)"
    )
    
    args = parser.parse_args()
    
    skill = ApprovalWorkflowSkill(args.vault_path)
    
    if args.check:
        result = skill.run('check')
    elif args.execute:
        result = skill.run('execute')
    elif args.create:
        if not args.action:
            print("Error: --action required for create mode")
            exit(1)
        
        result = skill.run('create',
                          action_type=args.action,
                          amount=args.amount,
                          recipient=args.recipient,
                          reason=args.reason,
                          subject=args.subject,
                          content=args.content,
                          platform=args.platform)
    else:
        result = 1
    
    exit(0 if result == 0 else 1)


if __name__ == "__main__":
    main()
