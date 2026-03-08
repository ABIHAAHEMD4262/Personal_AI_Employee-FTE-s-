#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Content Writer - Generate engaging posts using proven frameworks.

Usage:
    python content_writer.py /path/to/vault --topic "AI" --style "thought-leadership"
"""

import random
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


class LinkedInContentWriter:
    """Generate engaging LinkedIn posts."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.config_path = Path(__file__).parent / 'config.json'
        self.config = self._load_config()
        
        # Content frameworks
        self.frameworks = {
            'thought-leadership': self._thought_leadership,
            'story': self._story_framework,
            'list': self._list_framework,
            'announcement': self._announcement_framework,
            'before-after': self._before_after_framework,
            'how-to': self._how_to_framework,
        }
        
        # Hashtag sets by topic
        self.hashtag_sets = {
            'ai': ['#AI', '#ArtificialIntelligence', '#MachineLearning', '#Automation', '#Tech'],
            'business': ['#Business', '#Entrepreneurship', '#Startup', '#Growth', '#Leadership'],
            'productivity': ['#Productivity', '#TimeManagement', '#Efficiency', '#WorkLifeBalance'],
            'tech': ['#Technology', '#Innovation', '#DigitalTransformation', '#FutureOfWork'],
            'personal': ['#PersonalBranding', '#Career', '#ProfessionalDevelopment', '#Networking'],
        }
    
    def log(self, message: str, level: str = "INFO"):
        print(f"[{level}] {message}")
    
    def _load_config(self) -> Dict[str, Any]:
        default = {
            'default_style': 'thought-leadership',
            'include_emojis': True,
            'include_hashtags': True,
            'max_length': 1300,
            'cta_options': [
                "What's your take?",
                "Thoughts?",
                "Let me know in the comments 👇",
                "Share if you agree",
                "Tag someone who needs to see this",
            ]
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return {**default, **json.load(f)}
            except:
                pass
        return default
    
    def generate(self, topic: str, style: str = None, context: str = None) -> str:
        """
        Generate a LinkedIn post.
        
        Args:
            topic: Main topic/subject
            style: Post framework style
            context: Additional context/details
            
        Returns:
            Generated post content
        """
        if style is None:
            style = self.config.get('default_style', 'thought-leadership')
        
        if style == 'all':
            # Generate multiple variations
            posts = []
            for framework_style in self.frameworks.keys():
                post = self._generate_single(topic, framework_style, context)
                posts.append(f"--- {framework_style.upper()} ---\n{post}")
            return '\n\n'.join(posts)
        
        return self._generate_single(topic, style, context)
    
    def _generate_single(self, topic: str, style: str, context: str = None) -> str:
        """Generate single post using specified framework."""
        framework = self.frameworks.get(style, self._thought_leadership)
        post = framework(topic, context or '')
        
        # Add hashtags if configured
        if self.config.get('include_hashtags', True):
            hashtags = self._get_hashtags(topic)
            post = f"{post}\n\n{hashtags}"
        
        return post
    
    def _thought_leadership(self, topic: str, context: str) -> str:
        """Thought leadership framework."""
        hooks = [
            f"💡 Hot take: {topic}",
            f"💡 Unpopular opinion about {topic}",
            f"💡 Here's what nobody tells you about {topic}",
            f"💡 I've been thinking about {topic}...",
        ]
        
        points = [
            f"Here's what I've learned:",
            "Let me explain:",
            "Three things to know:",
        ]
        
        hook = random.choice(hooks)
        point_intro = random.choice(points)
        cta = random.choice(self.config.get('cta_options', ['Thoughts?']))
        
        post = f"""{hook}

{point_intro}

1️⃣ First key insight about {topic}
2️⃣ Second important perspective
3️⃣ Third actionable takeaway

The bottom line? {context or 'Understanding this changes everything.'}

{cta}"""
        
        return post
    
    def _story_framework(self, topic: str, context: str) -> str:
        """Story/journey framework."""
        hooks = [
            f"📖 Let me tell you how I approached {topic}...",
            f"📖 Here's my journey with {topic}",
            f"📖 3 months ago, I started exploring {topic}",
        ]
        
        hook = random.choice(hooks)
        cta = random.choice(self.config.get('cta_options', ["What's your experience?"]))
        
        post = f"""{hook}

The challenge:
{context or 'I was struggling with the usual problems...'}

What I tried:
• Approach 1: Traditional methods
• Approach 2: New tools and techniques  
• Approach 3: Combination of both

The breakthrough:
When I combined automation with human oversight, everything changed.

The result:
✅ 10x productivity
✅ Zero burnout
✅ Better outcomes

Lesson learned: {topic} isn't about working harder—it's about working smarter.

{cta}"""
        
        return post
    
    def _list_framework(self, topic: str, context: str) -> str:
        """List/educational framework."""
        hooks = [
            f"📋 7 lessons I learned about {topic}",
            f"📋 {topic}: 5 things you need to know",
            f"📋 My top 10 tips for {topic}",
        ]
        
        hook = random.choice(hooks)
        cta = random.choice(self.config.get('cta_options', ['Save this for later!']))
        
        post = f"""{hook}

{context or 'After months of experimentation, here are the insights that mattered most:'}

1. First principle or insight
2. Common mistake to avoid
3. Tool or technique that works
4. Metric to track
5. Resource I recommend
6. Habit that changed everything
7. One thing I'd do differently

{random.choice(['Which one resonates most?', 'What would you add to this list?', 'Bookmark this for reference.'])}

{cta}"""
        
        return post
    
    def _announcement_framework(self, topic: str, context: str) -> str:
        """Announcement framework."""
        hooks = [
            f"🚀 Exciting news!",
            f"🚀 I'm thrilled to announce...",
            f"🚀 After weeks of work...",
        ]
        
        hook = random.choice(hooks)
        
        post = f"""{hook}

{context or f'I just launched something new around {topic}!'}

What it is:
A solution that helps with {topic}

Why I built it:
• Problem 1 I was facing
• Problem 2 others experience
• Gap in the market

Key features:
✅ Feature/benefit 1
✅ Feature/benefit 2
✅ Feature/benefit 3

Who it's for:
Anyone dealing with {topic.lower()}

{random.choice(['Link in comments 👇', 'DM me for details', 'Early access available'])}

{random.choice(['Thoughts?', 'Questions? Ask below!', 'Share with someone who needs this'])}"""
        
        return post
    
    def _before_after_framework(self, topic: str, context: str) -> str:
        """Before/after transformation framework."""
        hooks = [
            f"⚡ The transformation:",
            f"⚡ Before vs After:",
            f"⚡ How things changed:",
        ]
        
        hook = random.choice(hooks)
        
        post = f"""{hook}

BEFORE {topic}:
❌ Problem 1
❌ Problem 2
❌ Problem 3

AFTER {topic}:
✅ Benefit 1
✅ Benefit 2
✅ Benefit 3

{context or 'The key was finding the right system.'}

How I did it:
1. Step one
2. Step two
3. Step three

{random.choice(['Want details? Comment below', 'Save this for inspiration', 'Tag someone who needs this'])}"""
        
        return post
    
    def _how_to_framework(self, topic: str, context: str) -> str:
        """How-to educational framework."""
        hooks = [
            f"🔧 How to master {topic}:",
            f"🔧 Step-by-step guide to {topic}",
            f"🔧 My process for {topic}",
        ]
        
        hook = random.choice(hooks)
        
        post = f"""{hook}

{context or "Here's my exact process:"}

Step 1: Foundation
Start with the basics. Don't skip this.

Step 2: Setup
Get your tools and environment ready.

Step 3: Execution
Take consistent action.

Step 4: Optimization
Measure and improve.

Step 5: Scale
Double down on what works.

{random.choice(['Which step are you stuck on?', 'Save this for later', 'Follow for more guides'])}

{random.choice(self.config.get('cta_options', ['Thoughts?']))}"""
        
        return post
    
    def _get_hashtags(self, topic: str) -> str:
        """Get relevant hashtags for topic."""
        topic_lower = topic.lower()
        
        # Find matching hashtag set
        hashtags = []
        for key, tags in self.hashtag_sets.items():
            if key in topic_lower:
                hashtags = tags
                break
        
        # Default hashtags
        if not hashtags:
            hashtags = ['#Innovation', '#Technology', '#Business']
        
        # Add topic-specific hashtag
        topic_tag = f"#{topic.replace(' ', '')}"
        if topic_tag not in hashtags:
            hashtags.insert(0, topic_tag)
        
        return ' '.join(hashtags[:5])
    
    def save_to_file(self, content: str, filename: str = None) -> Path:
        """Save generated content to file."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"LINKEDIN_CONTENT_{timestamp}.md"
        
        filepath = self.vault_path / 'Drafts' / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        markdown = f"""---
type: linkedin_content
created: {datetime.now().isoformat()}
status: draft
---

# Generated LinkedIn Content

{content}

---
*Generated by LinkedIn Content Writer Skill*
"""
        filepath.write_text(markdown)
        return filepath


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Content Writer")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--topic", "-t", required=True, help="Post topic")
    parser.add_argument("--style", "-s", default="thought-leadership",
                       help="Post style/framework")
    parser.add_argument("--context", "-c", help="Additional context")
    parser.add_argument("--count", "-n", type=int, default=1, help="Number of variations")
    parser.add_argument("--save", action="store_true", help="Save to Drafts folder")
    parser.add_argument("--post", action="store_true", help="Create post for approval")
    
    args = parser.parse_args()
    
    writer = LinkedInContentWriter(args.vault_path)
    
    # Generate content
    if args.style == 'all':
        content = writer.generate(args.topic, 'all', args.context)
    else:
        variations = []
        for _ in range(args.count):
            variations.append(writer.generate(args.topic, args.style, args.context))
        content = '\n\n---\n\n'.join(variations)
    
    print("\n" + "="*60)
    print("GENERATED LINKEDIN POST")
    print("="*60 + "\n")
    print(content)
    print("\n" + "="*60)
    
    # Save if requested
    if args.save:
        filepath = writer.save_to_file(content)
        print(f"\n✅ Saved to: {filepath}")
    
    # Create post for approval if requested
    if args.post:
        print("\n📝 To post this content:")
        print("  1. Copy the content above")
        print("  2. Run: python skills/actions/post-linkedin/post_linkedin.py VAULT --create --content \"...\"")


if __name__ == "__main__":
    main()
