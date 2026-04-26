# Facebook & Instagram MCP Server Setup Guide

This guide walks you through setting up Facebook and Instagram integration for your AI Employee.

## Prerequisites

1. A Facebook account with admin access to a Facebook Page
2. (Optional) Instagram Business Account linked to your Facebook Page
3. Node.js v24+ installed
4. Facebook Developer account

## Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. Select **Business** as the app type
4. Fill in:
   - App Name: `AI Employee`
   - App Contact Email: your email
5. Click **Create App**

## Step 2: Add Facebook Login Product

1. In your app dashboard, scroll down to **Add Products to Your App**
2. Find **Facebook Login** and click **Set Up**
3. Select **Web** as the platform
4. Enter your site URL (can be `http://localhost` for testing)
5. Save

## Step 3: Configure Permissions

1. Go to **App Review** → **Permissions and Features**
2. Request the following permissions:
   - `pages_manage_posts` - Create posts on your Page
   - `pages_read_engagement` - Read Page insights
   - `pages_show_list` - Access your Pages
   - `instagram_basic` - Basic Instagram access (if using Instagram)
   - `instagram_content_publish` - Publish Instagram posts (if using Instagram)
   - `pages_read_user_content` - Read Page content
   - `pages_manage_engagement` - Manage comments

3. Submit for review (for personal use, you can stay in Development Mode)

## Step 4: Get Page Access Token

### Option A: Using Graph API Explorer (Recommended for Testing)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **Get Token** → **Get Page Access Token**
4. Select the permissions you need
5. Copy the generated token
6. **Important**: This is a short-lived token (~1 hour)

### Option B: Generate Long-Lived Token (Recommended for Production)

1. Get a short-lived User Token from Graph API Explorer
2. Exchange it for a long-lived token:

```bash
# Replace with your values
APP_ID=your_app_id
APP_SECRET=your_app_secret
SHORT_LIVED_TOKEN=your_short_lived_token

curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=${APP_ID}&client_secret=${APP_SECRET}&fb_exchange_token=${SHORT_LIVED_TOKEN}"
```

3. Copy the long-lived token (valid for 60 days)

## Step 5: Get Your Page ID

1. Go to your Facebook Page
2. Click **About** → **Page Info**
3. Scroll down to find **Page ID**
4. Alternatively, use Graph API Explorer:

```bash
# Get your pages
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_ACCESS_TOKEN"
```

The response will include your page ID:
```json
{
  "data": [
    {
      "name": "Your Page Name",
      "access_token": "PAGE_ACCESS_TOKEN",
      "id": "YOUR_PAGE_ID"
    }
  ]
}
```

## Step 6: (Optional) Get Instagram Business Account ID

1. Link your Instagram account to your Facebook Page:
   - Go to your Facebook Page
   - Click **Settings** → **Linked Accounts**
   - Connect your Instagram Business account

2. Get the Instagram Account ID:

```bash
curl -X GET "https://graph.facebook.com/v18.0/YOUR_PAGE_ID?fields=instagram_business_account&access_token=YOUR_PAGE_ACCESS_TOKEN"
```

Response:
```json
{
  "instagram_business_account": {
    "id": "YOUR_INSTAGRAM_ACCOUNT_ID"
  }
}
```

## Step 7: Configure Environment Variables

1. Copy the `.env.example` file to `.env`:

```bash
cd skills/mcp-servers/facebook-mcp
cp .env.example .env
```

2. Edit `.env` with your values:

```env
FACEBOOK_ACCESS_TOKEN=your_long_lived_page_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id  # Optional
```

## Step 8: Test the MCP Server

1. Start the server:

```bash
cd skills/mcp-servers/facebook-mcp
npm start
```

2. You should see:
```
✅ Facebook MCP Server running on stdio

Available tools:
  📘 Facebook:
    facebook_create_post - Create page post
    facebook_get_posts - Get recent posts
    facebook_get_insights - Get page analytics
    ...
```

3. Test with the Python client:

```bash
cd skills/actions/facebook
python facebook_mcp_client.py get_posts --limit 5
```

## Step 9: Create Your First Post

```bash
python facebook_create_post.py /path/to/vault \
  --message "Hello from AI Employee! 🤖" \
  --hashtags "#AI #Automation"
```

This will create an approval request in your vault's `Pending_Approval` folder.

## Troubleshooting

### Error: "Missing required environment variables"

- Ensure `.env` file exists and has correct values
- Check that there are no extra spaces or quotes around values

### Error: "Facebook API Error: Invalid OAuth access token"

- Your token has expired. Generate a new long-lived token
- Long-lived tokens expire after 60 days. Set a reminder to renew

### Error: "Unsupported get request"

- Verify your Page ID is correct
- Ensure your access token has `pages_show_list` permission

### Error: "Permissions error"

- Go to your App Dashboard → **App Review**
- Ensure all required permissions are approved
- For Development Mode, add your Facebook account as a tester

### Instagram Posts Not Working

- Ensure Instagram account is converted to **Business Account**
- Verify Instagram is linked to Facebook Page
- Check `INSTAGRAM_ACCOUNT_ID` is correct in `.env`

## Token Renewal Reminder

Set a calendar reminder for **55 days** from when you generate your long-lived token to renew it before expiration.

To check token expiry:

```bash
curl -X GET "https://graph.facebook.com/v18.0/debug_token?input_token=YOUR_TOKEN&access_token=YOUR_APP_ID|APP_SECRET"
```

## Security Notes

⚠️ **NEVER commit your `.env` file to Git!**

- The `.env` file is already in `.gitignore`
- Store backup copies in a secure password manager
- Rotate tokens regularly
- Use separate tokens for development and production

## Next Steps

After successful setup:

1. Test posting to Facebook
2. Generate insights reports
3. Set up scheduled posts via the scheduler
4. Integrate with CEO Briefing for weekly analytics

## API Rate Limits

- **Page Posts**: 250 per hour
- **Insights**: 200 per hour
- **Comments**: 250 per hour

The MCP server handles rate limiting automatically. If you hit limits, it will retry after the cooldown period.

## Additional Resources

- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [Instagram API Documentation](https://developers.facebook.com/docs/instagram-api)
- [Page Access Token Guide](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
