#!/bin/bash
# Test Complete Workflow
# Tests: Gmail Watcher → Orchestrator → Plan → Approval → Send → Done

VAULT="AI_Employee_Vault"

echo "🤖 Complete Email Workflow Test"
echo "================================"
echo ""

# Check prerequisites
echo "1️⃣ Checking prerequisites..."

if ! python -c "from google.oauth2.credentials import Credentials" 2>/dev/null; then
    echo "  ❌ Gmail dependencies not installed"
    exit 1
fi
echo "  ✅ Gmail dependencies OK"

if [ ! -f "skills/watchers/gmail-watcher/credentials.json" ]; then
    echo "  ❌ Gmail credentials not found"
    exit 1
fi
echo "  ✅ Credentials OK"

echo ""
echo "================================"
echo "✅ Prerequisites OK!"
echo "================================"
echo ""
echo "📋 NEXT: Start the workflow"
echo ""
echo "Terminal 1 - Gmail Watcher:"
echo "  python skills/watchers/gmail-watcher/gmail_watcher.py $VAULT --interval 60"
echo ""
echo "Terminal 2 - Qwen Orchestrator:"
echo "  python qwen_orchestrator.py $VAULT --watch --interval 30"
echo ""
echo "Then send a test email to: abihacodes@gmail.com"
echo "(Star the email to mark as important)"
echo ""
echo "When email appears in Pending_Approval:"
echo "  mv $VAULT/Pending_Approval/*.md $VAULT/Approved/"
echo ""
echo "The rest is automatic! ✨"
