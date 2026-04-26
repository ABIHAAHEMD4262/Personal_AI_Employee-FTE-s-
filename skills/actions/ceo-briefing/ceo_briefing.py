#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO Briefing Generator - Gold Tier AI Employee

Generates comprehensive weekly CEO briefing including:
- Financial summary from Odoo
- Social media performance (Facebook/Instagram)
- Task completion analysis
- Bottleneck identification
- Proactive suggestions

Usage:
    python ceo_briefing.py /path/to/vault --period weekly
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


def parse_args():
    parser = argparse.ArgumentParser(
        description='Generate CEO Briefing'
    )
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--period', type=str, default='weekly',
                        choices=['daily', 'weekly', 'monthly'],
                        help='Briefing period')
    parser.add_argument('--days', type=int, default=None,
                        help='Override period days')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file path')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    return parser.parse_args()


def load_credentials():
    """Load all required credentials."""
    env_paths = [
        Path(__file__).parent / '../../mcp-servers/odoo-mcp/.env',
        Path(__file__).parent / '../../mcp-servers/facebook-mcp/.env',
        Path(__file__).parent / '.env',
        Path.home() / '.env',
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
    else:
        load_dotenv()
    
    return {
        'odoo': {
            'url': os.getenv('ODOO_URL', 'http://localhost:8069'),
            'database': os.getenv('ODOO_DATABASE'),
            'api_key': os.getenv('ODOO_API_KEY'),
            'user_id': os.getenv('ODOO_USER_ID'),
        },
        'facebook': {
            'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN'),
            'page_id': os.getenv('FACEBOOK_PAGE_ID'),
            'instagram_account_id': os.getenv('INSTAGRAM_ACCOUNT_ID'),
        }
    }


