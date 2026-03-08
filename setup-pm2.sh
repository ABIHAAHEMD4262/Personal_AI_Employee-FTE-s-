#!/bin/bash
# PM2 Setup for AI Employee - Production-ready process management
# PM2 is easier to manage than cron for long-running processes

echo "🤖 AI Employee - PM2 Setup"
echo "=========================="
echo ""

BASE_DIR="/mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)"
VAULT_PATH="/mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)/AI_Employee_Vault"

cd "$BASE_DIR"

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "⚠️  PM2 not found. Installing..."
    npm install -g pm2
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install PM2"
        echo "   Run: npm install -g pm2"
        exit 1
    fi
    echo "✅ PM2 installed"
fi

echo "✅ PM2 available: $(pm2 -v)"
echo ""

# Stop any existing AI Employee processes
echo "🛑 Stopping existing AI Employee processes..."
pm2 stop ai-employee-all 2>/dev/null || true
pm2 delete ai-employee-all 2>/dev/null || true
echo ""

# Start Gmail Watcher
echo "📧 Starting Gmail Watcher..."
pm2 start skills/watchers/gmail-watcher/gmail_watcher.py \
  --name "ai-gmail-watcher" \
  --interpreter python3 \
  -- \
  "$VAULT_PATH" \
  --interval 120 \
  --log "$BASE_DIR/logs/gmail_watcher.log"

# Start File System Watcher
echo "📁 Starting File System Watcher..."
pm2 start watchers/filesystem_watcher.py \
  --name "ai-fs-watcher" \
  --interpreter python3 \
  -- \
  "$VAULT_PATH" \
  --interval 30 \
  --log "$BASE_DIR/logs/fs_watcher.log"

# Start Qwen Orchestrator
echo "🤖 Starting Qwen Orchestrator..."
pm2 start qwen_orchestrator.py \
  --name "ai-orchestrator" \
  --interpreter python3 \
  -- \
  "$VAULT_PATH" \
  --watch \
  --interval 30 \
  --log "$BASE_DIR/logs/orchestrator.log"

# Wait for processes to start
sleep 3

echo ""
echo "💾 Saving PM2 configuration..."
pm2 save --force

echo ""
echo "⚙️  Setting up PM2 startup..."
# Get the startup command for this system
pm2 startup | tail -1 | bash 2>/dev/null || true

echo ""
echo "✅ PM2 Setup Complete!"
echo ""
echo "📊 Process Status:"
pm2 status ai-gmail-watcher ai-fs-watcher ai-orchestrator
echo ""
echo "📋 PM2 Commands:"
echo "   pm2 status                    # Check status"
echo "   pm2 logs                      # View all logs"
echo "   pm2 logs ai-gmail-watcher     # View Gmail logs"
echo "   pm2 restart all               # Restart all"
echo "   pm2 stop all                  # Stop all"
echo "   pm2 delete all                # Remove all"
echo "   pm2 monit                     # Real-time monitoring"
echo ""
echo "📁 Log files: $BASE_DIR/logs/"
echo ""
echo "🔄 To auto-start on boot, run the command shown above (pm2 startup)"
