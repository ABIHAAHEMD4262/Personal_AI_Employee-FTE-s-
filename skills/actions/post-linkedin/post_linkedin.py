#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post LinkedIn Skill - Create and post LinkedIn content with approval.

Usage:
    python post_linkedin.py /path/to/vault --create --content "Post text"
    python post_linkedin.py /path/to/vault --execute
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class PostLinkedInSkill:
    """Post to LinkedIn with approval workflow."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        
        # Folders
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        self.scheduled_folder = self.vault_path / 'Scheduled'
        
        for folder in [self.pending_folder, self.approved_folder,
                       self.done_folder, self.scheduled_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Config
        self.config_path = Path(__file__).parent / 'config.json'
        self.config = self._load_config()
    
    def log(self, message: str, level: str = "INFO"):
        print(f"[{level}] {message}")
    
    def _load_config(self) -> Dict[str, Any]:
        default = {
            'hashtags': ['#business', '#growth'],
            'require_approval': True,
            'post_signature': '',
        }
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return {**default, **json.load(f)}
            except:
                pass
        return default
    
    def create_post(self, content: str, schedule_time: str = None) -> Optional[Path]:
        """Create a LinkedIn post (requires approval)."""
        try:
            now = datetime.now()
            filename = f"LINKEDIN_POST_{now.strftime('%Y%m%d_%H%M%S')}.md"
            
            if schedule_time:
                filepath = self.scheduled_folder / filename
                status = 'scheduled'
            else:
                filepath = self.pending_folder / filename
                status = 'pending_approval'
            
            # Add hashtags
            hashtags = ' '.join(self.config.get('hashtags', []))
            full_content = f"{content}\n\n{hashtags}"
            
            file_content = f"""---
type: approval_request
action: social_post
platform: LinkedIn
content: {content[:100]}{'...' if len(content) > 100 else ''}
created: {now.isoformat()}
scheduled: {schedule_time or ''}
status: {status}
---

# LinkedIn Post Request

## Content
{full_content}

