---
name: post-linkedin
description: |
  Post to LinkedIn for business promotion and lead generation.
  Creates drafts for approval before posting.
  
  Use when:
  - Sharing business updates
  - Posting about completed projects
  - Generating leads through content
  
  NOT when:
  - Posting without approval
  - Sharing sensitive client information
---

# Post LinkedIn Skill

Post to LinkedIn with approval workflow.

## Usage

```bash
# Create post draft
python skills/actions/post-linkedin/post_linkedin.py VAULT \
  --create --content "Excited to announce our new product..."

# Schedule post
python skills/actions/post-linkedin/post_linkedin.py VAULT \
  --schedule --date "2026-03-01T10:00:00" --content "Post content"

# Process approved posts
python skills/actions/post-linkedin/post_linkedin.py VAULT --execute
```

## Workflow

1. Create post content
2. Generate approval request
3. User approves (move to /Approved)
4. Post via LinkedIn API/MCP
5. Log and archive

## Post Templates

### Business Update
```
🚀 Exciting News!

We just completed [project] for [client].
Results: [metric]

#business #growth #success
```

### Lead Generation
```
💡 Are you struggling with [problem]?

Here's how we help:
- Solution 1
- Solution 2

DM us to learn more!

#consulting #solution
```
