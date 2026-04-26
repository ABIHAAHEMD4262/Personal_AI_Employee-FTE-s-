#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter/X Watcher - Monitor Twitter for mentions, DMs, and notifications.

Uses Playwright to automate Twitter and detect important notifications.

Usage:
    python twitter_watcher.py /path/to/vault [--interval 300] [--once] [--setup-session]
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


class TwitterNotification:
    """Represents a Twitter notification."""

    def __init__(self, from_name: str, notification_type: str, content: str, keywords: List[str]):
        self.from_name = from_name
        self.notification_type = notification_type
        self.content = content
        self.keywords = keywords
        self.timestamp = datetime.now()
        self.id = f"{from_name}_{notification_type}_{int(self.timestamp.timestamp())}"


class TwitterWatcher(BaseWatcher):
    """
    Watches Twitter for notifications and messages using Playwright.
    """

    def __init__(self, vault_path: str, check_interval: int = 300):
        super().__init__(vault_path, check_interval)

        # Session path
        self.session_path = Path(__file__).parent / 'twitter_session'
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
            'keywords': ['invoice', 'payment', 'urgent', 'help', 'question', 'order', 'purchase', 'pricing'],
            'notification_types': ['mentions', 'replies', 'dms', 'likes', 'retweets'],
            'headless': True,
            'check_mentions': True,
            'check_dms': True,
            'check_notifications': True,
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
        cache_file = self.vault_path / '.twitter_processed.cache'
        if cache_file.exists():
            try:
                self.processed_ids = set(
                    cache_file.read_text().strip().split('\n')
                )
                self.processed_ids.discard('')
            except:
                self.processed_ids = set()

    def _save_processed_ids(self):
        cache_file = self.vault_path / '.twitter_processed.cache'
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
        """Setup Twitter session (login once, session persists)."""
        if not self.playwright_available:
            print("❌ Playwright not installed.")
            print("Run: pip install playwright && playwright install chromium")
            return False

        try:
            from playwright.sync_api import sync_playwright

            print("\n🔐 Setting up Twitter session...")
            print("A browser window will open. Log in to Twitter/X.")
            print("Press Ctrl+C when you see your Twitter feed.\n")

            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,
                    viewport={'width': 1280, 'height': 720}
                )

                page = browser.pages[0]
                page.goto('https://twitter.com/')

                try:
                    # Wait for user to login and see feed
                    page.wait_for_url('https://twitter.com/home*', timeout=120000)
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

    def check_for_updates(self) -> List[TwitterNotification]:
        """Check Twitter for new notifications and messages."""
        if not self.playwright_available:
            return []

        if not self.session_path.exists():
            self.logger.warning("Twitter session not found. Run with --setup-session first.")
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
                    # Navigate to Twitter
                    page.goto('https://twitter.com/home', timeout=30000)
                    page.wait_for_load_state('networkidle', timeout=30000)
                    time.sleep(3)

                    # Check notifications if enabled
                    if self.config.get('check_notifications', True):
                        notif_list = self._check_notifications(page)
                        notifications.extend(notif_list)

                    # Check DMs if enabled
                    if self.config.get('check_dms', True):
                        dm_list = self._check_dms(page)
                        notifications.extend(dm_list)

                    # Check mentions if enabled
                    if self.config.get('check_mentions', True):
                        mention_list = self._check_mentions(page)
                        notifications.extend(mention_list)

                    browser.close()

                except Exception as e:
                    self.logger.error(f"Error accessing Twitter: {e}")
                    try:
                        browser.close()
                    except:
                        pass
                    return []

            if notifications:
                self._save_processed_ids()

            return notifications

        except Exception as e:
            self.logger.error(f"Twitter check failed: {e}")
            return []

    def _check_notifications(self, page) -> List[TwitterNotification]:
        """Check Twitter notifications."""
        notifications = []

        try:
            # Click on notifications bell
            notif_button = page.query_selector('[aria-label="Notifications"]')
            if notif_button:
                notif_button.click()
                time.sleep(2)

                # Get notification items
                notif_items = page.query_selector_all('[data-testid="cellInnerDiv"]')

                for item in notif_items[:10]:  # Limit to 10
                    try:
                        content = item.inner_text()

                        # Determine type
                        notif_type = 'general'
                        if 'liked' in content.lower():
                            notif_type = 'like'
                        elif 'retweeted' in content.lower() or 'reposted' in content.lower():
                            notif_type = 'retweet'
                        elif 'follow' in content.lower():
                            notif_type = 'follow'
                        elif 'mention' in content.lower():
                            notif_type = 'mention'

                        # Extract sender name
                        lines = content.strip().split('\n')
                        from_name = lines[0] if lines else "Unknown"

                        # Check keywords
                        keywords_found = []
                        content_lower = content.lower()
                        for keyword in self.config.get('keywords', []):
                            if keyword.lower() in content_lower:
                                keywords_found.append(keyword)

                        notif = TwitterNotification(
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

        except Exception as e:
            self.logger.debug(f"Error checking notifications: {e}")

        return notifications

    def _check_dms(self, page) -> List[TwitterNotification]:
        """Check Twitter Direct Messages."""
        notifications = []

        try:
            # Click on Messages icon
            messages_button = page.query_selector('[aria-label="Messages"]')
            if messages_button:
                messages_button.click()
                time.sleep(2)

                # Get message threads
                threads = page.query_selector_all('[data-testid="cellInnerDiv"]')

                for thread in threads[:5]:  # Limit to 5
                    try:
                        content = thread.inner_text()

                        # Check for unread indicator
                        has_unread = 'unread' in content.lower()

                        # Extract sender name and message
                        lines = content.strip().split('\n')
                        from_name = lines[0] if lines else "Unknown"
                        message_text = '\n'.join(lines[1:3]) if len(lines) > 1 else ""

                        # Check keywords
                        keywords_found = []
                        content_lower = content.lower()
                        for keyword in self.config.get('keywords', []):
                            if keyword.lower() in content_lower:
                                keywords_found.append(keyword)

                        # Only create notification if unread or keywords match
                        if has_unread or keywords_found:
                            notif = TwitterNotification(
                                from_name=from_name,
                                notification_type='dm',
                                content=f"From: {from_name}\n{message_text}",
                                keywords=keywords_found
                            )

                            if notif.id not in self.processed_ids:
                                notifications.append(notif)
                                self.processed_ids.add(notif.id)

                    except Exception as e:
                        self.logger.debug(f"Error processing message: {e}")

        except Exception as e:
            self.logger.debug(f"Error checking messages: {e}")

        return notifications

    def _check_mentions(self, page) -> List[TwitterNotification]:
        """Check Twitter mentions."""
        notifications = []

        try:
            # Navigate to mentions
            page.goto('https://twitter.com/notifications/mentions', timeout=30000)
            time.sleep(3)

            # Get mention items
            mentions = page.query_selector_all('[data-testid="cellInnerDiv"]')

            for mention in mentions[:10]:  # Limit to 10
                try:
                    content = mention.inner_text()

                    # Extract sender name
                    lines = content.strip().split('\n')
                    from_name = lines[0] if lines else "Unknown"

                    # Check keywords
                    keywords_found = []
                    content_lower = content.lower()
                    for keyword in self.config.get('keywords', []):
                        if keyword.lower() in content_lower:
                            keywords_found.append(keyword)

                    notif = TwitterNotification(
                        from_name=from_name,
                        notification_type='mention',
                        content=content,
                        keywords=keywords_found
                    )

                    if notif.id not in self.processed_ids and keywords_found:
                        notifications.append(notif)
                        self.processed_ids.add(notif.id)

                except Exception as e:
                    self.logger.debug(f"Error processing mention: {e}")

        except Exception as e:
            self.logger.debug(f"Error checking mentions: {e}")

        return notifications

    def create_action_file(self, item: TwitterNotification) -> Optional[Path]:
        """Create action file for Twitter notification."""
        try:
            safe_name = "".join(c for c in item.from_name if c.isalnum() or c in ' -_')[:30]
            filename = f"TWITTER_{item.notification_type}_{safe_name}.md"
            filepath = self.needs_action / filename

            actions = self._get_suggested_actions(item.notification_type, item.keywords)

            content = f"""---
type: twitter
from: {item.from_name}
notification_type: {item.notification_type}
received: {item.timestamp.isoformat()}
priority: {'high' if item.keywords else 'normal'}
status: pending
keywords: {json.dumps(item.keywords)}
---

# Twitter/X: {item.notification_type.title()} from {item.from_name}

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

        if notif_type == 'dm':
            actions.extend([
                '- [ ] Read message carefully',
                '- [ ] Draft professional reply',
                '- [ ] Send reply via Twitter DM',
            ])
        elif notif_type == 'mention':
            actions.extend([
                '- [ ] Check mention context',
                '- [ ] Engage with mention (like/reply)',
                '- [ ] Retweet if appropriate',
            ])
        elif notif_type == 'reply':
            actions.extend([
                '- [ ] Review reply to your tweet',
                '- [ ] Respond if needed',
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

    parser = argparse.ArgumentParser(description="Twitter/X Watcher")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--interval", "-i", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--setup-session", action="store_true")

    args = parser.parse_args()

    watcher = TwitterWatcher(args.vault_path, check_interval=args.interval)

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
