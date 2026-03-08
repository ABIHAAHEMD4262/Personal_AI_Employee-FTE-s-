#!/bin/bash
# Start all AI Employee watchers

VAULT_PATH="/mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)/AI_Employee_Vault"
BASE_DIR="/mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)"

cd "$BASE_DIR"

echo "🚀 Starting AI Employee Watchers..."

# Start Gmail Watcher
echo "📧 Starting Gmail Watcher..."
python3 skills/watchers/gmail-watcher/gmail_watcher.py "$VAULT_PATH" --interval 120 &
GMAIL_PID=$!
echo "   Gmail Watcher PID: $GMAIL_PID"

# Start File System Watcher
echo "📁 Starting File System Watcher..."
python3 watchers/filesystem_watcher.py "$VAULT_PATH" --interval 30 &
FS_PID=$!
echo "   File System Watcher PID: $FS_PID"

# Start Qwen Orchestrator
echo "🤖 Starting Qwen Orchestrator..."
python3 qwen_orchestrator.py "$VAULT_PATH" --watch --interval 30 &
ORCH_PID=$!
echo "   Orchestrator PID: $ORCH_PID"

# Save PIDs
echo "$GMAIL_PID" > /tmp/gmail_watcher.pid
echo "$FS_PID" > /tmp/fs_watcher.pid
echo "$ORCH_PID" > /tmp/orchestrator.pid

echo ""
echo "✅ All watchers started!"
echo ""
echo "To stop: ./stop-watchers.sh"
echo "To check status: ./check-watchers-status.sh"
echo ""
echo "View logs: tail -f /tmp/ai-employee.log"
echo ""

# Redirect output to log file
exec >> /tmp/ai-employee.log 2>&1

# Wait for all background processes
wait
