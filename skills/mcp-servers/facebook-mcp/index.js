#!/usr/bin/env node
/**
 * Facebook/Instagram MCP Server - Gold Tier AI Employee
 * 
 * Provides Facebook and Instagram integration via Graph API
 * Capabilities: Post creation, insights, page management
 * 
 * Usage:
 *   npm start
 * 
 * Environment Variables:
 *   FACEBOOK_ACCESS_TOKEN - Page Access Token (required)
 *   FACEBOOK_PAGE_ID - Facebook Page ID (required)
 *   INSTAGRAM_ACCOUNT_ID - Instagram Business Account ID (optional)
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import fetch from 'node-fetch';
import dotenv from 'dotenv';

dotenv.config();

// Configuration
const FACEBOOK_ACCESS_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN;
const FACEBOOK_PAGE_ID = process.env.FACEBOOK_PAGE_ID;
const INSTAGRAM_ACCOUNT_ID = process.env.INSTAGRAM_ACCOUNT_ID;

// Validate configuration
if (!FACEBOOK_ACCESS_TOKEN || !FACEBOOK_PAGE_ID) {
  console.error('❌ Missing required environment variables:');
  console.error('   FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID');
  console.error('   Please create a .env file in skills/mcp-servers/facebook-mcp/');
  process.exit(1);
}

console.error('🔌 Facebook MCP Server starting...');
console.error(`   Page ID: ${FACEBOOK_PAGE_ID}`);
if (INSTAGRAM_ACCOUNT_ID) {
  console.error(`   Instagram Account: ${INSTAGRAM_ACCOUNT_ID}`);
}

/**
 * Facebook Graph API Client
 */
class FacebookClient {
  constructor(accessToken, pageId, instagramAccountId) {
    this.accessToken = accessToken;
    this.pageId = pageId;
    this.instagramAccountId = instagramAccountId;
    this.baseURL = 'https://graph.facebook.com/v18.0';
  }

  async get(url, params = {}) {
    const fullUrl = new URL(`${this.baseURL}${url}`);
    fullUrl.searchParams.append('access_token', this.accessToken);
    
    for (const [key, value] of Object.entries(params)) {
      fullUrl.searchParams.append(key, value);
    }

    const response = await fetch(fullUrl.toString());
    const result = await response.json();

    if (result.error) {
      throw new Error(`Facebook API Error: ${result.error.message}`);
    }

    return result;
  }

  async post(url, data = {}) {
    const fullUrl = `${this.baseURL}${url}`;
    
    const response = await fetch(fullUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...data,
        access_token: this.accessToken,
      }),
    });

    const result = await response.json();

    if (result.error) {
      throw new Error(`Facebook API Error: ${result.error.message}`);
    }

    return result;
  }

  // Post to Facebook Page
  async createPost(message, link = null, photoUrl = null) {
    const data = {
      message,
    };

    if (link) {
      data.link = link;
    }

    if (photoUrl) {
      data.photo = photoUrl;
    }

    return await this.post(`/${this.pageId}/feed`, data);
  }

  // Get Page posts
  async getPosts(limit = 10) {
    return await this.get(`/${this.pageId}/posts`, { limit });
  }

  // Get Page insights
  async getInsights(metrics = ['page_impressions', 'page_engaged_users', 'page_post_engagements'], period = 'day') {
    return await this.get(`/${this.pageId}/insights`, {
      metric: metrics.join(','),
      period,
    });
  }

  // Get comments on a post
  async getComments(postId, limit = 10) {
    return await this.get(`/${postId}/comments`, { limit });
  }

  // Create comment on a post
  async createComment(postId, message) {
    return await this.post(`/${postId}/comments`, { message });
  }

  // Instagram: Create media container
  async createInstagramMedia(imageUrl = null, videoUrl = null, caption = '') {
    if (!this.instagramAccountId) {
      throw new Error('Instagram Account ID not configured');
    }

    const mediaType = videoUrl ? 'VIDEO' : 'IMAGE';
    const mediaUrl = videoUrl || imageUrl;

    return await this.post(`/${this.instagramAccountId}/media`, {
      image_url: imageUrl,
      video_url: videoUrl,
      media_type: mediaType,
      caption,
    });
  }

  // Instagram: Publish media
  async publishInstagramMedia(containerId) {
    if (!this.instagramAccountId) {
      throw new Error('Instagram Account ID not configured');
    }

    return await this.post(`/${this.instagramAccountId}/media_publish`, {
      creation_id: containerId,
    });
  }

  // Instagram: Get insights
  async getInstagramInsights(metrics = ['impressions', 'reach', 'profile_views']) {
    if (!this.instagramAccountId) {
      throw new Error('Instagram Account ID not configured');
    }

    return await this.get(`/${this.instagramAccountId}/insights`, {
      metric: metrics.join(','),
    });
  }

  // Instagram: Get recent media
  async getInstagramMedia(limit = 10) {
    if (!this.instagramAccountId) {
      throw new Error('Instagram Account ID not configured');
    }

    return await this.get(`/${this.instagramAccountId}/media`, {
      limit,
      fields: 'id,caption,media_type,media_url,permalink,timestamp',
    });
  }
}

