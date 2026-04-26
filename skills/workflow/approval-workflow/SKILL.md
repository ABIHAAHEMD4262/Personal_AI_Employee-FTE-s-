---
name: approval-workflow
description: |
  Human-in-the-loop approval workflow for sensitive actions.
  Manages approval requests between /Pending_Approval/, /Approved/, and /Rejected/ folders.
  
  Use when:
  - Sensitive actions require human approval (payments, emails, posts)
  - User wants to review before executing actions
  - Company Handbook rules require approval
  
  NOT when:
  - Actions are pre-approved in Company Handbook
  - Low-risk routine tasks
  - Emergency situations (use emergency bypass)
---

# Approval Workflow Skill

Manage human-in-the-loop approvals for sensitive actions.

## Usage

### Via Claude Code

```bash
# Check pending approvals
claude "Check what approvals are pending in AI_Employee_Vault"

# Process approved items
claude "Execute all approved actions in AI_Employee_Vault/Approved"

# Create approval request
claude "Create approval request for payment of $500 to Client A"
```

### Via Python Script

```bash
# Check pending approvals
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault --check

# Process approved items
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault --execute

# Create approval request
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault \
  --create --action payment --amount 500 --recipient "Client A"
```

## Workflow

```
Action Needed → Create Approval Request → /Pending_Approval/
                                              ↓
                                    Human Reviews
                                              ↓
                          ┌───────────────────┴───────────────────┐
                          ↓                                       ↓
                    Move to /Approved/                      Move to /Rejected/
                          ↓                                       ↓
                    Execute Action                          Log & Archive
                          ↓
                    Move to /Done/
```

## Approval Request Format

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-02-27T10:30:00Z
expires: 2026-02-28T10:30:00Z
status: pending
priority: normal
---

# Approval Request: Payment

## Action Details
- **Type:** Payment
- **Amount:** $500.00
- **Recipient:** Client A
- **Reason:** Invoice #1234 payment

## Context
Additional details about why this action is needed.

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.

## Deadline
This request expires on 2026-02-28T10:30:00Z
```

## Action Types

| Type | Approval Required | Auto-Approve Threshold |
|------|-------------------|----------------------|
| payment | Always | Never |
| email_send | New contacts only | Known contacts |
| social_post | Always (until trusted) | After N approved posts |
| file_delete | Important files | Temporary files |
| api_call | Sensitive APIs | Read-only APIs |

## Folder Structure

```
Vault/
├── Pending_Approval/
│   ├── PAYMENT_Client_A_2026-02-27.md
│   └── EMAIL_reply_2026-02-27.md
├── Approved/
│   └── (executed automatically)
├── Rejected/
│   └── (archived with reason)
└── Logs/
    └── approval_log.md
```

## Commands

### Check Pending

```bash
python approval_workflow.py VAULT --check
```

Output:
```
Pending Approvals: 2
- PAYMENT_Client_A: $500.00 (expires in 23h)
- EMAIL_reply: to client@example.com (expires in 23h)
```

### Execute Approved

```bash
python approval_workflow.py VAULT --execute
```

Output:
```
Approved Actions: 1
Executing: PAYMENT_Client_A
  → Payment processed via MCP
  → Logged to approval_log.md
  → Moved to /Done/
```

### Create Request

```bash
python approval_workflow.py VAULT --create \
  --action payment \
  --amount 500 \
  --recipient "Client A" \
  --reason "Invoice #1234"
```

## Integration

Works with:
- `send-email` - Requires approval before sending
- `post-linkedin` - Requires approval before posting
- `process-drop` - Creates approval for sensitive files
- `update-dashboard` - Shows pending approval count

## Security

- All approval actions are logged
- Expired approvals are automatically rejected
- Sensitive data is redacted in logs
- Approval history is immutable
