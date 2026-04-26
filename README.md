# Personal AI Employee - Gold Tier

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

This is the **Gold Tier** implementation of the Personal AI Employee hackathon - a fully autonomous AI employee with Odoo ERP integration, Facebook/Instagram social media management, CEO briefing generation, and Ralph Wiggum Loop for multi-step task completion.

---

## 🏆 Gold Tier Status

**✅ COMPLETE** - All Gold Tier requirements implemented:

- ✅ All Silver Tier requirements
- ✅ Full cross-domain integration (Personal + Business)
- ✅ Odoo Community ERP integration (Docker + MCP)
- ✅ Facebook & Instagram integration (Graph API + MCP)
- ✅ Weekly CEO Briefing with accounting audit
- ✅ Ralph Wiggum Loop for autonomous tasks
- ✅ Comprehensive error recovery
- ✅ Audit logging

---

## 📦 What's Included

### Bronze Tier (Foundation)
| Component | Description | Location |
|-----------|-------------|----------|
| **Obsidian Vault** | Dashboard, Handbook, Goals | `AI_Employee_Vault/` |
| **File Watcher** | Monitors /Inbox for new files | `watchers/filesystem_watcher.py` |
| **Process Drop Skill** | Processes files in /Needs_Action | `skills/process-drop/` |

### Silver Tier (Functional)
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

### Gold Tier (Autonomous) - NEW!
| Component | Description | Location |
|-----------|-------------|----------|
| **Odoo ERP** | Self-hosted accounting via Docker | `odoo/` |
| **Odoo MCP Server** | Odoo JSON-RPC API integration | `skills/mcp-servers/odoo-mcp/` |
| **Odoo Skills** | Create invoices, register payments | `skills/actions/odoo/` |
| **Facebook MCP** | Facebook Graph API integration | `skills/mcp-servers/facebook-mcp/` |
| **Facebook Skills** | Create posts, get insights | `skills/actions/facebook/` |
| **Instagram Skills** | Instagram Business integration | `skills/actions/facebook/` |
| **Social Summary** | Generate social media reports | `skills/actions/facebook/social_media_summary.py` |
| **CEO Briefing** | Weekly business audit reports | `skills/actions/ceo-briefing/` |
| **Ralph Loop** | Autonomous multi-step tasks | `skills/workflow/ralph-loop/` |

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

## 🚀 Gold Tier Quick Start

### Gold Tier Setup (60 minutes)

#### Step 1: Verify Gold Tier Installation

```bash
# Run verification script
chmod +x verify-gold-tier.sh
./verify-gold-tier.sh AI_Employee_Vault
```

This checks all Gold Tier requirements are in place.

#### Step 2: Set Up Odoo ERP (20 minutes)

```bash
# Navigate to Odoo directory
cd odoo

# Make setup script executable
chmod +x setup-odoo.sh

# Start Odoo with Docker Compose
./setup-odoo.sh
```

This will:
- Start Odoo Community 19.0 with PostgreSQL
- Create necessary data directories
- Make Odoo available at http://localhost:8069

**Initial Odoo Configuration:**

1. Open http://localhost:8069 in your browser
2. Create database:
   - Database name: `odoo`
   - Email: `admin@example.com`
   - Password: `admin`
3. Install modules: **Accounting**, **Invoicing**, **Contacts**
4. Enable Developer Mode: Settings → Activate developer mode
5. Get API credentials:
   - Settings → Users → Your User → Generate API Key
   - Note your User ID (from URL)

**Configure Odoo MCP:**

```bash
cd ../skills/mcp-servers/odoo-mcp
cp .env.example .env
nano .env  # Edit with your Odoo credentials
npm install
```

#### Step 3: Set Up Facebook/Instagram (15 minutes)

```bash
cd ../facebook-mcp
cp .env.example .env
nano .env  # Edit with your Facebook credentials
npm install
```

**Get Facebook Credentials:**

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an App (Business type)
3. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
4. Generate Access Token with permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
5. Get Page ID from your Facebook Page "About" section
6. (Optional) Get Instagram Business Account ID

