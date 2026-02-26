# Personal AI Employee (Digital FTE) - Project Context

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI employee that manages personal and business affairs 24/7. The architecture is **local-first**, **agent-driven**, and employs **human-in-the-loop** patterns for sensitive actions.

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine and task executor |
| **Memory/GUI** | Obsidian (Markdown vault) | Dashboard, knowledge base, long-term memory |
| **Senses** | Python "Watcher" scripts | Monitor Gmail, WhatsApp, filesystems to trigger AI |
| **Hands** | MCP Servers | External actions (email, browser automation, payments) |
| **Persistence** | Ralph Wiggum Loop | Stop hook pattern for autonomous multi-step tasks |

### Key Concepts

- **Watchers**: Lightweight Python scripts that run continuously, monitoring inputs and creating actionable `.md` files in `/Needs_Action` folder
- **Ralph Wiggum Loop**: A Stop hook pattern that keeps Claude iterating until tasks are complete
- **Human-in-the-Loop**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **CEO Briefing**: Autonomous weekly audit generating revenue reports, bottleneck analysis, and proactive suggestions

## Directory Structure

```
Personal_AI_Employee(FTE's)/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json          # Skill dependencies tracking
├── .qwen/skills/             # Qwen skills directory
│   └── browsing-with-playwright/
│       ├── SKILL.md          # Browser automation skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool reference (22 tools)
│       └── scripts/
│           ├── mcp-client.py      # Universal MCP client (HTTP + stdio)
│           ├── start-server.sh    # Start Playwright MCP server
│           ├── stop-server.sh     # Stop Playwright MCP server
│           └── verify.py          # Server health check
└── .gitattributes            # Git line-ending configuration
```

## Available Skills

### browsing-with-playwright

Browser automation via Playwright MCP server for web scraping, form submission, UI testing, and any browser interaction.

**Server Management:**
```bash
# Start server (keeps browser context alive)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Stop server (closes browser + process)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh

# Verify server is running
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py
```

**Key Tools Available:**
- `browser_navigate` - Navigate to URL
- `browser_snapshot` - Capture accessibility snapshot (preferred over screenshot)
- `browser_click`, `browser_type`, `browser_fill_form` - Element interaction
- `browser_evaluate` - Execute JavaScript
- `browser_run_code` - Run complex Playwright code snippets
- `browser_take_screenshot` - Capture screenshots
- `browser_wait_for` - Wait for text/time conditions

**Usage Pattern:**
```bash
# Call any tool via mcp-client.py
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py \
  call -u http://localhost:8808 \
  -t browser_navigate \
  -p '{"url": "https://example.com"}'
```

## Hackathon Tiers

| Tier | Description | Estimated Time |
|------|-------------|----------------|
| **Bronze** | Foundation: Obsidian vault, 1 Watcher, basic folder structure | 8-12 hours |
| **Silver** | Functional: Multiple Watchers, MCP server, approval workflow | 20-30 hours |
| **Gold** | Autonomous: Full integration, Odoo accounting, social media, Ralph loop | 40+ hours |
| **Platinum** | Production: Cloud deployment, Cloud/Local split, 24/7 operation | 60+ hours |

## Vault Folder Structure (Recommended)

```
Vault/
├── Inbox/                 # Raw incoming items
├── Needs_Action/          # Items requiring Claude's attention
├── In_Progress/<agent>/   # Claimed items (prevents double-work)
├── Pending_Approval/      # Awaiting human approval
├── Approved/              # Approved actions (triggers execution)
├── Rejected/              # Rejected actions
├── Done/                  # Completed tasks
├── Plans/                 # Generated plan.md files
├── Accounting/            # Bank transactions, invoices
├── Briefings/             # CEO briefing reports
└── Business_Goals.md      # Objectives and metrics
```

## Development Notes

- **Python Version**: 3.13+ required for Watcher scripts
- **Node.js**: v24+ LTS for MCP servers
- **Obsidian**: v1.10.6+ for vault management
- **All AI functionality should be implemented as Agent Skills** (per hackathon requirements)

## Wednesday Research Meetings

- **When**: Every Wednesday at 10:00 PM
- **First Meeting**: January 7th, 2026
- **Zoom**: [Link in main hackathon document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- **YouTube**: https://www.youtube.com/@panaversity

## Related Documentation

- **Main Blueprint**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md` (1201 lines) - Comprehensive architecture guide with templates, code examples, and implementation details
- **Playwright Tools**: `.qwen/skills/browsing-with-playwright/references/playwright-tools.md` - Complete MCP tool reference
