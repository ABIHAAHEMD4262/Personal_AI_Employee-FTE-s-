# Facebook/Instagram MCP Server

Model Context Protocol (MCP) server for Facebook and Instagram integration via Graph API.

## Features

- **Facebook Page Management**: Create posts, get insights, manage comments
- **Instagram Business**: Create posts, get media, analytics
- **Social Media Summary**: Generate comprehensive reports for CEO briefings

## Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your Facebook credentials
nano .env
```

## Configuration

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Select "Business" app type
4. Fill in app details

### Step 2: Get Page Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Click "Generate Access Token"
4. Grant these permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_insights`

5. Copy the generated access token

### Step 3: Get Page ID

1. Go to your Facebook Page
2. Click "About"
3. Find "Page ID" (or use Graph API Explorer: `me/accounts`)

### Step 4: Get Instagram Business Account ID (Optional)

1. Convert to Instagram Business Account
2. Connect to Facebook Page
3. Get ID via Graph API: `me/instagram_business_account`

### Step 5: Configure .env

```env
# Facebook Settings
FACEBOOK_ACCESS_TOKEN=your-page-access-token-here
FACEBOOK_PAGE_ID=your-page-id-here

# Instagram Settings (optional)
INSTAGRAM_ACCOUNT_ID=your-instagram-business-account-id
```

## Usage

### Start Server

```bash
npm start
```

### Available Tools

#### Facebook

| Tool | Description |
|------|-------------|
| `facebook_create_post` | Create a new Facebook post |
| `facebook_get_posts` | Get recent page posts |
| `facebook_get_insights` | Get page analytics |
| `facebook_get_post_insights` | Get specific post analytics |
| `facebook_create_comment` | Post a comment |
| `facebook_get_comments` | Get post comments |

#### Instagram

| Tool | Description |
|------|-------------|
| `instagram_create_post` | Create Instagram post (image/video) |
| `instagram_get_media` | Get recent media |
| `instagram_get_insights` | Get Instagram analytics |

#### Summary

| Tool | Description |
|------|-------------|
| `facebook_generate_summary` | Generate comprehensive social media report |

## Example Usage

### Create Facebook Post

```javascript
const result = await mcp.callTool('facebook_create_post', {
  message: 'Excited to announce our new product launch! 🚀',
  link: 'https://example.com/product',
  photo_url: 'https://example.com/image.jpg'
});
```

### Get Page Insights

```javascript
const result = await mcp.callTool('facebook_get_insights', {
  metrics: ['page_impressions', 'page_engaged_users', 'page_post_engagements'],
  period: 'week'
});
```

### Create Instagram Post

```javascript
const result = await mcp.callTool('instagram_create_post', {
  image_url: 'https://example.com/image.jpg',
  caption: 'Beautiful day! ☀️ #lifestyle'
});
```

### Generate Social Media Summary

```javascript
const result = await mcp.callTool('facebook_generate_summary', {
  include_facebook: true,
  include_instagram: true,
  days: 7
});
```

## Integration with AI Employee

Add to your MCP configuration:

```json
{
  "servers": [
    {
      "name": "facebook",
      "command": "node",
      "args": ["/path/to/skills/mcp-servers/facebook-mcp/index.js"],
      "cwd": "/path/to/skills/mcp-servers/facebook-mcp",
      "env": {
        "FACEBOOK_ACCESS_TOKEN": "your-token",
        "FACEBOOK_PAGE_ID": "your-page-id",
        "INSTAGRAM_ACCOUNT_ID": "your-ig-account-id"
      }
    }
  ]
}
```

## Approval Workflow

For Gold Tier, all social media posts should go through approval:

1. Create post draft in `/Pending_Approval/`
2. User reviews and moves to `/Approved/`
3. MCP server publishes the post
4. Result logged to `/Logs/`

Example approval file:

```markdown
---
type: approval_request
action: facebook_post
message: "Excited to announce..."
scheduled_time: "2026-01-07T10:00:00Z"
status: pending
---

# Facebook Post Approval

**Message**: Excited to announce our new product!

**Link**: https://example.com/product

**To Approve**: Move to /Approved folder
```

## Troubleshooting

### Token Expired

Facebook tokens expire. Generate a long-lived token:

```bash
# Exchange short-lived token for long-lived (valid 60 days)
curl -G "https://graph.facebook.com/v18.0/oauth/access_token" \
  -d grant_type=fb_exchange_token \
  -d client_id={app-id} \
  -d client_secret={app-secret} \
  -d fb_exchange_token={short-lived-token}
```

### Permission Denied

- Check token has required permissions
- Re-authorize with Graph API Explorer
- Ensure page role is Admin or Editor

### Instagram Post Fails

- Must be Instagram Business Account
- Must be connected to Facebook Page
- Check account is in `INSTAGRAM_ACCOUNT_ID`

## Development

```bash
# Run in development mode (auto-reload)
npm run dev

# Run tests
npm test
```

## Resources

- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Facebook Permissions](https://developers.facebook.com/docs/permissions/)

## Security Notes

- Never commit `.env` file with tokens
- Rotate access tokens regularly
- Use app roles to limit access
- Monitor API usage for anomalies
