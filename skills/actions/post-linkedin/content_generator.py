#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Content Generator - Generate business posts to generate sales.

Creates engaging LinkedIn posts about your AI automation services.

Usage:
    python content_generator.py /path/to/vault --topic "AI automation" --generate
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any


class LinkedInContentGenerator:
    """Generate engaging LinkedIn business posts."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.business_goals = self.vault_path / 'Business_Goals.md'
        self.config_path = Path(__file__).parent / 'config.json'
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        default = {
            'hashtags': ['#AIAutomation', '#DigitalTransformation', '#BusinessGrowth', '#AI', '#Automation'],
            'post_templates': self._get_default_templates(),
            'services': [
                'AI Employee Implementation',
                'Business Process Automation',
                'Email Automation Systems',
                'Workflow Optimization',
                'Custom AI Solutions',
            ],
            'pain_points': [
                'spending too much time on repetitive tasks',
                'missing important emails and opportunities',
                'struggling to keep up with customer inquiries',
                'losing leads due to slow response times',
                'manual data entry eating up your day',
            ],
            'benefits': [
                'save 20+ hours per week',
                'never miss an important email again',
                'respond to leads in seconds, not hours',
                'automate 80% of your daily tasks',
                'scale your business without hiring more staff',
            ],
        }

        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return {**default, **json.load(f)}
            except:
                pass
        return default

    def _get_default_templates(self) -> List[str]:
        return [
            # Problem-Agitate-Solution template
            """🚀 Are you {pain_point}?

You're not alone. Most business owners struggle with this daily.

But here's the truth: {agitation}

That's where AI automation comes in. I help businesses like yours {benefit}.

💡 Imagine:
✅ {benefit_detail_1}
✅ {benefit_detail_2}
✅ {benefit_detail_3}

Ready to transform your business? Let's talk!

