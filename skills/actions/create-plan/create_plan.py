#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Plan Skill - Generate Plan.md files with structured action items.

Reads action files from /Needs_Action and creates detailed plans in /Plans.

Usage:
    python create_plan.py /path/to/vault [--verbose] [--file FILENAME]
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


class CreatePlanSkill:
    """
    Generate structured Plan.md files for multi-step tasks.
    """
    
    def __init__(self, vault_path: str, verbose: bool = False):
        """
        Initialize the skill.
        
        Args:
            vault_path: Path to the Obsidian vault root
            verbose: Enable verbose output
        """
        self.vault_path = Path(vault_path).resolve()
        self.verbose = verbose
        
        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans_folder = self.vault_path / 'Plans'
        
        # Ensure folders exist
        self.plans_folder.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.created_count = 0
        self.failed_count = 0
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message."""
        print(f"[{level}] {message}")
    
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
    
    def detect_task_type(self, frontmatter: Dict, content: str) -> str:
        """
        Detect the type of task from the action file.
        
        Returns:
            Task type string (email, invoice, meeting_notes, etc.)
        """
        file_type = frontmatter.get('type', '').lower()
        original_name = frontmatter.get('original_name', '').lower()
        category = frontmatter.get('category', '').lower()
        
        # Check file type first
        if 'email' in file_type:
            return 'email_reply'
        elif 'whatsapp' in file_type:
            return 'message_reply'
        elif 'invoice' in original_name or 'invoice' in content.lower():
            return 'invoice'
        elif 'payment' in original_name or 'payment' in content.lower():
            return 'payment'
        elif 'meeting' in original_name or 'meeting' in content.lower():
            return 'meeting_notes'
        elif 'document' in category or original_name.endswith('.pdf'):
            return 'document_review'
        elif 'file_drop' in file_type:
            return 'file_processing'
        
        return 'general_task'
    
    def get_task_steps(self, task_type: str, content: str) -> List[str]:
        """
        Get predefined steps for a task type.
        
        Args:
            task_type: Type of task
            content: Full content of action file
            
        Returns:
            List of step descriptions
        """
        templates = {
            'email_reply': [
                'Read and understand the email content',
                'Identify key points and required response',
                'Draft a professional reply',
                'Review draft for accuracy and tone',
                'Send email (requires approval)',
            ],
            'message_reply': [
                'Read the message content',
                'Identify urgency and required action',
                'Draft an appropriate response',
                'Send message (requires approval)',
            ],
            'invoice': [
                'Identify the client/customer',
                'Determine the amount and services',
                'Generate invoice PDF',
                'Review invoice details',
                'Send invoice to client (requires approval)',
                'Log in accounting records',
            ],
            'payment': [
                'Verify payment amount and recipient',
                'Check approval status',
                'Process payment via MCP (requires approval)',
                'Confirm payment completion',
                'Update accounting records',
            ],
            'meeting_notes': [
                'Extract key discussion points',
                'Identify action items and owners',
                'Schedule follow-up tasks',
                'File notes in appropriate location',
            ],
            'document_review': [
                'Read document content',
                'Summarize key information',
                'Extract actionable items',
                'File or archive document',
            ],
            'file_processing': [
                'Identify file type and content',
                'Determine required processing',
                'Execute processing steps',
                'File completed item',
            ],
            'general_task': [
                'Review task requirements',
                'Break down into subtasks',
                'Execute each subtask',
                'Verify completion',
                'Move to Done folder',
            ],
        }
        
        return templates.get(task_type, templates['general_task'])
    
    def extract_key_info(self, content: str, task_type: str) -> Dict[str, str]:
        """
        Extract key information from content.
        
        Returns:
            Dict of extracted information
        """
        info = {}
        
        # Extract amounts
        amount_match = re.search(r'\$[\d,]+\.?\d*', content)
        if amount_match:
            info['amount'] = amount_match.group()
        
        # Extract dates
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', content)
        if date_match:
            info['date'] = date_match.group()
        
        # Extract email addresses
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content)
        if email_match:
            info['email'] = email_match.group()
        
        # Extract names (from: header or similar)
        from_match = re.search(r'from:\s*(.+)', content, re.IGNORECASE)
        if from_match:
            info['from'] = from_match.group(1).strip()
        
        return info
    
    def estimate_time(self, task_type: str) -> str:
        """Estimate time for task type."""
        estimates = {
            'email_reply': '10 minutes',
            'message_reply': '5 minutes',
            'invoice': '15 minutes',
            'payment': '10 minutes',
            'meeting_notes': '20 minutes',
            'document_review': '15 minutes',
            'file_processing': '10 minutes',
            'general_task': '30 minutes',
        }
        return estimates.get(task_type, '30 minutes')
    
    def generate_plan_content(self, task_type: str, action_file: Dict) -> str:
        """
        Generate full Plan.md content.
        
        Args:
            task_type: Type of task
            action_file: Parsed action file data
            
        Returns:
            Full markdown content for Plan.md
        """
        frontmatter = action_file['frontmatter']
        content = action_file['content']
        source_file = frontmatter.get('original_name', 'unknown')
        
        # Get steps and key info
        steps = self.get_task_steps(task_type, content)
        key_info = self.extract_key_info(content, task_type)
        time_estimate = self.estimate_time(task_type)
        
        # Generate objective
        objectives = {
            'email_reply': f"Reply to email from {key_info.get('from', 'sender')}",
            'message_reply': f"Respond to message requiring attention",
            'invoice': f"Generate and send invoice for {key_info.get('amount', 'services rendered')}",
            'payment': f"Process payment of {key_info.get('amount', 'amount')}",
            'meeting_notes': "Extract and action items from meeting notes",
            'document_review': "Review and process document",
            'file_processing': f"Process file: {source_file}",
            'general_task': "Complete the required task",
        }
        
        objective = objectives.get(task_type, "Complete the required task")
        
        # Build content
        now = datetime.now().isoformat()
        plan_name = f"PLAN_{task_type}_{datetime.now().strftime('%Y%m%d')}"
        
        plan_content = f"""---
