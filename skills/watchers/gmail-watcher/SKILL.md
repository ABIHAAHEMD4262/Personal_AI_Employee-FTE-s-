---
name: gmail-watcher
description: |
  Monitor Gmail for important/unread emails and create action files.
  Uses Gmail API to fetch emails and saves them as .md files in /Needs_Action.
  
  Use when:
  - You want to monitor Gmail automatically
  - Important emails need processing by AI
  - Email triage is needed
  
  NOT when:
  - Only checking email occasionally (use manual check)
  - Gmail API is not configured
---

# Gmail Watcher Skill

Monitor Gmail and create action files for important emails.

## Usage

### Via Qwen Code

```bash
# Process new Gmail messages
qwen "Check Gmail and process new important emails"
```

### Via Python Script

```bash
# Run watcher continuously
python skills/watchers/gmail-watcher/gmail_watcher.py VAULT_PATH --interval 120

# Run once (for cron)
python skills/watchers/gmail-watcher/gmail_watcher.py VAULT_PATH --once

# Check configuration
python skills/watchers/gmail-watcher/gmail_watcher.py VAULT_PATH --check-config
```

## Setup

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials.json

### 2. Configure Environment

```bash
# Set environment variable
export GMAIL_CREDENTIALS="/path/to/credentials.json"

# Or create .env file in watcher folder
echo 'GMAIL_CREDENTIALS=/path/to/credentials.json' > .env
```

### 3. First Run Authentication

```bash
# First run will open browser for OAuth
python skills/watchers/gmail-watcher/gmail_watcher.py VAULT_PATH --auth
```

## Configuration

Create `config.json` in gmail-watcher folder:

```json
{
  "check_interval": 120,
  "query": "is:unread is:important",
  "labels": ["INBOX"],
  "max_results": 10,
  "keywords": ["urgent", "asap", "invoice", "payment"],
  "exclude_senders": ["noreply@", "notifications@"]
}
```

## Action File Format

```markdown
---
type: email
from: john@example.com
subject: Invoice Payment Required
received: 2026-02-27T10:30:00Z
message_id: 18e4c1234567890
priority: high
status: pending
labels: ["INBOX", "IMPORTANT"]
---

# Email: Invoice Payment Required

## From
john@example.com

## Received
2026-02-27T10:30:00Z

## Content
Dear Team,

Please find attached the invoice for January services...

## Suggested Actions
- [ ] Reply to sender
- [ ] Process payment (requires approval)
- [ ] Forward to accounting
- [ ] Archive after processing
```

## Features

- **Keyword Detection**: Flag emails with urgent keywords
- **Sender Filtering**: Exclude automated senders
- **Label Support**: Filter by Gmail labels
- **Duplicate Prevention**: Track processed message IDs
- **Persistent Cache**: Survives restarts

## Integration

Works with:
- `send-email` - Reply to emails
- `approval-workflow` - Payment-related emails
- `create-plan` - Generate action plans
- `process-drop` - Process email attachments
