# 📧 Gmail Watcher - Complete Test Commands

## Quick Test (5 Commands)

```bash
# Navigate to project
cd /mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)

# 1. Check Gmail configuration
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --check-config

# 2. Authenticate with Gmail (if not done)
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --auth

# 3. Run watcher once (test mode)
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --once

# 4. Start continuous monitoring
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --interval 60

# 5. Check for created files
ls -la AI_Employee_Vault/Needs_Action/
```

---

## 🔍 Detailed Testing Steps

### Step 1: Verify Configuration

```bash
cd /mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)

# Check if Gmail credentials exist
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --check-config
```

**Expected Output:**
```
✅ Configuration OK
  Credentials: credentials.json
  Token: skills/mcp-servers/email-mcp/token.json
  Query: is:unread is:important
```

**If token not found, authenticate:**
```bash
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --auth
```

This will open a browser. Log in and grant permissions.

---

### Step 2: Send Test Email

From your personal email, send:

```
To: abihacodes@gmail.com
Subject: Test Email for AI Employee
Content: Hello, this is a test email to verify the Gmail Watcher is working.
```

**⭐ IMPORTANT:** Star the email (mark as Important) in Gmail, or it won't be detected!

The query is: `is:unread is:important`

---

### Step 3: Run Gmail Watcher (Single Check)

```bash
# Run once to check for new emails
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --once
```

**Expected Output:**
```
Found 1 new item(s)
Created: EMAIL_Test_Email_for_AI_Employee_18e4a2b3c5d6f7g8.md
Processed 1 email(s)
```

---

### Step 4: Verify Action File Created

```bash
# Check Needs_Action folder
ls -la AI_Employee_Vault/Needs_Action/

# View the created file
cat AI_Employee_Vault/Needs_Action/EMAIL_*.md
```

**Expected Content:**
```markdown
---
type: email
from: your-personal@email.com
to: abihacodes@gmail.com
subject: Test Email for AI Employee
received: 2026-03-03T20:30:00
message_id: 18e4a2b3c5d6f7g8
priority: high
status: pending
labels: ["INBOX", "IMPORTANT", "UNREAD"]
---

# Email: Test Email for AI Employee

## From
your-personal@email.com

## Content
Hello, this is a test email to verify the Gmail Watcher is working.

## Suggested Actions
- [ ] Read and understand email content
- [ ] Draft appropriate reply
- [ ] Send reply (requires approval)
- [ ] Archive email after processing
```

---

### Step 5: Run Continuous Monitoring

```bash
# Start watcher (checks every 60 seconds)
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --interval 60
```

**Keep this running in Terminal 1**

---

### Step 6: Send Another Test Email

While the watcher is running, send another email:

```
To: abihacodes@gmail.com
Subject: Second Test - Urgent
Content: This is another test email.
```

**Star it!**

**Watch Terminal 1 output:**
```
2026-03-03 20:35:00 - GmailWatcher - INFO: Found 1 new item(s)
2026-03-03 20:35:00 - GmailWatcher - INFO: Created: EMAIL_Second_Test_Urgent_18e4a2b3c5d6f7g9.md
```

---

### Step 7: Test Qwen Orchestrator Integration

**In Terminal 2:**

```bash
# Start orchestratorpython3 qwen_orchestrator.py AI_Employee_Vault --watch --interval 30

```

**Watch output:**
```
[INFO] Processing: EMAIL_Second_Test_Urgent_18e4a2b3c5d6f7g9.md
[INFO] Step 1: Creating action plan...
[INFO]   → Plan created successfully
[INFO] Step 2: Moving to Pending_Approval...
[INFO]   → Moved EMAIL_Second_Test_Urgent_18e4a2b3c5d6f7g9.md to Pending_Approval
[INFO]   → Moved PLAN_email_reply_18e4a2b3c5d6f7g9.md to Pending_Approval
```

---

### Step 8: Verify Files Moved to Pending_Approval

```bash
# Check Pending_Approval folder
ls -la AI_Employee_Vault/Pending_Approval/

# Should see both EMAIL and PLAN files
```

---

### Step 9: Approve and Send Reply

```bash
# Move to Approved (triggers auto-reply)
mv AI_Employee_Vault/Pending_Approval/EMAIL_*.md AI_Employee_Vault/Approved/
mv AI_Employee_Vault/Pending_Approval/PLAN_*.md AI_Employee_Vault/Approved/

# Wait 30 seconds for orchestrator to process
```

