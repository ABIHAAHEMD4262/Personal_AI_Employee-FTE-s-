#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

This is the Bronze tier Watcher - simplest to implement and requires no API credentials.
Drop any file into the /Inbox folder and this watcher will create an action file.

Usage:
    python filesystem_watcher.py /path/to/vault [--interval 30] [--once]

Features:
    - Monitors /Inbox folder for new files
    - Copies files to /Needs_Action with metadata
    - Supports any file type (PDF, images, documents, etc.)
    - Creates companion .md file with file metadata
"""

import hashlib
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

from base_watcher import BaseWatcher


class FileDropItem:
    """Represents a file dropped for processing."""
    
    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.name = source_path.name
        self.size = source_path.stat().st_size
        self.hash = self._calculate_hash()
        self.extension = source_path.suffix.lower()
    
    def _calculate_hash(self) -> str:
        """Calculate MD5 hash for deduplication."""
        hash_md5 = hashlib.md5()
        with open(self.source_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_category(self) -> str:
        """Infer category from file extension."""
        categories = {
            '.pdf': 'document',
            '.doc': 'document',
            '.docx': 'document',
            '.txt': 'document',
            '.md': 'document',
            '.xls': 'spreadsheet',
            '.xlsx': 'spreadsheet',
            '.csv': 'spreadsheet',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.webp': 'image',
            '.mp3': 'audio',
            '.wav': 'audio',
            '.mp4': 'video',
            '.mov': 'video',
            '.zip': 'archive',
            '.rar': 'archive',
            '.tar': 'archive',
            '.gz': 'archive',
        }
        return categories.get(self.extension, 'unknown')


class FileSystemWatcher(BaseWatcher):
    """
    Watches the /Inbox folder for new files.
    
    When a file is detected:
    1. Copy to /Needs_Action with prefixed name
    2. Create companion .md file with metadata
    3. Track hash to avoid reprocessing
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.drop_folder = self.vault_path / 'Inbox'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        self.processed_hashes: set = set()
        self._load_processed_hashes()
    
    def _load_processed_hashes(self):
        """Load previously processed file hashes from cache."""
        cache_file = self.vault_path / '.processed_files.cache'
        if cache_file.exists():
            try:
                self.processed_hashes = set(
                    cache_file.read_text().strip().split('\n')
                )
                self.logger.info(
                    f"Loaded {len(self.processed_hashes)} processed file hashes"
                )
            except Exception as e:
                self.logger.warning(f"Could not load cache: {e}")
                self.processed_hashes = set()
    
    def _save_processed_hashes(self):
        """Save processed file hashes to cache."""
        cache_file = self.vault_path / '.processed_files.cache'
        try:
            cache_file.write_text('\n'.join(self.processed_hashes))
        except Exception as e:
            self.logger.warning(f"Could not save cache: {e}")
    
    def check_for_updates(self) -> List[FileDropItem]:
        """
        Check /Inbox folder for new files.
        
        Returns:
            List of FileDropItem objects for new files
        """
        items = []
        
        if not self.drop_folder.exists():
            return items
        
        for file_path in self.drop_folder.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                item = FileDropItem(file_path)
                
                # Skip already processed files
                if item.hash in self.processed_hashes:
                    continue
                
                items.append(item)
                self.processed_hashes.add(item.hash)
        
        # Persist the updated hash set
        if items:
            self._save_processed_hashes()
        
        return items
    
    def create_action_file(self, item: FileDropItem) -> Optional[Path]:
        """
        Create action file for dropped file.
        
        Copies the file to /Needs_Action and creates companion .md metadata file.
        
        Args:
            item: FileDropItem to process
            
        Returns:
            Path to created .md file
        """
        try:
            # Generate unique filename
            timestamp = item.source_path.stat().st_mtime
            safe_name = item.name.replace(' ', '_')
            dest_name = f"FILE_{safe_name}"
            dest_path = self.needs_action / dest_name
            
            # Copy file
            shutil.copy2(item.source_path, dest_path)
            self.logger.info(f"Copied: {item.name} -> {dest_name}")
            
            # Remove original from Inbox
            item.source_path.unlink()
            
            # Create companion metadata file
            meta_path = dest_path.with_suffix('.md')
            category = item.get_category()
            
            content = self._generate_content(item, dest_name, category)
            meta_path.write_text(content)
            
            return meta_path
            
        except Exception as e:
            self.logger.error(f"Failed to create action file: {e}")
            return None
    
    def _generate_content(self, item: FileDropItem, 
                          dest_name: str, 
                          category: str) -> str:
        """Generate markdown content for the action file."""
        
        frontmatter = self.generate_frontmatter(
            item_type='file_drop',
            original_name=item.name,
            size=item.size,
            category=category,
            hash=item.hash
        )
        
        # Generate suggested actions based on category
        suggested_actions = self._get_suggested_actions(category)
        
        content = f"""{frontmatter}

# File Drop: {item.name}

## File Information

| Property | Value |
|----------|-------|
| Original Name | {item.name} |
| Stored As | {dest_name} |
| Size | {self._format_size(item.size)} |
| Category | {category} |
| Hash | {item.hash} |

## Description

A new file has been dropped into the Inbox for processing.

## Suggested Actions

{suggested_actions}

---

*File moved from /Inbox to /Needs_Action automatically*
"""
        return content
    
    def _get_suggested_actions(self, category: str) -> str:
        """Get suggested actions based on file category."""
        actions = {
            'document': [
                '- [ ] Review document content',
                '- [ ] Extract key information',
                '- [ ] Categorize and file appropriately',
                '- [ ] Take any required actions',
            ],
            'spreadsheet': [
                '- [ ] Review data content',
                '- [ ] Update accounting records if financial',
                '- [ ] Archive after processing',
            ],
            'image': [
                '- [ ] Review image content',
                '- [ ] Add to appropriate project folder',
                '- [ ] Extract text if OCR needed',
            ],
            'audio': [
                '- [ ] Transcribe if needed',
                '- [ ] Extract key points',
                '- [ ] File appropriately',
            ],
            'video': [
                '- [ ] Review video content',
                '- [ ] Extract key information',
                '- [ ] File appropriately',
            ],
            'archive': [
                '- [ ] Extract archive contents',
                '- [ ] Process extracted files',
                '- [ ] Clean up archive',
            ],
            'unknown': [
                '- [ ] Identify file type',
                '- [ ] Review content',
                '- [ ] Process accordingly',
            ],
        }
        return '\n'.join(actions.get(category, actions['unknown']))
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="File System Watcher - Monitor drop folder for new files"
    )
    parser.add_argument(
        "vault_path",
        help="Path to Obsidian vault"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="Check interval in seconds (default: 30)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (for testing/cron)"
    )
    
    args = parser.parse_args()
    
    watcher = FileSystemWatcher(args.vault_path, args.interval)
    
    if args.once:
        count = watcher.run_once()
        print(f"Processed {count} file(s)")
    else:
        watcher.run()


if __name__ == "__main__":
    main()
