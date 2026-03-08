#!/bin/bash
# Silver Tier Final Verification Script
# Tests all Silver Tier requirements

echo "🥈 SILVER TIER - FINAL VERIFICATION"
echo "===================================="
echo ""
echo "Date: $(date)"
echo "Testing all Silver Tier requirements..."
echo ""

BASE_DIR="/mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)"
VAULT="AI_Employee_Vault"
cd "$BASE_DIR"

PASS=0
FAIL=0

test_requirement() {
    local name="$1"
    local command="$2"
    
    echo -n "Testing: $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo "✅ PASS"
        ((PASS++))
        return 0
    else
        echo "❌ FAIL"
        ((FAIL++))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. WATCHER SCRIPTS (2+ required)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_requirement "Gmail Watcher exists" \
    "test -f skills/watchers/gmail-watcher/gmail_watcher.py"

test_requirement "File System Watcher exists" \
    "test -f watchers/filesystem_watcher.py"

test_requirement "Gmail Watcher syntax" \
    "python3 -m py_compile skills/watchers/gmail-watcher/gmail_watcher.py"

test_requirement "File System Watcher syntax" \
    "python3 -m py_compile watchers/filesystem_watcher.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. LINKEDIN AUTO-POST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_requirement "LinkedIn Content Generator exists" \
    "test -f skills/actions/post-linkedin/content_generator.py"

test_requirement "LinkedIn Post Skill exists" \
    "test -f skills/actions/post-linkedin/post_linkedin.py"

test_requirement "LinkedIn Auto-Post Script exists" \
    "test -f linkedin-auto-post.sh"

test_requirement "LinkedIn Auto-Post Script executable" \
    "test -x linkedin-auto-post.sh"

test_requirement "LinkedIn Content Generator works" \
    "python3 skills/actions/post-linkedin/content_generator.py $VAULT --generate --count 1"

test_requirement "LinkedIn post file created" \
    "ls $VAULT/Pending_Approval/LINKEDIN_POST_*.md 2>/dev/null | head -1"

test_requirement "LinkedIn session exists" \
    "test -d skills/watchers/linkedin-watcher/linkedin_session"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. CREATE PLAN SKILL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_requirement "Create Plan skill exists" \
    "test -f skills/actions/create-plan/create_plan.py"

test_requirement "Create Plan syntax" \
    "python3 -m py_compile skills/actions/create-plan/create_plan.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. SEND EMAIL SKILL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_requirement "Send Email skill exists" \
    "test -f skills/actions/send-email/send_email.py"

test_requirement "Send Email syntax" \
    "python3 -m py_compile skills/actions/send-email/send_email.py"

test_requirement "Email MCP Server exists" \
    "test -f skills/mcp-servers/email-mcp/email_mcp_server.js"

test_requirement "Gmail credentials exist" \
    "test -f credentials.json"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. HUMAN-IN-THE-LOOP APPROVAL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_requirement "Pending_Approval folder exists" \
    "test -d $VAULT/Pending_Approval"

test_requirement "Approved folder exists" \
    "test -d $VAULT/Approved"

test_requirement "Rejected folder exists" \
    "test -d $VAULT/Rejected"

test_requirement "Done folder exists" \
    "test -d $VAULT/Done"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. QWEN ORCHESTRATOR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_requirement "Qwen Orchestrator exists" \
    "test -f qwen_orchestrator.py"

test_requirement "Qwen Orchestrator syntax" \
    "python3 -m py_compile qwen_orchestrator.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. CRON SCHEDULING"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_requirement "Cron Setup Script exists" \
    "test -f setup-cron-jobs.sh"

test_requirement "Cron Setup Script executable" \
    "test -x setup-cron-jobs.sh"

test_requirement "PM2 Setup Script exists" \
    "test -f setup-pm2.sh"

test_requirement "PM2 Setup Script executable" \
    "test -x setup-pm2.sh"

test_requirement "Start Watchers Script exists" \
    "test -f start-watchers.sh"

test_requirement "Start Watchers Script executable" \
    "test -x start-watchers.sh"

test_requirement "Stop Watchers Script exists" \
    "test -f stop-watchers.sh"

test_requirement "Stop Watchers Script executable" \
    "test -x stop-watchers.sh"

test_requirement "Check Status Script exists" \
    "test -f check-watchers-status.sh"

test_requirement "Check Status Script executable" \
    "test -x check-watchers-status.sh"

test_requirement "Cron script syntax valid" \
    "bash -n setup-cron-jobs.sh"

test_requirement "PM2 script syntax valid" \
    "bash -n setup-pm2.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. VAULT STRUCTURE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_requirement "Needs_Action folder exists" \
    "test -d $VAULT/Needs_Action"

test_requirement "Plans folder exists" \
    "test -d $VAULT/Plans"

test_requirement "Dashboard.md exists" \
    "test -f $VAULT/Dashboard.md"

test_requirement "Business_Goals.md exists" \
    "test -f $VAULT/Business_Goals.md"

test_requirement "Company_Handbook.md exists" \
    "test -f $VAULT/Company_Handbook.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VERIFICATION SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Passed: $PASS"
echo "❌ Failed: $FAIL"
echo ""

TOTAL=$((PASS + FAIL))
PERCENTAGE=$((PASS * 100 / TOTAL))

echo "Completion: $PERCENTAGE%"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 SUCCESS! All Silver Tier requirements met!"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Setup scheduling: ./setup-cron-jobs.sh OR ./setup-pm2.sh"
    echo "   2. Test LinkedIn post: ./linkedin-auto-post.sh"
    echo "   3. Send test email and verify workflow"
    echo "   4. Record demo video"
    echo "   5. Submit: https://forms.gle/JR9T1SJq5rmQyGkGA"
    echo ""
    echo "📖 Documentation:"
    echo "   • LINKEDIN_AND_CRON_SETUP.md - Complete setup guide"
    echo "   • GMAIL_WATCHER_FLOW_GUIDE.md - Email workflow details"
    echo "   • SILVER_TIER_COMPLETION_GUIDE.md - Implementation guide"
    exit 0
else
    echo "⚠️  Some requirements failed. Please fix the issues above."
    exit 1
fi
