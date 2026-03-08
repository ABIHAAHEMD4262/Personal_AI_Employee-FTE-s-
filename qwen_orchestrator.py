#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen Orchestrator - Orchestrates the complete email workflow.

Workflow:
1. Scans /Needs_Action/ for new email files
2. Runs create-plan skill to generate Plan.md
3. Moves email + plan to /Pending_Approval/
4. Watches /Approved/ for user approval
5. When approved: sends email reply
6. Moves everything to /Done/

Usage:
    python qwen_orchestrator.py /path/to/vault [--watch]
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


class QwenOrchestrator:
    """Orchestrate email workflow with Qwen Code."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        
        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_folder = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        # Ensure folders exist
        for folder in [self.plans_folder, self.pending_approval, 
                       self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Skills
        self.create_plan_script = self.vault_path.parent / 'skills' / 'actions' / 'create-plan' / 'create_plan.py'
        self.auto_reply_script = self.vault_path.parent / 'skills' / 'actions' / 'auto-reply' / 'auto_reply.py'
        self.update_dashboard_script = self.vault_path.parent / 'skills' / 'utils' / 'update-dashboard' / 'update_dashboard.py'
    
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
    
    def extract_sender_email(self, from_field: str) -> str:
        """Extract email address from From field."""
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_field)
        return match.group() if match else ""
    
    def run_create_plan(self) -> bool:
        """Run create-plan skill."""
        try:
            result = subprocess.run([
                'python', str(self.create_plan_script),
                str(self.vault_path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log("  → Plan created successfully")
                return True
            else:
                self.log(f"  → Plan creation failed: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"  → Error running create-plan: {e}", "ERROR")
            return False
    
    def move_to_pending(self, email_file: Path, plan_file: Path = None):
        """Move email and plan to Pending_Approval."""
        try:
            # Move email file
            dest = self.pending_approval / email_file.name
            shutil.move(str(email_file), str(dest))
            self.log(f"  → Moved {email_file.name} to Pending_Approval")
            
            # Move plan file if exists
            if plan_file and plan_file.exists():
                plan_dest = self.pending_approval / plan_file.name
                shutil.move(str(plan_file), str(plan_dest))
                self.log(f"  → Moved {plan_file.name} to Pending_Approval")
                
        except Exception as e:
            self.log(f"  → Error moving files: {e}", "ERROR")
    
    def send_approved_email(self, approval_file: Path) -> bool:
        """Send email from approved file (email or approval request)."""
        try:
            content = approval_file.read_text()
            frontmatter = self.parse_frontmatter(content)

            action_type = frontmatter.get('action', '')
            file_type = frontmatter.get('type', '')

            # Check if it's an approval request OR an original email file
            if action_type == 'email_send':
                # It's a proper approval request with to:/subject: fields
                to_email = frontmatter.get('to', '')
                subject = frontmatter.get('subject', '')
                content_match = re.search(r'## Content\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                email_content = content_match.group(1).strip() if content_match else content
            elif file_type == 'email' or 'EMAIL_' in approval_file.name:
                # It's an original email file - extract reply-to from "from" field
                from_email = frontmatter.get('from', '')
                # Extract just the email address from "Name <email@domain.com>"
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_email)
                to_email = email_match.group() if email_match else ''
                
                subject = frontmatter.get('subject', 'Re: Your Email')
                if not subject.startswith('Re:'):
                    subject = f'Re: {subject}'
                
                # Extract original email content for context
                content_match = re.search(r'## Content\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                original_content = content_match.group(1).strip() if content_match else ''
                
                # Generate simple reply content
                email_content = f"""Thank you for your email.

We have received your message regarding "{subject}" and will respond shortly.

Original message:
{original_content}

---
Sent by AI Employee (Automated)"""
            else:
                return False

            if not to_email:
                self.log("  → No recipient email address found", "ERROR")
                return False

            # Send via send-email skill
            result = subprocess.run([
                'python', str(self.vault_path.parent / 'skills' / 'actions' / 'send-email' / 'send_email.py'),
                str(self.vault_path),
                '--send',
                '--to', to_email,
                '--subject', subject,
                '--content', email_content,
                '--no-approval'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.log("  → Email sent successfully")
                return True
            else:
                self.log(f"  → Send failed: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"  → Error sending email: {e}", "ERROR")
            return False
    
    def move_to_done(self, file: Path):
        """Move file to Done folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        done_today = self.done / today
        done_today.mkdir(parents=True, exist_ok=True)
        
        dest = done_today / file.name
        shutil.move(str(file), str(dest))
        self.log(f"  → Moved {file.name} to Done/{today}")
    
    def process_new_emails(self):
        """Process new email files in Needs_Action."""
        if not self.needs_action.exists():
            return
        
        email_files = list(self.needs_action.glob('EMAIL_*.md'))
        
        for email_file in email_files:
            self.log(f"\nProcessing: {email_file.name}")
            
            # Step 1: Create plan
            self.log("Step 1: Creating action plan...")
            if self.run_create_plan():
                # Find the created plan file
                plan_files = list(self.plans_folder.glob('PLAN_*.md'))
                plan_file = max(plan_files, key=lambda p: p.stat().st_mtime) if plan_files else None
                
                # Step 2: Move to Pending_Approval
                self.log("Step 2: Moving to Pending_Approval...")
                self.move_to_pending(email_file, plan_file)
            else:
                self.log("  → Skipping due to plan creation failure", "ERROR")
    
    def process_approved_emails(self):
        """Process approved email files."""
        if not self.approved.exists():
            return
        
        approval_files = list(self.approved.glob('*.md'))
        
        for approval_file in approval_files:
            # Only process email-related files
            if not approval_file.name.startswith('EMAIL_'):
                continue
                
            self.log(f"\nProcessing approved: {approval_file.name}")
            
            # Send email
            if self.send_approved_email(approval_file):
                # Move to Done
                self.move_to_done(approval_file)
            else:
                self.log("  → Failed to send email", "ERROR")
    
    def update_dashboard(self):
        """Update dashboard."""
        try:
            subprocess.run([
                'python', str(self.update_dashboard_script),
                str(self.vault_path)
            ], capture_output=True, timeout=10)
        except:
            pass
    
    def run_once(self):
        """Run orchestration once."""
        self.log("=" * 50)
        self.log("Qwen Orchestrator - Processing emails")
        self.log("=" * 50)
        
        # Process new emails
        self.process_new_emails()
        
        # Process approved emails
        self.process_approved_emails()
        
        # Update dashboard
        self.update_dashboard()
        
        self.log("\n" + "=" * 50)
        self.log("Orchestration complete")
        self.log("=" * 50)
    
    def run_watch(self, interval: int = 30):
        """Run orchestration continuously."""
        import time
        
        self.log(f"Starting Qwen Orchestrator (interval: {interval}s)")
        
        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.log("\nStopped by user")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Qwen Orchestrator - Automate email workflow"
    )
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run continuously"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Check interval in seconds"
    )
    
    args = parser.parse_args()
    
    orchestrator = QwenOrchestrator(args.vault_path)
    
    if args.watch:
        orchestrator.run_watch(args.interval)
    else:
        orchestrator.run_once()


if __name__ == "__main__":
    main()