#### Step 4: Test Gold Tier Features

```bash
# Test Odoo MCP
cd skills/mcp-servers/odoo-mcp
npm test

# Test Facebook MCP
cd ../facebook-mcp
npm test

# Generate CEO Briefing
cd ../../../../
python skills/actions/ceo-briefing/ceo_briefing.py AI_Employee_Vault --period weekly
```

#### Step 5: Start Autonomous Operations

```bash
# Start Ralph Wiggum Loop for autonomous task processing
python skills/workflow/ralph-loop/ralph_loop.py AI_Employee_Vault \
  "Process all pending items and generate CEO briefing" \
  --max-iterations 10 \
  --verbose
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
│   ├── Logs/                   # Activity logs
│   └── Briefings/              # CEO briefing reports
│
├── odoo/                       # 🔵 GOLD - Odoo ERP
│   ├── docker-compose.yml      # Docker setup
│   ├── odoo.conf               # Odoo configuration
│   └── setup-odoo.sh           # Setup script
│
├── watchers/
│   ├── base_watcher.py         # Base class for all watchers
│   └── filesystem_watcher.py   # File drop watcher (Bronze)
│
├── skills/
│   ├── watchers/
│   │   ├── gmail-watcher/      # Gmail monitoring
│   │   └── whatsapp-watcher/   # WhatsApp monitoring
│   │
│   ├── actions/
│   │   ├── create-plan/        # Plan.md generation
│   │   ├── send-email/         # Email sending
│   │   ├── post-linkedin/      # LinkedIn posting
│   │   ├── odoo/               # 🔵 GOLD - Odoo skills
│   │   │   ├── odoo_create_invoice.py
│   │   │   └── odoo_mcp_client.py
│   │   ├── facebook/           # 🔵 GOLD - Facebook/Instagram
│   │   │   ├── facebook_create_post.py
│   │   │   ├── facebook_mcp_client.py
│   │   │   └── social_media_summary.py
│   │   └── ceo-briefing/       # 🔵 GOLD - CEO reports
│   │       └── ceo_briefing.py
│   │
│   ├── workflow/
│   │   ├── approval-workflow/  # HITL approvals
│   │   ├── schedule-task/      # Task scheduling
│   │   └── ralph-loop/         # 🔵 GOLD - Autonomous loop
│   │       └── ralph_loop.py
│   │
│   ├── utils/
│   │   └── update-dashboard/   # Dashboard updates
│   │
│   └── mcp-servers/
│       ├── email-mcp/          # Email integration
│       ├── linkedin-mcp/       # LinkedIn integration
│       ├── odoo-mcp/           # 🔵 GOLD - Odoo ERP
│       └── facebook-mcp/       # 🔵 GOLD - Facebook/Instagram
│
├── requirements.txt            # Python dependencies
└── verify-gold-tier.sh         # 🔵 GOLD - Verification script
```
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

## 🔧 Gold Tier Usage

### Odoo ERP Integration

```bash
# Create invoice (requires approval)
python skills/actions/odoo/odoo_create_invoice.py AI_Employee_Vault \
  --partner-id 1 \
  --amount 1500.00 \
  --description "Web Development Services"

# Register payment
python skills/actions/odoo/odoo_mcp_client.py register_payment \
  --invoice-id 123 \
  --amount 1500.00

# Get invoices
python skills/actions/odoo/odoo_mcp_client.py get_invoices --limit 10

# Search partners
python skills/actions/odoo/odoo_mcp_client.py search_partners --query "Client"
```

### Facebook/Instagram Integration

