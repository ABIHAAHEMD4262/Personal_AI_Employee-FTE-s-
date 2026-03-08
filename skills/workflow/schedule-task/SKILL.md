---
name: schedule-task
description: |
  Schedule recurring tasks via cron or Task Scheduler.
  Sets up automated triggers for daily briefings, weekly audits, etc.
  
  Use when:
  - Setting up daily briefings at 8 AM
  - Scheduling weekly CEO audits on Sunday
  - Creating custom recurring tasks
  
  NOT when:
  - One-time tasks (run manually)
  - Tasks requiring immediate execution
---

# Schedule Task Skill

Schedule recurring tasks via system scheduler.

## Usage

```bash
# Setup daily briefing at 8 AM
python skills/workflow/schedule-task/schedule_task.py VAULT \
  --daily --time "08:00" --task "daily_briefing"

# Setup weekly audit on Sunday at 10 PM
python skills/workflow/schedule-task/schedule_task.py VAULT \
  --weekly --day "Sunday" --time "22:00" --task "weekly_audit"

# List scheduled tasks
python skills/workflow/schedule-task/schedule_task.py VAULT --list

# Remove scheduled task
python skills/workflow/schedule-task/schedule_task.py VAULT --remove --task "daily_briefing"
```

## Pre-configured Tasks

| Task | Default Schedule | Command |
|------|------------------|---------|
| daily_briefing | Mon-Fri 8:00 AM | process Needs_Action |
| weekly_audit | Sunday 10:00 PM | generate CEO briefing |
| cleanup | Daily 11:00 PM | archive old files |

## Cron Examples

### Linux/Mac
```bash
# Daily briefing at 8 AM
0 8 * * 1-5 cd /path && python process_drop.py VAULT

# Weekly audit Sunday 10 PM
0 22 * * 0 cd /path && python weekly_audit.py VAULT
```

### Windows Task Scheduler
```powershell
# Create scheduled task
schtasks /create /tn "AI_Employee_Daily" /tr "python process_drop.py" /sc daily /st 08:00
```
