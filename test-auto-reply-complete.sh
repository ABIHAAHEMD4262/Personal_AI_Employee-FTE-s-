#!/bin/bash
# Complete Auto Email Reply Test
# Tests the full workflow from email to reply

VAULT="AI_Employee_Vault"

echo "📧 Auto Email Reply - Complete Test"
echo "===================================="
echo ""

# Step 1: Check for email files in Needs_Action
echo "1️⃣ Checking Needs_Action folder..."
EMAIL_FILE=$(ls -t $VAULT/Needs_Action/EMAIL_*.md 2>/dev/null | head -1)

if [ -z "$EMAIL_FILE" ]; then
    echo "  ⚠️  No email files found in Needs_Action"
    echo ""
    echo "  Run Gmail Watcher first:"
    echo "  python skills/watchers/gmail-watcher/gmail_watcher.py $VAULT --once"
    exit 1
fi

echo "  ✅ Found: $(basename $EMAIL_FILE)"

# Step 2: Show email content
echo ""
echo "2️⃣ Email content:"
echo "  ---"
head -25 "$EMAIL_FILE"
echo "  ---"

# Step 3: Approve (move to Approved)
echo ""
echo "3️⃣ Approving email (moving to Approved)..."
mv "$EMAIL_FILE" "$VAULT/Approved/"

if [ $? -eq 0 ]; then
    echo "  ✅ Approved!"
else
    echo "  ❌ Failed to approve"
    exit 1
fi

# Step 4: Run auto-reply
echo ""
echo "4️⃣ Running auto-reply..."
python skills/actions/auto-reply/auto_reply.py $VAULT

# Step 5: Check result
echo ""
echo "5️⃣ Checking result..."

# Check if file moved to Done
TODAY=$(date +%Y-%m-%d)
if [ -f "$VAULT/Done/$TODAY/$(basename $EMAIL_FILE)" ]; then
    echo "  ✅ Email processed and moved to Done!"
else
    echo "  ⚠️  Check status manually"
    ls -la $VAULT/Done/$TODAY/ 2>/dev/null
fi

echo ""
echo "===================================="
echo "✅ Test Complete!"
echo "===================================="
echo ""
echo "Check your Gmail sent folder to verify the reply was sent."