**Check orchestrator logs:**
```
[INFO] Processing approved: EMAIL_Second_Test_Urgent_18e4a2b3c5d6f7g9.md
[INFO] Sending email via Gmail API...
[INFO]   → Gmail API sent! Message ID: new_message_id
[INFO]   → Email sent successfully!
[INFO]   → Moved to Done/2026-03-03/
```

---

### Step 10: Verify Reply Sent

**Check Gmail Sent folder:**
- Open: https://mail.google.com/mail/u/0/#sent
- Look for reply to your test email

**Check Done folder:**
```bash
ls -la AI_Employee_Vault/Done/$(date +%Y-%m-%d)/
```

---

## 🐛 Troubleshooting Commands

### Gmail Watcher Not Detecting Emails

```bash
# 1. Check if emails are marked important
# In Gmail, star the email

# 2. Check if emails are unread
# Don't open the email in Gmail

# 3. Test with different query
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --once
# Edit config.json to use query: "is:unread"

# 4. Check processed cache
cat AI_Employee_Vault/.gmail_processed.cache

# 5. Clear cache (to reprocess all)
rm AI_Employee_Vault/.gmail_processed.cache
```

---

### Authentication Issues

```bash
# Re-authenticate
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --auth

# Check token file
cat skills/mcp-servers/email-mcp/token.json

# Check credentials
cat credentials.json
```

---

### View Logs

```bash
# Gmail watcher logs (if running with redirect)
tail -f /tmp/ai-employee/gmail_watcher.log

# Orchestrator logs
tail -f /tmp/ai-employee/orchestrator.log

# All logs
tail -f /tmp/ai-employee/*.log
```

---

### Check Process Status

```bash
# If using PM2
pm2 status
pm2 logs ai-gmail-watcher

# If using cron
ps aux | grep gmail_watcher

# Check cron jobs
crontab -l
```

---

## 📊 Complete Test Script

Run this complete test:

```bash
#!/bin/bash
# test-gmail-watcher.sh

echo "📧 Gmail Watcher - Complete Test"
echo "================================"
echo ""

cd /mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)

echo "Step 1: Checking configuration..."
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --check-config
echo ""

echo "Step 2: Running single check..."
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --once
echo ""

echo "Step 3: Checking Needs_Action folder..."
ls -la AI_Employee_Vault/Needs_Action/ | head -10
echo ""

echo "Step 4: Checking processed cache..."
wc -l AI_Employee_Vault/.gmail_processed.cache
echo ""

echo "✅ Test complete!"
echo ""
echo "📋 Next: Send a test email and run again"
```

---

## 🎯 Quick Verification Commands

```bash
# 1. Is Gmail Watcher working?
python3 skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --once && echo "✅ Working"

# 2. Are files being created?
ls AI_Employee_Vault/Needs_Action/EMAIL_*.md 2>/dev/null && echo "✅ Files created"

# 3. Is orchestrator processing?
ls AI_Employee_Vault/Pending_Approval/*.md 2>/dev/null && echo "✅ Orchestrator working"

# 4. Are emails being sent?
ls AI_Employee_Vault/Done/$(date +%Y-%m-%d)/EMAIL_*.md 2>/dev/null && echo "✅ Emails sent"

# 5. Complete workflow test
./verify-silver-tier.sh | grep -A 5 "Gmail Watcher"
```

---

## 📋 Test Checklist

- [ ] Gmail credentials configured
- [ ] OAuth token obtained
- [ ] Test email sent (and starred!)
- [ ] Gmail Watcher detects email
- [ ] EMAIL_*.md file created in Needs_Action
- [ ] Orchestrator creates PLAN_*.md
- [ ] Files moved to Pending_Approval
- [ ] You approve (move to Approved)
- [ ] Reply email sent automatically
- [ ] Files moved to Done
- [ ] Reply visible in Gmail Sent folder

---

## 🎉 Success Indicators

```
✅ Configuration OK
✅ Found 1 new item(s)
✅ Created: EMAIL_Test_*.md
✅ Plan created successfully
✅ Moved to Pending_Approval
✅ Email sent successfully
✅ Check Gmail Sent folder - reply is there!
```

---

**Your Gmail Watcher is working correctly!** 🚀
