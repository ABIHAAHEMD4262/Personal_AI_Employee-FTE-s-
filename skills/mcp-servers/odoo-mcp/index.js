#!/usr/bin/env node
/**
 * Odoo MCP Server - Gold Tier AI Employee
 * 
 * Provides Odoo Community Edition integration via JSON-RPC API
 * Capabilities: Accounting, Invoicing, Contacts, Products, Reporting
 * 
 * Usage:
 *   npm start
 * 
 * Environment Variables:
 *   ODOO_URL - Odoo instance URL (default: http://localhost:8069)
 *   ODOO_DATABASE - Database name (required)
 *   ODOO_API_KEY - API key for authentication (required)
 *   ODOO_USER_ID - User ID (required)
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import fetch from 'node-fetch';
import dotenv from 'dotenv';

dotenv.config();

// Configuration
const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DATABASE = process.env.ODOO_DATABASE;
const ODOO_API_KEY = process.env.ODOO_API_KEY;
const ODOO_USER_ID = process.env.ODOO_USER_ID;

// Validate configuration
if (!ODOO_DATABASE || !ODOO_API_KEY || !ODOO_USER_ID) {
  console.error('❌ Missing required environment variables:');
  console.error('   ODOO_DATABASE, ODOO_API_KEY, ODOO_USER_ID');
  console.error('   Please create a .env file in skills/mcp-servers/odoo-mcp/');
  process.exit(1);
}

console.error('🔌 Odoo MCP Server starting...');
console.error(`   URL: ${ODOO_URL}`);
console.error(`   Database: ${ODOO_DATABASE}`);
console.error(`   User ID: ${ODOO_USER_ID}`);

/**
 * Odoo JSON-RPC Client
 */
class OdooClient {
  constructor(baseUrl, db, apiKey, userId) {
    this.baseUrl = `${baseUrl}/jsonrpc`;
    this.db = db;
    this.apiKey = apiKey;
    this.userId = parseInt(userId);
  }

  async call(service, method, args = []) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service,
          method,
          args,
        },
        id: Date.now(),
      }),
    });

    const result = await response.json();
    
    if (result.error) {
      throw new Error(`Odoo API Error: ${result.error.message}`);
    }

    return result.result;
  }

  // Execute KW method (most common Odoo API call)
  async execute(model, method, args = [], kwargs = {}) {
    return await this.call('object', 'execute_kw', [
      this.db,
      this.userId,
      this.apiKey,
      model,
      method,
      args,
      kwargs,
    ]);
  }

  // Search records
  async search(model, domain = [], options = {}) {
    return await this.execute(model, 'search', [domain], options);
  }

  // Search and read records
  async searchRead(model, domain = [], fields = [], options = {}) {
    return await this.execute(model, 'search_read', [domain, fields], options);
  }

  // Create record
  async create(model, values) {
    return await this.execute(model, 'create', [values]);
  }

  // Update record
  async write(model, id, values) {
    return await this.execute(model, 'write', [[id], values]);
  }

  // Delete record
  async unlink(model, id) {
    return await this.execute(model, 'unlink', [[id]]);
  }

  // Get record by ID
  async read(model, id, fields = []) {
    const results = await this.execute(model, 'read', [[id], fields]);
    return results.length > 0 ? results[0] : null;
  }

  // Get field names
  async getFields(model) {
    return await this.execute(model, 'fields_get', [], {});
  }
}

// Initialize client
const odoo = new OdooClient(ODOO_URL, ODOO_DATABASE, ODOO_API_KEY, ODOO_USER_ID);

/**
 * Create MCP Server
 */
const server = new McpServer({
  name: 'odoo-mcp-server',
  version: '1.0.0',
  description: 'Odoo Community Edition integration for AI Employee',
});

// ============================================================================
// ACCOUNTING TOOLS
// ============================================================================

