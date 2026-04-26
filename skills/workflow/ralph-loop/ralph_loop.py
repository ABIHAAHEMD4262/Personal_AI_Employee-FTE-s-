#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ralph Wiggum Loop - Gold Tier AI Employee

Autonomous multi-step task completion loop.
Keeps Claude Code iterating until tasks are complete.

Based on the Ralph Wiggum pattern from the hackathon document:
"A Stop hook pattern that keeps Claude iterating until tasks are complete"

Usage:
    python ralph_loop.py /path/to/vault "Process all emails and send replies"
"""

import os
import sys
import json
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


def parse_args():
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Autonomous task completion'
    )
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('task', type=str, help='Task description/prompt')
    parser.add_argument('--max-iterations', type=int, default=10,
                        help='Maximum iterations before giving up')
    parser.add_argument('--timeout', type=int, default=3600,
                        help='Timeout in seconds (default: 1 hour)')
    parser.add_argument('--check-interval', type=int, default=30,
                        help='Check interval in seconds')
    parser.add_argument('--state-folder', type=str, default=None,
                        help='Custom state folder path')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate without executing')
    
    return parser.parse_args()


class RalphLoop:
    """Ralph Wiggum Loop implementation for autonomous task completion."""
    
    def __init__(
        self,
        vault_path: str,
        task: str,
        max_iterations: int = 10,
        timeout: int = 3600,
        check_interval: int = 30,
        state_folder: Optional[str] = None,
        verbose: bool = False,
        dry_run: bool = False
    ):
        self.vault_path = Path(vault_path).resolve()
        self.task = task
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.check_interval = check_interval
        self.verbose = verbose
        self.dry_run = dry_run
        
        # State folder
        if state_folder:
            self.state_folder = Path(state_folder)
        else:
            self.state_folder = self.vault_path / 'In_Progress' / 'ralph_loop'
        
        self.state_folder.mkdir(parents=True, exist_ok=True)
        
        # State file
        self.state_file = self.state_folder / f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Initialize state
        self.state = {
            'task': task,
            'created': datetime.now().isoformat(),
            'iterations': 0,
            'status': 'pending',
            'history': [],
            'completion_criteria': {
                'needs_action_empty': True,
                'all_approved_processed': True,
                'task_complete_flag': False,
            }
        }
        
        # Folders to monitor
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
    
    def log(self, message: str, level: str = "INFO"):
        """Log message."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
        
        # Also save to state
        self.state['history'].append({
            'timestamp': timestamp,
            'level': level,
            'message': message
        })
    
    def save_state(self):
        """Save current state to file."""
        self.state['updated'] = datetime.now().isoformat()
        
        if not self.dry_run:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
    
    def check_completion(self) -> tuple[bool, str]:
        """
        Check if task is complete.
        Returns (is_complete, reason)
        """
        # Check iteration limit
        if self.state['iterations'] >= self.max_iterations:
            return True, f"Max iterations ({self.max_iterations}) reached"
        
        # Check timeout
        created = datetime.fromisoformat(self.state['created'])
        if (datetime.now() - created).total_seconds() > self.timeout:
            return True, f"Timeout ({self.timeout}s) reached"
        
        # Check if Needs_Action is empty (if that was the goal)
        if self.state['completion_criteria'].get('needs_action_empty'):
            needs_action_count = len(list(self.needs_action.glob('*.md'))) if self.needs_action.exists() else 0
            if needs_action_count == 0:
                return True, "Needs_Action folder is empty"
        
        # Check if all approved items are processed
        if self.state['completion_criteria'].get('all_approved_processed'):
            approved_count = len(list(self.approved.glob('*.md'))) if self.approved.exists() else 0
            if approved_count == 0:
                self.log("All approved items processed", "INFO")
        
        # Check for explicit completion flag
        if self.state['completion_criteria'].get('task_complete_flag'):
            # Look for TASK_COMPLETE marker file
            complete_files = list(self.state_folder.glob('TASK_COMPLETE*'))
            if complete_files:
                return True, "Task completion flag detected"
        
        # Check if a Plan.md exists and is complete
        if self.plans.exists():
            plan_files = list(self.plans.glob('PLAN_*.md'))
            for plan_file in plan_files:
                content = plan_file.read_text()
                if 'TASK_COMPLETE' in content or '[x]' in content:
                    # Check if all checkboxes are marked
                    lines = content.split('\n')
                    checkboxes = [l for l in lines if '- [' in l]
                    if checkboxes and all('[x]' in cb for cb in checkboxes):
                        return True, "All plan items completed"
        
        return False, "Task still in progress"
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get current vault context for Claude."""
        context = {
            'needs_action': [],
            'pending_approval': [],
            'approved': [],
            'plans': [],
        }
        
        # Get Needs_Action items
        if self.needs_action.exists():
            for f in self.needs_action.glob('*.md'):
                context['needs_action'].append({
                    'name': f.name,
                    'content': f.read_text()[:500]  # First 500 chars
                })
        
        # Get Pending_Approval items
        if self.pending_approval.exists():
            for f in self.pending_approval.glob('*.md'):
                context['pending_approval'].append({
                    'name': f.name,
                    'content': f.read_text()[:500]
                })
        
        # Get Approved items
        if self.approved.exists():
            for f in self.approved.glob('*.md'):
                context['approved'].append({
                    'name': f.name,
                    'content': f.read_text()[:500]
                })
        
        # Get Plans
        if self.plans.exists():
            for f in self.plans.glob('*.md'):
                context['plans'].append({
                    'name': f.name,
                    'content': f.read_text()
                })
        
        return context
    
    def generate_prompt(self, iteration: int) -> str:
        """Generate prompt for Claude Code."""
        context = self.get_current_context()
        
        prompt = f"""# Task: {self.task}

