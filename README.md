# Personal AI Employee - Silver Tier

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

This is the **Silver Tier** implementation of the Personal AI Employee hackathon - a functional autonomous agent with email integration, approval workflows, and automated posting.

---

## 📦 What's Included

### Bronze Tier (Foundation)
| Component | Description | Location |
|-----------|-------------|----------|
| **Obsidian Vault** | Dashboard, Handbook, Goals | `AI_Employee_Vault/` |
| **File Watcher** | Monitors /Inbox for new files | `watchers/filesystem_watcher.py` |
| **Process Drop Skill** | Processes files in /Needs_Action | `skills/process-drop/` |

### Silver Tier (New)
| Component | Description | Location |
|-----------|-------------|----------|
| **Gmail Watcher** | Monitor Gmail for important emails | `skills/watchers/gmail-watcher/` |
| **Create Plan Skill** | Generate Plan.md files | `skills/actions/create-plan/` |
| **Approval Workflow** | Human-in-the-loop approvals | `skills/workflow/approval-workflow/` |
| **Send Email** | Send emails via MCP | `skills/actions/send-email/` |
| **Post LinkedIn** | Auto-post to LinkedIn | `skills/actions/post-linkedin/` |
| **Schedule Task** | Cron/Task Scheduler setup | `skills/workflow/schedule-task/` |
| **Update Dashboard** | Keep dashboard current | `skills/utils/update-dashboard/` |
| **Email MCP Server** | Gmail integration server | `skills/mcp-servers/email-mcp/` |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js v24+ (for MCP servers)
- Obsidian (optional, for viewing vault)
- Gmail API credentials (for email features)

### Setup (15 minutes)

