#!/bin/bash
# Check if watchers are running

echo "📊 AI Employee Watchers Status"
echo "=============================="
echo ""

check_process() {
    local name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "✅ $name: Running (PID: $pid)"
            return 0
        else
            echo "❌ $name: Not running (stale PID file)"
            return 1
        fi
    else
        echo "❌ $name: Not started"
        return 1
    fi
}

check_process "Gmail Watcher" "/tmp/gmail_watcher.pid"
check_process "File System Watcher" "/tmp/fs_watcher.pid"
check_process "Orchestrator" "/tmp/orchestrator.pid"

echo ""
echo "To start: ./start-watchers.sh"
echo "To stop: ./stop-watchers.sh"
echo ""
echo "View logs: tail -f /tmp/ai-employee.log"
