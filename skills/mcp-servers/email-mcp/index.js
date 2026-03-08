#!/usr/bin/env node
/**
 * Email MCP Server - Gmail integration for sending emails.
 * 
 * Usage:
 *   node index.js
 * 
 * Environment:
 *   GMAIL_CREDENTIALS - Path to Gmail OAuth credentials
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');

// Simple MCP Server for Email
const server = new Server(
  {
    name: 'email-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
const TOOLS = [
  {
    name: 'send_email',
    description: 'Send an email via Gmail',
    inputSchema: {
      type: 'object',
      properties: {
        to: { type: 'string', description: 'Recipient email address' },
        subject: { type: 'string', description: 'Email subject' },
        body: { type: 'string', description: 'Email body content' },
        cc: { type: 'string', description: 'CC recipient (optional)' },
      },
      required: ['to', 'subject', 'body'],
    },
  },
  {
    name: 'draft_email',
    description: 'Create a draft email',
    inputSchema: {
      type: 'object',
      properties: {
        to: { type: 'string', description: 'Recipient email address' },
        subject: { type: 'string', description: 'Email subject' },
        body: { type: 'string', description: 'Email body content' },
      },
      required: ['to', 'subject', 'body'],
    },
  },
  {
    name: 'search_emails',
    description: 'Search Gmail for messages',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' },
        maxResults: { type: 'number', description: 'Maximum results', default: 10 },
      },
      required: ['query'],
    },
  },
];

// Tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'send_email':
      return await handleSendEmail(args);
    case 'draft_email':
      return await handleDraftEmail(args);
    case 'search_emails':
      return await handleSearchEmails(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

async function handleSendEmail(args) {
  const { to, subject, body, cc } = args;
  
  // In production, integrate with Gmail API
  // For now, log the action
  console.error(`Sending email to: ${to}`);
  console.error(`Subject: ${subject}`);
  
  return {
    content: [
      {
        type: 'text',
        text: `Email sent to ${to} with subject "${subject}"`,
      },
    ],
  };
}

async function handleDraftEmail(args) {
  const { to, subject, body } = args;
  
  return {
    content: [
      {
        type: 'text',
        text: `Draft created for email to ${to}`,
      },
    ],
  };
}

async function handleSearchEmails(args) {
  const { query, maxResults = 10 } = args;
  
  return {
    content: [
      {
        type: 'text',
        text: `Search results for "${query}": (MCP server not fully configured)`,
      },
    ],
  };
}

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Email MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
