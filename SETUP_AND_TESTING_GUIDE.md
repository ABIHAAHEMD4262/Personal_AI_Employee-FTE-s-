# AI Employee - Complete Setup & Testing Guide

This guide walks you through setting up and testing each tier of your AI Employee.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Bronze Tier Setup & Testing](#bronze-tier)
3. [Silver Tier Setup & Testing](#silver-tier)
4. [Gold Tier Setup & Testing](#gold-tier)
5. [API Configuration Guides](#api-configuration)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.13+ installed
- ✅ Node.js v24+ installed
- ✅ Obsidian installed
- ✅ Docker and Docker Compose installed
- ✅ Git installed
- ✅ Stable internet connection

### Install Python Dependencies

```bash
cd /path/to/Personal_AI_Employee(FTE's)
pip install -r requirements.txt
playwright install chromium
```

---

## Bronze Tier

### What's Included

- Obsidian vault with Dashboard.md, Company_Handbook.md, Business_Goals.md
- Filesystem watcher
- Basic folder structure
- Claude orchestrator

### Setup

1. **Verify Vault Structure**

```bash
ls AI_Employee_Vault/
# Should show: Inbox, Needs_Action, Done, Plans, Pending_Approval, Approved, Rejected, Logs, Briefings, Accounting
```

2. **Verify Core Documents Exist**

```bash
cat AI_Employee_Vault/Dashboard.md
cat AI_Employee_Vault/Company_Handbook.md
cat AI_Employee_Vault/Business_Goals.md
```

### Testing

#### Test 1: Filesystem Watcher

```bash
# Drop a test file in Inbox
echo "Test message for processing" > AI_Employee_Vault/Inbox/test_bronze.txt

# Run the filesystem watcher once
python watchers/filesystem_watcher.py AI_Employee_Vault --once

# Check if file was processed
ls AI_Employee_Vault/Needs_Action/
# You should see: FILE_test_bronze.txt.md
```

**Expected Result:** File copied to Needs_Action with metadata file created.

#### Test 2: Claude Code Integration

```bash
# Test Claude can read the vault
claude "Read AI_Employee_Vault/Dashboard.md and summarize the current status"
```

\*\*Expected Result:\*\* Claude reads and summarizes the dashboard.

#### Test 3: Folder Structure Validation

```bash
# Run this to verify all required folders exist
python -c "
from pathlib import Path
vault = Path('AI_Employee_Vault')
folders = ['Inbox', 'Needs_Action', 'In_Progress', 'Pending_Approval', 'Approved', 'Rejected', 'Done', 'Plans', 'Briefings', 'Accounting', 'Logs']
for f in folders:
    assert (vault / f).exists(), f'{f} missing'
print('✅ All required folders exist')
"
```

**Expected Result:** "✅ All required folders exist"

### Bronze Tier Checklist

- [ ] Obsidian vault created and accessible
- [ ] Dashboard.md exists with content
- [ ] Company_Handbook.md exists with rules
- [ ] Business_Goals.md exists with objectives
- [ ] All required folders exist
- [ ] Filesystem watcher processes files correctly
- [ ] Claude can read and write to vault

---

## Silver Tier

### What's Included

- Multiple watchers (Gmail, WhatsApp, LinkedIn, Facebook)
- Email MCP server
- Approval workflow
- Auto-reply skill
- Create-plan skill
- Schedule-task utility

### Setup

#### 1. Gmail Watcher Setup

**Step 1: Enable Gmail API**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Gmail API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Download `credentials.json`
6. Place it in `skills/watchers/gmail-watcher/credentials.json`

**Step 2: Run OAuth Flow**

```bash
cd skills/watchers/gmail-watcher
python gmail_watcher.py --setup-oauth
# Browser will open, authorize access to Gmail
```

**Step 3: Test Gmail Watcher**

```bash
# Check for new emails
python gmail_watcher.py /path/to/AI_Employee_Vault --once

# Check Needs_Action folder
ls AI_Employee_Vault/Needs_Action/
# You should see EMAIL_*.md files for unread messages
```

#### 2. WhatsApp Watcher Setup

**Step 1: Install Playwright**

```bash
pip install playwright
playwright install chromium
```

**Step 2: Setup WhatsApp Session**

```bash
cd skills/watchers/whatsapp-watcher
python whatsapp_watcher.py /path/to/AI_Employee_Vault --setup-session
# Browser opens, scan QR code with WhatsApp mobile
# Wait until you see your chats, then press Ctrl+C
```

**Step 3: Test WhatsApp Watcher**

```bash
python whatsapp_watcher.py /path/to/AI_Employee_Vault --once
```

#### 3. Email MCP Server

**Status:** Already installed with OAuth token.

**Test:**

```bash
cd skills/mcp-servers/email-mcp
node email_mcp_server.js
# Should show: ✅ Email MCP Server running
```

#### 4. Approval Workflow Test

```bash
cd skills/workflow/approval-workflow

# Create a test approval request
python approval_workflow.py --create --type payment \
  --data '{"amount": 100, "recipient": "Test Recipient", "reason": "Test payment"}'

# Check Pending_Approval folder
ls AI_Employee_Vault/Pending_Approval/

# Execute the approval
python approval_workflow.py --execute
```

#### 5. Auto-Reply Skill Test

```bash
cd skills/actions/auto-reply

# Test auto-reply creation
python auto_reply.py /path/to/AI_Employee_Vault \
  --category invoice \
  --from "test@example.com" \
  --subject "Invoice Request"
```

#### 6. Schedule-Task Test

```bash
cd skills/workflow/schedule-task

# Schedule a daily briefing at 8:00 AM
python schedule_task.py --daily --time "08:00" --task "daily_briefing"

# List scheduled tasks
python schedule_task.py --list
```

### Silver Tier Checklist

- [ ] Gmail watcher detects and processes emails
- [ ] WhatsApp watcher detects messages with keywords
- [ ] Email MCP server runs successfully
- [ ] Approval workflow creates and processes requests
- [ ] Auto-reply skill generates appropriate responses
- [ ] Create-plan skill generates plan files
- [ ] Schedule-task utility can schedule tasks
- [ ] Facebook MCP server installed and configured

---

## Gold Tier

### What's Included

- Full cross-domain integration
- Odoo accounting integration
- Facebook/Instagram posting
- Twitter/X integration
- LinkedIn integration
- CEO Briefing generation
- Ralph Wiggum loop
- Multiple MCP servers

### Setup

#### 1. Odoo Setup

**Step 1: Start Odoo**

```bash
cd odoo
./start-odoo.sh
```

**Step 2: Initial Configuration**

1. Open http://localhost:8069 in browser
2. Create database:
   - Database name: `odoo`
   - Master password: `odoo`
   - Email: your email
   - Password: your password
3. Install apps:
   - **Invoicing** (or Accounting)
   - **Contacts**
   - **Sales** (optional)

**Step 3: Enable Developer Mode**

1. Go to **Settings**
2. Scroll to bottom
3. Click **Activate the developer mode**

**Step 4: Generate API Key**

1. Go to **Settings** → **Users & Companies** → **Users**
2. Click your user (usually Admin)
3. Click **API Keys** tab
4. Click **Add API Key**
5. Copy the API key
6. Note your User ID from URL (e.g., `/web#id=2&action=...` → ID is 2)

**Step 5: Configure Odoo MCP**

```bash
cd skills/mcp-servers/odoo-mcp
# .env file already created, edit with your values
nano .env

# Update:
# ODOO_DATABASE=odoo
# ODOO_API_KEY=your-api-key
# ODOO_USER_ID=2
```

**Step 6: Test Odoo MCP**

```bash
cd skills/mcp-servers/odoo-mcp
npm start
# Should show: ✅ Odoo MCP Server running
```

**Step 7: Test Odoo Integration**

```bash
cd skills/actions/odoo

# Search for partners
python odoo_mcp_client.py search_partners --query "Admin"

# Create a test invoice
python odoo_mcp_client.py create_invoice \
  --partner-id 1 \
  --lines "Consulting Service" 500.00 1
```

#### 2. Facebook/Instagram Setup

**Step 1: Create Facebook App**

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create App → **Business** type
3. Add **Facebook Login** product

**Step 2: Get Page Access Token**

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Click **Get Token** → **Get Page Access Token**
4. Select permissions: `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`
5. Copy the token

**Step 3: Get Page ID**

```bash
# In Graph API Explorer, GET: me/accounts
# Find your page ID in the response
```

**Step 4: (Optional) Get Instagram Account ID**

```bash
# In Graph API Explorer, GET: YOUR_PAGE_ID?fields=instagram_business_account
```

**Step 5: Configure Facebook MCP**

```bash
cd skills/mcp-servers/facebook-mcp
# .env file already created, edit with your values
nano .env

# Update:
# FACEBOOK_ACCESS_TOKEN=your-token
# FACEBOOK_PAGE_ID=your-page-id
# INSTAGRAM_ACCOUNT_ID=your-ig-id (optional)
```

**Step 6: Setup Facebook Watcher**

```bash
cd skills/watchers/facebook-watcher
python facebook_watcher.py /path/to/AI_Employee_Vault --setup-session
# Browser opens, log in to Facebook
# Wait until you see your feed, then press Ctrl+C
```

**Step 7: Test Facebook Posting**

```bash
cd skills/actions/facebook

# Create a test post (with approval)
python facebook_create_post.py /path/to/AI_Employee_Vault \
  --message "Test post from AI Employee" \
  --hashtags "#AI #Automation"

# Check Pending_Approval folder, then move file to Approved to publish
```

#### 3. Twitter/X Setup

**Step 1: Setup Twitter Watcher**

```bash
cd skills/watchers/twitter-watcher
python twitter_watcher.py /path/to/AI_Employee_Vault --setup-session
# Browser opens, log in to Twitter/X
# Wait until you see your feed, then press Ctrl+C
```

**Step 2: Test Twitter Posting**

```bash
cd skills/actions/twitter

# Create a test tweet
python twitter_create_post.py /path/to/AI_Employee_Vault \
  --message "Test tweet from AI Employee 🤖" \
  --hashtags "#AI #Automation"

# Check Pending_Approval folder
```

**Step 3: Install Twitter MCP (Optional)**

```bash
cd skills/mcp-servers/twitter-mcp
npm install  # Already done
npm start
```

#### 4. LinkedIn Setup

**Step 1: Setup LinkedIn Watcher**

```bash
cd skills/watchers/linkedin-watcher
python linkedin_watcher.py /path/to/AI_Employee_Vault --setup-session
# Browser opens, log in to LinkedIn
# Wait until you see your feed, then press Ctrl+C
```

**Step 2: Test LinkedIn MCP**

```bash
cd skills/mcp-servers/linkedin-mcp
npm start
```

#### 5. CEO Briefing Test

```bash
cd skills/actions/ceo-briefing

# Generate a test briefing
python ceo_briefing.py /path/to/AI_Employee_Vault --verbose

# Check Briefings folder
ls AI_Employee_Vault/Briefings/
```

#### 6. Ralph Wiggum Loop Test

```bash
cd skills/workflow/ralph-loop

# Test with dry-run first
python ralph_loop.py --dry-run --verbose

# Create a test task
echo "Test task" > AI_Employee_Vault/Needs_Action/TEST_TASK.md

# Run Ralph loop (will process the task)
python ralph_loop.py /path/to/AI_Employee_Vault --verbose --max-iterations 5
```

### Gold Tier Checklist

- [ ] Odoo running and accessible at http://localhost:8069
- [ ] Odoo MCP server connects successfully
- [ ] Can create invoices in Odoo
- [ ] Facebook MCP server runs
- [ ] Can post to Facebook via approval workflow
- [ ] Twitter watcher session saved
- [ ] Can create tweets via approval workflow
- [ ] LinkedIn watcher session saved
- [ ] LinkedIn MCP server runs
- [ ] CEO Briefing generates successfully
- [ ] Ralph Wiggum loop processes tasks
- [ ] All watchers running (Gmail, WhatsApp, Facebook, Twitter, LinkedIn)

---

## API Configuration

### Gmail API

1. [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Download credentials.json → `skills/watchers/gmail-watcher/credentials.json`

### Facebook Graph API

1. [Facebook Developers](https://developers.facebook.com/)
2. Create Business app
3. Add Facebook Login product
4. Get Page Access Token via [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
5. Get Page ID
6. Configure in `skills/mcp-servers/facebook-mcp/.env`

**Detailed Guide:** See `skills/mcp-servers/facebook-mcp/SETUP_GUIDE.md`

### Instagram (via Facebook Graph API)

1. Convert Instagram to Business Account
2. Link to Facebook Page
3. Get Instagram Account ID via Graph API
4. Configure in `skills/mcp-servers/facebook-mcp/.env`

### Twitter/X

- Uses Playwright automation (no API key needed)
- Session saved in `skills/watchers/twitter-watcher/twitter_session`

### LinkedIn

- Uses Playwright automation (no API key needed)
- Session saved in `skills/watchers/linkedin-watcher/linkedin_session`

### Odoo

1. Start Odoo: `cd odoo && ./start-odoo.sh`
2. Create database
3. Enable Developer Mode
4. Generate API Key: Settings → Users → Your User → API Keys
5. Get User ID from URL
6. Configure in `skills/mcp-servers/odoo-mcp/.env`

---

## Troubleshooting

### Odoo Won't Start

```bash
# Check Docker
docker info

# Check logs
cd odoo
docker-compose logs -f

# Restart
docker-compose down
docker-compose up -d
```

### Facebook Token Expired

- Tokens expire after 60 days
- Generate new token via Graph API Explorer
- Update `.env` file

### Watchers Not Detecting Anything

```bash
# Check session exists
ls skills/watchers/*/session

# Re-setup session
python *_watcher.py --setup-session

# Check logs
tail -f /tmp/watcher_*.log
```

### MCP Server Won't Connect

```bash
# Check .env file exists
cat skills/mcp-servers/*/env

# Verify credentials
# Test each server individually:
cd skills/mcp-servers/facebook-mcp
npm start
```

### Approval Workflow Not Working

```bash
# Check folder structure
ls AI_Employee_Vault/Pending_Approval/
ls AI_Employee_Vault/Approved/

# Test workflow manually
python skills/workflow/approval-workflow/approval_workflow.py --check
```

---

## Quick Start Commands

### Start Everything

```bash
# 1. Start Odoo
cd odoo && ./start-odoo.sh &

# 2. Start watchers (in separate terminals)
python watchers/filesystem_watcher.py AI_Employee_Vault
python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault
python skills/watchers/whatsapp-watcher/whatsapp_watcher.py AI_Employee_Vault

# 3. Start orchestrator
python claude_orchestrator.py AI_Employee_Vault --watch
```

### Stop Everything

```bash
# Stop Odoo
cd odoo && docker-compose down

# Kill watchers
pkill -f ".*_watcher.py"

# Stop orchestrator
pkill -f claude_orchestrator
```

---

## Next Steps

After completing all tiers:

1. **Set up cron jobs** for automated tasks
2. **Configure Cloud deployment** (Platinum tier)
3. **Add more watchers** (Slack, Discord, etc.)
4. **Customize Company Handbook** with your rules
5. **Monitor and review** logs weekly

---

**Generated:** 2026-04-03
**Version:** 1.0.0