1. **Install Python dependencies:**
   ```bash
   # Core dependencies
   pip install watchdog

   # Optional: Gmail integration
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

2. **Install Node.js dependencies (for MCP):**
   ```bash
   cd skills/mcp-servers/email-mcp
   npm install
   ```

3. **Configure Gmail (if using email features):**

   **Note:** Your `credentials.json` is already configured in the project root.

   ```bash
   # Step 1: Run OAuth authentication (requires browser)
   python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --auth

   # This will:
   # 1. Open a browser window
   # 2. Ask you to sign in with Google
   # 3. Save the token to skills/watchers/gmail-watcher/token.json

   # Step 2: Verify configuration
   python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --check-config
   ```

4. **Start the File Watcher:**
   ```bash
   python watchers/filesystem_watcher.py AI_Employee_Vault --interval 30
   ```

---

## 📁 Folder Structure

```
Personal_AI_Employee(FTE's)/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Main dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Objectives and metrics
│   ├── Inbox/                  # Drop files here
│   ├── Needs_Action/           # Files awaiting processing
│   ├── Plans/                  # Generated action plans
│   ├── Pending_Approval/       # Awaiting human approval
│   ├── Approved/               # Approved actions (auto-executed)
│   ├── Rejected/               # Rejected actions
│   ├── Done/                   # Completed items
│   ├── Drafts/                 # Email drafts
│   ├── Scheduled/              # Scheduled posts
│   └── Logs/                   # Activity logs
│
├── watchers/
│   ├── base_watcher.py         # Base class for all watchers
│   └── filesystem_watcher.py   # File drop watcher (Bronze)
│
├── skills/
│   ├── watchers/
│   │   ├── gmail-watcher/      # 🔵 NEW - Gmail monitoring
│   │   └── whatsapp-watcher/   # 🔵 NEW - WhatsApp monitoring
│   │
│   ├── actions/
│   │   ├── create-plan/        # 🔵 NEW - Plan.md generation
│   │   ├── send-email/         # 🔵 NEW - Email sending
│   │   └── post-linkedin/      # 🔵 NEW - LinkedIn posting
│   │
│   ├── workflow/
│   │   ├── approval-workflow/  # 🔵 NEW - HITL approvals
│   │   └── schedule-task/      # 🔵 NEW - Task scheduling
│   │
│   ├── utils/
│   │   └── update-dashboard/   # 🔵 NEW - Dashboard updates
│   │
│   └── mcp-servers/
│       └── email-mcp/          # 🔵 NEW - Email MCP server
│
└── requirements.txt            # Python dependencies
```

---

## 🔧 Usage

### File Watcher (Bronze)

```bash
# Continuous monitoring
python watchers/filesystem_watcher.py AI_Employee_Vault --interval 30

# Run once (for cron)
python watchers/filesystem_watcher.py AI_Employee_Vault --once
```

### Gmail Watcher (Silver)

```bash
# First-time OAuth setup
python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --auth

# Continuous monitoring
python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --interval 120

# Run once
python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --once

# Check configuration
python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --check-config
```

### Create Plan (Silver)

```bash
# Generate plans for all pending items
python skills/actions/create-plan/create_plan.py AI_Employee_Vault

# Verbose output
python skills/actions/create-plan/create_plan.py AI_Employee_Vault --verbose
```

### Approval Workflow (Silver)

```bash
# Check pending approvals
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault --check

# Execute approved actions
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault --execute

# Create approval request
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault \
  --create --action payment --amount 500 --recipient "Client A"
```

### Send Email (Silver)

```bash
# Send email (creates approval request)
python skills/actions/send-email/send_email.py AI_Employee_Vault \
  --send --to client@example.com --subject "Invoice" --content "Please find attached..."

# Draft email
python skills/actions/send-email/send_email.py AI_Employee_Vault \
  --draft --to client@example.com --subject "Update" --content "Here's the update..."

# Process approved emails
python skills/actions/send-email/send_email.py AI_Employee_Vault --process-approved
```

### Post LinkedIn (Silver)

```bash
# Create post (requires approval)
python skills/actions/post-linkedin/post_linkedin.py AI_Employee_Vault \
  --create --content "Excited to announce our new product launch! #business"

# Execute approved posts
python skills/actions/post-linkedin/post_linkedin.py AI_Employee_Vault --execute
```

### Schedule Task (Silver)

```bash
# Daily briefing at 8 AM
python skills/workflow/schedule-task/schedule_task.py AI_Employee_Vault \
  --daily --time "08:00" --task "daily_briefing"

# Weekly audit on Sunday at 10 PM
python skills/workflow/schedule-task/schedule_task.py AI_Employee_Vault \
  --weekly --day "Sunday" --time "22:00" --task "weekly_audit"

# List scheduled tasks
python skills/workflow/schedule-task/schedule_task.py AI_Employee_Vault --list
```

### Update Dashboard (Silver)

```bash
# Full update
python skills/utils/update-dashboard/update_dashboard.py AI_Employee_Vault

# Quick update (counts only)
python skills/utils/update-dashboard/update_dashboard.py AI_Employee_Vault --quick
```

---

## 🔄 Silver Tier Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        PERCEPTION LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │File Watcher │  │Gmail Watcher│  │WhatsApp     │              │
│  │(Bronze)     │  │(Silver)     │  │Watcher      │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          │                                       │
│                          ▼                                       │
│               ┌───────────────────┐                              │
│               │  /Needs_Action/   │                              │
│               └─────────┬─────────┘                              │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        REASONING LAYER                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    QWEN CODE                               │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │Create Plan   │  │Approval      │  │Update        │     │  │
│  │  │Skill         │  │Workflow      │  │Dashboard     │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ACTION LAYER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │Send Email   │  │Post         │  │Schedule     │              │
│  │(MCP)        │  │LinkedIn     │  │Tasks        │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Silver Tier Checklist

- [x] **Bronze Tier Complete** (Foundation)
- [x] **2+ Watcher scripts** (Filesystem + Gmail)
- [x] **Post on LinkedIn** skill
- [x] **Create Plan.md** skill
- [x] **Email MCP server** + send skill
- [x] **Approval workflow** skill
- [x] **Scheduling setup** (cron/Task Scheduler)
- [x] **All as Agent Skills**

---

## 🔐 Security & Approval

### Actions Requiring Approval

| Action | Approval Required | Auto-Approve |
|--------|-------------------|--------------|
| Payment | Always | Never |
| Email to new contact | Yes | Known contacts |
| LinkedIn post | Yes | After N approved |
| File deletion | Important files | Temp files |

### Approval Process

1. Action creates request in `/Pending_Approval/`
2. User reviews and moves to `/Approved/` or `/Rejected/`
3. Approved actions execute automatically
4. All actions logged to `/Logs/`

---

## 🧪 Testing

### Test Approval Workflow

```bash
# Create test approval request
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault \
  --create --action payment --amount 100 --recipient "Test Client"

# Check pending
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault --check

# Manually move file to /Approved, then:
python skills/workflow/approval-workflow/approval_workflow.py AI_Employee_Vault --execute
```

### Test Gmail Watcher

```bash
# Check config first
python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --check-config

# Run once
python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --once
```

### Test Full Workflow

```bash
# 1. Drop a file
echo "Test document" > AI_Employee_Vault/Inbox/test.txt

# 2. Run watcher
python watchers/filesystem_watcher.py AI_Employee_Vault --once

# 3. Create plan
python skills/actions/create-plan/create_plan.py AI_Employee_Vault

# 4. Process file
python skills/process-drop/process_drop.py AI_Employee_Vault

# 5. Update dashboard
python skills/utils/update-dashboard/update_dashboard.py AI_Employee_Vault
```

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [Dashboard.md](./AI_Employee_Vault/Dashboard.md) | Real-time status overview |
| [Company_Handbook.md](./AI_Employee_Vault/Company_Handbook.md) | Rules of engagement |
| [Business_Goals.md](./AI_Employee_Vault/Business_Goals.md) | Objectives and metrics |
| [SKILL.md](./skills/) | Individual skill documentation |

---

## ⏭️ Next Steps (Gold Tier)

After mastering Silver, consider adding:

1. **WhatsApp Watcher** - Monitor WhatsApp messages
2. **Odoo Integration** - Accounting system via MCP
3. **Facebook/Instagram** - Social media posting
4. **Twitter (X)** - Tweet automation
5. **Weekly CEO Briefing** - Autonomous audit reports
6. **Ralph Wiggum Loop** - Multi-step autonomous tasks

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Gmail auth fails | Re-run `--auth` flag, check credentials.json |
| MCP server won't start | Run `npm install` in email-mcp folder |
| Approval not executing | Check file is in /Approved folder |
| Dashboard not updating | Check file permissions on Dashboard.md |
| Scheduled tasks not running | Check cron with `crontab -l` or Task Scheduler |

---

## 📚 Resources

- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md) - Full architecture guide
- [Obsidian Download](https://obsidian.md/download) - Knowledge base app
- [Qwen Code](https://github.com/QwenLM/Qwen) - AI reasoning engine
- [Gmail API Setup](https://developers.google.com/gmail/api/quickstart/python) - Email integration
- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1) - Every Wednesday 10:00 PM

---

*Built for the Personal AI Employee Hackathon 0 - Building Autonomous FTEs in 2026*
