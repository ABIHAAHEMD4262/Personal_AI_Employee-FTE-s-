#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Social Media Summary Skill - Gold Tier AI Employee

Generates comprehensive social media summary from Facebook and Instagram
for inclusion in CEO Briefing reports.

Usage:
    python social_media_summary.py /path/to/vault --days 7 --output briefing.md
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate social media summary'
    )
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--days', type=int, default=7,
                        help='Number of days to summarize')
    parser.add_argument('--include-instagram', action='store_true',
                        help='Include Instagram data')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file path (optional)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    return parser.parse_args()


def load_credentials():
    """Load Facebook/Instagram credentials from environment."""
    env_paths = [
        Path(__file__).parent / '../../mcp-servers/facebook-mcp/.env',
        Path(__file__).parent / '.env',
        Path.home() / '.env',
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
    else:
        load_dotenv()  # Load from system environment
    
    return {
        'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN'),
        'page_id': os.getenv('FACEBOOK_PAGE_ID'),
        'instagram_account_id': os.getenv('INSTAGRAM_ACCOUNT_ID'),
    }


class SocialMediaAnalyzer:
    """Analyze Facebook and Instagram data."""
    
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
        
        try:
            response = requests.get(full_url, params=params, timeout=10)
            result = response.json()
            
            if 'error' in result:
                if self.verbose:
                    print(f"⚠️  API Warning: {result['error']['message']}")
                return {'data': []}
            
            return result
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Request Error: {e}")
            return {'data': []}
    
    def get_facebook_insights(self, period='week'):
        """Get Facebook page insights."""
        metrics = [
            'page_impressions',
            'page_engaged_users',
            'page_post_engagements',
            'page_fans',
            'page_views',
        ]
        
        result = self.get(f'/{self.page_id}/insights', {
            'metric': ','.join(metrics),
            'period': period
        })
        
        insights = {}
        for item in result.get('data', []):
            value = item.get('values', [{}])[0].get('value', 0)
            insights[item['name']] = value
        
        return insights
    
    def get_facebook_posts(self, limit=10):
        """Get recent Facebook posts."""
        result = self.get(f'/{self.page_id}/posts', {'limit': limit})
        return result.get('data', [])
    
    def get_instagram_insights(self):
        """Get Instagram insights."""
        if not self.instagram_account_id:
            return {}
        
        metrics = ['impressions', 'reach', 'profile_views', 'follower_count']
        
        result = self.get(f'/{self.instagram_account_id}/insights', {
            'metric': ','.join(metrics)
        })
        
        insights = {}
        for item in result.get('data', []):
            value = item.get('values', [{}])[0].get('value', 0)
            insights[item['name']] = value
        
        return insights
    
    def get_instagram_media(self, limit=10):
        """Get recent Instagram media."""
        if not self.instagram_account_id:
            return []
        
        result = self.get(f'/{self.instagram_account_id}/media', {
            'limit': limit,
            'fields': 'id,caption,media_type,like_count,comments_count'
        })
        
        return result.get('data', [])
    
    def generate_summary(self, days=7, include_instagram=False):
        """Generate comprehensive summary."""
        summary = {
            'period': f"Last {days} days",
            'generated_at': datetime.now().isoformat(),
            'facebook': self.get_facebook_insights(),
            'posts': [],
            'instagram': None,
        }
        
        # Get recent posts
        posts = self.get_facebook_posts(days)
        summary['posts'] = [{
            'id': p.get('id'),
            'message': p.get('message', '')[:100] if p.get('message') else '',
            'created_time': p.get('created_time'),
            'likes': p.get('likes', {}).get('summary', {}).get('total_count', 0),
            'comments': p.get('comments', {}).get('summary', {}).get('total_count', 0),
            'shares': p.get('shares', {}).get('count', 0),
        } for p in posts[:10]]
        
        # Get Instagram data if requested
        if include_instagram and self.instagram_account_id:
            summary['instagram'] = self.get_instagram_insights()
            summary['instagram_media'] = self.get_instagram_media(5)
        
        return summary


