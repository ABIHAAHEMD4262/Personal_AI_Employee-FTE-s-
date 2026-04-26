# 🤖 Complete Email Workflow with Claude Orchestrator

## Your Exact Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    EMAIL WORKFLOW                            │
└─────────────────────────────────────────────────────────────┘

1. Gmail Watcher detects email
   ↓
2. Creates: /Needs_Action/EMAIL_*.md
   ↓
3. CLAUDE ORCHESTRATOR runs (every 30s)
   ↓
4. Creates: /Plans/PLAN_*.md
   ↓
5. Moves to: /Pending_Approval/
   ↓
6. YOU: Review and move to /Approved/
   ↓
7. CLAUDE ORCHESTRATOR detects approval
   ↓
8. Sends email reply automatically
   ↓
9. Moves to: /Done/YYYY-MM-DD/
   ↓
10. Dashboard updated

```

---

## 🚀 Quick Start

### Step 1: Start Gmail Watcher

```bash
cd /mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)

python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --interval 60
```

Keep this running in Terminal 1.

---

### Step 2: Start Claude Orchestrator

```bash
# In Terminal 2
python claude_orchestrator.py AI_Employee_Vault --watch --interval 30
```

Keep this running in Terminal 2.

---

### Step 3: Send Test Email

From any email account:

```
To: abihacodes@gmail.com
Subject: Test Email for AI Employee
Content: Hello, this is a test email.
```

**⭐ IMPORTANT:** Star the email (mark as Important)

---

### Step 4: Watch the Magic

```
Timeline:
├─ 0s:   Email sent
├─ 30s:  Gmail Watcher detects → Creates EMAIL_*.md in Needs_Action
├─ 60s:  Claude Orchestrator runs → Creates PLAN_*.md
├─ 60s:  Moves both to Pending_Approval
├─ 90s:  YOU move to Approved (manual step)
├─ 120s: Claude Orchestrator detects → Sends reply
├─ 120s: Moves to Done
└─ 120s: Dashboard updated
```

---

### Step 5: Approve Email (Manual Step)

When you see notification from Orchestrator:

```bash
# Check Pending_Approval folder
ls AI_Employee_Vault/Pending_Approval/

# Move to Approved (this triggers auto-reply)
mv AI_Employee_Vault/Pending_Approval/EMAIL_*.md \
   AI_Employee_Vault/Approved/

mv AI_Employee_Vault/Pending_Approval/PLAN_*.md \
   AI_Employee_Vault/Approved/
```

---

## 📊 Complete File Flow

```
Gmail
  ↓
/Needs_Action/
  ├── EMAIL_Testing_12345.md     (created by Gmail Watcher)
  ↓
Claude Orchestrator runs
  ↓
/Plans/
  ├── PLAN_email_reply_12345.md  (created by create-plan skill)
  ↓
/Pending_Approval/
  ├── EMAIL_Testing_12345.md     (moved by orchestrator)
  ├── PLAN_email_reply_12345.md  (moved by orchestrator)
  ↓
YOU review and move to /Approved/
  ↓
/Approved/
  ├── EMAIL_Testing_12345.md
  ├── PLAN_email_reply_12345.md
  ↓
Claude Orchestrator detects approval
  ↓
AUTO: Send email reply
  ↓
/Done/2026-03-02/
  ├── EMAIL_Testing_12345.md     (final destination)
  └── PLAN_email_reply_12345.md  (final destination)
```

---

## 🎯 One-Command Test

```bash
# Run complete test
./test-complete-workflow.sh
```

---

## 🔧 Manual Testing Step by Step

```bash
# Terminal 1: Gmail Watcher
python skills/watchers/gmail-watcher/gmail_watcher.py AI_Employee_Vault --interval 60

# Terminal 2: Claude Orchestrator
python claude_orchestrator.py AI_Employee_Vault --watch --interval 30

# Terminal 3: Send test email from your phone/computer
# Then monitor:
watch -n 5 'ls -la AI_Employee_Vault/Needs_Action/'
watch -n 5 'ls -la AI_Employee_Vault/Pending_Approval/'
watch -n 5 'ls -la AI_Employee_Vault/Done/$(date +%Y-%m-%d)/'
```

---

## 📋 What Each Component Does

| Component | Role |
|-----------|------|
| **Gmail Watcher** | Monitors Gmail, creates EMAIL_*.md files |
| **Claude Orchestrator** | Coordinates workflow, creates plans, moves files |
| **Create Plan Skill** | Generates action plan for each email |
| **You (Human)** | Review and approve in Pending_Approval |
| **Auto-Reply** | Sends email when approved |
| **Send Email** | Actually sends the reply via Gmail |

---

## ✅ Checklist

- [ ] Gmail Watcher running
- [ ] Claude Orchestrator running
- [ ] Test email sent and starred
- [ ] EMAIL_*.md appears in Needs_Action
- [ ] PLAN_*.md created in Plans
- [ ] Both files moved to Pending_Approval
- [ ] You move files to Approved
- [ ] Email reply sent automatically
- [ ] Files moved to Done
- [ ] Dashboard updated

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Email not detected | Make sure it's starred/important |
| Plan not created | Check create-plan skill exists |
| Files not moving | Check folder permissions |
| Email not sent | Verify Gmail credentials |
| Orchestrator not running | Check Python path and permissions |

---

## 🎉 Success Indicators

```
✅ Gmail Watcher: "Found 1 new item(s)"
✅ Claude Orchestrator: "Plan created successfully"
✅ Claude Orchestrator: "Moved to Pending_Approval"
✅ YOU: Move files to Approved
✅ Claude Orchestrator: "Email sent successfully"
✅ Claude Orchestrator: "Moved to Done"
✅ Check Gmail Sent folder - reply is there!
```

---

**Your complete automated email workflow is ready!** 🚀