// Initialize client
const fbClient = new FacebookClient(FACEBOOK_ACCESS_TOKEN, FACEBOOK_PAGE_ID, INSTAGRAM_ACCOUNT_ID);

/**
 * Create MCP Server
 */
const server = new McpServer({
  name: 'facebook-mcp-server',
  version: '1.0.0',
  description: 'Facebook/Instagram integration for AI Employee',
});

// ============================================================================
// FACEBOOK PAGE TOOLS
// ============================================================================

server.tool(
  'facebook_create_post',
  'Create a new post on Facebook Page',
  {
    message: z.string().describe('Post message/content'),
    link: z.string().optional().describe('Optional link to share'),
    photo_url: z.string().optional().describe('Optional photo URL to share'),
  },
  async ({ message, link, photo_url }) => {
    try {
      const result = await fbClient.createPost(message, link, photo_url);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Facebook post created successfully!\n\n**Post ID**: ${result.id}\n\n${link ? `**Link**: ${link}` : ''}\n${photo_url ? `**Photo**: ${photo_url}` : ''}\n\nThe post is now live on your Facebook Page.`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error creating Facebook post: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'facebook_get_posts',
  'Get recent posts from Facebook Page',
  {
    limit: z.number().default(10).describe('Number of posts to retrieve'),
  },
  async ({ limit }) => {
    try {
      const result = await fbClient.getPosts(limit);
      const posts = result.data || [];

      if (posts.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '📭 No posts found on this page.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `📱 Recent Facebook Posts (${posts.length} found):\n\n${posts.map((post, i) => 
              `**${i + 1}. ${post.id}**\n` +
              `${post.message ? `${post.message.substring(0, 100)}${post.message.length > 100 ? '...' : ''}` : '[No text]'}\n` +
              `   Created: ${post.created_time || 'Unknown'}\n` +
              `   Likes: ${post.likes?.summary?.total_count || 0} | Comments: ${post.comments?.summary?.total_count || 0}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting posts: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'facebook_get_insights',
  'Get Facebook Page insights/analytics',
  {
    metrics: z.array(z.enum(['page_impressions', 'page_engaged_users', 'page_post_engagements', 'page_fans', 'page_views'])).optional().describe('Metrics to retrieve'),
    period: z.enum(['day', 'week', 'month', 'lifetime']).default('week').describe('Time period'),
  },
  async ({ metrics, period }) => {
    try {
      const result = await fbClient.getInsights(metrics, period);
      const insights = result.data || [];

      if (insights.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '📊 No insights data available for this period.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `📈 Facebook Page Insights (${period})\n\n${insights.map(insight => 
              `**${insight.title}**\n` +
              `   Value: ${insight.values?.[0]?.value || 0}\n` +
              `${insight.description ? `   ${insight.description}` : ''}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting insights: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'facebook_get_post_insights',
  'Get insights for a specific Facebook post',
  {
    post_id: z.string().describe('Post ID'),
  },
  async ({ post_id }) => {
    try {
      const result = await fbClient.get(`/${post_id}/insights`, {
        metric: 'post_impressions,post_engagements,post_clicks,post_shares',
      });
      const insights = result.data || [];

      return {
        content: [
          {
            type: 'text',
            text: `📈 Post Insights for ${post_id}\n\n${insights.map(insight => 
              `**${insight.title}**: ${insight.values?.[0]?.value || 0}`
            ).join('\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting post insights: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'facebook_create_comment',
  'Create a comment on a Facebook post',
  {
    post_id: z.string().describe('Post ID to comment on'),
    message: z.string().describe('Comment message'),
  },
  async ({ post_id, message }) => {
    try {
      const result = await fbClient.createComment(post_id, message);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Comment posted successfully!\n\n**Comment ID**: ${result.id}\n**Message**: ${message}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error posting comment: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'facebook_get_comments',
  'Get comments on a Facebook post',
  {
    post_id: z.string().describe('Post ID'),
    limit: z.number().default(10).describe('Number of comments'),
  },
  async ({ post_id, limit }) => {
    try {
      const result = await fbClient.getComments(post_id, limit);
      const comments = result.data || [];

      if (comments.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '💬 No comments on this post yet.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `💬 Comments on Post ${post_id} (${comments.length} found):\n\n${comments.map((comment, i) => 
              `**${i + 1}. ${comment.from?.name || 'Unknown'}**\n` +
              `   ${comment.message}\n` +
              `   Created: ${comment.created_time}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting comments: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// INSTAGRAM TOOLS
// ============================================================================

server.tool(
  'instagram_create_post',
  'Create a new post on Instagram (requires Instagram Business Account)',
  {
    image_url: z.string().optional().describe('Image URL for the post'),
    video_url: z.string().optional().describe('Video URL for the post'),
    caption: z.string().describe('Post caption'),
  },
  async ({ image_url, video_url, caption }) => {
    try {
      if (!INSTAGRAM_ACCOUNT_ID) {
        return {
          content: [
            {
              type: 'text',
              text: '❌ Instagram Account ID not configured. Please set INSTAGRAM_ACCOUNT_ID in .env file.',
            },
          ],
          isError: true,
        };
      }

      if (!image_url && !video_url) {
        return {
          content: [
            {
              type: 'text',
              text: '❌ Either image_url or video_url must be provided.',
            },
          ],
          isError: true,
        };
      }

      // Step 1: Create media container
      const containerResult = await fbClient.createInstagramMedia(image_url, video_url, caption);
      const containerId = containerResult.id;

      // Step 2: Publish the media
      const publishResult = await fbClient.publishInstagramMedia(containerId);

      return {
        content: [
          {
            type: 'text',
            text: `✅ Instagram post created successfully!\n\n**Media ID**: ${publishResult.id}\n**Caption**: ${caption}\n\nThe post is being processed and will appear on Instagram shortly.`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error creating Instagram post: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'instagram_get_media',
  'Get recent Instagram media posts',
  {
    limit: z.number().default(10).describe('Number of media items'),
  },
  async ({ limit }) => {
    try {
      if (!INSTAGRAM_ACCOUNT_ID) {
        return {
          content: [
            {
              type: 'text',
              text: '❌ Instagram Account ID not configured.',
            },
          ],
          isError: true,
        };
      }

      const result = await fbClient.getInstagramMedia(limit);
      const media = result.data || [];

      if (media.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '📷 No Instagram media found.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `📷 Recent Instagram Posts (${media.length} found):\n\n${media.map((item, i) => 
              `**${i + 1}. ${item.id}**\n` +
              `   Type: ${item.media_type}\n` +
              `   ${item.caption ? `${item.caption.substring(0, 50)}${item.caption.length > 50 ? '...' : ''}` : ''}\n` +
              `   Posted: ${item.timestamp}\n` +
              `   ${item.permalink ? `Link: ${item.permalink}` : ''}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting Instagram media: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'instagram_get_insights',
  'Get Instagram account insights/analytics',
  {
    metrics: z.array(z.enum(['impressions', 'reach', 'profile_views', 'follower_count', 'website_clicks'])).optional().describe('Metrics to retrieve'),
  },
  async ({ metrics }) => {
    try {
      if (!INSTAGRAM_ACCOUNT_ID) {
        return {
          content: [
            {
              type: 'text',
              text: '❌ Instagram Account ID not configured.',
            },
          ],
          isError: true,
        };
      }

      const result = await fbClient.getInstagramInsights(metrics);
      const insights = result.data || [];

      if (insights.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '📊 No Instagram insights data available.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `📈 Instagram Insights\n\n${insights.map(insight => 
              `**${insight.title}**: ${insight.values?.[0]?.value || 0}\n` +
              `${insight.description ? `   ${insight.description}` : ''}`
            ).join('\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting Instagram insights: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// SOCIAL MEDIA SUMMARY
// ============================================================================

server.tool(
  'facebook_generate_summary',
  'Generate comprehensive social media summary for Facebook and Instagram',
  {
    include_facebook: z.boolean().default(true).describe('Include Facebook data'),
    include_instagram: z.boolean().default(false).describe('Include Instagram data'),
    days: z.number().default(7).describe('Number of days to summarize'),
  },
  async ({ include_facebook, include_instagram, days }) => {
    try {
      const summary = {
        facebook: null,
        instagram: null,
        generated_at: new Date().toISOString(),
        period: `${days} days`,
      };

      // Facebook Summary
      if (include_facebook) {
        const [posts, insights] = await Promise.all([
          fbClient.getPosts(days),
          fbClient.getInsights(['page_impressions', 'page_engaged_users', 'page_post_engagements'], 'week'),
        ]);

        summary.facebook = {
          total_posts: posts.data?.length || 0,
          total_impressions: insights.data?.find(i => i.name === 'page_impressions')?.values?.[0]?.value || 0,
          total_engaged_users: insights.data?.find(i => i.name === 'page_engaged_users')?.values?.[0]?.value || 0,
          total_engagements: insights.data?.find(i => i.name === 'page_post_engagements')?.values?.[0]?.value || 0,
        };
      }

      // Instagram Summary
      if (include_instagram && INSTAGRAM_ACCOUNT_ID) {
        const [media, insights] = await Promise.all([
          fbClient.getInstagramMedia(days),
          fbClient.getInstagramInsights(['impressions', 'reach', 'profile_views']),
        ]);

        summary.instagram = {
          total_posts: media.data?.length || 0,
          total_impressions: insights.data?.find(i => i.name === 'impressions')?.values?.[0]?.value || 0,
          total_reach: insights.data?.find(i => i.name === 'reach')?.values?.[0]?.value || 0,
          profile_views: insights.data?.find(i => i.name === 'profile_views')?.values?.[0]?.value || 0,
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `📊 Social Media Summary (Last ${days} Days)\n\n` +
              `${summary.facebook ? 
                `**Facebook**\n` +
                `• Posts: ${summary.facebook.total_posts}\n` +
                `• Impressions: ${summary.facebook.total_impressions.toLocaleString()}\n` +
                `• Engaged Users: ${summary.facebook.total_engaged_users.toLocaleString()}\n` +
                `• Total Engagements: ${summary.facebook.total_engagements.toLocaleString()}\n\n` : ''}` +
              `${summary.instagram ? 
                `**Instagram**\n` +
                `• Posts: ${summary.instagram.total_posts}\n` +
                `• Impressions: ${summary.instagram.total_impressions.toLocaleString()}\n` +
                `• Reach: ${summary.instagram.total_reach.toLocaleString()}\n` +
                `• Profile Views: ${summary.instagram.profile_views.toLocaleString()}` : ''}\n\n` +
              `Generated: ${summary.generated_at}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error generating summary: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// SERVER STARTUP
// ============================================================================

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('✅ Facebook MCP Server running on stdio');
  console.error('');
  console.error('Available tools:');
  console.error('  📘 Facebook:');
  console.error('    facebook_create_post - Create page post');
  console.error('    facebook_get_posts - Get recent posts');
  console.error('    facebook_get_insights - Get page analytics');
  console.error('    facebook_get_post_insights - Get post analytics');
  console.error('    facebook_create_comment - Post comment');
  console.error('    facebook_get_comments - Get post comments');
  console.error('  📷 Instagram:');
  console.error('    instagram_create_post - Create Instagram post');
  console.error('    instagram_get_media - Get recent media');
  console.error('    instagram_get_insights - Get Instagram analytics');
  console.error('  📊 Summary:');
  console.error('    facebook_generate_summary - Generate social media report');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
