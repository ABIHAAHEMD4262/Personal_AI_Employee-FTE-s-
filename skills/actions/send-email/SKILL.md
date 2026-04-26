---
name: send-email
description: |
  Send emails via MCP server with human-in-the-loop approval.
  Supports sending, drafting, and searching emails through Gmail.
  
  Use when:
  - Replying to emails from /Needs_Action
  - Sending new emails that require approval
  - Drafting emails for review
  
  NOT when:
  - Reading emails only (use gmail-watcher)
  - Sending without approval (violates Company Handbook)
---

# Send Email Skill

Send emails via MCP server with approval workflow.

## Usage

### Via Claude Code

```bash
# Send a reply email
claude "Send reply to FILE_invoice.pdf in Needs_Action"

# Draft email for approval
claude "Draft email to client@example.com about project update"

# Search emails
claude "Search emails from last week about invoice"
```

### Via Python Script

```bash
# Send email (requires approval file in /Approved)
python skills/actions/send-email/send_email.py VAULT --send --to email@example.com --subject "Hello" --content "Message"

# Draft email
python skills/actions/send-email/send_email.py VAULT --draft --to email@example.com --subject "Hello" --content "Message"

# Search emails
python skills/actions/send-email/send_email.py VAULT --search "invoice" --max 10
```

## MCP Server Setup

### 1. Install Dependencies

```bash
cd skills/mcp-servers/email-mcp
npm install
```

### 2. Configure Credentials

```bash
# Set environment variable
export GMAIL_CREDENTIALS="/path/to/credentials.json"

# Or add to .env file
echo 'GMAIL_CREDENTIALS=/path/to/credentials.json' > .env
```

### 3. Start MCP Server

```bash
# Start server
node skills/mcp-servers/email-mcp/index.js

# Or via npx
npx -y @modelcontextprotocol/server-gmail
```

### 4. Configure in Claude Code

Add to your MCP configuration:
```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  ]
}
```

## Workflow

```
Email Action Needed
        ↓
Create Approval Request → /Pending_Approval/
        ↓
    User Approves (move to /Approved)
        ↓
Execute via MCP Server
        ↓
Log & Move to /Done
```

## Email Templates

### Reply Template
```markdown
---
type: email_reply
to: client@example.com
subject: Re: Original Subject
in_reply_to: message_id
status: draft
---

## Content
Dear Client,

[Reply content]

Best regards,
[Your name]
```

### New Email Template
```markdown
---
type: email_new
to: recipient@example.com
cc: optional@example.com
subject: Subject Line
status: pending_approval
---

## Content
[Email body]
```

## Approval Integration

All sent emails require approval unless:
- Replying to known contacts (in Company Handbook)
- Auto-approved by rules in config.json

## Error Handling

- **Auth Error**: Re-run OAuth flow
- **Rate Limit**: Wait and retry
- **Invalid Recipient**: Log error, skip
- **Content Filter**: Flag for review
