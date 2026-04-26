#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Watcher - Monitor Facebook for notifications, messages, and posts.

Uses Playwright to automate Facebook and detect important notifications.

Usage:
    python facebook_watcher.py /path/to/vault [--interval 300] [--once] [--setup-session]
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


class FacebookNotification:
    """Represents a Facebook notification."""

    def __init__(self, from_name: str, notification_type: str, content: str, keywords: List[str]):
        self.from_name = from_name
        self.notification_type = notification_type
        self.content = content
        self.keywords = keywords
        self.timestamp = datetime.now()
        self.id = f"{from_name}_{notification_type}_{int(self.timestamp.timestamp())}"


class FacebookWatcher(BaseWatcher):
    """
    Watches Facebook for notifications and messages using Playwright.
    """

    def __init__(self, vault_path: str, check_interval: int = 300):
        super().__init__(vault_path, check_interval)

        # Session path
        self.session_path = Path(__file__).parent / 'facebook_session'
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
            'keywords': ['invoice', 'payment', 'urgent', 'help', 'question', 'order', 'purchase'],
            'notification_types': ['messages', 'comments', 'mentions', 'reactions', 'page_notifications'],
            'headless': True,
            'check_messages': True,
            'check_notifications': True,
            'check_page_insights': False,
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
        cache_file = self.vault_path / '.facebook_processed.cache'
        if cache_file.exists():
            try:
                self.processed_ids = set(
                    cache_file.read_text().strip().split('\n')
                )
                self.processed_ids.discard('')
            except:
                self.processed_ids = set()

    def _save_processed_ids(self):
        cache_file = self.vault_path / '.facebook_processed.cache'
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
        """Setup Facebook session (login once, session persists)."""
        if not self.playwright_available:
            print("❌ Playwright not installed.")
            print("Run: pip install playwright && playwright install chromium")
            return False

        try:
            from playwright.sync_api import sync_playwright

            print("\n🔐 Setting up Facebook session...")
            print("A browser window will open. Log in to Facebook.")
            print("Press Ctrl+C when you see your Facebook feed.\n")

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,
                    viewport={'width': 1280, 'height': 720}
                )

                page = browser.pages[0]
                page.goto('https://www.facebook.com/')

                try:
                    # Wait for user to login and see feed
                    page.wait_for_url('https://www.facebook.com/', timeout=120000)
                    print("\n✅ Session saved successfully!")
                    print("   Future runs will use this session (no login needed)")
                except:
                    print("\n⏱️  Timeout - session may not be saved")

                time.sleep(5)
                browser.close()

            return True

        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False

    def check_for_updates(self) -> List[FacebookNotification]:
        """Check Facebook for new notifications and messages."""
        if not self.playwright_available:
            return []

        if not self.session_path.exists():
            self.logger.warning("Facebook session not found. Run with --setup-session first.")
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
                    # Navigate to Facebook
                    page.goto('https://www.facebook.com/', timeout=30000)
                    page.wait_for_load_state('networkidle', timeout=30000)
                    time.sleep(3)

                    # Check notifications if enabled
                    if self.config.get('check_notifications', True):
                        notif_list = self._check_notifications(page)
                        notifications.extend(notif_list)

                    # Check messages if enabled
                    if self.config.get('check_messages', True):
                        msg_list = self._check_messages(page)
                        notifications.extend(msg_list)

                    # Check page insights if enabled
                    if self.config.get('check_page_insights', False):
                        insights = self._check_page_insights(page)
                        if insights:
                            notif = FacebookNotification(
                                from_name='Facebook Page',
                                notification_type='page_insights',
                                content=insights,
                                keywords=['insights', 'analytics']
                            )
                            if notif.id not in self.processed_ids:
                                notifications.append(notif)
                                self.processed_ids.add(notif.id)

                    browser.close()

                except Exception as e:
                    self.logger.error(f"Error accessing Facebook: {e}")
                    try:
                        browser.close()
                    except:
                        pass
                    return []

            if notifications:
                self._save_processed_ids()

            return notifications

        except Exception as e:
            self.logger.error(f"Facebook check failed: {e}")
            return []

    def _check_notifications(self, page) -> List[FacebookNotification]:
        """Check Facebook notifications."""
        notifications = []

        try:
            # Click on notifications bell
            notif_button = page.query_selector('[aria-label="Notifications"]')
            if notif_button:
                notif_button.click()
                time.sleep(2)

                # Get notification items
                notif_items = page.query_selector_all('[role="menuitem"]')

                for item in notif_items[:10]:  # Limit to 10
                    try:
                        content = item.inner_text()

                        # Determine type
                        notif_type = 'general'
                        if 'comment' in content.lower():
                            notif_type = 'comment'
                        elif 'react' in content.lower():
                            notif_type = 'reaction'
                        elif 'mention' in content.lower():
                            notif_type = 'mention'
                        elif 'message' in content.lower():
                            notif_type = 'message'

                        # Extract sender name (first line)
                        lines = content.strip().split('\n')
                        from_name = lines[0] if lines else "Unknown"

                        # Check keywords
                        keywords_found = []
                        content_lower = content.lower()
                        for keyword in self.config.get('keywords', []):
                            if keyword.lower() in content_lower:
                                keywords_found.append(keyword)

                        notif = FacebookNotification(
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

                # Close notifications dropdown
                page.keyboard.press('Escape')
                time.sleep(1)

        except Exception as e:
            self.logger.debug(f"Error checking notifications: {e}")

        return notifications

    def _check_messages(self, page) -> List[FacebookNotification]:
        """Check Facebook Messenger for new messages."""
        notifications = []

        try:
            # Click on Messenger icon
            messenger_button = page.query_selector('[aria-label="Messenger"]')
            if messenger_button:
                messenger_button.click()
                time.sleep(2)

                # Get message threads
                threads = page.query_selector_all('[role="menuitem"]')

                for thread in threads[:5]:  # Limit to 5
                    try:
                        content = thread.inner_text()

                        # Check for unread indicator
                        has_unread = False
                        unread_badge = thread.query_selector('[class*="unread"]')
                        if unread_badge:
                            has_unread = True

                        # Extract sender name
                        lines = content.strip().split('\n')
                        from_name = lines[0] if lines else "Unknown"
                        message_text = '\n'.join(lines[1:]) if len(lines) > 1 else ""

                        # Check keywords
                        keywords_found = []
                        content_lower = content.lower()
                        for keyword in self.config.get('keywords', []):
                            if keyword.lower() in content_lower:
                                keywords_found.append(keyword)

                        # Only create notification if unread or keywords match
                        if has_unread or keywords_found:
                            notif = FacebookNotification(
                                from_name=from_name,
                                notification_type='message',
                                content=f"From: {from_name}\n{message_text}",
                                keywords=keywords_found
                            )

                            if notif.id not in self.processed_ids:
                                notifications.append(notif)
                                self.processed_ids.add(notif.id)

                    except Exception as e:
                        self.logger.debug(f"Error processing message: {e}")

                # Close messenger dropdown
                page.keyboard.press('Escape')
                time.sleep(1)

        except Exception as e:
            self.logger.debug(f"Error checking messages: {e}")

        return notifications

    def _check_page_insights(self, page) -> Optional[str]:
        """Check Facebook Page insights (optional)."""
        try:
            # Navigate to your page
            page.goto('https://www.facebook.com/pages/?category=your_pages', timeout=30000)
            time.sleep(3)

            # Click on first page
            pages = page.query_selector_all('[role="link"]')
            if pages:
                pages[0].click()
                time.sleep(3)

                # Look for insights/professional dashboard
                insights_link = page.query_selector('[aria-label*="Professional Dashboard"]')
                if insights_link:
                    insights_link.click()
                    time.sleep(3)

                    # Extract basic metrics
                    insights_content = page.inner_text()

                    # Look for key metrics
                    metrics = []
                    for keyword in ['reach', 'engagement', 'followers', 'impressions']:
                        if keyword in insights_content.lower():
                            metrics.append(keyword)

                    if metrics:
                        return f"Page insights updated. Metrics available: {', '.join(metrics)}"

            return None

        except Exception as e:
            self.logger.debug(f"Error checking page insights: {e}")
            return None

    def create_action_file(self, item: FacebookNotification) -> Optional[Path]:
        """Create action file for Facebook notification."""
        try:
            safe_name = "".join(c for c in item.from_name if c.isalnum() or c in ' -_')[:30]
            filename = f"FACEBOOK_{item.notification_type}_{safe_name}.md"
            filepath = self.needs_action / filename

            actions = self._get_suggested_actions(item.notification_type, item.keywords)

            content = f"""---
type: facebook
from: {item.from_name}
notification_type: {item.notification_type}
received: {item.timestamp.isoformat()}
priority: {'high' if item.keywords else 'normal'}
status: pending
keywords: {json.dumps(item.keywords)}
---

# Facebook: {item.notification_type.title()} from {item.from_name}

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
                '- [ ] Send reply via Facebook Messenger',
            ])
        elif notif_type == 'comment':
            actions.extend([
                '- [ ] Review comment on post',
                '- [ ] Respond to comment if needed',
                '- [ ] Hide/delete if inappropriate',
            ])
        elif notif_type == 'mention':
            actions.extend([
                '- [ ] Check mention context',
                '- [ ] Engage with mention (like/reply)',
            ])
        elif 'invoice' in keywords or 'payment' in keywords:
            actions.extend([
                '- [ ] Process payment/invoice request',
                '- [ ] Create invoice if needed',
                '- [ ] Update accounting',
            ])
        elif 'urgent' in keywords or 'help' in keywords:
            actions.extend([
                '- [ ] Prioritize this request',
                '- [ ] Respond promptly',
            ])
        else:
            actions.extend([
                '- [ ] Determine if action needed',
                '- [ ] Respond if appropriate',
            ])

        return '\n'.join(actions)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Facebook Watcher")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--interval", "-i", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--setup-session", action="store_true")

    args = parser.parse_args()

    watcher = FacebookWatcher(args.vault_path, check_interval=args.interval)

    if args.setup_session:
        success = watcher.setup_session()
        exit(0 if success else 1)

    if args.once:
        count = watcher.run_once()
        print(f"✅ Processed {count} notification(s)")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
