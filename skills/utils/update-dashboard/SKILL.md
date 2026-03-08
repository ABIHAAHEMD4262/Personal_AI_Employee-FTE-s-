---
name: update-dashboard
description: |
  Update Dashboard.md with current status, metrics, and notifications.
  Called after processing tasks to keep dashboard current.
  
  Use when:
  - After processing files from Needs_Action
  - When approval status changes
  - During daily/weekly briefings
  
  NOT when:
  - Dashboard is locked for editing
  - Only reading status (use read operations)
---

# Update Dashboard Skill

Keep Dashboard.md synchronized with vault state.

## Usage

```bash
# Full dashboard update
python skills/utils/update-dashboard/update_dashboard.py VAULT

# Update specific section
python skills/utils/update-dashboard/update_dashboard.py VAULT --section "pending_tasks"

# Quick status refresh
python skills/utils/update-dashboard/update_dashboard.py VAULT --quick
```

## Sections Updated

| Section | Data Source |
|---------|-------------|
| Quick Status | Counts from folders |
| Pending Tasks | /Needs_Action contents |
| Pending Approvals | /Pending_Approval contents |
| Financial Snapshot | /Accounting contents |
| Recent Notifications | Generated from actions |
| System Status | Watcher/process state |

## Dashboard Format

```markdown
---
last_updated: 2026-02-27T10:30:00Z
status: active
---

# 🏠 AI Employee Dashboard

## 📊 Quick Status
| Metric | Value | Status |
|--------|-------|--------|
| Pending Tasks | 3 | ⚠️ 3 pending |
| Awaiting Approval | 1 | ⏳ Review needed |

## 📥 Inbox Summary
- EMAIL_invoice_client: Invoice from Client A
- FILE_contract: New contract PDF

## 🎯 Active Tasks
- Processing invoice for Client A
- Draft reply to urgent email

## ⏳ Pending Approvals
- PAYMENT_Client_A: $500.00

## 💰 Financial Snapshot
| Period | Revenue | Expenses | Net |
|--------|---------|----------|-----|
| This Week | $2,450 | $150 | $2,300 |
```
