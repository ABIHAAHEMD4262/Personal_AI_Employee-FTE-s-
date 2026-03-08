#!/usr/bin/env python3
"""Fix token format by adding credentials"""

import json
from pathlib import Path

# Load credentials
creds = json.load(open('credentials.json'))
token = json.load(open('skills/mcp-servers/email-mcp/token.json'))

# Add missing fields
token['client_id'] = creds['installed']['client_id']
token['client_secret'] = creds['installed']['client_secret']

# Save updated token
json.dump(token, open('skills/mcp-servers/email-mcp/token.json', 'w'), indent=2)

print("✅ Token updated with client_id and client_secret")
print("📁 Token saved to: skills/mcp-servers/email-mcp/token.json")
print("\nNow test email sending:")
print("  python3 test-send-email.py")
