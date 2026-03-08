---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for urgent messages using Playwright.
  Detects keywords like "urgent", "asap", "invoice", "payment" and creates action files.
  
  Use when:
  - You want to monitor WhatsApp automatically
  - Urgent messages need immediate attention
  - Client communication via WhatsApp
  
  NOT when:
  - Only checking occasionally (use manual check)
  - WhatsApp Web is not accessible
  - You don't have an active WhatsApp session
  
  ⚠️ WARNING: Be aware of WhatsApp's terms of service when using automation.
---

# WhatsApp Watcher Skill

Monitor WhatsApp Web and create action files for urgent messages.

## Usage

### Via Qwen Code

```bash
# Check WhatsApp and process urgent messages
qwen "Check WhatsApp for urgent messages"
```

### Via Python Script

```bash
# Run watcher continuously
python skills/watchers/whatsapp-watcher/whatsapp_watcher.py VAULT_PATH --interval 60

# Run once (for testing)
python skills/watchers/whatsapp-watcher/whatsapp_watcher.py VAULT_PATH --once

# Setup WhatsApp session (opens browser for QR scan)
python skills/watchers/whatsapp-watcher/whatsapp_watcher.py VAULT_PATH --setup-session
```

## Setup

### 1. Install Dependencies

```bash
pip install playwright
playwright install chromium
```

### 2. First-Time Session Setup

```bash
# This will open a browser - scan the QR code with WhatsApp
python skills/watchers/whatsapp-watcher/whatsapp_watcher.py VAULT_PATH --setup-session
```

### 3. Session Storage

Session data is stored in:
```
skills/watchers/whatsapp-watcher/whatsapp_session/
```

## Configuration

Create `config.json` in whatsapp-watcher folder:

```json
{
  "check_interval": 60,
  "keywords": ["urgent", "asap", "invoice", "payment", "help", "call me"],
  "check_duration": 30,
  "headless": true
}
```

## Action File Format

```markdown
---
type: whatsapp
from: +1234567890
chat: John Doe
received: 2026-02-27T10:30:00Z
priority: high
status: pending
keywords: ["urgent", "invoice"]
---

# WhatsApp Message: John Doe

## From
+1234567890 (John Doe)

## Received
2026-02-27T10:30:00Z

## Message
Hi, this is urgent! Can you send me the invoice for last month?

## Keywords Detected
- urgent
- invoice

## Suggested Actions
- [ ] Reply to sender
- [ ] Create and send invoice (requires approval)
- [ ] Follow up if needed
```

## Features

- **Keyword Detection**: Flag messages with urgent keywords
- **Session Persistence**: Remains logged in across restarts
- **Unread Detection**: Only processes new unread messages
- **Privacy**: Runs in headless mode by default

## Integration

Works with:
- `send-email` - Reply via email
- `approval-workflow` - Payment-related messages
- `create-plan` - Generate action plans

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not showing | Delete whatsapp_session/ folder and re-run --setup-session |
| Session expired | Re-run --setup-session to refresh |
| No messages detected | Check if messages are marked as unread |
| Browser won't open | Ensure playwright is installed: `playwright install chromium` |
