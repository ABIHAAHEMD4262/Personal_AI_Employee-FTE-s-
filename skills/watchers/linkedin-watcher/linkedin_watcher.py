#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher - Monitor LinkedIn for notifications and messages.

Uses Playwright to automate LinkedIn and detect important notifications.

Usage:
    python linkedin_watcher.py /path/to/vault [--interval 300] [--once] [--setup-session]
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Import base watcher
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'watchers'))
from base_watcher import BaseWatcher


class LinkedInNotification:
    """Represents a LinkedIn notification."""
    
    def __init__(self, from_name: str, notification_type: str, content: str, keywords: List[str]):
        self.from_name = from_name
        self.notification_type = notification_type
        self.content = content
        self.keywords = keywords
        self.timestamp = datetime.now()
        self.id = f"{from_name}_{notification_type}_{int(self.timestamp.timestamp())}"


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for notifications using Playwright.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 300):
        super().__init__(vault_path, check_interval)
        
        # Session path
        self.session_path = Path(__file__).parent / 'linkedin_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.config_path = Path(__file__).parent / 'config.json'
        self.config = self._load_config()
        
        # Processed IDs
        self.processed_ids: set = set()
        self._load_processed_ids()
        
        # Check playwright
        self.playwright_available = self._check_playwright()
    
    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            'keywords': ['hiring', 'opportunity', 'project', 'collaboration', 'freelance'],
            'notification_types': ['messages', 'comments', 'connection_requests'],
            'headless': True,
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)
                    default_config.update(config)
            except:
                pass
        
        return default_config
    
    def _load_processed_ids(self):
        cache_file = self.vault_path / '.linkedin_processed.cache'
        if cache_file.exists():
            try:
                self.processed_ids = set(
                    cache_file.read_text().strip().split('\n')
                )
                self.processed_ids.discard('')
            except:
                self.processed_ids = set()
    
    def _save_processed_ids(self):
        cache_file = self.vault_path / '.linkedin_processed.cache'
        try:
            ids_list = list(self.processed_ids)[-1000:]
            cache_file.write_text('\n'.join(ids_list))
        except:
            pass
    
    def _check_playwright(self) -> bool:
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            self.logger.warning(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )
            return False
    
    def setup_session(self):
        """Setup LinkedIn session."""
        if not self.playwright_available:
            print("Playwright not installed.")
            print("Run: pip install playwright && playwright install chromium")
            return False
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = browser.pages[0]
                page.goto('https://www.linkedin.com/login')
                
                print("\n🔐 LinkedIn login opened.")
                print("Log in to your LinkedIn account.")
                print("Press Ctrl+C when you see your feed.")
                
                try:
                    page.wait_for_url('https://www.linkedin.com/feed/*', timeout=120000)
                    print("\n✅ Session saved successfully!")
                except:
                    print("\n⏱️  Timeout - you can still use the browser.")
                
                time.sleep(5)
                browser.close()
                
            return True
            
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def check_for_updates(self) -> List[LinkedInNotification]:
        """Check LinkedIn for new notifications."""
        if not self.playwright_available:
            return []
        
        if not self.session_path.exists():
            self.logger.warning("LinkedIn session not found. Run with --setup-session first.")
            return []
        
        try:
            from playwright.sync_api import sync_playwright
            
            notifications = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.config.get('headless', True)
                )
                
                page = browser.pages[0]
                
                try:
                    page.goto('https://www.linkedin.com/')
                    page.wait_for_load_state('networkidle', timeout=30000)
                    time.sleep(3)
                    
                    # Check for notifications badge
                    notif_bubble = page.query_selector('.notification-badge__bullet')
                    if notif_bubble:
                        # Navigate to notifications
                        page.goto('https://www.linkedin.com/notifications/')
                        time.sleep(3)
                        
                        # Get notification items
                        notif_items = page.query_selector_all('li.notification-item')
                        
                        for item in notif_items[:10]:  # Limit to 10
                            try:
                                # Extract notification details
                                from_elem = item.query_selector('[data-tracking="notification_actor_name"]')
                                from_name = from_elem.inner_text() if from_elem else "Unknown"
                                
                                content_elem = item.query_selector('.notification-item__message')
                                content = content_elem.inner_text() if content_elem else ""
                                
                                # Determine type
                                notif_type = 'general'
                                if 'message' in content.lower():
                                    notif_type = 'message'
                                elif 'comment' in content.lower():
                                    notif_type = 'comment'
                                elif 'connection' in content.lower():
                                    notif_type = 'connection'
                                
                                # Check keywords
                                keywords_found = []
                                content_lower = content.lower()
                                for keyword in self.config.get('keywords', []):
                                    if keyword.lower() in content_lower:
                                        keywords_found.append(keyword)
                                
                                notif = LinkedInNotification(
                                    from_name=from_name,
                                    notification_type=notif_type,
                                    content=content,
                                    keywords=keywords_found
                                )
                                
                                if notif.id not in self.processed_ids and keywords_found:
                                    notifications.append(notif)
                                    self.processed_ids.add(notif.id)
                                    
                            except Exception as e:
                                self.logger.debug(f"Error processing notification: {e}")
                    
                    browser.close()
                    
                except Exception as e:
                    self.logger.error(f"Error accessing LinkedIn: {e}")
                    browser.close()
                    return []
            
            if notifications:
                self._save_processed_ids()
            
            return notifications
            
        except Exception as e:
            self.logger.error(f"LinkedIn check failed: {e}")
            return []
    
    def create_action_file(self, item: LinkedInNotification) -> Optional[Path]:
        """Create action file for LinkedIn notification."""
        try:
            safe_name = "".join(c for c in item.from_name if c.isalnum() or c in ' -_')[:30]
            filename = f"LINKEDIN_{item.notification_type}_{safe_name}.md"
            filepath = self.needs_action / filename
            
            actions = self._get_suggested_actions(item.notification_type, item.keywords)
            
            content = f"""---
type: linkedin
from: {item.from_name}
notification_type: {item.notification_type}
received: {item.timestamp.isoformat()}
priority: {'high' if item.keywords else 'normal'}
status: pending
keywords: {json.dumps(item.keywords)}
---

# LinkedIn: {item.notification_type.title()} from {item.from_name}

## From
{item.from_name}

## Received
{item.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Content
{item.content}

## Keywords Detected
{', '.join(item.keywords) if item.keywords else 'None'}

## Suggested Actions
{actions}
"""
            filepath.write_text(content)
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to create action file: {e}")
            return None
    
    def _get_suggested_actions(self, notif_type: str, keywords: List[str]) -> str:
        actions = ['- [ ] Review notification content']
        
        if notif_type == 'message':
            actions.extend([
                '- [ ] Read message carefully',
                '- [ ] Draft professional reply',
                '- [ ] Send reply via LinkedIn',
            ])
        elif notif_type == 'connection':
            actions.extend([
                '- [ ] Review sender profile',
                '- [ ] Accept or decline connection',
                '- [ ] Send welcome message if accepted',
            ])
        elif 'hiring' in keywords or 'opportunity' in keywords:
            actions.extend([
                '- [ ] Evaluate opportunity',
                '- [ ] Respond with interest or decline politely',
            ])
        else:
            actions.extend([
                '- [ ] Determine if action needed',
                '- [ ] Respond if appropriate',
            ])
        
        return '\n'.join(actions)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Watcher")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--interval", "-i", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--setup-session", action="store_true")
    
    args = parser.parse_args()
    
    watcher = LinkedInWatcher(args.vault_path, check_interval=args.interval)
    
    if args.setup_session:
        success = watcher.setup_session()
        exit(0 if success else 1)
    
    if args.once:
        count = watcher.run_once()
        print(f"Processed {count} notification(s)")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
