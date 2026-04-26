#!/usr/bin/env node
/**
 * LinkedIn MCP Server - Gold Tier AI Employee
 *
 * Provides LinkedIn integration via Playwright automation
 * Capabilities: Post creation, messaging, connection management, job search
 *
 * Usage:
 *   npm start
 *
 * Note: This server uses Playwright instead of LinkedIn API
 * Requires a saved LinkedIn session
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
const LINKEDIN_SESSION_PATH = process.env.LINKEDIN_SESSION_PATH || path.join(__dirname, '../../watchers/linkedin-watcher/linkedin_session');
const VAULT_PATH = process.env.VAULT_PATH || process.cwd();

console.error('🔌 LinkedIn MCP Server starting...');
console.error(`   Session Path: ${LINKEDIN_SESSION_PATH}`);
console.error(`   Vault Path: ${VAULT_PATH}`);

/**
 * LinkedIn Client using Playwright
 */
class LinkedInClient {
  constructor(sessionPath) {
    this.sessionPath = sessionPath;
  }

  async executePython(script, args = []) {
    const pythonScript = path.join(__dirname, 'linkedin_client.py');
    const cmd = `python3 "${pythonScript}" --session "${this.sessionPath}" ${args.map(a => `"${a}"`).join(' ')}`;
    
    try {
      const result = execSync(cmd, { 
        encoding: 'utf-8',
        timeout: 60000 
      });
      return JSON.parse(result);
    } catch (error) {
      throw new Error(`LinkedIn automation failed: ${error.message}`);
    }
  }

  async createPost(message) {
    return await this.executePython('post', [message]);
  }

  async getFeed(limit = 10) {
    return await this.executePython('feed', [limit.toString()]);
  }

  async getMessages(limit = 10) {
    return await this.executePython('messages', [limit.toString()]);
  }

  async sendMessage(recipientName, message) {
    return await this.executePython('send_message', [recipientName, message]);
  }

  async getConnectionRequests(limit = 10) {
    return await this.executePython('connection_requests', [limit.toString()]);
  }

  async acceptConnectionRequest(profileUrl) {
    return await this.executePython('accept_connection', [profileUrl]);
  }

  async searchJobs(keywords, location = '', limit = 10) {
    return await this.executePython('search_jobs', [keywords, location, limit.toString()]);
  }

  async getNotifications(limit = 10) {
    return await this.executePython('notifications', [limit.toString()]);
  }
}

// Initialize client
const linkedinClient = new LinkedInClient(LINKEDIN_SESSION_PATH);

/**
 * Create MCP Server
 */
const server = new McpServer({
  name: 'linkedin-mcp-server',
  version: '1.0.0',
  description: 'LinkedIn integration for AI Employee via Playwright',
});

// ============================================================================
// LINKEDIN POST TOOLS
// ============================================================================

