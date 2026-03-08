#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Monitor WhatsApp Web for urgent messages.

Uses Playwright to automate WhatsApp Web and detect urgent messages.

Usage:
    python whatsapp_watcher.py /path/to/vault [--interval 60] [--once] [--setup-session]

⚠️ WARNING: Be aware of WhatsApp's terms of service when using automation.
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


class WhatsAppMessage:
    """Represents a WhatsApp message."""
    
    def __init__(self, chat_name: str, phone: str, text: str, keywords: List[str]):
        self.chat_name = chat_name
        self.phone = phone
        self.text = text
        self.keywords = keywords
        self.timestamp = datetime.now()
        self.id = f"{phone}_{int(self.timestamp.timestamp())}"
    
    def is_urgent(self) -> bool:
        return len(self.keywords) > 0


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for urgent messages using Playwright.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the WhatsApp Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
        """
        super().__init__(vault_path, check_interval)
        
        # Session path
        self.session_path = Path(__file__).parent / 'whatsapp_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.config_path = Path(__file__).parent / 'config.json'
        self.config = self._load_config()
        
        # Processed message IDs
        self.processed_ids: set = set()
        self._load_processed_ids()
        
        # Check if playwright is available
        self.playwright_available = self._check_playwright()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load watcher configuration."""
        default_config = {
            'keywords': ['urgent', 'asap', 'invoice', 'payment', 'help', 'call me'],
            'check_duration': 30,  # seconds to wait for page load
            'headless': True,
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")
        
        return default_config
    
    def _load_processed_ids(self):
        """Load previously processed message IDs."""
        cache_file = self.vault_path / '.whatsapp_processed.cache'
        if cache_file.exists():
            try:
                self.processed_ids = set(
                    cache_file.read_text().strip().split('\n')
                )
                self.processed_ids.discard('')
                self.logger.info(
                    f"Loaded {len(self.processed_ids)} processed message IDs"
                )
            except Exception as e:
                self.logger.warning(f"Could not load cache: {e}")
                self.processed_ids = set()
    
    def _save_processed_ids(self):
        """Save processed message IDs to cache."""
        cache_file = self.vault_path / '.whatsapp_processed.cache'
        try:
            ids_list = list(self.processed_ids)[-1000:]
            cache_file.write_text('\n'.join(ids_list))
        except Exception as e:
            self.logger.warning(f"Could not save cache: {e}")
    
    def _check_playwright(self) -> bool:
        """Check if playwright is installed."""
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            self.logger.warning(
                "Playwright not installed. Run: pip install playwright && playwright install chromium"
            )
            return False
    
    def setup_session(self):
        """Setup WhatsApp session by scanning QR code."""
        if not self.playwright_available:
            print("Playwright not installed.")
            print("Run: pip install playwright && playwright install chromium")
            return False
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Show browser for QR scan
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = browser.pages[0]
                page.goto('https://web.whatsapp.com')
                
                print("\n📱 WhatsApp Web opened.")
                print("Scan the QR code with your WhatsApp mobile app.")
                print("Press Ctrl+C when you're logged in and see your chats.")
                
                try:
                    # Wait for chat list to appear (indicates login)
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=60000)
                    print("\n✅ Session saved successfully!")
                except:
                    print("\n⏱️  Timeout - you can still use the browser.")
                
                # Keep browser open for a bit
                time.sleep(5)
                browser.close()
                
            return True
            
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def check_for_updates(self) -> List[WhatsAppMessage]:
        """
        Check WhatsApp Web for new urgent messages.
        
        Returns:
            List of WhatsAppMessage objects
        """
        if not self.playwright_available:
            return []
        
        if not self.session_path.exists():
            self.logger.warning("WhatsApp session not found. Run with --setup-session first.")
            return []
        
        try:
            from playwright.sync_api import sync_playwright
            
            messages = []
            
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.config.get('headless', True),
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = browser.pages[0]
                
                try:
                    page.goto('https://web.whatsapp.com')
                    page.wait_for_selector('[data-testid="chat-list"]', 
                                          timeout=self.config.get('check_duration', 30) * 1000)
                    
                    # Wait for page to load
                    time.sleep(3)
                    
                    # Find unread chats
                    unread_chats = page.query_selector_all('[aria-label*="unread"]')
                    
                    for chat in unread_chats:
                        try:
                            # Get chat name
                            chat_name_elem = chat.query_selector('[dir="auto"]')
                            chat_name = chat_name_elem.inner_text() if chat_name_elem else "Unknown"
                            
                            # Get message text
                            message_elem = chat.query_selector('[data-testid="chat-cell-message"]')
                            message_text = message_elem.inner_text() if message_elem else ""
                            
                            # Try to extract phone/contact info
                            phone = "Unknown"
                            
                            # Check for keywords
                            keywords_found = []
                            text_lower = message_text.lower()
                            for keyword in self.config.get('keywords', []):
                                if keyword.lower() in text_lower:
                                    keywords_found.append(keyword)
                            
                            if keywords_found:
                                msg = WhatsAppMessage(
                                    chat_name=chat_name,
                                    phone=phone,
                                    text=message_text,
                                    keywords=keywords_found
                                )
                                
                                if msg.id not in self.processed_ids:
                                    messages.append(msg)
                                    self.processed_ids.add(msg.id)
                                    
                        except Exception as e:
                            self.logger.debug(f"Error processing chat: {e}")
                    
                    browser.close()
                    
                except Exception as e:
                    self.logger.error(f"Error accessing WhatsApp Web: {e}")
                    browser.close()
                    return []
            
            # Save cache if we have new messages
            if messages:
                self._save_processed_ids()
            
            return messages
            
        except Exception as e:
            self.logger.error(f"WhatsApp check failed: {e}")
            return []
    
    def create_action_file(self, item: WhatsAppMessage) -> Optional[Path]:
        """
        Create action file for WhatsApp message.
        
        Args:
            item: WhatsAppMessage to process
            
        Returns:
            Path to created .md file
        """
        try:
            # Generate filename
            safe_name = "".join(c for c in item.chat_name if c.isalnum() or c in ' -_')[:30]
            filename = f"WHATSAPP_{safe_name}_{item.id[:8]}.md"
            filepath = self.needs_action / filename
            
            # Generate suggested actions
            actions = self._get_suggested_actions(item.keywords)
            
            # Create content
            content = f"""---
type: whatsapp
from: {item.phone}
chat: {item.chat_name}
received: {item.timestamp.isoformat()}
message_id: {item.id}
priority: high
status: pending
keywords: {json.dumps(item.keywords)}
---

# WhatsApp Message: {item.chat_name}

## From
{item.phone} ({item.chat_name})

## Received
{item.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## Message
{item.text}

## Keywords Detected
{', '.join(item.keywords)}

## Suggested Actions
{actions}
"""
            filepath.write_text(content)
            return filepath
            
        except Exception as e:
            self.logger.error(f"Failed to create action file: {e}")
            return None
    
    def _get_suggested_actions(self, keywords: List[str]) -> str:
        """Get suggested actions based on keywords."""
        actions = ['- [ ] Read and understand the message']
        
        if 'invoice' in keywords or 'payment' in keywords:
            actions.extend([
                '- [ ] Identify amount and details',
                '- [ ] Create invoice or process payment (requires approval)',
                '- [ ] Reply with confirmation',
            ])
        elif 'urgent' in keywords or 'asap' in keywords:
            actions.extend([
                '- [ ] Respond promptly (high priority)',
                '- [ ] Take required action immediately',
            ])
        elif 'help' in keywords:
            actions.extend([
                '- [ ] Understand what help is needed',
                '- [ ] Provide assistance or schedule call',
            ])
        else:
            actions.extend([
                '- [ ] Draft appropriate reply',
                '- [ ] Send reply',
            ])
        
        actions.append('- [ ] Archive message after processing')
        
        return '\n'.join(actions)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="WhatsApp Watcher - Monitor WhatsApp Web for urgent messages"
    )
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for testing)"
    )
    parser.add_argument(
        "--setup-session",
        action="store_true",
        help="Setup WhatsApp session (scan QR code)"
    )
    
    args = parser.parse_args()
    
    watcher = WhatsAppWatcher(args.vault_path, check_interval=args.interval)
    
    if args.setup_session:
        success = watcher.setup_session()
        exit(0 if success else 1)
    
    if args.once:
        count = watcher.run_once()
        print(f"Processed {count} message(s)")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
