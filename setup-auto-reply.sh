#!/bin/bash
# Auto Email Reply Setup & Test
# Complete workflow test for automated email replies

VAULT="AI_Employee_Vault"

echo "📧 Auto Email Reply - Complete Setup"
echo "====================================="
echo ""

# Step 1: Check prerequisites
echo "1️⃣ Checking prerequisites..."

if ! python -c "from google.oauth2.credentials import Credentials" 2>/dev/null; then
    echo "  ❌ Gmail dependencies not installed"
    echo "     Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
    exit 1
fi
echo "  ✅ Gmail dependencies OK"

if [ ! -f "skills/watchers/gmail-watcher/credentials.json" ]; then
    echo "  ❌ Gmail credentials not found"
    echo "     Check: skills/watchers/gmail-watcher/credentials.json"
    exit 1
fi
echo "  ✅ Credentials OK"

# Step 2: Start Gmail Watcher (background)
echo ""
echo "2️⃣ Starting Gmail Watcher in background..."
python skills/watchers/gmail-watcher/gmail_watcher.py $VAULT --interval 30 &
WATCHER_PID=$!
echo "  ✅ Gmail Watcher started (PID: $WATCHER_PID)"

# Step 3: Instructions
echo ""
echo "====================================="
echo "✅ Setup Complete!"
echo "====================================="
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Send a test email to: abihacodes@gmail.com"
echo "   Subject: Test Email"
echo "   Content: Hello AI Employee"
echo "   ⭐ IMPORTANT: Mark as Important (star it)"
echo ""
echo "2. Wait ~30 seconds for Gmail Watcher to detect it"
echo ""
echo "3. Check for action file:"
echo "   ls -la $VAULT/Needs_Action/EMAIL_*.md"
echo ""
echo "4. Approve the email (move to Approved):"
echo "   mv $VAULT/Needs_Action/EMAIL_*.md $VAULT/Approved/"
echo ""
echo "5. Auto-reply will process and send:"
echo "   python skills/actions/auto-reply/auto_reply.py $VAULT"
echo ""
echo "====================================="
echo ""
echo "📝 OR run the complete test script:"
echo "   ./test-auto-reply-complete.sh"
echo ""

# Save watcher PID for cleanup
echo $WATCHER_PID > /tmp/gmail_watcher.pid

echo "To stop Gmail Watcher: kill $WATCHER_PID"