def format_summary(summary):
    """Format summary as markdown."""
    lines = [
        "# 📊 Social Media Summary",
        "",
        f"**Period**: {summary['period']}",
        f"**Generated**: {summary['generated_at']}",
        "",
    ]
    
    # Facebook Section
    fb = summary.get('facebook', {})
    if fb:
        lines.extend([
            "## 📘 Facebook",
            "",
            "### Key Metrics",
            "",
            f"- **Impressions**: {fb.get('page_impressions', 0):,}",
            f"- **Engaged Users**: {fb.get('page_engaged_users', 0):,}",
            f"- **Post Engagements**: {fb.get('page_post_engagements', 0):,}",
            f"- **Page Likes**: {fb.get('page_fans', 0):,}",
            f"- **Page Views**: {fb.get('page_views', 0):,}",
            "",
        ])
        
        # Top Posts
        posts = summary.get('posts', [])
        if posts:
            lines.extend([
                "### Recent Posts",
                "",
            ])
            
            for i, post in enumerate(posts[:5], 1):
                lines.append(f"**{i}. {post['id']}**")
                lines.append(f"   - Posted: {post['created_time']}")
                lines.append(f"   - Engagement: 👍 {post['likes']} | 💬 {post['comments']} | 🔄 {post['shares']}")
                if post['message']:
                    lines.append(f"   - Content: {post['message']}...")
                lines.append("")
    
    # Instagram Section
    ig = summary.get('instagram')
    if ig:
        lines.extend([
            "## 📷 Instagram",
            "",
            "### Key Metrics",
            "",
            f"- **Impressions**: {ig.get('impressions', 0):,}",
            f"- **Reach**: {ig.get('reach', 0):,}",
            f"- **Profile Views**: {ig.get('profile_views', 0):,}",
            f"- **Followers**: {ig.get('follower_count', 0):,}",
            "",
        ])
        
        # Recent Media
        media = summary.get('instagram_media', [])
        if media:
            lines.extend([
                "### Recent Media",
                "",
            ])
            
            for i, item in enumerate(media[:3], 1):
                lines.append(f"**{i}. {item['id']}**")
                lines.append(f"   - Type: {item.get('media_type', 'Unknown')}")
                lines.append(f"   - Engagement: ❤️ {item.get('like_count', 0)} | 💬 {item.get('comments_count', 0)}")
                if item.get('caption'):
                    caption = item['caption'][:50] + '...' if len(item.get('caption', '')) > 50 else item['caption']
                    lines.append(f"   - Caption: {caption}")
                lines.append("")
    
    # Analysis
    lines.extend([
        "## 📈 Analysis",
        "",
    ])
    
    # Calculate engagement rate
    total_engagement = fb.get('page_post_engagements', 0)
    total_impressions = fb.get('page_impressions', 0)
    engagement_rate = (total_engagement / total_impressions * 100) if total_impressions > 0 else 0
    
    lines.extend([
        f"- **Facebook Engagement Rate**: {engagement_rate:.2f}%",
        f"- **Total Posts**: {len(summary.get('posts', []))}",
    ])
    
    if ig:
        ig_engagement = sum(m.get('like_count', 0) + m.get('comments_count', 0) for m in summary.get('instagram_media', []))
        ig_posts = len(summary.get('instagram_media', []))
        lines.append(f"- **Instagram Avg Engagement**: {ig_engagement / ig_posts:.1f} per post" if ig_posts > 0 else "- **Instagram Posts**: 0")
    
    lines.append("")
    
    return "\n".join(lines)


def main():
    args = parse_args()
    vault_path = Path(args.vault_path).resolve()
    
    print(f"📊 Generating social media summary...")
    print(f"   Period: Last {args.days} days")
    print(f"   Include Instagram: {args.include_instagram}")
    
    # Load credentials
    creds = load_credentials()
    
    if not creds['access_token'] or not creds['page_id']:
        print("❌ Missing Facebook credentials.")
        print("   Please set FACEBOOK_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env file.")
        sys.exit(1)
    
    # Create analyzer
    analyzer = SocialMediaAnalyzer(
        creds['access_token'],
        creds['page_id'],
        creds['instagram_account_id']
    )
    analyzer.verbose = args.verbose
    
    # Generate summary
    summary = analyzer.generate_summary(
        days=args.days,
        include_instagram=args.include_instagram
    )
    
    # Format as markdown
    markdown = format_summary(summary)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(markdown)
        print(f"✅ Summary saved to: {output_path}")
    else:
        # Save to Briefings folder
        briefings_folder = vault_path / 'Briefings'
        briefings_folder.mkdir(parents=True, exist_ok=True)
        
        filename = f"Social_Media_Summary_{datetime.now().strftime('%Y-%m-%d')}.md"
        output_path = briefings_folder / filename
        output_path.write_text(markdown)
        
        print(f"✅ Summary saved to: {output_path}")
    
    # Print preview
    print("\n" + "=" * 50)
    print(markdown[:500] + "..." if len(markdown) > 500 else markdown)
    print("=" * 50)


if __name__ == "__main__":
    main()