```bash
# Create Facebook post (requires approval)
python skills/actions/facebook/facebook_create_post.py AI_Employee_Vault \
  --message "Excited to announce our new product! 🚀" \
  --link "https://example.com/product" \
  --hashtags "#business" "#startup"

# Get Facebook posts
python skills/actions/facebook/facebook_mcp_client.py get_posts --limit 5

# Get Facebook insights
python skills/actions/facebook/facebook_mcp_client.py get_insights

# Generate social media summary
python skills/actions/facebook/social_media_summary.py AI_Employee_Vault \
  --days 7 \
  --include-instagram \
  --output AI_Employee_Vault/Briefings/Social_Summary.md
```

### CEO Briefing

```bash
# Generate weekly briefing
python skills/actions/ceo-briefing/ceo_briefing.py AI_Employee_Vault \
  --period weekly

# Generate monthly briefing
python skills/actions/ceo-briefing/ceo_briefing.py AI_Employee_Vault \
  --period monthly

# Generate custom period briefing
python skills/actions/ceo-briefing/ceo_briefing.py AI_Employee_Vault \
  --days 14 \
  --output AI_Employee_Vault/Briefings/Custom_Briefing.md
```

### Ralph Wiggum Loop (Autonomous Tasks)

```bash
# Process all pending items autonomously
python skills/workflow/ralph-loop/ralph_loop.py AI_Employee_Vault \
  "Process all emails, create invoices, and schedule social posts" \
  --max-iterations 10 \
  --verbose

# Run with timeout
python skills/workflow/ralph-loop/ralph_loop.py AI_Employee_Vault \
  "Complete all pending approvals and generate CEO briefing" \
  --timeout 3600 \
  --check-interval 30
```

---

## 🔄 Gold Tier Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        PERCEPTION LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │File Watcher │  │Gmail Watcher│  │Facebook     │  │Odoo     ││
│  │             │  │             │  │Watcher      │  │Watcher  ││
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────┬────┘│
│         │                │                │              │      │
│         └────────────────┼────────────────┼──────────────┘      │
│                          │                │                     │
│                          ▼                ▼                     │
│               ┌───────────────────┐  ┌──────────────┐           │
│               │  /Needs_Action/   │  │  /Odoo/      │           │
│               └─────────┬─────────┘  └──────────────┘           │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        REASONING LAYER                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    CLAUDE CODE                               │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │Create Plan   │  │Approval      │  │Ralph Wiggum  │     │  │
│  │  │Skill         │  │Workflow      │  │Loop          │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │  │
│  │  │CEO Briefing  │  │Odoo          │  │Social Media  │     │  │
│  │  │              │  │Integration   │  │Summary       │     │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────┬────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ACTION LAYER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │
│  │Send Email   │  │Post         │  │Odoo         │  │Facebook│ │
│  │(MCP)        │  │LinkedIn     │  │Invoices     │  │Posts   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘ │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │Instagram    │  │CEO          │                               │
│  │Posts        │  │Briefing     │                               │
│  └─────────────┘  └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Gold Tier Checklist

- [x] **All Silver Tier requirements** (Foundation + Functional)
- [x] **Odoo ERP Integration** (Docker + MCP server)
- [x] **Odoo Skills** (Create invoice, register payment, search partners)
- [x] **Facebook Integration** (Graph API + MCP server)
- [x] **Facebook Skills** (Create post, get insights, get posts)
- [x] **Instagram Integration** (Business account + posting)
- [x] **Instagram Skills** (Create post, get media, get insights)
- [x] **Social Media Summary** (Combined Facebook + Instagram reports)
- [x] **CEO Briefing** (Weekly accounting audit + business metrics)
- [x] **Ralph Wiggum Loop** (Autonomous multi-step task completion)
- [x] **Full cross-domain integration** (Personal + Business)
- [x] **Error recovery** (Graceful degradation)
- [x] **Audit logging** (All actions logged)
- [x] **All as Agent Skills** (Modular, reusable skills)

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
- [Claude Code](https://claude.ai/code) - AI reasoning engine
- [Gmail API Setup](https://developers.google.com/gmail/api/quickstart/python) - Email integration
- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1) - Every Wednesday 10:00 PM

---

*Built for the Personal AI Employee Hackathon 0 - Building Autonomous FTEs in 2026*