## Current State
- **Iteration**: {iteration}/{self.max_iterations}
- **Status**: In Progress

## Vault Context

### Needs_Action ({len(context['needs_action'])} items)
"""
        
        for item in context['needs_action'][:3]:
            prompt += f"\n- **{item['name']}**: {item['content'][:100]}...\n"
        
        prompt += f"""
### Pending_Approval ({len(context['pending_approval'])} items)
"""
        
        for item in context['pending_approval'][:3]:
            prompt += f"\n- **{item['name']}**: {item['content'][:100]}...\n"
        
        prompt += f"""
### Approved (Ready to Execute) ({len(context['approved'])} items)
"""
        
        for item in context['approved'][:3]:
            prompt += f"\n- **{item['name']}**: {item['content'][:100]}...\n"
        
        prompt += f"""
## Instructions

1. Review the current vault state above
2. Process any items in /Needs_Action folder
3. Create plans for complex tasks
4. Move approval requests to /Pending_Approval
5. Execute approved actions
6. Move completed items to /Done

## Completion Criteria

The task is complete when:
- All items in /Needs_Action are processed
- All approved actions are executed
- No pending approvals remain (or they require human intervention)

## Important

- After completing your work, if the task is NOT complete, output: "TASK_INCOMPLETE - continuing loop"
- If the task IS complete, output: "TASK_COMPLETE" and move all processed items to /Done

Begin processing now.
"""
        
        return prompt
    
    def run_claude(self, prompt: str) -> tuple[bool, str]:
        """Run Claude Code with the given prompt."""
        if self.dry_run:
            self.log(f"[DRY RUN] Would run Claude with prompt: {prompt[:100]}...")
            return True, "Dry run - no output"
        
        try:
            # Run Claude Code
            result = subprocess.run(
                ['claude', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per iteration
                cwd=str(self.vault_path)
            )
            
            output = result.stdout + result.stderr
            
            # Check for completion markers
            if 'TASK_COMPLETE' in output:
                return True, output
            
            if 'TASK_INCOMPLETE' in output:
                return False, output
            
            # Default: check if work was done
            return False, output
            
        except subprocess.TimeoutExpired:
            self.log("Claude iteration timed out", "WARNING")
            return False, "Timeout"
        except Exception as e:
            self.log(f"Error running Claude: {e}", "ERROR")
            return False, str(e)
    
    def run(self) -> bool:
        """Run the Ralph Wiggum Loop."""
        self.log(f"🚀 Starting Ralph Wiggum Loop")
        self.log(f"   Task: {self.task}")
        self.log(f"   Max iterations: {self.max_iterations}")
        self.log(f"   Timeout: {self.timeout}s")
        self.log(f"   Vault: {self.vault_path}")
        
        if self.dry_run:
            self.log("   DRY RUN MODE - No actual execution")
        
        self.save_state()
        
        start_time = time.time()
        
        try:
            while True:
                # Check completion
                is_complete, reason = self.check_completion()
                
                if is_complete:
                    self.log(f"✅ Task complete: {reason}")
                    self.state['status'] = 'completed'
                    self.state['completed'] = datetime.now().isoformat()
                    self.state['completion_reason'] = reason
                    self.save_state()
                    return True
                
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    self.log(f"⏰ Timeout reached ({elapsed:.0f}s)", "WARNING")
                    self.state['status'] = 'timeout'
                    self.save_state()
                    return False
                
                # Run iteration
                self.state['iterations'] += 1
                iteration = self.state['iterations']
                
                self.log(f"🔄 Iteration {iteration}/{self.max_iterations}")
                
                # Generate prompt
                prompt = self.generate_prompt(iteration)
                
                # Run Claude
                success, output = self.run_claude(prompt)
                
                if self.verbose:
                    self.log(f"   Output: {output[:200]}...")
                
                # Save state
                self.save_state()
                
                # Wait before next iteration
                if not is_complete:
                    self.log(f"   Waiting {self.check_interval}s before next check...")
                    time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            self.log("⚠️  Loop interrupted by user", "WARNING")
            self.state['status'] = 'interrupted'
            self.save_state()
            return False
        
        except Exception as e:
            self.log(f"❌ Error: {e}", "ERROR")
            self.state['status'] = 'error'
            self.state['error'] = str(e)
            self.save_state()
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current loop status."""
        return {
            'task': self.state['task'],
            'iterations': self.state['iterations'],
            'status': self.state['status'],
            'created': self.state['created'],
            'updated': self.state.get('updated'),
            'history_count': len(self.state['history']),
        }


def main():
    args = parse_args()
    
    # Create loop
    loop = RalphLoop(
        vault_path=args.vault_path,
        task=args.task,
        max_iterations=args.max_iterations,
        timeout=args.timeout,
        check_interval=args.check_interval,
        state_folder=args.state_folder,
        verbose=args.verbose,
        dry_run=args.dry_run
    )
    
    # Run loop
    success = loop.run()
    
    # Print summary
    status = loop.get_status()
    
    print("\n" + "=" * 50)
    print("Ralph Wiggum Loop Summary")
    print("=" * 50)
    print(f"Task: {status['task']}")
    print(f"Status: {status['status']}")
    print(f"Iterations: {status['iterations']}")
    print(f"Created: {status['created']}")
    print(f"Completed: {status.get('updated', 'N/A')}")
    print("=" * 50)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
