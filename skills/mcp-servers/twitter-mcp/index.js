#!/usr/bin/env node
/**
 * Twitter/X MCP Server - Gold Tier AI Employee
 *
 * Provides Twitter/X integration via Playwright automation
 * Capabilities: Post creation, timeline monitoring, engagement
 *
 * Usage:
 *   npm start
 *
 * Note: This server uses Playwright instead of Twitter API
 * Requires a saved Twitter session
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import dotenv from 'dotenv';
import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const TWITTER_SESSION_PATH = process.env.TWITTER_SESSION_PATH || path.join(__dirname, '../../watchers/twitter-watcher/twitter_session');
const VAULT_PATH = process.env.VAULT_PATH || process.cwd();

console.error('🔌 Twitter MCP Server starting...');
console.error(`   Session Path: ${TWITTER_SESSION_PATH}`);
console.error(`   Vault Path: ${VAULT_PATH}`);

/**
 * Twitter Client using Playwright
 */
class TwitterClient {
  constructor(sessionPath) {
    this.sessionPath = sessionPath;
  }

  async executePython(script, args = []) {
    const pythonScript = path.join(__dirname, 'twitter_client.py');
    const cmd = `python3 "${pythonScript}" --session "${this.sessionPath}" ${args.map(a => `"${a}"`).join(' ')}`;
    
    try {
      const result = execSync(cmd, { 
        encoding: 'utf-8',
        timeout: 60000 
      });
      return JSON.parse(result);
    } catch (error) {
      throw new Error(`Twitter automation failed: ${error.message}`);
    }
  }

  async createTweet(message) {
    if (message.length > 280) {
      throw new Error(`Tweet too long: ${message.length}/280 characters`);
    }

    return await this.executePython('tweet', [message]);
  }

  async getTimeline(limit = 10) {
    return await this.executePython('timeline', [limit.toString()]);
  }

  async getNotifications(limit = 10) {
    return await this.executePython('notifications', [limit.toString()]);
  }

  async getMentions(limit = 10) {
    return await this.executePython('mentions', [limit.toString()]);
  }

  async likeTweet(tweetId) {
    return await this.executePython('like', [tweetId]);
  }

  async retweet(tweetId) {
    return await this.executePython('retweet', [tweetId]);
  }

  async replyToTweet(tweetId, message) {
    if (message.length > 280) {
      throw new Error(`Reply too long: ${message.length}/280 characters`);
    }

    return await this.executePython('reply', [tweetId, message]);
  }
}

// Initialize client
const twitterClient = new TwitterClient(TWITTER_SESSION_PATH);

/**
 * Create MCP Server
 */
const server = new McpServer({
  name: 'twitter-mcp-server',
  version: '1.0.0',
  description: 'Twitter/X integration for AI Employee via Playwright',
});

// ============================================================================
// TWEET CREATION TOOLS
// ============================================================================

