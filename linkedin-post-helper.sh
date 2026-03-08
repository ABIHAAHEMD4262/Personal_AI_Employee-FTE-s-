#!/bin/bash
# LinkedIn Auto-Post Helper - Semi-automated posting
# Generates content, copies to clipboard, you paste and post

VAULT="AI_Employee_Vault"

echo "📝 LinkedIn Post Generator"
echo "=========================="
echo ""

# Generate or use provided content
if [ -n "$1" ]; then
    CONTENT="$*"
else
    # Generate content using content writer
    echo "🤖 Generating content..."
    CONTENT=$(python skills/utils/linkedin-content-writer/content_writer.py $VAULT \
        --topic "AI automation" --style "thought-leadership" 2>/dev/null | \
        grep -A 100 "GENERATED" | tail -n +3 | head -20)
fi

echo "✅ Generated content:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$CONTENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Try to copy to clipboard
if command -v xclip &> /dev/null; then
    echo "$CONTENT" | xclip -selection clipboard
    echo "✅ Copied to clipboard!"
elif command -v xsel &> /dev/null; then
    echo "$CONTENT" | xsel --clipboard
    echo "✅ Copied to clipboard!"
elif command -v wl-copy &> /dev/null; then
    echo "$CONTENT" | wl-copy
    echo "✅ Copied to clipboard!"
else
    echo "⚠️  Cannot copy to clipboard (no xclip/xsel/wl-copy)"
    echo "   Please copy manually from above."
fi

echo ""
echo "📋 Next steps:"
echo "   1. Open: https://www.linkedin.com/feed/"
echo "   2. Click 'Start a post'"
echo "   3. Paste the content"
echo "   4. Click 'Post'"
echo ""
echo "🔗 Open LinkedIn: https://www.linkedin.com/feed/"

# Optionally open browser
if command -v xdg-open &> /dev/null; then
    read -p "Open LinkedIn in browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open "https://www.linkedin.com/feed/"
    fi
fi