type: action_plan
created: {now}
status: pending
priority: normal
source: {source_file}
task_type: {task_type}
estimated_time: {time_estimate}
---

# Plan: {objective}

## Objective
{objective}

## Steps
"""
        
        # Add steps
        for step in steps:
            plan_content += f"- [ ] {step}\n"
        
        # Add key information
        if key_info:
            plan_content += "\n## Key Information\n\n"
            for key, value in key_info.items():
                plan_content += f"- **{key.title()}:** {value}\n"
        
        # Add required resources
        plan_content += f"""
## Required Resources
- Source file: `/Needs_Action/{source_file}`
- Access to relevant systems

## Notes
- This plan was auto-generated based on the action file type
- Review and adjust steps as needed
- Move to /Done when all steps are complete

---
*Generated by AI Employee Create Plan Skill*
"""
        
        return plan_content
    
    def read_action_file(self, md_path: Path) -> Optional[Dict[str, Any]]:
        """Read and parse an action file."""
        try:
            content = md_path.read_text()
            frontmatter = self.parse_frontmatter(content)
            
            return {
                'md_path': md_path,
                'frontmatter': frontmatter,
                'content': content,
            }
        except Exception as e:
            self.log(f"Failed to read {md_path.name}: {e}", "ERROR")
            return None
    
    def create_plan(self, action_file: Dict) -> Optional[Path]:
        """
        Create a Plan.md file for an action file.
        
        Args:
            action_file: Parsed action file data
            
        Returns:
            Path to created plan file, or None if failed
        """
        try:
            frontmatter = action_file['frontmatter']
            content = action_file['content']
            
            # Detect task type
            task_type = self.detect_task_type(frontmatter, content)
            
            # Generate plan content
            plan_content = self.generate_plan_content(task_type, action_file)
            
            # Create filename
            source_name = frontmatter.get('original_name', 'unknown')
            safe_name = re.sub(r'[^\w\-_]', '_', source_name)
            plan_name = f"PLAN_{task_type}_{safe_name[:30]}_{datetime.now().strftime('%Y%m%d')}.md"
            
            # Save plan
            plan_path = self.plans_folder / plan_name
            plan_path.write_text(plan_content)
            
            self.log(f"Created plan: {plan_name}")
            self.log(f"  Task type: {task_type}")
            self.log(f"  Estimated time: {self.estimate_time(task_type)}")
            
            return plan_path
            
        except Exception as e:
            self.log(f"Failed to create plan: {e}", "ERROR")
            return None
    
    def run(self) -> int:
        """
        Run the skill - create plans for all pending items.
        
        Returns:
            Number of plans created
        """
        self.log("Create Plan Skill starting")
        self.log(f"Vault: {self.vault_path}")
        
        if not self.needs_action.exists():
            self.log("Needs_Action folder not found", "WARNING")
            return 0
        
        # Find all action files (skip already planned)
        action_files = list(self.needs_action.glob('*.md'))
        
        if not action_files:
            self.log("No action files found to create plans for")
            return 0
        
        self.log(f"Found {len(action_files)} action file(s)")
        
        # Create plans
        for md_path in action_files:
            action_file = self.read_action_file(md_path)
            
            if action_file is None:
                self.failed_count += 1
                continue
            
            if self.create_plan(action_file):
                self.created_count += 1
            else:
                self.failed_count += 1
        
        self.log(f"Created {self.created_count} plan(s) successfully")
        if self.failed_count > 0:
            self.log(f"Failed: {self.failed_count} file(s)", "WARNING")
        
        return self.created_count


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create Plan Skill - Generate Plan.md files"
    )
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--file", "-f",
        help="Create plan for specific file only"
    )
    
    args = parser.parse_args()
    
    skill = CreatePlanSkill(args.vault_path, verbose=args.verbose)
    created = skill.run()
    
    # Exit with error if no plans created
    if created == 0:
        exit(1)


if __name__ == "__main__":
    main()