## Details
- **Platform:** LinkedIn
- **Character Count:** {len(full_content)}
{f"- **Scheduled:** {schedule_time}" if schedule_time else ""}

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.
"""
            filepath.write_text(file_content)
            self.log(f"Created LinkedIn post: {filename}")
            return filepath
            
        except Exception as e:
            self.log(f"Failed to create post: {e}", "ERROR")
            return None
    
    def execute_approved(self) -> int:
        """Execute approved LinkedIn posts."""
        posted = 0
        
        if not self.approved_folder.exists():
            return 0
        
        for md_file in self.approved_folder.glob('*.md'):
            try:
                content = md_file.read_text()
                frontmatter = self._parse_frontmatter(content)
                
                if frontmatter.get('action') != 'social_post':
                    continue
                if frontmatter.get('platform') != 'LinkedIn':
                    continue
                
                # Extract post content
                content_start = content.find('## Content')
                if content_start != -1:
                    post_content = content[content_start:].split('\n')[2:]
                    post_text = '\n'.join(post_content).split('\n##')[0].strip()
                    
                    self.log(f"Posting to LinkedIn...")
                    self.log(f"  Content: {post_text[:50]}...")
                    
                    # Actually post to LinkedIn using Playwright
                    success = self._post_to_linkedin(post_text)
                    
                    if success:
                        self.log(f"  → Posted successfully to LinkedIn")
                        self.log(f"  → Check: https://www.linkedin.com/feed/")
                        
                        # Move to Done
                        today = datetime.now().strftime('%Y-%m-%d')
                        done_folder = self.done_folder / today
                        done_folder.mkdir(parents=True, exist_ok=True)
                        md_file.rename(done_folder / md_file.name)
                        posted += 1
                    else:
                        self.log(f"  → Failed to post to LinkedIn", "ERROR")
                    
            except Exception as e:
                self.log(f"Error processing {md_file.name}: {e}", "ERROR")
        
        return posted
    
    def _post_to_linkedin(self, content: str) -> bool:
        """
        Actually post to LinkedIn using Playwright.
        
        Args:
            content: Post content
            
        Returns:
            True if posted successfully
        """
        try:
            from playwright.sync_api import sync_playwright
            
            session_path = Path(__file__).parent.parent.parent / 'watchers' / 'linkedin-watcher' / 'linkedin_session'
            
            if not session_path.exists():
                self.log("  → LinkedIn session not found. Run --setup-session first.", "ERROR")
                return False
            
            max_retries = 2
            for attempt in range(max_retries):
                result = self._try_post_to_linkedin(content, session_path)
                if result:
                    return True
                
                self.log(f"  → Attempt {attempt + 1} failed, retrying...", "WARNING")
                import time
                time.sleep(3)
            
            return False
                    
        except ImportError:
            self.log("  → Playwright not installed. Run: pip install playwright", "ERROR")
            return False
        except Exception as e:
            self.log(f"  → Error posting: {e}", "ERROR")
            return False
    
    def _try_post_to_linkedin(self, content: str, session_path: Path) -> bool:
        """Single attempt to post to LinkedIn."""
        browser = None
        try:
            from playwright.sync_api import sync_playwright, TimeoutError
            
            with sync_playwright() as p:
                # Launch browser with saved session
                browser = p.chromium.launch_persistent_context(
                    str(session_path),
                    headless=False,  # Visible for debugging
                    viewport={'width': 1280, 'height': 720},
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Set realistic headers
                page.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Navigate to LinkedIn
                page.goto('https://www.linkedin.com/', timeout=20000)
                page.wait_for_timeout(8000)
                
                # Check if logged in
                current_url = page.url
                if 'login' in current_url.lower():
                    self.log(f"  → Session expired. Re-run --setup-session", "ERROR")
                    browser.close()
                    return False
                
                # Click "Start a post"
                share_box = page.query_selector('button:has-text("Start a post")')
                if not share_box:
                    share_box = page.query_selector('[data-testid="share-box-start-editor"]')
                
                if not share_box:
                    self.log("  → Share box not found", "ERROR")
                    browser.close()
                    return False
                
                self.log("  → Found share box, clicking...")
                share_box.click()
                page.wait_for_timeout(5000)  # Wait for modal to open
                
                # Take screenshot to debug
                page.screenshot(path='linkedin_step1.png')
                
                # Find text input - LinkedIn uses a specific div structure
                text_input = None
                
                # Try multiple selectors
                selectors = [
                    '[contenteditable="true"][role="textbox"]',
                    '.editor-content[contenteditable="true"]',
                    'div[contenteditable="true"].inline-editor',
                    '[data-placeholder*="What do you"]',
                ]
                
                for selector in selectors:
                    text_input = page.query_selector(selector)
                    if text_input:
                        self.log(f"  → Found text input: {selector}")
                        break
                
                if not text_input:
                    self.log("  → Text input not found, trying generic...", "WARNING")
                    text_input = page.query_selector('div[contenteditable="true"]')
                
                if not text_input:
                    self.log("  → Could not find text input", "ERROR")
                    page.screenshot(path='linkedin_error.png')
                    browser.close()
                    return False
                
                # Clear existing content
                text_input.click()
                page.wait_for_timeout(500)
                text_input.press('Control+A')
                page.wait_for_timeout(300)
                text_input.press('Backspace')
                page.wait_for_timeout(500)
                
                # Type content slowly (LinkedIn needs this)
                self.log("  → Typing content...")
                text_input.type(content, delay=50)
                page.wait_for_timeout(5000)  # Wait for Post button to enable
                
                # Take screenshot after typing
                page.screenshot(path='linkedin_step2.png')
                
                # NOW find and click the Post button
                # LinkedIn has MULTIPLE "Post" buttons - we need the one in the modal
                self.log("  → Looking for Post button...")
                
                post_button = None
                
                # The Post button is usually in a footer with specific classes
                # Try to find it by looking for the enabled Post button
                post_selectors = [
                    'button[aria-label="Post"]:not([disabled])',
                    'button.ml2:not([disabled]):has-text("Post")',
                    '.share-actions__primary-action:not([disabled])',
                    'button:has-text("Post"):not([aria-disabled="true"])',
                ]
                
                for selector in post_selectors:
                    post_button = page.query_selector(selector)
                    if post_button:
                        self.log(f"  → Found Post button: {selector}")
                        break
                
                # If still not found, try finding any enabled Post button
                if not post_button:
                    buttons = page.query_selector_all('button:has-text("Post")')
                    for btn in buttons:
                        is_disabled = btn.get_attribute('disabled')
                        is_aria_disabled = btn.get_attribute('aria-disabled')
                        if not is_disabled and is_aria_disabled != 'true':
                            post_button = btn
                            self.log("  → Found Post button by iteration")
                            break
                
                if not post_button:
                    self.log("  → Post button not found!", "ERROR")
                    self.log("  → Checking if content was typed...", "WARNING")
                    page.screenshot(path='linkedin_no_button.png')
                    
                    # Try one more approach - look for any button in the share footer
                    footer_buttons = page.query_selector_all('.share-box-footer button')
                    if footer_buttons:
                        post_button = footer_buttons[-1]  # Usually the rightmost is Post
                        self.log("  → Using footer button as fallback")
                
                if post_button:
                    self.log("  → Clicking Post button...")
                    post_button.click()
                    page.wait_for_timeout(8000)
                    
                    # Take final screenshot
                    page.screenshot(path='linkedin_final.png')
                    self.log("  → Screenshots saved for debugging")
                    
                    # Check if we're back on feed (post succeeded)
                    if 'feed' in page.url.lower():
                        self.log("  → ✅ Post successful! Back on feed")
                    else:
                        self.log("  → Post button clicked, checking result...")
                    
                    browser.close()
                    return True
                else:
                    self.log("  → ❌ Could not find Post button after typing", "ERROR")
                    browser.close()
                    return False
                    
        except Exception as e:
            if browser:
                try:
                    browser.close()
                except:
                    pass
            self.log(f"  → Error: {e}", "ERROR")
            return False
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        frontmatter = {}
        in_frontmatter = False
        for line in content.split('\n'):
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()
        return frontmatter


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Post LinkedIn Skill")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--create", action="store_true", help="Create post")
    action.add_argument("--execute", action="store_true", help="Execute approved")
    action.add_argument("--schedule", action="store_true", help="Schedule post")
    
    parser.add_argument("--content", "-c", help="Post content")
    parser.add_argument("--date", "-d", help="Schedule date (ISO format)")
    
    args = parser.parse_args()
    
    skill = PostLinkedInSkill(args.vault_path)
    
    if args.create or args.schedule:
        if not args.content:
            print("Error: --content required")
            exit(1)
        schedule = args.date if args.schedule else None
        result = skill.create_post(args.content, schedule)
        exit(0 if result else 1)
    elif args.execute:
        posted = skill.execute_approved()
        print(f"Posted {posted} update(s) to LinkedIn")


if __name__ == "__main__":
    main()
