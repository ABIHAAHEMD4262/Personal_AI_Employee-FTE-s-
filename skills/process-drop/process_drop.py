#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Drop Skill - Process files dropped into the AI Employee vault.

This is the core Agent Skill for the Bronze tier. It processes files
that have been placed in /Needs_Action by the filesystem_watcher.py.

Usage:
    python process_drop.py /path/to/vault [--verbose] [--dry-run]
"""

import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple


class ProcessDropSkill:
    """
    Agent Skill for processing dropped files.
    
    Reads action files from /Needs_Action, processes the associated
    files, and moves completed items to /Done.
    """
    
    def __init__(self, vault_path: str, verbose: bool = False, dry_run: bool = False):
        """
        Initialize the skill.
        
        Args:
            vault_path: Path to the Obsidian vault root
            verbose: Enable verbose output
            dry_run: Show what would be done without making changes
        """
        self.vault_path = Path(vault_path).resolve()
        self.verbose = verbose
        self.dry_run = dry_run
        
        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.dashboard = self.vault_path / 'Dashboard.md'
        
        # Processing results
        self.processed_count = 0
        self.failed_count = 0
        self.results: List[Dict[str, Any]] = []
        
        # Ensure directories exist
        if not self.dry_run:
            self.done.mkdir(parents=True, exist_ok=True)
    
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
    
    def read_action_file(self, md_path: Path) -> Optional[Dict[str, Any]]:
        """
        Read and parse an action file.
        
        Returns:
            Dict with frontmatter and content, or None if failed
        """
        try:
            content = md_path.read_text()
            frontmatter = self.parse_frontmatter(content)
            
            # Find associated file
            base_name = md_path.stem  # e.g., "FILE_document"
            associated_file = None
            
            for ext in ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', 
                       '.jpg', '.png', '.mp3', '.mp4', '.zip']:
                candidate = md_path.parent / f"{base_name}{ext}"
                if candidate.exists():
                    associated_file = candidate
                    break
            
            return {
                'md_path': md_path,
                'frontmatter': frontmatter,
                'content': content,
                'associated_file': associated_file,
            }
        except Exception as e:
            self.log(f"Failed to read {md_path.name}: {e}", "ERROR")
            return None
    
    def analyze_content(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the content and determine processing actions.
        
        Returns:
            Analysis results with suggested actions
        """
        frontmatter = action_data['frontmatter']
        content = action_data['content']
        
        file_type = frontmatter.get('type', 'unknown')
        category = frontmatter.get('category', 'unknown')
        original_name = frontmatter.get('original_name', 'unknown')
        size = frontmatter.get('size', '0')
        
        # Extract suggested actions from content
        actions = []
        action_pattern = r'- \[ \] (.+)'
        actions = re.findall(action_pattern, content)
        
        # Extract key information based on category
        extracted = {}
        if category == 'document':
            # Try to extract document type, dates, amounts
            amount_match = re.search(r'\$[\d,]+\.?\d*', content)
            if amount_match:
                extracted['amount'] = amount_match.group()
            
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', content)
            if date_match:
                extracted['date'] = date_match.group()
        
        return {
            'file_type': file_type,
            'category': category,
            'original_name': original_name,
            'size': size,
            'actions': actions,
            'extracted': extracted,
            'summary': self._generate_summary(content, category),
        }
    
    def _generate_summary(self, content: str, category: str) -> str:
        """Generate a brief summary of the content."""
        # Extract first meaningful paragraph
        lines = content.split('\n')
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('---') and not line.startswith('#'):
                summary_lines.append(line)
                if len(summary_lines) >= 2:
                    break
        
        return ' '.join(summary_lines)[:200] + '...' if summary_lines else 'No summary available'
    
    def process_file(self, action_data: Dict[str, Any]) -> bool:
        """
        Process a single file drop.
        
        Args:
            action_data: Parsed action file data
            
        Returns:
            True if processing succeeded
        """
        frontmatter = action_data['frontmatter']
        md_path = action_data['md_path']
        associated_file = action_data['associated_file']
        
        # Analyze content
        analysis = self.analyze_content(action_data)
        
        self.log(f"Processing: {analysis['original_name']}")
        self.log(f"  Type: {analysis['category']}")
        self.log(f"  Summary: {analysis['summary'][:80]}...")
        
        if analysis['extracted']:
            self.log(f"  Extracted: {analysis['extracted']}")
        
        # Create today's done folder
        today = datetime.now().strftime('%Y-%m-%d')
        done_folder = self.done / today
        if not self.dry_run:
            done_folder.mkdir(parents=True, exist_ok=True)
        
        # Move files to Done
        if associated_file and associated_file.exists():
            if not self.dry_run:
                shutil.move(str(associated_file), str(done_folder / associated_file.name))
            self.log(f"  Moved: {associated_file.name}")
        
        if not self.dry_run:
            shutil.move(str(md_path), str(done_folder / md_path.name))
        self.log(f"  Moved: {md_path.name}")
        
        # Record result
        self.results.append({
            'file': analysis['original_name'],
            'category': analysis['category'],
            'summary': analysis['summary'],
            'extracted': analysis['extracted'],
            'status': 'completed',
        })
        
        return True
    
    def update_dashboard(self):
        """Update Dashboard.md with processing results."""
        if not self.dashboard.exists():
            self.log("Dashboard.md not found, skipping update")
            return
        
        try:
            content = self.dashboard.read_text()
            
            # Update last_updated
            now = datetime.now().isoformat()
            content = re.sub(
                r'last_updated: [^\n]+',
                f'last_updated: {now}',
                content
            )
            
            # Update pending tasks count
            pending_count = len(list(self.needs_action.glob('*.md')))
            pending_status = '✅ Clear' if pending_count == 0 else f'⚠️ {pending_count} pending'
            
            # Update Quick Status section
            content = re.sub(
                r'\| Pending Tasks \| [^\n]+ \|',
                f'| Pending Tasks | {pending_count} | {pending_status} |',
                content
            )
            
            # Add to Recent Notifications
            if self.processed_count > 0:
                notification = f"- Processed {self.processed_count} file(s) at {now}"
                
                # Find Recent Notifications section and add entry
                notification_section = '## 🔔 Recent Notifications\n'
                if notification_section in content:
                    content = content.replace(
                        notification_section,
                        f"{notification_section}\n{notification}\n"
                    )
            
            if not self.dry_run:
                self.dashboard.write_text(content)
            
            self.log("Updated Dashboard.md")
            
        except Exception as e:
            self.log(f"Failed to update Dashboard.md: {e}", "ERROR")
    
    def run(self) -> Tuple[int, int]:
        """
        Run the skill - process all pending files.
        
        Returns:
            Tuple of (processed_count, failed_count)
        """
        self.log(f"Process Drop Skill starting")
        self.log(f"Vault: {self.vault_path}")
        
        if not self.needs_action.exists():
            self.log("Needs_Action folder not found", "WARNING")
            return (0, 0)
        
        # Find all action files
        action_files = list(self.needs_action.glob('*.md'))
        
        if not action_files:
            self.log("No pending files to process")
            return (0, 0)
        
        self.log(f"Found {len(action_files)} pending file(s)")
        
        # Process each file
        for md_path in action_files:
            action_data = self.read_action_file(md_path)
            
            if action_data is None:
                self.failed_count += 1
                continue
            
            try:
                if self.process_file(action_data):
                    self.processed_count += 1
                else:
                    self.failed_count += 1
            except Exception as e:
                self.log(f"Processing failed: {e}", "ERROR")
                self.failed_count += 1
        
        # Update dashboard
        if self.processed_count > 0:
            self.update_dashboard()
        
        self.log(f"Processed {self.processed_count} file(s) successfully")
        self.log(f"Failed: {self.failed_count} file(s)")
        
        return (self.processed_count, self.failed_count)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process Drop Skill - Process files in Needs_Action folder"
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
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    skill = ProcessDropSkill(
        args.vault_path,
        verbose=args.verbose,
        dry_run=args.dry_run
    )
    
    processed, failed = skill.run()
    
    if args.dry_run:
        print("\n[DRY RUN] No changes were made")
    
    # Exit with error code if any failures
    if failed > 0:
        exit(1)


if __name__ == "__main__":
    main()
