# Personal AI Employee - Bronze Tier

> **Tagline:** Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

This is the **Bronze Tier** implementation of the Personal AI Employee hackathon - a foundational autonomous agent that processes files dropped into your Obsidian vault.

---

## 📦 What's Included

| Component | Description | Location |
|-----------|-------------|----------|
| **Obsidian Vault** | Dashboard, Handbook, Goals | `AI_Employee_Vault/` |
| **File Watcher** | Monitors /Inbox for new files | `watchers/filesystem_watcher.py` |
| **Process Drop Skill** | Processes files in /Needs_Action | `skills/process-drop/` |
| **Base Watcher** | Template for future watchers | `watchers/base_watcher.py` |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Obsidian (optional, for viewing vault)
- Qwen Code access

### Setup (5 minutes)

1. **Verify Python version:**
   ```bash
   python --version  # Should be 3.13+
   ```

2. **Start the File Watcher:**
   ```bash
   # Terminal 1 - Run watcher in background
   python watchers/filesystem_watcher.py AI_Employee_Vault --interval 30
   ```

3. **Drop a file to test:**
   ```bash
   # Copy any file to the Inbox
   cp some_document.pdf AI_Employee_Vault/Inbox/
   
   # Wait 30 seconds - watcher will move it to Needs_Action
   ```

4. **Process the file:**
   ```bash
   # Terminal 2 - Run the process drop skill
   python skills/process-drop/process_drop.py AI_Employee_Vault
   ```

5. **Check results:**
   - Open `AI_Employee_Vault/Dashboard.md` in Obsidian
   - Check `AI_Employee_Vault/Done/` for processed files

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
│   ├── Done/                   # Completed items
│   ├── Plans/                  # Generated plans
│   ├── Approved/               # Approved actions
│   ├── Rejected/               # Rejected actions
│   └── Briefings/              # CEO briefings
│
├── watchers/
│   ├── base_watcher.py         # Base class for all watchers
│   └── filesystem_watcher.py   # File drop watcher (Bronze)
│
└── skills/
    └── process-drop/
        ├── SKILL.md            # Skill documentation
        └── process_drop.py     # Processing logic
```

---

## 🔧 Usage

### File Watcher Options

```bash
# Continuous monitoring (default)
python watchers/filesystem_watcher.py AI_Employee_Vault

# Custom check interval (every 60 seconds)
python watchers/filesystem_watcher.py AI_Employee_Vault --interval 60

# Run once (for cron jobs)
python watchers/filesystem_watcher.py AI_Employee_Vault --once
```

### Process Drop Skill Options

```bash
# Process all pending files
python skills/process-drop/process_drop.py AI_Employee_Vault

# Verbose output
python skills/process-drop/process_drop.py AI_Employee_Vault --verbose

# Dry run (preview without changes)
python skills/process-drop/process_drop.py AI_Employee_Vault --dry-run
```

### With Qwen Code

```bash
# Let Qwen process files
qwen "Process all files in AI_Employee_Vault/Needs_Action"

# Ask Qwen to summarize
qwen "Read AI_Employee_Vault/Done and create a summary"
```

---

## 📋 Bronze Tier Checklist

- [x] **Obsidian vault** with Dashboard.md and Company_Handbook.md
- [x] **One working Watcher** script (filesystem_watcher.py)
- [x] **Qwen Code** reading/writing to vault
- [x] **Basic folder structure**: /Inbox, /Needs_Action, /Done
- [x] **Agent Skill** for file processing (process_drop)

---

## 🔄 Workflow

```
1. Drop file → AI_Employee_Vault/Inbox/
                    ↓
2. filesystem_watcher.py detects (every 30s)
                    ↓
3. Moves to → AI_Employee_Vault/Needs_Action/
                    ↓
4. process_drop skill processes
                    ↓
5. Moves to → AI_Employee_Vault/Done/YYYY-MM-DD/
                    ↓
6. Updates → Dashboard.md
```

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [Dashboard.md](./AI_Employee_Vault/Dashboard.md) | Real-time status overview |
| [Company_Handbook.md](./AI_Employee_Vault/Company_Handbook.md) | Rules of engagement |
| [Business_Goals.md](./AI_Employee_Vault/Business_Goals.md) | Objectives and metrics |
| [SKILL.md](./skills/process-drop/SKILL.md) | Process drop skill docs |

---

## 🧪 Testing

### Test the Watcher

```bash
# Run watcher once
python watchers/filesystem_watcher.py AI_Employee_Vault --once

# Drop a test file
echo "Test content" > AI_Employee_Vault/Inbox/test.txt

# Run watcher again
python watchers/filesystem_watcher.py AI_Employee_Vault --once

# Check Needs_Action folder
ls AI_Employee_Vault/Needs_Action/
```

### Test the Skill

```bash
# Dry run first
python skills/process-drop/process_drop.py AI_Employee_Vault --dry-run

# Then process for real
python skills/process-drop/process_drop.py AI_Employee_Vault

# Check Done folder
ls AI_Employee_Vault/Done/
```

---

## ⏭️ Next Steps (Silver Tier)

After mastering Bronze, consider adding:

1. **Gmail Watcher** - Monitor email for important messages
2. **MCP Server** - Enable external actions (send emails, etc.)
3. **Approval Workflow** - Human-in-the-loop for sensitive actions
4. **Scheduled Tasks** - Cron jobs for regular processing
5. **Plan.md Generation** - Qwen creates action plans

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Watcher not detecting files | Check interval, ensure file not hidden (no `.` prefix) |
| Skill reports "No pending files" | Ensure watcher moved files to Needs_Action |
| Dashboard not updating | Check file permissions, ensure vault path is correct |
| Python version error | Upgrade to Python 3.13+ |

---

## 📚 Resources

- [Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md) - Full architecture guide
- [Obsidian Download](https://obsidian.md/download) - Knowledge base app
- [Qwen Code](https://github.com/QwenLM/Qwen) - AI reasoning engine
- [Wednesday Research Meetings](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1) - Every Wednesday 10:00 PM

---

*Built for the Personal AI Employee Hackathon 0 - Building Autonomous FTEs in 2026*
