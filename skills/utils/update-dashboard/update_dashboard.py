#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Dashboard Skill - Keep Dashboard.md synchronized with vault state.

Usage:
    python update_dashboard.py /path/to/vault [--section SECTION] [--quick]
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class UpdateDashboardSkill:
    """Update Dashboard.md with current vault state."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.dashboard = self.vault_path / 'Dashboard.md'
    
    def log(self, message: str, level: str = "INFO"):
        print(f"[{level}] {message}")
    
    def count_files(self, folder: Path, extension: str = '.md') -> int:
        """Count files in folder."""
        if not folder.exists():
            return 0
        return len(list(folder.glob(f'*{extension}')))
    
    def get_folder_contents(self, folder: Path, limit: int = 5) -> List[str]:
        """Get list of recent files in folder."""
        if not folder.exists():
            return []
        
        files = []
        for f in sorted(folder.glob('*.md'), reverse=True)[:limit]:
            files.append(f"- {f.stem}")
        return files
    
    def get_pending_approvals(self) -> List[Dict]:
        """Get pending approval details."""
        approvals = []
        folder = self.vault_path / 'Pending_Approval'
        
        if not folder.exists():
            return approvals
        
        for f in folder.glob('*.md'):
            try:
                content = f.read_text()
                frontmatter = self._parse_frontmatter(content)
                approvals.append({
                    'name': f.stem,
                    'type': frontmatter.get('action', 'unknown'),
                    'amount': frontmatter.get('amount', ''),
                })
            except:
                pass
        
        return approvals
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        frontmatter = {}
        in_frontmatter = False
        for line in content.split('\n'):
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter
    
    def generate_notifications(self) -> List[str]:
        """Generate notifications from recent activity."""
        notifications = []
        
        # Check for pending approvals
        pending = self.count_files(self.vault_path / 'Pending_Approval')
        if pending > 0:
            notifications.append(f"⚠️ {pending} approval(s) awaiting review")
        
        # Check for items in Needs_Action
        needs_action = self.count_files(self.vault_path / 'Needs_Action')
        if needs_action > 5:
            notifications.append(f"📋 High volume: {needs_action} items need processing")
        
        # Check for newly completed items today
        today = datetime.now().strftime('%Y-%m-%d')
        done_today = self.count_files(self.vault_path / 'Done' / today)
        if done_today > 0:
            notifications.append(f"✅ {done_today} task(s) completed today")
        
        return notifications
    
    def update_full(self):
        """Perform full dashboard update."""
        if not self.dashboard.exists():
            self.log("Dashboard.md not found", "WARNING")
            return False
        
        try:
            content = self.dashboard.read_text()
            now = datetime.now()
            
            # Update timestamp
            content = re.sub(
                r'last_updated: [^\n]+',
                f'last_updated: {now.isoformat()}',
                content
            )
            
            # Count metrics
            pending_count = self.count_files(self.vault_path / 'Needs_Action')
            approval_count = self.count_files(self.vault_path / 'Pending_Approval')
            
            pending_status = '✅ Clear' if pending_count == 0 else f'⚠️ {pending_count} pending'
            approval_status = '✅ Clear' if approval_count == 0 else f'⏳ {approval_count} awaiting'
            
            # Update Quick Status table
            content = re.sub(
                r'\| Pending Tasks \| [^\n]+ \|',
                f'| Pending Tasks | {pending_count} | {pending_status} |',
                content
            )
            content = re.sub(
                r'\| Awaiting Approval \| [^\n]+ \|',
                f'| Awaiting Approval | {approval_count} | {approval_status} |',
                content
            )
            
            # Update Inbox Summary
            inbox_items = self.get_folder_contents(self.vault_path / 'Needs_Action')
            if inbox_items:
                inbox_section = '\n'.join(inbox_items)
                content = re.sub(
                    r'(## 📥 Inbox Summary\n\n).*?(\n\n)',
                    f'\\1{inbox_section}\\2',
                    content,
                    flags=re.DOTALL
                )
            
            # Update Pending Approvals
            approvals = self.get_pending_approvals()
            if approvals:
                approval_list = '\n'.join([
                    f"- {a['name']}: {a['amount']}" for a in approvals
                ])
                content = re.sub(
                    r'(## ⏳ Pending Approvals\n\n).*?(\n\n)',
                    f'\\1{approval_list}\\2',
                    content,
                    flags=re.DOTALL
                )
            else:
                content = re.sub(
                    r'(## ⏳ Pending Approvals\n\n).*?(\n\n)',
                    '\\1*No items awaiting approval*\\2',
                    content,
                    flags=re.DOTALL
                )
            
            # Update Recent Notifications
            notifications = self.generate_notifications()
            if notifications:
                notif_list = '\n'.join(notifications)
                content = re.sub(
                    r'(## 🔔 Recent Notifications\n\n).*?(\n\n)',
                    f'\\1{notif_list}\\2',
                    content,
                    flags=re.DOTALL
                )
            
            # Write updated content
            self.dashboard.write_text(content)
            self.log("Dashboard updated successfully")
            return True
            
        except Exception as e:
            self.log(f"Failed to update dashboard: {e}", "ERROR")
            return False
    
    def update_quick(self):
        """Quick update - just timestamp and counts."""
        if not self.dashboard.exists():
            return False
        
        try:
            content = self.dashboard.read_text()
            now = datetime.now()
            
            # Update timestamp only
            content = re.sub(
                r'last_updated: [^\n]+',
                f'last_updated: {now.isoformat()}',
                content
            )
            
            # Update pending count
            pending_count = self.count_files(self.vault_path / 'Needs_Action')
            pending_status = '✅ Clear' if pending_count == 0 else f'⚠️ {pending_count} pending'
            
            content = re.sub(
                r'\| Pending Tasks \| [^\n]+ \|',
                f'| Pending Tasks | {pending_count} | {pending_status} |',
                content
            )
            
            self.dashboard.write_text(content)
            self.log("Quick dashboard update complete")
            return True
            
        except Exception as e:
            self.log(f"Failed to update dashboard: {e}", "ERROR")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Dashboard Skill")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument(
        "--section", "-s",
        help="Update specific section only"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Quick update (timestamp + counts only)"
    )
    
    args = parser.parse_args()
    
    skill = UpdateDashboardSkill(args.vault_path)
    
    if args.quick:
        success = skill.update_quick()
    else:
        success = skill.update_full()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
