#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter/X Post Skill - Gold Tier AI Employee

Creates Twitter/X posts with approval workflow.
Uses Playwright for Twitter automation.

Usage:
    python twitter_create_post.py /path/to/vault \
        --message "Exciting news!" \
        --hashtags "#AI #Automation"
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create Twitter/X post'
    )
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--message', type=str, required=True,
                        help='Post message/content (max 280 characters)')
    parser.add_argument('--hashtags', type=str, nargs='+', default=[],
                        help='Hashtags for the post')
    parser.add_argument('--schedule', type=str, default=None,
                        help='Schedule for later (YYYY-MM-DD HH:MM)')
    parser.add_argument('--no-approval', action='store_true',
                        help='Skip approval request')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    return parser.parse_args()


def generate_frontmatter(**kwargs):
    """Generate YAML frontmatter."""
    lines = ["---"]
    for key, value in kwargs.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def create_approval_request(vault_path, message, hashtags=None, schedule=None):
    """Create approval request file for Twitter post."""
    pending_folder = Path(vault_path) / 'Pending_Approval'
    pending_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"TWITTER_POST_{timestamp}.md"

    hashtags_str = ' '.join(hashtags) if hashtags else ''
    full_message = f"{message}\n\n{hashtags_str}" if hashtags else message

    # Check character count
    char_count = len(full_message)
    char_warning = ""
    if char_count > 280:
        char_warning = f"\n\n⚠️ **WARNING**: Message is {char_count} characters (Twitter limit: 280)"

    content = f'''{generate_frontmatter(
        type='approval_request',
        action='twitter_post',
        message=message.replace('\n', '\\n'),
        hashtags=' '.join(hashtags) if hashtags else '',
        character_count=char_count,
        scheduled_time=schedule or '',
        created=datetime.now().isoformat(),
        status='pending'
    )}

# Twitter/X Post Approval Request

## Post Content

{full_message}

## Character Count

{char_count}/280{char_warning}

{'## Scheduled Time' if schedule else ''}
{schedule if schedule else 'Post immediately upon approval'}

## To Approve
Move this file to `/Approved` folder to publish the post.

## To Reject
Move this file to `/Rejected` folder to cancel.
'''

    filepath = pending_folder / filename
    filepath.write_text(content)

    return filepath


def create_scheduled_post(vault_path, message, hashtags=None, schedule=None):
    """Create scheduled post file."""
    scheduled_folder = Path(vault_path) / 'Scheduled'
    scheduled_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"SCHEDULED_TWITTER_{timestamp}.md"

    hashtags_str = ' '.join(hashtags) if hashtags else ''
    full_message = f"{message}\n\n{hashtags_str}" if hashtags else message

    content = f'''{generate_frontmatter(
        type='scheduled_post',
        platform='twitter',
        message=message.replace('\n', '\\n'),
        hashtags=' '.join(hashtags) if hashtags else '',
        scheduled_time=schedule,
        created=datetime.now().isoformat(),
        status='scheduled'
    )}

# Scheduled Twitter/X Post

## Post Content

{full_message}

## Scheduled For

{schedule}

## Execution

This post will be automatically published at the scheduled time.
'''

    filepath = scheduled_folder / filename
    filepath.write_text(content)

    return filepath


def create_action_file(vault_path, message, hashtags=None):
    """Create action file for Claude to process."""
    needs_action = Path(vault_path) / 'Needs_Action'
    needs_action.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"TWITTER_POST_{timestamp}.md"

    hashtags_str = ' '.join(hashtags) if hashtags else ''
    full_message = f"{message}\n\n{hashtags_str}" if hashtags else message

    content = f'''{generate_frontmatter(
        type='twitter_post_request',
        message=message.replace('\n', '\\n'),
        hashtags=' '.join(hashtags) if hashtags else '',
        created=datetime.now().isoformat(),
        status='pending'
    )}

# Twitter/X Post Request

## Post Content

{full_message}

## Next Steps
1. Review content for brand alignment
2. Check character count (max 280)
3. Post to Twitter via Playwright
4. Log result
'''

    filepath = needs_action / filename
    filepath.write_text(content)

    return filepath


def main():
    args = parse_args()
    vault_path = Path(args.vault_path).resolve()

    print(f"🐦 Creating Twitter/X post")
    print(f"   Message: {args.message[:50]}...")
    if args.hashtags:
        print(f"   Hashtags: {' '.join(args.hashtags)}")
    if args.schedule:
        print(f"   Scheduled: {args.schedule}")

    # Check character count
    full_message = f"{args.message}\n\n{' '.join(args.hashtags)}" if args.hashtags else args.message
    char_count = len(full_message)
    if char_count > 280:
        print(f"\n⚠️  WARNING: Message is {char_count} characters (Twitter limit: 280)")
        print("   Please shorten your message.")
        sys.exit(1)

    # Check if scheduling
    if args.schedule:
        filepath = create_scheduled_post(
            vault_path,
            args.message,
            args.hashtags,
            args.schedule
        )
        print(f"✅ Post scheduled: {filepath.name}")
        print(f"   Will publish at: {args.schedule}")
        return

    # Check if approval is required (default: True)
    require_approval = not args.no_approval

    if require_approval:
        # Create approval request
        filepath = create_approval_request(
            vault_path,
            args.message,
            args.hashtags,
            args.schedule
        )
        print(f"✅ Approval request created: {filepath.name}")
        print(f"   Location: {filepath}")
        print(f"\n💡 Move file to /Approved to publish post")
    else:
        # Create action file for direct processing
        filepath = create_action_file(
            vault_path,
            args.message,
            args.hashtags
        )
        print(f"✅ Action file created: {filepath.name}")
        print(f"   Location: {filepath}")
        print(f"\n💡 Claude will process this file and post to Twitter")


if __name__ == "__main__":
    main()