#AIAutomation #BusinessGrowth #DigitalTransformation""",

            # Success story template
            """📈 Just helped another client {achievement}!

Before working with us:
❌ {before_problem}
❌ {before_time_waste}
❌ {before_frustration}

After implementing our AI Employee system:
✅ {after_benefit}
✅ {after_time_saved}
✅ {after_satisfaction}

The result? {result}

Want similar results for your business? DM me!

#SuccessStory #AIAutomation #BusinessTransformation""",

            # Educational template
            """💡 Did you know? {fact}

Most businesses don't realize that {insight}

Here's what you can automate TODAY:
✅ {automation_1}
✅ {automation_2}
✅ {automation_3}

The best part? {benefit}

Stop wasting time on tasks that AI can handle.

Comment "AUTOMATE" below and I'll send you a free consultation! 👇

#AIEducation #Automation #Productivity""",

            # Question template
            """❓ Quick question for business owners:

How many hours per week do you spend on {task}?

If you're like most of my clients, it's probably 10-20 hours.

Here's the thing: {insight}

What if you could get that time back? {benefit}

I'm offering 3 FREE automation audits this week.

First come, first served. Who's interested? 🙋‍♂️

#BusinessOwner #TimeManagement #AIAutomation""",

            # Behind the scenes template
            """🔧 Behind the scenes of an AI automation project:

Just finished implementing an AI Employee for {client_type}.

The challenge? {challenge}

Our solution:
⚙️ {solution_1}
⚙️ {solution_2}
⚙️ {solution_3}

The result? {result}

This is the power of intelligent automation.

Want to see what's possible for your business? Let's connect!

#BehindTheScenes #AIDevelopment #Automation""",
        ]

    def load_business_info(self) -> Dict[str, Any]:
        """Load business information from Business_Goals.md."""
        if not self.business_goals.exists():
            return {}

        content = self.business_goals.read_text()
        info = {}

        # Extract revenue goals
        if 'Monthly goal:' in content:
            for line in content.split('\n'):
                if 'Monthly goal:' in line:
                    info['revenue_goal'] = line.split(':')[1].strip()
                if 'Current MTD:' in line:
                    info['current_revenue'] = line.split(':')[1].strip()

        # Extract active projects
        projects = []
        in_projects = False
        for line in content.split('\n'):
            if 'Active Projects' in line:
                in_projects = True
                continue
            if in_projects and line.startswith('1.') or line.startswith('2.'):
                projects.append(line.strip())
            if in_projects and line.startswith('---'):
                break

        info['active_projects'] = projects
        return info

    def generate_post(self, topic: str = None, style: str = 'mixed') -> str:
        """
        Generate a LinkedIn post.

        Args:
            topic: Specific topic (optional)
            style: 'problem', 'success', 'educational', 'question', 'behind_scenes', or 'mixed'

        Returns:
            Generated post content
        """
        business_info = self.load_business_info()

        # Select template based on style
        if style == 'mixed' or style not in self.config['post_templates']:
            template = random.choice(self.config['post_templates'])
        else:
            template = self.config['post_templates'][0]  # Default to first

        # Fill in template
        post = template.format(
            pain_point=random.choice(self.config['pain_points']),
            agitation="Every hour spent on manual tasks is an hour lost from growing your business.",
            benefit=random.choice(self.config['benefits']),
            benefit_detail_1="Automated email responses within minutes",
            benefit_detail_2="24/7 customer inquiry handling",
            benefit_detail_3="Zero manual data entry",
            achievement="increase their response rate by 300%",
            before_problem="Overwhelmed with emails",
            before_time_waste="Spending 3 hours daily on admin",
            before_frustration="Missing leads due to slow responses",
            after_benefit="AI handles all email triage",
            after_time_saved="15 hours saved per week",
            after_satisfaction="Never miss an opportunity",
            result="Happier clients and more closed deals",
            fact="80% of businesses waste 10+ hours weekly on tasks AI can automate",
            insight="Your competition is already using AI to move faster",
            automation_1="Email responses and follow-ups",
            automation_2="Lead qualification and nurturing",
            automation_3="Appointment scheduling and reminders",
            task="manual administrative work",
            client_type="a consulting firm",
            challenge="They were drowning in unqualified leads",
            solution_1="AI-powered lead scoring system",
            solution_2="Automated qualification workflow",
            solution_3="Smart calendar booking",
        )

        # Add hashtags
        hashtags = ' '.join(self.config.get('hashtags', []))
        post += f"\n\n{hashtags}"

        return post

    def generate_multiple_posts(self, count: int = 5) -> List[str]:
        """Generate multiple unique posts."""
        posts = []
        styles = ['problem', 'success', 'educational', 'question', 'behind_scenes']

        for i in range(count):
            style = styles[i % len(styles)]
            post = self.generate_post(style=style)
            posts.append(post)

        return posts

    def save_post_to_file(self, content: str, folder: str = 'Pending_Approval') -> Optional[Path]:
        """Save generated post to a file."""
        try:
            now = datetime.now()
            filename = f"LINKEDIN_POST_{now.strftime('%Y%m%d_%H%M%S')}.md"
            filepath = self.vault_path / folder / filename

            file_content = f"""---
type: approval_request
action: social_post
platform: LinkedIn
content: AI Automation Business Post
created: {now.isoformat()}
status: pending
generated_by: linkedin_content_generator
---

# LinkedIn Post Request

## Content
{content}

## Details
- **Platform:** LinkedIn
- **Character Count:** {len(content)}
- **Generated:** {now.strftime('%Y-%m-%d %H:%M:%S')}
- **Hashtags:** Included

## To Approve
Move this file to `/Approved` folder to post automatically.

## To Reject
Move this file to `/Rejected` folder with reason.

---
*Generated by AI Employee Content Generator*
"""
            filepath.write_text(file_content)
            return filepath

        except Exception as e:
            print(f"Error saving post: {e}")
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Content Generator")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--topic", "-t", help="Post topic")
    parser.add_argument("--style", "-s", default='mixed',
                       choices=['problem', 'success', 'educational', 'question', 'behind_scenes', 'mixed'])
    parser.add_argument("--generate", action="store_true", help="Generate and save post")
    parser.add_argument("--count", type=int, default=1, help="Number of posts to generate")
    parser.add_argument("--preview", action="store_true", help="Preview without saving")

    args = parser.parse_args()

    generator = LinkedInContentGenerator(args.vault_path)

    if args.generate or args.preview:
        if args.count > 1:
            posts = generator.generate_multiple_posts(args.count)
            for i, post in enumerate(posts, 1):
                print(f"\n{'='*60}")
                print(f"POST {i}")
                print('='*60)
                print(post)
                print('='*60)
        else:
            post = generator.generate_post(args.topic, args.style)
            print("\n" + "="*60)
            print("GENERATED LINKEDIN POST")
            print("="*60)
            print(post)
            print("="*60)

            if args.generate and not args.preview:
                filepath = generator.save_post_to_file(post)
                if filepath:
                    print(f"\n✅ Post saved to: {filepath}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