server.tool(
  'odoo_create_invoice',
  'Create a new customer invoice in Odoo Accounting',
  {
    partner_id: z.number().describe('Customer/Partner ID'),
    invoice_date: z.string().optional().describe('Invoice date (YYYY-MM-DD)'),
    due_date: z.string().optional().describe('Due date (YYYY-MM-DD)'),
    invoice_lines: z.array(z.object({
      name: z.string().describe('Line item description'),
      price_unit: z.number().describe('Unit price'),
      quantity: z.number().default(1).describe('Quantity'),
      account_id: z.number().optional().describe('Account ID (optional)'),
    })).describe('Invoice line items'),
    narration: z.string().optional().describe('Additional notes'),
  },
  async ({ partner_id, invoice_date, due_date, invoice_lines, narration }) => {
    try {
      // Prepare invoice data
      const invoiceData = {
        move_type: 'out_invoice',
        partner_id: partner_id,
        invoice_line_ids: invoice_lines.map(line => [0, 0, {
          name: line.name,
          price_unit: line.price_unit,
          quantity: line.quantity,
          ...(line.account_id && { account_id: line.account_id }),
        }]),
        ...(invoice_date && { invoice_date }),
        ...(due_date && { invoice_date_due: due_date }),
        ...(narration && { narration }),
      };

      const invoiceId = await odoo.create('account.move', invoiceData);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Invoice created successfully!\n\n**Invoice ID**: ${invoiceId}\n**Customer ID**: ${partner_id}\n**Lines**: ${invoice_lines.length} item(s)\n\nNext steps:\n- Post the invoice to confirm it\n- Send to customer\n- Track payment`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error creating invoice: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'odoo_post_invoice',
  'Post an invoice to confirm it (changes state from Draft to Posted)',
  {
    invoice_id: z.number().describe('Invoice ID to post'),
  },
  async ({ invoice_id }) => {
    try {
      await odoo.execute('account.move', 'action_post', [[invoice_id]]);
      
      return {
        content: [
          {
            type: 'text',
            text: `✅ Invoice ${invoice_id} posted successfully!\n\nThe invoice is now confirmed and sent to the customer.`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error posting invoice: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'odoo_register_payment',
  'Register a payment for an invoice',
  {
    invoice_id: z.number().describe('Invoice ID'),
    amount: z.number().describe('Payment amount'),
    payment_date: z.string().optional().describe('Payment date (YYYY-MM-DD)'),
    payment_method: z.string().optional().describe('Payment method (e.g., "manual", "bank_transfer")'),
    reference: z.string().optional().describe('Payment reference'),
  },
  async ({ invoice_id, amount, payment_date, payment_method, reference }) => {
    try {
      // Create payment wizard
      const paymentRegisterId = await odoo.execute('account.payment.register', 'create', [{
        payment_type: 'inbound',
        amount: amount,
        currency_id: 1, // Default to first currency (usually USD/EUR)
        ...(payment_date && { payment_date }),
        ...(payment_method && { payment_method_id: payment_method }),
        ...(reference && { communication: reference }),
      }], {
        active_model: 'account.move',
        active_ids: [invoice_id],
      });

      // Create the payment
      await odoo.execute('account.payment.register', 'create_payments', [[paymentRegisterId]]);

      return {
        content: [
          {
            type: 'text',
            text: `✅ Payment registered successfully!\n\n**Invoice**: ${invoice_id}\n**Amount**: $${amount}\n${reference ? `**Reference**: ${reference}` : ''}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error registering payment: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'odoo_get_invoices',
  'Get list of invoices with optional filtering',
  {
    partner_id: z.number().optional().describe('Filter by customer ID'),
    state: z.enum(['draft', 'posted', 'cancel']).optional().describe('Filter by status'),
    limit: z.number().default(10).describe('Maximum number of results'),
  },
  async ({ partner_id, state, limit }) => {
    try {
      const domain = [];
      
      if (partner_id) domain.push(['partner_id', '=', partner_id]);
      if (state) domain.push(['state', '=', state]);

      const invoices = await odoo.searchRead('account.move', domain, [
        'id', 'name', 'partner_id', 'amount_total', 'amount_residual', 
        'state', 'invoice_date', 'invoice_date_due'
      ], { limit });

      return {
        content: [
          {
            type: 'text',
            text: `📋 Invoices (${invoices.length} found):\n\n${invoices.map(inv => 
              `**${inv.name}** - ${inv.partner_id?.[1] || 'Unknown'}\n` +
              `   Amount: $${inv.amount_total} | Due: $${inv.amount_residual}\n` +
              `   Status: ${inv.state} | Due Date: ${inv.invoice_date_due || 'N/A'}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting invoices: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'odoo_get_invoice',
  'Get detailed information about a specific invoice',
  {
    invoice_id: z.number().describe('Invoice ID'),
  },
  async ({ invoice_id }) => {
    try {
      const invoice = await odoo.read('account.move', invoice_id, [
        'id', 'name', 'partner_id', 'amount_total', 'amount_residual',
        'state', 'invoice_date', 'invoice_date_due', 'narration',
        'invoice_line_ids'
      ]);

      if (!invoice) {
        return {
          content: [
            {
              type: 'text',
              text: `❌ Invoice ${invoice_id} not found`,
            },
          ],
          isError: true,
        };
      }

      return {
        content: [
          {
            type: 'text',
            text: `📄 Invoice ${invoice.name}\n\n` +
              `**Customer**: ${invoice.partner_id?.[1] || 'Unknown'}\n` +
              `**Total**: $${invoice.amount_total}\n` +
              `**Due**: $${invoice.amount_residual}\n` +
              `**Status**: ${invoice.state}\n` +
              `**Date**: ${invoice.invoice_date}\n` +
              `**Due Date**: ${invoice.invoice_date_due || 'N/A'}\n` +
              `${invoice.narration ? `\n**Notes**: ${invoice.narration}` : ''}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting invoice: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// CONTACT MANAGEMENT
// ============================================================================

server.tool(
  'odoo_create_partner',
  'Create a new contact/partner in Odoo',
  {
    name: z.string().describe('Contact name'),
    email: z.string().optional().describe('Email address'),
    phone: z.string().optional().describe('Phone number'),
    company_name: z.string().optional().describe('Company name'),
    street: z.string().optional().describe('Street address'),
    city: z.string().optional().describe('City'),
    country: z.string().optional().describe('Country'),
  },
  async ({ name, email, phone, company_name, street, city, country }) => {
    try {
      const partnerData = {
        name,
        ...(email && { email }),
        ...(phone && { phone }),
        ...(company_name && { company_name }),
        ...(street && { street }),
        ...(city && { city }),
        ...(country && { country }),
      };

      const partnerId = await odoo.create('res.partner', partnerData);

      return {
        content: [
          {
            type: 'text',
            text: `✅ Contact created successfully!\n\n**ID**: ${partnerId}\n**Name**: ${name}\n${email ? `**Email**: ${email}` : ''}\n${phone ? `**Phone**: ${phone}` : ''}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error creating contact: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'odoo_search_partners',
  'Search for contacts/partners in Odoo',
  {
    query: z.string().optional().describe('Search query (name, email, or company)'),
    limit: z.number().default(10).describe('Maximum results'),
  },
  async ({ query, limit }) => {
    try {
      const domain = query ? [
        '|', '|',
        ['name', 'ilike', query],
        ['email', 'ilike', query],
        ['company_name', 'ilike', query],
      ] : [];

      const partners = await odoo.searchRead('res.partner', domain, [
        'id', 'name', 'email', 'phone', 'company_name', 'city', 'country'
      ], { limit });

      return {
        content: [
          {
            type: 'text',
            text: `👥 Contacts (${partners.length} found):\n\n${partners.map(p => 
              `**${p.name}** (${p.id})\n` +
              `${p.email ? `📧 ${p.email}` : ''}\n` +
              `${p.phone ? `📱 ${p.phone}` : ''}\n` +
              `${p.company_name ? `🏢 ${p.company_name}` : ''}\n` +
              `${p.city || p.country ? `📍 ${[p.city, p.country].filter(Boolean).join(', ')}` : ''}`
            ).join('\n\n')}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error searching contacts: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ============================================================================
// FINANCIAL REPORTING
// ============================================================================

server.tool(
  'odoo_get_account_summary',
  'Get summary of accounts (receivable, payable, etc.)',
  {},
  async () => {
    try {
      // Get account types
      const accounts = await odoo.searchRead('account.account', [
        ['deprecated', '=', false]
      ], [
        'id', 'code', 'name', 'account_type', 'balance'
      ], { limit: 50 });

      // Group by type
      const summary = {
        receivable: [],
        payable: [],
        income: [],
        expense: [],
        other: [],
      };

      accounts.forEach(acc => {
        const type = acc.account_type || 'other';
        if (type.includes('receivable')) summary.receivable.push(acc);
        else if (type.includes('payable')) summary.payable.push(acc);
        else if (type.includes('income')) summary.income.push(acc);
        else if (type.includes('expense')) summary.expense.push(acc);
        else summary.other.push(acc);
      });

      return {
        content: [
          {
            type: 'text',
            text: `📊 Account Summary\n\n` +
              `**Receivable Accounts**: ${summary.receivable.length}\n` +
              `**Payable Accounts**: ${summary.payable.length}\n` +
              `**Income Accounts**: ${summary.income.length}\n` +
              `**Expense Accounts**: ${summary.expense.length}\n` +
              `**Other Accounts**: ${summary.other.length}\n\n` +
              `Total accounts: ${accounts.length}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting account summary: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'odoo_get_receivables',
  'Get accounts receivable (money owed to you)',
  {
    limit: z.number().default(20).describe('Maximum results'),
  },
  async ({ limit }) => {
    try {
      // Get unpaid customer invoices
      const invoices = await odoo.searchRead('account.move', [
        ['move_type', '=', 'out_invoice'],
        ['state', '=', 'posted'],
        ['payment_state', '!=', 'paid'],
      ], [
        'id', 'name', 'partner_id', 'amount_total', 'amount_residual',
        'invoice_date', 'invoice_date_due'
      ], { limit, order: 'invoice_date_due ASC' });

      const totalReceivable = invoices.reduce((sum, inv) => sum + (inv.amount_residual || 0), 0);

      return {
        content: [
          {
            type: 'text',
            text: `💰 Accounts Receivable\n\n` +
              `**Total Outstanding**: $${totalReceivable.toFixed(2)}\n\n` +
              `${invoices.length > 0 ? invoices.map(inv => 
                `**${inv.name}** - ${inv.partner_id?.[1] || 'Unknown'}\n` +
                `   Due: $${inv.amount_residual} | Total: $${inv.amount_total}\n` +
                `   Due Date: ${inv.invoice_date_due || 'Overdue'}`
              ).join('\n\n') : 'No outstanding invoices'}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting receivables: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);

server.tool(
  'odoo_get_financial_summary',
  'Get comprehensive financial summary for CEO briefing',
  {
    period_days: z.number().default(30).describe('Number of days to summarize'),
  },
  async ({ period_days }) => {
    try {
      const today = new Date();
      const startDate = new Date(today.getTime() - (period_days * 24 * 60 * 60 * 1000));
      
      // Get invoices in period
      const invoices = await odoo.searchRead('account.move', [
        ['move_type', 'in', ['out_invoice', 'in_invoice']],
        ['state', '=', 'posted'],
        ['invoice_date', '>=', startDate.toISOString().split('T')[0]],
      ], ['id', 'move_type', 'amount_total', 'amount_residual', 'partner_id', 'invoice_date']);

      // Calculate metrics
      const revenue = invoices
        .filter(i => i.move_type === 'out_invoice')
        .reduce((sum, i) => sum + (i.amount_total || 0), 0);
      
      const expenses = invoices
        .filter(i => i.move_type === 'in_invoice')
        .reduce((sum, i) => sum + (i.amount_total || 0), 0);
      
      const profit = revenue - expenses;
      
      const unpaidInvoices = invoices
        .filter(i => i.move_type === 'out_invoice' && i.payment_state !== 'paid')
        .reduce((sum, i) => sum + (i.amount_residual || 0), 0);

      return {
        content: [
          {
            type: 'text',
            text: `📈 Financial Summary (Last ${period_days} Days)\n\n` +
              `**Revenue**: $${revenue.toFixed(2)}\n` +
              `**Expenses**: $${expenses.toFixed(2)}\n` +
              `**Profit**: $${profit.toFixed(2)}\n` +
              `**Profit Margin**: ${revenue > 0 ? ((profit / revenue) * 100).toFixed(1) : 0}%\n\n` +
              `**Outstanding Receivables**: $${unpaidInvoices.toFixed(2)}\n\n` +
              `**Invoice Count**: ${invoices.length}\n` +
              `- Customer Invoices: ${invoices.filter(i => i.move_type === 'out_invoice').length}\n` +
              `- Vendor Bills: ${invoices.filter(i => i.move_type === 'in_invoice').length}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `❌ Error getting financial summary: ${error.message}`,
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
  console.error('✅ Odoo MCP Server running on stdio');
  console.error('');
  console.error('Available tools:');
  console.error('  📄 odoo_create_invoice - Create customer invoice');
  console.error('  📮 odoo_post_invoice - Post invoice');
  console.error('  💰 odoo_register_payment - Register payment');
  console.error('  📋 odoo_get_invoices - List invoices');
  console.error('  📄 odoo_get_invoice - Get invoice details');
  console.error('  👥 odoo_create_partner - Create contact');
  console.error('  🔍 odoo_search_partners - Search contacts');
  console.error('  📊 odoo_get_account_summary - Account summary');
  console.error('  💵 odoo_get_receivables - Get receivables');
  console.error('  📈 odoo_get_financial_summary - Financial report');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
