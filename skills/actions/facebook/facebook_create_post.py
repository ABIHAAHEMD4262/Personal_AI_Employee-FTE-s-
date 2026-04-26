#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Post Skill - Gold Tier AI Employee

Creates Facebook posts with approval workflow.
Requires Facebook MCP server to be running.

Usage:
    python facebook_create_post.py /path/to/vault \
        --message "Exciting news!" \
        --link "https://example.com"
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create Facebook post'
    )
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--message', type=str, required=True,
                        help='Post message/content')
    parser.add_argument('--link', type=str, default=None,
                        help='Optional link to share')
    parser.add_argument('--photo-url', type=str, default=None,
                        help='Optional photo URL')
    parser.add_argument('--hashtags', type=str, nargs='+', default=[],
                        help='Hashtags for the post')
    parser.add_argument('--schedule', type=str, default=None,
                        help='Schedule for later (YYYY-MM-DD HH:MM)')
    parser.add_argument('--create-approval', action='store_true',
                        help='Create approval request (default)')
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


def create_approval_request(vault_path, message, link=None, photo_url=None, hashtags=None, schedule=None):
    """Create approval request file for Facebook post."""
    pending_folder = Path(vault_path) / 'Pending_Approval'
    pending_folder.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"FACEBOOK_POST_{timestamp}.md"
    
    hashtags_str = ' '.join(hashtags) if hashtags else ''
    full_message = f"{message}\n\n{hashtags_str}" if hashtags else message
    
    content = f'''{generate_frontmatter(
        type='approval_request',
        action='facebook_post',
        message=message.replace('\n', '\\n'),
        link=link or '',
        photo_url=photo_url or '',
        hashtags=' '.join(hashtags) if hashtags else '',
        scheduled_time=schedule or '',
        created=datetime.now().isoformat(),
        status='pending'
    )}

# Facebook Post Approval Request

## Post Content

{full_message}

{'## Link' if link else ''}
{link if link else ''}

{'## Photo' if photo_url else ''}
{photo_url if photo_url else ''}

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


def create_scheduled_post(vault_path, message, link=None, photo_url=None, hashtags=None, schedule=None):
    """Create scheduled post file."""
    scheduled_folder = Path(vault_path) / 'Scheduled'
    scheduled_folder.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"SCHEDULED_FACEBOOK_{timestamp}.md"
    
    hashtags_str = ' '.join(hashtags) if hashtags else ''
    full_message = f"{message}\n\n{hashtags_str}" if hashtags else message
    
    content = f'''{generate_frontmatter(
        type='scheduled_post',
        platform='facebook',
        message=message.replace('\n', '\\n'),
        link=link or '',
        photo_url=photo_url or '',
        hashtags=' '.join(hashtags) if hashtags else '',
        scheduled_time=schedule,
        created=datetime.now().isoformat(),
        status='scheduled'
    )}

# Scheduled Facebook Post

## Post Content

{full_message}

{'## Link' if link else ''}
{link if link else ''}

{'## Photo' if photo_url else ''}
{photo_url if photo_url else ''}

## Scheduled For

{schedule}

## Execution

This post will be automatically published at the scheduled time.
'''
    
    filepath = scheduled_folder / filename
    filepath.write_text(content)
    
    return filepath


def post_to_facebook(message, link=None, photo_url=None):
    """Call Facebook MCP server to create post."""
    # This would typically call the MCP server
    # For now, we'll create an action file
    
    mcp_script = Path(__file__).parent / 'facebook_mcp_client.py'
    
    if mcp_script.exists():
        result = subprocess.run([
            'python', str(mcp_script),
            'create_post',
            '--message', message,
            '--link', link or '',
            '--photo-url', photo_url or ''
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    else:
        return False, "MCP client not available"


def create_action_file(vault_path, message, link=None, photo_url=None, hashtags=None):
    """Create action file for Claude to process."""
    needs_action = Path(vault_path) / 'Needs_Action'
    needs_action.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"FACEBOOK_POST_{timestamp}.md"
    
    hashtags_str = ' '.join(hashtags) if hashtags else ''
    full_message = f"{message}\n\n{hashtags_str}" if hashtags else message
    
    content = f'''{generate_frontmatter(
        type='facebook_post_request',
        message=message.replace('\n', '\\n'),
        link=link or '',
        photo_url=photo_url or '',
        hashtags=' '.join(hashtags) if hashtags else '',
        created=datetime.now().isoformat(),
        status='pending'
    )}

# Facebook Post Request

## Post Content

{full_message}

{'## Link' if link else ''}
{link if link else ''}

{'## Photo' if photo_url else ''}
{photo_url if photo_url else ''}

## Next Steps
1. Review content for brand alignment
2. Check links are working
3. Post to Facebook via MCP server
4. Log result
'''
    
    filepath = needs_action / filename
    filepath.write_text(content)
    
    return filepath


def main():
    args = parse_args()
    vault_path = Path(args.vault_path).resolve()
    
    print(f"📘 Creating Facebook post")
    print(f"   Message: {args.message[:50]}...")
    if args.link:
        print(f"   Link: {args.link}")
    if args.photo_url:
        print(f"   Photo: {args.photo_url}")
    if args.hashtags:
        print(f"   Hashtags: {' '.join(args.hashtags)}")
    if args.schedule:
        print(f"   Scheduled: {args.schedule}")
    
    # Check if scheduling
    if args.schedule:
        filepath = create_scheduled_post(
            vault_path,
            args.message,
            args.link,
            args.photo_url,
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
            args.link,
            args.photo_url,
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
            args.link,
            args.photo_url,
            args.hashtags
        )
        print(f"✅ Action file created: {filepath.name}")
        
        # Try to post directly
        success, message = post_to_facebook(
            args.message,
            args.link,
            args.photo_url
        )
        
        if success:
            print(f"✅ Post published to Facebook")
            print(f"   {message}")
        else:
            print(f"⚠️  {message}")
            print(f"   File waiting in: {filepath}")


if __name__ == "__main__":
    main()
