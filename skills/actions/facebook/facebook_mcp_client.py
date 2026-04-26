#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook MCP Client - Communicates with Facebook MCP Server

Usage:
    python facebook_mcp_client.py create_post --message "Hello" --link "https://example.com"
    python facebook_mcp_client.py get_posts --limit 5
    python facebook_mcp_client.py get_insights
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '../../mcp-servers/facebook-mcp/.env'
load_dotenv(env_path)

FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID')


class FacebookClient:
    """Direct Facebook Graph API client."""
    
    def __init__(self, access_token, page_id, instagram_account_id=None):
        self.access_token = access_token
        self.page_id = page_id
        self.instagram_account_id = instagram_account_id
        self.base_url = 'https://graph.facebook.com/v18.0'
    
    def get(self, url, params=None):
        """Make GET request."""
        full_url = f"{self.base_url}{url}"
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        response = requests.get(full_url, params=params)
        result = response.json()
        
        if 'error' in result:
            raise Exception(f"Facebook API Error: {result['error']['message']}")
        
        return result
    
    def post(self, url, data=None):
        """Make POST request."""
        full_url = f"{self.base_url}{url}"
        if data is None:
            data = {}
        data['access_token'] = self.access_token
        
        response = requests.post(full_url, json=data)
        result = response.json()
        
        if 'error' in result:
            raise Exception(f"Facebook API Error: {result['error']['message']}")
        
        return result
    
    def create_post(self, message, link=None, photo_url=None):
        """Create Facebook post."""
        data = {'message': message}
        if link:
            data['link'] = link
        if photo_url:
            data['photo'] = photo_url
        
        return self.post(f'/{self.page_id}/feed', data)
    
    def get_posts(self, limit=10):
        """Get page posts."""
        return self.get(f'/{self.page_id}/posts', {'limit': limit})
    
    def get_insights(self, metrics=None, period='week'):
        """Get page insights."""
        if metrics is None:
            metrics = ['page_impressions', 'page_engaged_users', 'page_post_engagements']
        
        return self.get(f'/{self.page_id}/insights', {
            'metric': ','.join(metrics),
            'period': period
        })
    
    def get_comments(self, post_id, limit=10):
        """Get post comments."""
        return self.get(f'/{post_id}/comments', {'limit': limit})
    
    def create_comment(self, post_id, message):
        """Create comment on post."""
        return self.post(f'/{post_id}/comments', {'message': message})
    
    def get_instagram_media(self, limit=10):
        """Get Instagram media."""
        if not self.instagram_account_id:
            raise Exception("Instagram Account ID not configured")
        
        return self.get(f'/{self.instagram_account_id}/media', {
            'limit': limit,
            'fields': 'id,caption,media_type,media_url,permalink,timestamp'
        })
    
    def get_instagram_insights(self, metrics=None):
        """Get Instagram insights."""
        if not self.instagram_account_id:
            raise Exception("Instagram Account ID not configured")
        
        if metrics is None:
            metrics = ['impressions', 'reach', 'profile_views']
        
        return self.get(f'/{self.instagram_account_id}/insights', {
            'metric': ','.join(metrics)
        })


def main():
    parser = argparse.ArgumentParser(description='Facebook MCP Client')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create post command
    create_parser = subparsers.add_parser('create_post', help='Create Facebook post')
    create_parser.add_argument('--message', type=str, required=True)
    create_parser.add_argument('--link', type=str, default=None)
    create_parser.add_argument('--photo-url', type=str, default=None)
    
    # Get posts command
    posts_parser = subparsers.add_parser('get_posts', help='Get posts')
    posts_parser.add_argument('--limit', type=int, default=10)
    
    # Get insights command
    insights_parser = subparsers.add_parser('get_insights', help='Get insights')
    insights_parser.add_argument('--metrics', type=str, nargs='+', default=None)
    insights_parser.add_argument('--period', type=str, default='week')
    
    # Get comments command
    comments_parser = subparsers.add_parser('get_comments', help='Get comments')
    comments_parser.add_argument('--post-id', type=str, required=True)
    comments_parser.add_argument('--limit', type=int, default=10)
    
    # Create comment command
    comment_parser = subparsers.add_parser('create_comment', help='Create comment')
    comment_parser.add_argument('--post-id', type=str, required=True)
    comment_parser.add_argument('--message', type=str, required=True)
    
    # Generate summary command
    summary_parser = subparsers.add_parser('generate_summary', help='Generate summary')
    summary_parser.add_argument('--days', type=int, default=7)
    summary_parser.add_argument('--include-instagram', action='store_true')
    
    args = parser.parse_args()
    
    # Check credentials
    if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        print("❌ Missing Facebook credentials. Please set up .env file.")
        sys.exit(1)
    
    client = FacebookClient(
        FACEBOOK_ACCESS_TOKEN,
        FACEBOOK_PAGE_ID,
        INSTAGRAM_ACCOUNT_ID
    )
    
    try:
        if args.command == 'create_post':
            result = client.create_post(args.message, args.link, args.photo_url)
            print(f"✅ Post created: {result['id']}")
        
        elif args.command == 'get_posts':
            result = client.get_posts(args.limit)
            posts = result.get('data', [])
            print(f"📘 Recent Posts ({len(posts)} found):\n")
            for i, post in enumerate(posts[:5], 1):
                message = post.get('message', '[No text]')[:100]
                print(f"{i}. {message}...")
                print(f"   Created: {post.get('created_time', 'Unknown')}")
                print(f"   ID: {post['id']}\n")
        
        elif args.command == 'get_insights':
            result = client.get_insights(args.metrics, args.period)
            insights = result.get('data', [])
            print(f"📊 Page Insights ({args.period}):\n")
            for insight in insights:
                value = insight.get('values', [{}])[0].get('value', 0)
                print(f"• {insight['title']}: {value:,}")
        
        elif args.command == 'get_comments':
            result = client.get_comments(args.post_id, args.limit)
            comments = result.get('data', [])
            print(f"💬 Comments ({len(comments)} found):\n")
            for i, comment in enumerate(comments[:5], 1):
                print(f"{i}. {comment.get('from', {}).get('name', 'Unknown')}: {comment.get('message', '')}")
        
        elif args.command == 'create_comment':
            result = client.create_comment(args.post_id, args.message)
            print(f"✅ Comment posted: {result['id']}")
        
        elif args.command == 'generate_summary':
            # Generate comprehensive summary
            print(f"📊 Social Media Summary (Last {args.days} days)\n")
            print("=" * 50)
            
            # Facebook insights
            insights = client.get_insights()
            print("\n📘 Facebook:")
            for insight in insights.get('data', []):
                value = insight.get('values', [{}])[0].get('value', 0)
                print(f"  • {insight['title']}: {value:,}")
            
            # Instagram insights (if requested and available)
            if args.include_instagram and INSTAGRAM_ACCOUNT_ID:
                print("\n📷 Instagram:")
                ig_insights = client.get_instagram_insights()
                for insight in ig_insights.get('data', []):
                    value = insight.get('values', [{}])[0].get('value', 0)
                    print(f"  • {insight['title']}: {value:,}")
            
            print("\n" + "=" * 50)
            print(f"Generated: {datetime.now().isoformat()}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
