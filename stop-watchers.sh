#!/bin/bash
# Stop all AI Employee watchers

echo "🛑 Stopping AI Employee Watchers..."

# Kill processes
if [ -f /tmp/gmail_watcher.pid ]; then
    kill $(cat /tmp/gmail_watcher.pid) 2>/dev/null && echo "✅ Gmail Watcher stopped"
    rm -f /tmp/gmail_watcher.pid
fi

if [ -f /tmp/fs_watcher.pid ]; then
    kill $(cat /tmp/fs_watcher.pid) 2>/dev/null && echo "✅ File System Watcher stopped"
    rm -f /tmp/fs_watcher.pid
fi

if [ -f /tmp/orchestrator.pid ]; then
    kill $(cat /tmp/orchestrator.pid) 2>/dev/null && echo "✅ Orchestrator stopped"
    rm -f /tmp/orchestrator.pid
fi

echo ""
echo "✅ All watchers stopped!"
