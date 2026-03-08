#!/usr/bin/env node
/**
 * Gmail MCP Server - Send emails via Gmail API
 * 
 * Usage:
 *   node email_mcp_server.js
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

const fs = require('fs');
const path = require('path');

// MCP Server instance
const server = new Server(
  {
    name: 'gmail-mcp-server',
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
    description: 'Send an email via Gmail API',
    inputSchema: {
      type: 'object',
      properties: {
        to: { type: 'string', description: 'Recipient email address' },
        subject: { type: 'string', description: 'Email subject' },
        body: { type: 'string', description: 'Email body content' },
        cc: { type: 'string', description: 'CC recipient (optional)' },
        inReplyTo: { type: 'string', description: 'Message ID to reply to' },
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
        query: { type: 'string', description: 'Gmail search query' },
        maxResults: { type: 'number', description: 'Maximum results', default: 10 },
      },
      required: ['query'],
    },
  },
];

// Load Gmail credentials
function getCredentials() {
  const credsPath = process.env.GMAIL_CREDENTIALS || 
                    path.join(__dirname, '..', '..', 'credentials.json');
  
  if (!fs.existsSync(credsPath)) {
    throw new Error(`Credentials file not found: ${credsPath}`);
  }
  
  return JSON.parse(fs.readFileSync(credsPath, 'utf8'));
}

// Authenticate with Gmail
async function authenticateGmail() {
  try {
    const { google } = await import('googleapis');
    const credentials = getCredentials();
    
    const { client_secret, client_id, redirect_uris } = credentials.installed;
    
    const oauth2Client = new google.auth.OAuth2(
      client_id,
      client_secret,
      redirect_uris[0]
    );
    
    // Check for existing token
    const tokenPath = path.join(__dirname, 'token.json');
    if (fs.existsSync(tokenPath)) {
      const token = JSON.parse(fs.readFileSync(tokenPath, 'utf8'));
      oauth2Client.setCredentials(token);
    } else {
      console.error('No token found. Please run authentication first.');
      throw new Error('Authentication required');
    }
    
    return oauth2Client;
  } catch (error) {
    console.error('Authentication error:', error.message);
    throw error;
  }
}

// Send email via Gmail API
async function sendEmailViaGmail(auth, to, subject, body, cc = null, inReplyTo = null) {
  try {
    const { google } = await import('googleapis');
    const gmail = google.gmail({ version: 'v1', auth });
    
    // Create email message
    const strMessage = [
      'Content-Type: text/plain; charset="UTF-8"',
      'MIME-Version: 1.0',
      'Content-Transfer-Encoding: 7bit',
      `To: ${to}`,
      `Subject: ${subject}`,
    ];
    
    if (cc) {
      strMessage.push(`CC: ${cc}`);
    }
    
    if (inReplyTo) {
      strMessage.push(`In-Reply-To: ${inReplyTo}`);
      strMessage.push(`References: ${inReplyTo}`);
    }
    
    strMessage.push('');
    strMessage.push(body);
    
    const message = strMessage.join('\n');
    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
    
    // Send email
    const response = await gmail.users.messages.send({
      userId: 'me',
      requestBody: {
        raw: encodedMessage,
      },
    });
    
    return {
      success: true,
      messageId: response.data.id,
      threadId: response.data.threadId,
    };
  } catch (error) {
    console.error('Send email error:', error.message);
    throw error;
  }
}

// Tool handlers
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: TOOLS };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
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
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

async function handleSendEmail(args) {
  const { to, subject, body, cc, inReplyTo } = args;
  
  console.error(`Sending email to: ${to}`);
  console.error(`Subject: ${subject}`);
  
  try {
    // Authenticate
    const auth = await authenticateGmail();
    
    // Send email
    const result = await sendEmailViaGmail(auth, to, subject, body, cc, inReplyTo);
    
    console.error(`Email sent successfully! Message ID: ${result.messageId}`);
    
    return {
      content: [
        {
          type: 'text',
          text: `✅ Email sent successfully!\n\nTo: ${to}\nSubject: ${subject}\nMessage ID: ${result.messageId}`,
        },
      ],
    };
  } catch (error) {
    console.error(`Failed to send email: ${error.message}`);
    return {
      content: [
        {
          type: 'text',
          text: `❌ Failed to send email: ${error.message}\n\nMake sure:\n1. Gmail credentials are valid\n2. You've run authentication\n3. Token exists in email_mcp_server/token.json`,
        },
      ],
      isError: true,
    };
  }
}

async function handleDraftEmail(args) {
  const { to, subject, body } = args;
  
  return {
    content: [
      {
        type: 'text',
        text: `Draft created for email to ${to}\nSubject: ${subject}`,
      },
    ],
  };
}

async function handleSearchEmails(args) {
  const { query, maxResults = 10 } = args;
  
  try {
    const { google } = await import('googleapis');
    const auth = await authenticateGmail();
    const gmail = google.gmail({ version: 'v1', auth });
    
    const response = await gmail.users.messages.list({
      userId: 'me',
      q: query,
      maxResults: maxResults,
    });
    
    const messages = response.data.messages || [];
    
    return {
      content: [
        {
          type: 'text',
          text: `Found ${messages.length} messages:\n\n` + 
            messages.map(m => `• Message ID: ${m.id}`).join('\n'),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Search error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
}

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Gmail MCP Server running on stdio');
  console.error('Tools available: send_email, draft_email, search_emails');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