class OdooAnalyzer:
    """Analyze Odoo accounting data."""
    
    def __init__(self, config):
        self.base_url = f"{config['url']}/jsonrpc"
        self.db = config['database']
        self.api_key = config['api_key']
        self.user_id = int(config['user_id']) if config.get('user_id') else None
    
    def call(self, model, method, args=None, kwargs=None):
        """Execute KW method."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.db,
                    self.user_id,
                    self.api_key,
                    model,
                    method,
                    args or [],
                    kwargs or {}
                ]
            },
            "id": 1
        }
        
        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            result = response.json()
            
            if result.get('error'):
                return None
            
            return result.get('result')
        except Exception as e:
            return None
    
    def get_financial_summary(self, days=30) -> Dict[str, Any]:
        """Get financial summary for period."""
        today = datetime.now()
        start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # Get invoices
        invoices = self.call('account.move', 'search_read', [
            [
                ['move_type', 'in', ['out_invoice', 'in_invoice']],
                ['state', '=', 'posted'],
                ['invoice_date', '>=', start_date]
            ],
            ['id', 'move_type', 'amount_total', 'amount_residual', 'partner_id', 'invoice_date', 'payment_state']
        ], {'limit': 100})
        
        if not invoices:
            invoices = []
        
        # Calculate metrics
        revenue = sum(
            inv.get('amount_total', 0) 
            for inv in invoices 
            if inv.get('move_type') == 'out_invoice'
        )
        
        expenses = sum(
            inv.get('amount_total', 0) 
            for inv in invoices 
            if inv.get('move_type') == 'in_invoice'
        )
        
        profit = revenue - expenses
        
        unpaid = sum(
            inv.get('amount_residual', 0) 
            for inv in invoices 
            if inv.get('move_type') == 'out_invoice' and inv.get('payment_state') != 'paid'
        )
        
        return {
            'revenue': revenue,
            'expenses': expenses,
            'profit': profit,
            'profit_margin': (profit / revenue * 100) if revenue > 0 else 0,
            'unpaid_invoices': unpaid,
            'total_invoices': len(invoices),
            'customer_invoices': len([i for i in invoices if i.get('move_type') == 'out_invoice']),
            'vendor_bills': len([i for i in invoices if i.get('move_type') == 'in_invoice']),
        }
    
    def get_receivables(self, limit=10) -> List[Dict]:
        """Get outstanding receivables."""
        invoices = self.call('account.move', 'search_read', [
            [
                ['move_type', '=', 'out_invoice'],
                ['state', '=', 'posted'],
                ['payment_state', '!=', 'paid']
            ],
            ['id', 'name', 'partner_id', 'amount_total', 'amount_residual', 'invoice_date_due']
        ], {
            'limit': limit,
            'order': 'invoice_date_due ASC'
        })
        
        return invoices or []
    
    def get_top_customers(self, days=30, limit=5) -> List[Dict]:
        """Get top customers by revenue."""
        today = datetime.now()
        start_date = (today - timedelta(days=days)).strftime('%Y-%m-%d')
        
        invoices = self.call('account.move', 'search_read', [
            [
                ['move_type', '=', 'out_invoice'],
                ['state', '=', 'posted'],
                ['invoice_date', '>=', start_date],
                ['payment_state', '=', 'paid']
            ],
            ['partner_id', 'amount_total']
        ], {'limit': 100})
        
        if not invoices:
            return []
        
        # Aggregate by customer
        customer_revenue = {}
        for inv in invoices:
            partner = inv.get('partner_id')
            if partner:
                customer_id = partner[0]
                customer_name = partner[1]
                if customer_id not in customer_revenue:
                    customer_revenue[customer_id] = {'name': customer_name, 'revenue': 0}
                customer_revenue[customer_id]['revenue'] += inv.get('amount_total', 0)
        
        # Sort and return top
        top_customers = sorted(
            customer_revenue.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )[:limit]
        
        return top_customers


class FacebookAnalyzer:
    """Analyze Facebook/Instagram data."""
    
    def __init__(self, config):
        self.access_token = config['access_token']
        self.page_id = config['page_id']
        self.instagram_account_id = config.get('instagram_account_id')
        self.base_url = 'https://graph.facebook.com/v18.0'
    
    def get(self, url, params=None):
        """Make GET request."""
        full_url = f"{self.base_url}{url}"
        if params is None:
            params = {}
        params['access_token'] = self.access_token
        
        try:
            response = requests.get(full_url, params=params, timeout=10)
            return response.json()
        except:
            return {'data': []}
    
    def get_insights(self) -> Dict[str, Any]:
        """Get Facebook page insights."""
        metrics = [
            'page_impressions',
            'page_engaged_users',
            'page_post_engagements',
            'page_fans',
        ]
        
        result = self.get(f'/{self.page_id}/insights', {
            'metric': ','.join(metrics),
            'period': 'week'
        })
        
        insights = {}
        for item in result.get('data', []):
            value = item.get('values', [{}])[0].get('value', 0)
            insights[item['name']] = value
        
        return insights
    
    def get_instagram_insights(self) -> Dict[str, Any]:
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


class CEOBriefingGenerator:
    """Generate comprehensive CEO briefing."""
    
    def __init__(self, vault_path: str, credentials: Dict):
        self.vault_path = Path(vault_path)
        self.credentials = credentials
        
        self.odoo = OdooAnalyzer(credentials.get('odoo', {})) if credentials.get('odoo', {}).get('api_key') else None
        self.facebook = FacebookAnalyzer(credentials.get('facebook', {})) if credentials.get('facebook', {}).get('access_token') else None
    
    def get_period_days(self, period: str) -> int:
        """Convert period to days."""
        return {
            'daily': 1,
            'weekly': 7,
            'monthly': 30
        }.get(period, 7)
    
    def analyze_tasks(self, days: int) -> Dict[str, Any]:
        """Analyze task completion from vault."""
        done_folder = self.vault_path / 'Done'
        needs_action = self.vault_path / 'Needs_Action'
        pending = self.vault_path / 'Pending_Approval'
        
        # Count completed tasks
        completed = 0
        if done_folder.exists():
            today = datetime.now()
            start_date = today - timedelta(days=days)
            
            for item in done_folder.rglob('*.md'):
                try:
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime >= start_date:
                        completed += 1
                except:
                    pass
        
        # Count pending items
        pending_count = len(list(pending.glob('*.md'))) if pending.exists() else 0
        needs_action_count = len(list(needs_action.glob('*.md'))) if needs_action.exists() else 0
        
        return {
            'completed': completed,
            'pending_approval': pending_count,
            'needs_action': needs_action_count,
            'completion_rate': f"{completed / max(days, 1):.1f} per day"
        }
    
    def generate_bottlenecks(self, financial: Dict, tasks: Dict, social: Dict) -> List[str]:
        """Identify bottlenecks and issues."""
        bottlenecks = []
        
        # Financial bottlenecks
        if financial:
            if financial.get('unpaid_invoices', 0) > financial.get('revenue', 1) * 0.3:
                bottlenecks.append("⚠️ High outstanding receivables (>30% of revenue)")
            
            if financial.get('profit_margin', 100) < 20:
                bottlenecks.append("⚠️ Low profit margin (<20%)")
        
        # Task bottlenecks
        if tasks.get('pending_approval', 0) > 10:
            bottlenecks.append("⚠️ High pending approvals (>10 items)")
        
        if tasks.get('needs_action', 0) > 20:
            bottlenecks.append("⚠️ Large needs_action queue (>20 items)")
        
        # Social bottlenecks
        if social and social.get('facebook', {}).get('page_post_engagements', 0) < 100:
            bottlenecks.append("⚠️ Low social media engagement")
        
        return bottlenecks
    
    def generate_suggestions(self, financial: Dict, tasks: Dict, social: Dict) -> List[Dict]:
        """Generate proactive suggestions."""
        suggestions = []
        
        # Financial suggestions
        if financial:
            if financial.get('unpaid_invoices', 0) > 0:
                suggestions.append({
                    'category': 'Finance',
                    'action': 'Follow up on unpaid invoices',
                    'priority': 'high',
                    'details': f"${financial['unpaid_invoices']:,.2f} outstanding"
                })
            
            if financial.get('profit_margin', 100) < 30:
                suggestions.append({
                    'category': 'Finance',
                    'action': 'Review expense structure',
                    'priority': 'medium',
                    'details': f"Current margin: {financial['profit_margin']:.1f}%"
                })
        
        # Task suggestions
        if tasks.get('pending_approval', 0) > 5:
            suggestions.append({
                'category': 'Operations',
                'action': 'Clear approval queue',
                'priority': 'medium',
                'details': f"{tasks['pending_approval']} items awaiting approval"
            })
        
        # Social suggestions
        if social:
            suggestions.append({
                'category': 'Marketing',
                'action': 'Increase social media activity',
                'priority': 'low',
                'details': 'Schedule more posts for next week'
            })
        
        return suggestions
    
    def generate_briefing(self, period: str = 'weekly') -> str:
        """Generate complete CEO briefing."""
        days = self.days = self.get_period_days(period)
        period_label = period.capitalize()
        
        # Gather data
        financial = self.odoo.get_financial_summary(days) if self.odoo else None
        receivables = self.odoo.get_receivables(5) if self.odoo else []
        top_customers = self.odoo.get_top_customers(days) if self.odoo else []
        
        facebook_insights = self.facebook.get_insights() if self.facebook else {}
        instagram_insights = self.facebook.get_instagram_insights() if self.facebook else {}
        
        tasks = self.analyze_tasks(days)
        
        social = {
            'facebook': facebook_insights,
            'instagram': instagram_insights
        }
        
        bottlenecks = self.generate_bottlenecks(financial, tasks, social)
        suggestions = self.generate_suggestions(financial, tasks, social)
        
        # Generate markdown
        briefing = f"""# {period_label} CEO Briefing

