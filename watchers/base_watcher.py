#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract template for all Watcher scripts.

Watchers are the "senses" of the AI Employee, continuously monitoring
various inputs and creating actionable files for Claude to process.

Usage:
    Subclass this module and implement check_for_updates() and create_action_file()
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all Watcher implementations.
    
    All Watchers follow this pattern:
    1. Continuously monitor a data source
    2. Detect new/changed items
    3. Create .md action files in /Needs_Action folder
    4. Track processed items to avoid duplicates
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Track processed items (override in subclass if persistence needed)
        self.processed_ids: set = set()

    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check the data source for new items.
        
        Returns:
            List of new items to process
            
        Raises:
            Exception: If check fails (will be logged and retried)
        """
        pass

    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a .md action file in /Needs_Action folder.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to created file, or None if creation failed
        """
        pass

    def generate_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Generate YAML frontmatter for action files.
        
        Args:
            item_type: Type of item (email, file_drop, whatsapp, etc.)
            **kwargs: Additional frontmatter fields
            
        Returns:
            YAML frontmatter string
        """
        lines = [
            "---",
            f"type: {item_type}",
            f"created: {datetime.now().isoformat()}",
            "status: pending",
            "priority: normal",
        ]
        
        for key, value in kwargs.items():
            lines.append(f"{key}: {value}")
        
        lines.append("---")
        return "\n".join(lines)

    def run(self):
        """
        Main run loop. Continuously monitors and processes items.
        
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Vault path: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval}s")
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f"Found {len(items)} new item(s)")
                        for item in items:
                            filepath = self.create_action_file(item)
                            if filepath:
                                self.logger.info(f"Created: {filepath.name}")
                    else:
                        self.logger.debug("No new items")
                except Exception as e:
                    self.logger.error(f"Error processing items: {e}")
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f"\n{self.__class__.__name__} stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            raise

    def run_once(self) -> int:
        """
        Run a single check cycle (useful for testing or cron jobs).
        
        Returns:
            Number of items processed
        """
        items = self.check_for_updates()
        count = 0
        for item in items:
            if self.create_action_file(item):
                count += 1
        return count


def main():
    """CLI entry point for running watchers."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run a Watcher script"
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
        help="Run once and exit (for testing/cron)"
    )
    
    args = parser.parse_args()
    
    # Note: This is a base class - actual usage requires subclass
    print("BaseWatcher is an abstract class.")
    print("Subclass it and implement check_for_updates() and create_action_file()")
    print()
    print("Example:")
    print("  class MyWatcher(BaseWatcher):")
    print("      def check_for_updates(self):")
    print("          # Return list of new items")
    print("          return []")
    print()
    print("      def create_action_file(self, item):")
    print("          # Create .md file in Needs_Action")
    print("          pass")


if __name__ == "__main__":
    main()