server.tool(
  'linkedin_create_post',
  'Create a new post on LinkedIn',
  {
    message: z.string().describe('Post content/message'),
  },
  async ({ message }) => {
    try {
      const result = await linkedinClient.createPost(message);

      return {
        content: [
          {
            type: 'text',
            text: `✅ LinkedIn post created successfully!\n\n**Post**: ${message}\n\nThe post is now live on your LinkedIn profile.`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error creating LinkedIn post: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'linkedin_get_feed',
  'Get recent posts from your LinkedIn feed',
  {
    limit: z.number().default(10).describe('Number of posts to retrieve'),
  },
  async ({ limit }) => {
    try {
      const result = await linkedinClient.getFeed(limit);
      const posts = result.posts || [];

      if (posts.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '📭 No posts found on your LinkedIn feed.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `📱 Recent LinkedIn Feed Posts (${posts.length} found):\n\n${posts.map((post, i) =>
              `**${i + 1}. ${post.author || 'Unknown'}**\n` +
              `${post.text ? `${post.text.substring(0, 150)}${post.text.length > 150 ? '...' : ''}` : '[No text]'}\n` +
              `   Likes: ${post.likes || 0} | Comments: ${post.comments || 0}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting feed: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// LINKEDIN MESSAGING TOOLS
// ============================================================================

server.tool(
  'linkedin_get_messages',
  'Get recent LinkedIn messages',
  {
    limit: z.number().default(10).describe('Number of messages'),
  },
  async ({ limit }) => {
    try {
      const result = await linkedinClient.getMessages(limit);
      const messages = result.messages || [];

      if (messages.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '💬 No recent LinkedIn messages.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `💬 Recent LinkedIn Messages (${messages.length} found):\n\n${messages.map((msg, i) =>
              `**${i + 1}. ${msg.from || 'Unknown'}**\n` +
              `   ${msg.text || '[No text]'}\n` +
              `   Time: ${msg.time || 'Unknown'}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting messages: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'linkedin_send_message',
  'Send a message to a LinkedIn connection',
  {
    recipient_name: z.string().describe('Name of the recipient'),
    message: z.string().describe('Message content'),
  },
  async ({ recipient_name, message }) => {
    try {
      const result = await linkedinClient.sendMessage(recipient_name, message);

      return {
        content: [
          {
            type: 'text',
            text: `✅ Message sent to ${recipient_name}!\n\n**Message**: ${message}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error sending message: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// LINKEDIN CONNECTION TOOLS
// ============================================================================

server.tool(
  'linkedin_get_connection_requests',
  'Get pending LinkedIn connection requests',
  {
    limit: z.number().default(10).describe('Number of requests'),
  },
  async ({ limit }) => {
    try {
      const result = await linkedinClient.getConnectionRequests(limit);
      const requests = result.requests || [];

      if (requests.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '👥 No pending connection requests.',
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `👥 Pending Connection Requests (${requests.length} found):\n\n${requests.map((req, i) =>
              `**${i + 1}. ${req.name || 'Unknown'}**\n` +
              `   ${req.title || ''}\n` +
              `   ${req.mutual_connections || 0} mutual connections`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting connection requests: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'linkedin_accept_connection',
  'Accept a LinkedIn connection request',
  {
    profile_url: z.string().describe('Profile URL of the request'),
  },
  async ({ profile_url }) => {
    try {
      const result = await linkedinClient.acceptConnectionRequest(profile_url);

      return {
        content: [
          {
            type: 'text',
            text: `✅ Connection request accepted!\n\n**Profile**: ${profile_url}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error accepting connection: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// LINKEDIN JOB SEARCH TOOLS
// ============================================================================

server.tool(
  'linkedin_search_jobs',
  'Search for jobs on LinkedIn',
  {
    keywords: z.string().describe('Job search keywords'),
    location: z.string().optional().describe('Job location (optional)'),
    limit: z.number().default(10).describe('Number of jobs'),
  },
  async ({ keywords, location, limit }) => {
    try {
      const result = await linkedinClient.searchJobs(keywords, location, limit);
      const jobs = result.jobs || [];

      if (jobs.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: `💼 No jobs found for "${keywords}"${location ? ` in ${location}` : ''}.`,
            },
          ],
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `💼 Job Search Results (${jobs.length} found):\n\n${jobs.map((job, i) =>
              `**${i + 1}. ${job.title || 'Unknown'}**\n` +
              `   Company: ${job.company || 'Unknown'}\n` +
              `   Location: ${job.location || 'Unknown'}\n` +
              `   ${job.posted ? `Posted: ${job.posted}` : ''}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error searching jobs: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// LINKEDIN NOTIFICATIONS
// ============================================================================

server.tool(
  'linkedin_get_notifications',
  'Get recent LinkedIn notifications',
  {
    limit: z.number().default(10).describe('Number of notifications'),
  },
  async ({ limit }) => {
    try {
      const result = await linkedinClient.getNotifications(limit);
      const notifications = result.notifications || [];

      if (notifications.length === 0) {
        return {
          content: [
            {
              type: 'text',
              text: '🔔 No new LinkedIn notifications.',
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

// ============================================================================
// LINKEDIN SUMMARY
// ============================================================================

server.tool(
  'linkedin_generate_summary',
  'Generate comprehensive LinkedIn activity summary',
  {
    days: z.number().default(7).describe('Number of days to summarize'),
  },
  async ({ days }) => {
    try {
      const [notifications, messages, connectionRequests] = await Promise.all([
        linkedinClient.getNotifications(20),
        linkedinClient.getMessages(10),
        linkedinClient.getConnectionRequests(10),
      ]);

      const notifCount = notifications.notifications?.length || 0;
      const msgCount = messages.messages?.length || 0;
      const connCount = connectionRequests.requests?.length || 0;

      return {
        content: [
          {
            type: 'text',
            text: `📊 LinkedIn Activity Summary (Last ${days} Days)\n\n` +
              `**Notifications**: ${notifCount}\n` +
              `**Messages**: ${msgCount}\n` +
              `**Pending Connections**: ${connCount}\n\n` +
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
  console.error('✅ LinkedIn MCP Server running on stdio');
  console.error('');
  console.error('Available tools:');
  console.error('  💼 LinkedIn:');
  console.error('    linkedin_create_post - Create post');
  console.error('    linkedin_get_feed - Get feed posts');
  console.error('    linkedin_get_messages - Get messages');
  console.error('    linkedin_send_message - Send message');
  console.error('    linkedin_get_connection_requests - Get connection requests');
  console.error('    linkedin_accept_connection - Accept connection');
  console.error('    linkedin_search_jobs - Search jobs');
  console.error('    linkedin_get_notifications - Get notifications');
  console.error('  📊 Summary:');
  console.error('    linkedin_generate_summary - Generate activity report');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
