#!/bin/bash
# Cron Job Setup for AI Employee
# Sets up automated scheduling for all watchers and LinkedIn posting

echo "🤖 AI Employee - Cron Job Setup"
echo "================================"
echo ""

BASE_DIR="/mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)"
VAULT_PATH="/mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)/AI_Employee_Vault"

# Escape parentheses for cron
BASE_DIR_ESCAPED=$(echo "$BASE_DIR" | sed 's/(/\\(/g' | sed 's/)/\\)/g')
VAULT_PATH_ESCAPED=$(echo "$VAULT_PATH" | sed 's/(/\\(/g' | sed 's/)/\\)/g')

echo "Base Directory: $BASE_DIR"
echo "Vault Path: $VAULT_PATH"
echo ""

# Create log directory
LOG_DIR="/tmp/ai-employee"
mkdir -p "$LOG_DIR"
echo "✅ Log directory created: $LOG_DIR"

# Backup existing crontab
if crontab -l > /tmp/ai-employee-cron-backup.txt 2>/dev/null; then
    echo "✅ Existing crontab backed up to /tmp/ai-employee-cron-backup.txt"
else
    echo "ℹ️  No existing crontab found"
fi

# Create new crontab entries
CRON_ENTRIES="# AI Employee - Automated Scheduling
# Generated on $(date)

# Environment setup
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

# Start watchers on boot (runs once at system startup)
@reboot cd $BASE_DIR_ESCAPED && ./start-watchers.sh >> $LOG_DIR/startup.log 2>&1

# Gmail Watcher - Check every 2 minutes
*/2 * * * * cd $BASE_DIR_ESCAPED && python3 skills/watchers/gmail-watcher/gmail_watcher.py $VAULT_PATH_ESCAPED --interval 120 --once >> $LOG_DIR/gmail_watcher.log 2>&1

# File System Watcher - Check every minute
* * * * * cd $BASE_DIR_ESCAPED && python3 watchers/filesystem_watcher.py $VAULT_PATH_ESCAPED --interval 30 --once >> $LOG_DIR/fs_watcher.log 2>&1

# Qwen Orchestrator - Check every minute
* * * * * cd $BASE_DIR_ESCAPED && python3 qwen_orchestrator.py $VAULT_PATH_ESCAPED --watch --interval 30 >> $LOG_DIR/orchestrator.log 2>&1

# LinkedIn Auto-Post - Every Monday, Wednesday, Friday at 9:00 AM
0 9 * * 1,3,5 cd $BASE_DIR_ESCAPED && python3 skills/actions/post-linkedin/content_generator.py $VAULT_PATH_ESCAPED --generate >> $LOG_DIR/linkedin_content.log 2>&1

# Daily Dashboard Update - Every day at 8:00 AM
0 8 * * * cd $BASE_DIR_ESCAPED && python3 qwen_orchestrator.py $VAULT_PATH_ESCAPED --update-dashboard >> $LOG_DIR/dashboard.log 2>&1

# Weekly Business Audit - Every Sunday at 10:00 PM
0 22 * * 0 cd $BASE_DIR_ESCAPED && python3 qwen_orchestrator.py $VAULT_PATH_ESCAPED --weekly-audit >> $LOG_DIR/weekly_audit.log 2>&1

# Health Check - Every hour (restart if needed)
0 * * * * cd $BASE_DIR_ESCAPED && ./check-watchers-status.sh | grep -q \"❌\" && ./start-watchers.sh >> $LOG_DIR/health_check.log 2>&1

# Log Rotation - Daily at midnight (keep last 7 days)
0 0 * * * find $LOG_DIR -name \"*.log\" -mtime +7 -delete 2>/dev/null
"

# Add to crontab
echo "$CRON_ENTRIES" | crontab -

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Cron jobs installed successfully!"
    echo ""
    echo "📋 Installed Jobs:"
    echo "   • Gmail Watcher: Every 2 minutes"
    echo "   • File System Watcher: Every minute"
    echo "   • Qwen Orchestrator: Every minute"
    echo "   • LinkedIn Content Generation: Mon/Wed/Fri at 9:00 AM"
    echo "   • Daily Dashboard Update: 8:00 AM daily"
    echo "   • Weekly Business Audit: Sunday 10:00 PM"
    echo "   • Health Check: Every hour"
    echo ""
    echo "📊 View logs:"
    echo "   tail -f $LOG_DIR/gmail_watcher.log"
    echo "   tail -f $LOG_DIR/orchestrator.log"
    echo "   tail -f $LOG_DIR/linkedin_content.log"
    echo ""
    echo "📋 View all cron jobs:"
    echo "   crontab -l"
    echo ""
    echo "🗑️  Remove all AI Employee cron jobs:"
    echo "   crontab -r"
    echo ""
    echo "📁 Log location: $LOG_DIR"
else
    echo ""
    echo "❌ Failed to install cron jobs"
    exit 1
fi
