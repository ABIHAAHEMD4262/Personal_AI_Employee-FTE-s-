---
name: linkedin-content-writer
description: |
  Generate engaging LinkedIn posts using proven content frameworks.
  Creates viral-worthy content with hooks, value propositions, and CTAs.
  
  Use when:
  - You need to create engaging LinkedIn content
  - Want to follow proven post frameworks
  - Need variety in post styles
  
  NOT when:
  - You already have crafted content
  - Posting simple updates
---

# LinkedIn Content Writer Skill

Generate high-engagement LinkedIn posts using proven frameworks.

## Usage

```bash
# Generate post from topic
python skills/utils/linkedin-content-writer/content_writer.py VAULT \
  --topic "AI automation" --style "thought-leadership"

# Generate multiple variations
python skills/utils/linkedin-content-writer/content_writer.py VAULT \
  --topic "Personal AI Employee" --style "all" --count 3

# Generate and auto-post
python skills/utils/linkedin-content-writer/content_writer.py VAULT \
  --topic "Project launch" --style "announcement" --post
```

## Post Frameworks

### 1. Thought Leadership
```
💡 Controversial/Insightful Statement

Supporting argument 1
Supporting argument 2
Supporting argument 3

Call to action / Question for engagement

#hashtags
```

### 2. Story/ Journey
```
📖 Personal story hook

The challenge I faced
What I tried
The breakthrough moment
The result

Lesson learned + CTA

#hashtags
```

### 3. List/Educational
```
📋 Number + Benefit statement

Point 1 with explanation
Point 2 with explanation
Point 3 with explanation

Summary + CTA

#hashtags
```

### 4. Announcement
```
🚀 Exciting news hook

What we built/launched
Why it matters
Key features/benefits

CTA (link in comments)

#hashtags
```

### 5. Before/After
```
⚡ Transformation hook

BEFORE: The problem
AFTER: The solution

How we did it (brief)

CTA

#hashtags
```

## Examples

### Thought Leadership Example
```bash
python skills/utils/linkedin-content-writer/content_writer.py VAULT \
  --topic "AI is changing work" --style "thought-leadership"
```

**Output:**
```
💡 Hot take: AI won't replace your job. 
But someone using AI will.

I've spent the last month building an autonomous AI employee.
Here's what I learned:

1️⃣ AI excels at repetitive tasks (email triage, data entry)
2️⃣ Human judgment is still irreplaceable (strategy, relationships)
3️⃣ The winners will be those who combine both

The question isn't "Will AI take my job?"
It's "How can I use AI to be 10x more effective?"

What's your take? Are you embracing AI or resisting it?

#AI #FutureOfWork #Automation #Productivity
```

### Announcement Example
```bash
python skills/utils/linkedin-content-writer/content_writer.py VAULT \
  --topic "Personal AI Employee launch" --style "announcement"
```

**Output:**
```
🚀 After weeks of building, I'm excited to share...

My Personal AI Employee is LIVE!

What it does:
✅ Monitors Gmail 24/7
✅ Creates action plans automatically
✅ Manages approvals with human-in-the-loop
✅ Posts to LinkedIn autonomously

Why I built it:
- Email overload was killing my productivity
- I wanted to test autonomous agents
- The future is AI + human collaboration

Tech stack:
- Python + Playwright for automation
- MCP servers for external actions
- Obsidian for knowledge management

Demo video in comments 👇

#AI #Automation #PersonalAI #Innovation
```

## Configuration

Edit `config.json`:

```json
{
  "default_style": "thought-leadership",
  "include_emojis": true,
  "include_hashtags": true,
  "max_length": 1300,
  "cta_options": [
    "What's your take?",
    "Thoughts?",
    "Let me know in the comments",
    "Share if you agree"
  ]
}
```

## Integration

Works with:
- `post-linkedin` - Auto-post generated content
- `approval-workflow` - Review before posting
- `schedule-task` - Schedule posts
