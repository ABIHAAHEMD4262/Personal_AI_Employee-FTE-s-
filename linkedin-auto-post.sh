#!/bin/bash
# LinkedIn Auto-Post for Business - Generates and posts content to generate sales
# This script generates a business post, creates approval file, and can auto-post

VAULT="AI_Employee_Vault"
BASE_DIR="/mnt/g/Hackathon_0/Personal_AI_Employee(FTE's)"

cd "$BASE_DIR"

echo "🚀 LinkedIn Auto-Post for Business"
echo "===================================="
echo ""

# Generate content
echo "📝 Generating LinkedIn post content..."
python3 skills/actions/post-linkedin/content_generator.py $VAULT \
  --generate \
  --style mixed

if [ $? -ne 0 ]; then
    echo "❌ Failed to generate content"
    exit 1
fi

echo ""
echo "✅ Content generated successfully!"
echo ""

# Find the generated file
POST_FILE=$(ls -t $VAULT/Pending_Approval/LINKEDIN_POST_*.md 2>/dev/null | head -1)

if [ -z "$POST_FILE" ]; then
    echo "❌ No post file found"
    exit 1
fi

echo "📄 Created: $POST_FILE"
echo ""

# Show content
echo "📋 Post Content:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$POST_FILE" | grep -A 1000 "## Content" | tail -n +2 | head -20
echo "..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if auto-approve
if [ "$1" == "--auto-approve" ]; then
    echo "⚡ Auto-approve mode: Moving to Approved..."
    mv "$POST_FILE" "$VAULT/Approved/"
    
    echo "🚀 Posting to LinkedIn..."
    python3 skills/actions/post-linkedin/post_linkedin.py $VAULT --execute
    
    if [ $? -eq 0 ]; then
        echo "✅ Posted to LinkedIn successfully!"
    else
        echo "❌ Failed to post to LinkedIn"
    fi
else
    echo "📋 Next Steps:"
    echo "   1. Review the post in: $VAULT/Pending_Approval/"
    echo "   2. If approved, move to: $VAULT/Approved/"
    echo "   3. Run: python3 skills/actions/post-linkedin/post_linkedin.py $VAULT --execute"
    echo ""
    echo "🔗 Or auto-approve now with: $0 --auto-approve"
fi