server.tool(
  'twitter_create_tweet',
  'Create a new tweet on Twitter/X (max 280 characters)',
  {
    message: z.string().describe('Tweet content (max 280 characters)'),
  },
  async ({ message }) => {
    try {
      if (message.length > 280) {
        return {
          content: [
            {
              type: 'text',
              text: `❌ Tweet too long: ${message.length}/280 characters. Please shorten your message.`,
            },
          ],
          isError: true,
        };
      }

      const result = await twitterClient.createTweet(message);

      return {
        content: [
          {
            type: 'text',
            text: `✅ Tweet posted successfully!\n\n**Tweet**: ${message}\n\nThe tweet is now live on your Twitter/X profile.`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error posting tweet: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'twitter_get_timeline',
  'Get recent tweets from your Twitter/X timeline',
  {
    limit: z.number().default(10).describe('Number of tweets to retrieve'),
  },
  async ({ limit }) => {
    try {
      const result = await twitterClient.getTimeline(limit);
      const tweets = result.tweets || [];

      if (tweets.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '📭 No tweets found on your timeline.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `📱 Recent Timeline Tweets (${tweets.length} found):\n\n${tweets.map((tweet, i) =>
              `**${i + 1}. ${tweet.author || 'Unknown'}**\n` +
              `${tweet.text ? `${tweet.text.substring(0, 100)}${tweet.text.length > 100 ? '...' : ''}` : '[No text]'}\n` +
              `   Likes: ${tweet.likes || 0} | Retweets: ${tweet.retweets || 0}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting timeline: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'twitter_get_notifications',
  'Get recent notifications from Twitter/X',
  {
    limit: z.number().default(10).describe('Number of notifications'),
  },
  async ({ limit }) => {
    try {
      const result = await twitterClient.getNotifications(limit);
      const notifications = result.notifications || [];

      if (notifications.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '🔔 No new notifications.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `🔔 Recent Notifications (${notifications.length} found):\n\n${notifications.map((notif, i) =>
              `**${i + 1}. ${notif.type || 'Unknown'}**\n` +
              `   From: ${notif.from || 'Unknown'}\n` +
              `   ${notif.text || ''}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting notifications: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'twitter_get_mentions',
  'Get recent mentions of your account',
  {
    limit: z.number().default(10).describe('Number of mentions'),
  },
  async ({ limit }) => {
    try {
      const result = await twitterClient.getMentions(limit);
      const mentions = result.mentions || [];

      if (mentions.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '💬 No recent mentions.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `💬 Recent Mentions (${mentions.length} found):\n\n${mentions.map((mention, i) =>
              `**${i + 1}. ${mention.author || 'Unknown'}**\n` +
              `   ${mention.text ? mention.text.substring(0, 150) : '[No text]'}${mention.text && mention.text.length > 150 ? '...' : ''}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting mentions: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'twitter_like_tweet',
  'Like a tweet on Twitter/X',
  {
    tweet_id: z.string().describe('Tweet ID to like'),
  },
  async ({ tweet_id }) => {
    try {
      const result = await twitterClient.likeTweet(tweet_id);

      return {
        content: [
          {
            type: 'text',
            text: `❤️ Tweet liked successfully!\n\n**Tweet ID**: ${tweet_id}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error liking tweet: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'twitter_retweet',
  'Retweet a post on Twitter/X',
  {
    tweet_id: z.string().describe('Tweet ID to retweet'),
  },
  async ({ tweet_id }) => {
    try {
      const result = await twitterClient.retweet(tweet_id);

      return {
        content: [
          {
            type: 'text',
            text: `🔄 Tweet retweeted successfully!\n\n**Tweet ID**: ${tweet_id}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error retweeting: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'twitter_reply_to_tweet',
  'Reply to a tweet on Twitter/X',
  {
    tweet_id: z.string().describe('Tweet ID to reply to'),
    message: z.string().describe('Reply message (max 280 characters)'),
  },
  async ({ tweet_id, message }) => {
    try {
      if (message.length > 280) {
        return {
          content: [
            {
              type: 'text',
              text: `❌ Reply too long: ${message.length}/280 characters. Please shorten your message.`,
            },
          ],
          isError: true,
        };
      }

      const result = await twitterClient.replyToTweet(tweet_id, message);

      return {
        content: [
          {
            type: 'text',
            text: `✅ Reply posted successfully!\n\n**Tweet ID**: ${tweet_id}\n**Reply**: ${message}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error posting reply: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// TWITTER SUMMARY
// ============================================================================

server.tool(
  'twitter_generate_summary',
  'Generate comprehensive Twitter/X activity summary',
  {
    days: z.number().default(7).describe('Number of days to summarize'),
  },
  async ({ days }) => {
    try {
      const [notifications, mentions] = await Promise.all([
        twitterClient.getNotifications(20),
        twitterClient.getMentions(20),
      ]);

      const notifCount = notifications.notifications?.length || 0;
      const mentionCount = mentions.mentions?.length || 0;

      return {
        content: [
          {
            type: 'text',
            text: `📊 Twitter/X Activity Summary (Last ${days} Days)\n\n` +
              `**Notifications**: ${notifCount}\n` +
              `**Mentions**: ${mentionCount}\n\n` +
              `Generated: ${new Date().toISOString()}`,
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
  console.error('✅ Twitter MCP Server running on stdio');
  console.error('');
  console.error('Available tools:');
  console.error('  🐦 Twitter:');
  console.error('    twitter_create_tweet - Create tweet');
  console.error('    twitter_get_timeline - Get timeline');
  console.error('    twitter_get_notifications - Get notifications');
  console.error('    twitter_get_mentions - Get mentions');
  console.error('    twitter_like_tweet - Like tweet');
  console.error('    twitter_retweet - Retweet');
  console.error('    twitter_reply_to_tweet - Reply to tweet');
  console.error('  📊 Summary:');
  console.error('    twitter_generate_summary - Generate activity report');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
