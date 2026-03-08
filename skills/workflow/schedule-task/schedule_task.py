#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schedule Task Skill - Setup recurring tasks via cron or Task Scheduler.

Usage:
    python schedule_task.py /path/to/vault --daily --time "08:00" --task "daily_briefing"
    python schedule_task.py /path/to/vault --list
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


class ScheduleTaskSkill:
    """Schedule recurring tasks via system scheduler."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.script_dir = Path(__file__).parent.parent.parent
        self.config_path = Path(__file__).parent / 'scheduled_tasks.json'
        self.scheduled_tasks = self._load_tasks()
    
    def log(self, message: str, level: str = "INFO"):
        print(f"[{level}] {message}")
    
    def _load_tasks(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_tasks(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.scheduled_tasks, f, indent=2)
    
    def schedule_daily(self, task: str, time: str) -> bool:
        """Schedule a daily task."""
        hour, minute = time.split(':')
        
        if sys.platform == 'win32':
            return self._schedule_windows(task, 'daily', time=time)
        else:
            return self._schedule_cron(task, f"{minute} {hour} * * *")
    
    def schedule_weekly(self, task: str, day: str, time: str) -> bool:
        """Schedule a weekly task."""
        hour, minute = time.split(':')
        day_map = {
            'Sunday': '0', 'Monday': '1', 'Tuesday': '2',
            'Wednesday': '3', 'Thursday': '4', 'Friday': '5', 'Saturday': '6'
        }
        dow = day_map.get(day, '0')
        
        if sys.platform == 'win32':
            return self._schedule_windows(task, 'weekly', time=time, day=day)
        else:
            return self._schedule_cron(task, f"{minute} {hour} * * {dow}")
    
    def _schedule_cron(self, task: str, cron_expr: str) -> bool:
        """Add cron entry."""
        script = self._get_script_for_task(task)
        cron_entry = f"{cron_expr} cd {self.script_dir} && {script} {self.vault_path}\n"
        
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current = result.stdout if result.returncode == 0 else ""
            
            # Check if already scheduled
            if task in current:
                self.log(f"Task '{task}' already scheduled")
                return True
            
            # Add new entry
            new_crontab = current + f"\n# AI Employee: {task}\n{cron_entry}"
            
            # Install new crontab
            proc = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
            proc.communicate(new_crontab.encode())
            
            self.log(f"Scheduled '{task}' with cron: {cron_expr}")
            self.scheduled_tasks[task] = {
                'type': 'cron',
                'expression': cron_expr,
                'created': datetime.now().isoformat()
            }
            self._save_tasks()
            return True
            
        except Exception as e:
            self.log(f"Failed to schedule cron: {e}", "ERROR")
            return False
    
    def _schedule_windows(self, task: str, frequency: str, **kwargs) -> bool:
        """Create Windows Task Scheduler entry."""
        script = self._get_script_for_task(task)
        task_name = f"AI_Employee_{task}"
        
        try:
            # Build schtasks command
            cmd = [
                'schtasks', '/create',
                '/tn', task_name,
                '/tr', f'python {script} {self.vault_path}',
                '/sc', frequency,
            ]
            
            if frequency == 'daily':
                cmd.extend(['/st', kwargs.get('time', '08:00')])
            elif frequency == 'weekly':
                cmd.extend(['/d', kwargs.get('day', 'SUNDAY'), '/st', kwargs.get('time', '08:00')])
            
            subprocess.run(cmd, check=True)
            
            self.log(f"Scheduled '{task}' in Windows Task Scheduler")
            self.scheduled_tasks[task] = {
                'type': 'windows_task',
                'task_name': task_name,
                'created': datetime.now().isoformat()
            }
            self._save_tasks()
            return True
            
        except Exception as e:
            self.log(f"Failed to schedule Windows task: {e}", "ERROR")
            return False
    
    def _get_script_for_task(self, task: str) -> str:
        """Get script path for task type."""
        scripts = {
            'daily_briefing': 'python skills/process-drop/process_drop.py',
            'weekly_audit': 'python skills/workflow/weekly-audit/weekly_audit.py',
            'cleanup': 'python skills/utils/cleanup/cleanup.py',
            'process_drop': 'python skills/process-drop/process_drop.py',
        }
        return scripts.get(task, 'python skills/process-drop/process_drop.py')
    
    def list_tasks(self) -> List[Dict]:
        """List all scheduled tasks."""
        tasks = []
        
        # From config
        for name, info in self.scheduled_tasks.items():
            tasks.append({'name': name, **info})
        
        # From system
        if sys.platform != 'win32':
            try:
                result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'AI_Employee' in line or 'process_drop' in line:
                            tasks.append({'raw': line, 'source': 'crontab'})
            except:
                pass
        else:
            try:
                result = subprocess.run(
                    ['schtasks', '/query', '/fo', 'LIST', '/tn', 'AI_Employee_*'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    tasks.append({'raw': result.stdout, 'source': 'windows_task'})
            except:
                pass
        
        return tasks
    
    def remove_task(self, task: str) -> bool:
        """Remove a scheduled task."""
        try:
            if sys.platform == 'win32':
                task_name = f"AI_Employee_{task}"
                subprocess.run(['schtasks', '/delete', '/tn', task_name, '/f'], check=True)
            else:
                # Remove from crontab
                result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    new_lines = [l for l in lines if task not in l]
                    proc = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
                    proc.communicate('\n'.join(new_lines).encode())
            
            self.scheduled_tasks.pop(task, None)
            self._save_tasks()
            self.log(f"Removed task: {task}")
            return True
            
        except Exception as e:
            self.log(f"Failed to remove task: {e}", "ERROR")
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Schedule Task Skill")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--daily", action="store_true", help="Schedule daily task")
    action.add_argument("--weekly", action="store_true", help="Schedule weekly task")
    action.add_argument("--list", action="store_true", help="List scheduled tasks")
    action.add_argument("--remove", action="store_true", help="Remove task")
    
    parser.add_argument("--task", "-t", help="Task name")
    parser.add_argument("--time", help="Time (HH:MM format)")
    parser.add_argument("--day", help="Day of week (for weekly)")
    
    args = parser.parse_args()
    
    skill = ScheduleTaskSkill(args.vault_path)
    
    if args.list:
        tasks = skill.list_tasks()
        if tasks:
            print("\nScheduled Tasks:")
            for t in tasks:
                print(f"  - {t.get('name', 'Unknown')}: {t}")
        else:
            print("No tasks scheduled")
    
    elif args.remove:
        if not args.task:
            print("Error: --task required")
            exit(1)
        success = skill.remove_task(args.task)
        exit(0 if success else 1)
    
    elif args.daily or args.weekly:
        if not all([args.task, args.time]):
            print("Error: --task and --time required")
            exit(1)
        
        if args.daily:
            success = skill.schedule_daily(args.task, args.time)
        else:
            day = args.day or 'Sunday'
            success = skill.schedule_weekly(args.task, day, args.time)
        
        exit(0 if success else 1)


if __name__ == "__main__":
    main()
