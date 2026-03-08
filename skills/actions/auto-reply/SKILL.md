---
name: auto-reply
description: |
  Automatically reply to emails when user moves them to /Approved/ folder.
  Generates context-aware replies and sends via email MCP.
  
  Use when:
  - You want automated email replies
  - Move email to /Approved/ to trigger reply
  - Want AI to generate appropriate responses
  
  NOT when:
  - Manual review required before sending
  - Complex email requiring human judgment
---

# Auto Email Reply Skill

Automatically generate and send email replies when you approve emails.

## Workflow

```
Gmail Watcher detects email
     ↓
Creates: /Needs_Action/EMAIL_*.md
     ↓
YOU: Move to /Approved/
     ↓
AUTO: Generate reply
     ↓
AUTO: Send email
     ↓
AUTO: Move to /Done/
```

## Usage

```bash
# Process approved emails once
python skills/actions/auto-reply/auto_reply.py AI_Employee_Vault

# Watch continuously
python skills/actions/auto-reply/auto_reply.py AI_Employee_Vault --watch --interval 30
```

## Reply Types

| Email Type | Auto-Reply |
|------------|------------|
| Invoice/Payment | Acknowledgment + processing notice |
| Meeting/Schedule | Availability request |
| Question/Support | 24-hour response promise |
| Urgent | Priority response (2 hours) |
| General | Thank you + 24-hour response |

## Example

```bash
# 1. Gmail Watcher creates file
# /Needs_Action/EMAIL_Testing_12345.md

# 2. You approve (move file)
mv AI_Employee_Vault/Needs_Action/EMAIL_*.md \
   AI_Employee_Vault/Approved/

# 3. Auto-reply processes
python skills/actions/auto-reply/auto_reply.py AI_Employee_Vault

# 4. Email sent, file moved to Done
```
