---
name: linkedin-watcher
description: |
  Monitor LinkedIn for notifications, messages, and engagement.
  Creates action files for important notifications requiring response.
  
  Use when:
  - You want to monitor LinkedIn activity
  - Important messages need response
  - Track engagement on posts
  
  NOT when:
  - Only posting content (use post-linkedin skill)
  - LinkedIn is not accessible
---

# LinkedIn Watcher Skill

Monitor LinkedIn for notifications and messages.

## Usage

```bash
# Run watcher continuously
python skills/watchers/linkedin-watcher/linkedin_watcher.py VAULT_PATH --interval 300

# Run once
python skills/watchers/linkedin-watcher/linkedin_watcher.py VAULT_PATH --once

# Setup LinkedIn session
python skills/watchers/linkedin-watcher/linkedin_watcher.py VAULT_PATH --setup-session
```

## Setup

### 1. Install Dependencies

```bash
# Install playwright
pip install playwright --break-system-packages

# Install browser and system dependencies
playwright install chromium
playwright install-deps chromium
```

### 2. First-Time Session Setup

**Requires: Desktop environment with display (X11/Wayland)**

```bash
# This will open a browser - log in to LinkedIn
python skills/watchers/linkedin-watcher/linkedin_watcher.py VAULT_PATH --setup-session
```

**What happens:**
1. Chromium browser opens
2. LinkedIn login page appears
3. **You log in manually**
4. Once you see your feed, the session is saved
5. Close the browser

### 3. Headless/WSL Setup

If you're running in WSL or a headless environment:

**Option A: Use X11 Forwarding (SSH)**
```bash
ssh -X user@host
python skills/watchers/linkedin-watcher/linkedin_watcher.py VAULT_PATH --setup-session
```

**Option B: Use a Desktop Session**
- Run the setup command directly on a machine with a display
- Copy the `linkedin_session/` folder to your server

**Option C: Use GitHub OAuth (Alternative)**
- Consider using LinkedIn's official API instead
- Requires LinkedIn developer account

## Configuration

```json
{
  "check_interval": 300,
  "keywords": ["hiring", "opportunity", "project", "collaboration"],
  "notification_types": ["messages", "comments", "connection_requests"]
}
```

## Action File Format

```markdown
---
type: linkedin
from: John Doe
notification_type: message
received: 2026-02-27T10:30:00Z
priority: normal
---

# LinkedIn: Message from John Doe

## Content
Hi, I saw your profile and wanted to discuss a potential opportunity...

## Suggested Actions
- [ ] Review sender profile
- [ ] Draft professional reply
- [ ] Respond via LinkedIn
```