---
type: ceo_briefing
period: {period}
generated: {datetime.now().isoformat()}
days_covered: {days}
---

## 📊 Executive Summary

**Period**: Last {days} days ({(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')})

"""
        
        # Financial Section
        if financial:
            briefing += f"""
## 💰 Financial Performance

### Key Metrics
| Metric | Value |
|--------|-------|
| **Revenue** | ${financial['revenue']:,.2f} |
| **Expenses** | ${financial['expenses']:,.2f} |
| **Profit** | ${financial['profit']:,.2f} |
| **Profit Margin** | {financial['profit_margin']:.1f}% |
| **Outstanding** | ${financial['unpaid_invoices']:,.2f} |

### Invoice Summary
- Total Invoices: {financial['total_invoices']}
- Customer Invoices: {financial['customer_invoices']}
- Vendor Bills: {financial['vendor_bills']}

"""
            
            # Top Customers
            if top_customers:
                briefing += "### Top Customers\n\n"
                for i, customer in enumerate(top_customers, 1):
                    briefing += f"{i}. **{customer['name']}**: ${customer['revenue']:,.2f}\n"
                briefing += "\n"
            
            # Outstanding Receivables
            if receivables:
                briefing += "### Outstanding Receivables\n\n"
                for inv in receivables[:5]:
                    partner = inv.get('partner_id', ['Unknown'])[1]
                    briefing += f"- **{inv.get('name')}** ({partner}): ${inv.get('amount_residual', 0):,.2f} (Due: {inv.get('invoice_date_due', 'N/A')})\n"
                briefing += "\n"
        
        # Social Media Section
        if facebook_insights or instagram_insights:
            briefing += "## 📱 Social Media Performance\n\n"
            
            if facebook_insights:
                briefing += f"""### Facebook
| Metric | Value |
|--------|-------|
| **Impressions** | {facebook_insights.get('page_impressions', 0):,} |
| **Engaged Users** | {facebook_insights.get('page_engaged_users', 0):,} |
| **Post Engagements** | {facebook_insights.get('page_post_engagements', 0):,} |
| **Page Likes** | {facebook_insights.get('page_fans', 0):,} |

"""
            
            if instagram_insights:
                briefing += f"""### Instagram
| Metric | Value |
|--------|-------|
| **Impressions** | {instagram_insights.get('impressions', 0):,} |
| **Reach** | {instagram_insights.get('reach', 0):,} |
| **Profile Views** | {instagram_insights.get('profile_views', 0):,} |
| **Followers** | {instagram_insights.get('follower_count', 0):,} |

"""
        
        # Tasks Section
        briefing += f"""## ✅ Task Completion

### Summary
| Metric | Count |
|--------|-------|
| **Completed Tasks** | {tasks['completed']} |
| **Pending Approval** | {tasks['pending_approval']} |
| **Needs Action** | {tasks['needs_action']} |
| **Completion Rate** | {tasks['completion_rate']} |

"""
        
        # Bottlenecks
        if bottlenecks:
            briefing += "## ⚠️ Bottlenecks Identified\n\n"
            for bottleneck in bottlenecks:
                briefing += f"{bottleneck}\n"
            briefing += "\n"
        
        # Suggestions
        if suggestions:
            briefing += "## 💡 Proactive Suggestions\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                briefing += f"""### {i}. {suggestion['action']}
- **Category**: {suggestion['category']}
- **Priority**: {suggestion['priority']}
- **Details**: {suggestion['details']}

"""
        
        # Footer
        briefing += f"""---
*Generated by AI Employee v1.0 (Gold Tier)*
*Next briefing: {(datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')}*
"""
        
        return briefing
    
    def save_briefing(self, briefing: str, output_path: Optional[str] = None) -> Path:
        """Save briefing to file."""
        if output_path:
            path = Path(output_path)
        else:
            briefings_folder = self.vault_path / 'Briefings'
            briefings_folder.mkdir(parents=True, exist_ok=True)
            
            filename = f"CEO_Briefing_{datetime.now().strftime('%Y-%m-%d')}.md"
            path = briefings_folder / filename
        
        path.write_text(briefing)
        return path


def main():
    args = parse_args()
    vault_path = Path(args.vault_path).resolve()
    
    print(f"📊 Generating {args.period} CEO Briefing...")
    
    # Load credentials
    credentials = load_credentials()
    
    # Create generator
    generator = CEOBriefingGenerator(vault_path, credentials)
    
    # Generate briefing
    briefing = generator.generate_briefing(args.period)
    
    # Save
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = None
    
    saved_path = generator.save_briefing(briefing, output_path)
    
    print(f"✅ Briefing saved to: {saved_path}")
    print(f"\n📄 Preview:\n")
    print(briefing[:1000] + "..." if len(briefing) > 1000 else briefing)


if __name__ == "__main__":
    main()
