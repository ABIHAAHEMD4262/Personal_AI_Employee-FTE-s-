# Odoo MCP Server

Model Context Protocol (MCP) server for Odoo Community Edition integration.

## Features

- **Accounting**: Create invoices, register payments, track receivables
- **Contacts**: Manage customers and vendors
- **Reporting**: Financial summaries for CEO briefings

## Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env with your Odoo credentials
nano .env
```

## Configuration

Create a `.env` file in this directory:

```env
# Odoo Connection Settings
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_API_KEY=your-api-key-here
ODOO_USER_ID=2
```

### Getting Odoo Credentials

1. **Start Odoo**: `cd ../../odoo && ./setup-odoo.sh`
2. **Open Odoo**: http://localhost:8069
3. **Enable Developer Mode**: Settings → Activate developer mode
4. **Get User ID**: Settings → Users → Click your user → ID is in the URL
5. **Generate API Key**: Settings → Users → API Keys → Generate

## Usage

### Start Server

```bash
npm start
```

### Available Tools

#### Accounting

| Tool | Description |
|------|-------------|
| `odoo_create_invoice` | Create a new customer invoice |
| `odoo_post_invoice` | Post an invoice (confirm it) |
| `odoo_register_payment` | Register a payment for an invoice |
| `odoo_get_invoices` | List invoices with filters |
| `odoo_get_invoice` | Get detailed invoice information |

#### Contacts

| Tool | Description |
|------|-------------|
| `odoo_create_partner` | Create a new contact/customer |
| `odoo_search_partners` | Search for contacts |

#### Reporting

| Tool | Description |
|------|-------------|
| `odoo_get_account_summary` | Get summary of all accounts |
| `odoo_get_receivables` | Get outstanding receivables |
| `odoo_get_financial_summary` | Get financial summary for CEO briefing |

## Example Usage

### Create Invoice

```javascript
// Via MCP client
const result = await mcp.callTool('odoo_create_invoice', {
  partner_id: 1,
  invoice_date: '2026-01-07',
  invoice_lines: [
    {
      name: 'Web Development Services',
      price_unit: 1500.00,
      quantity: 1,
    }
  ],
  narration: 'Thank you for your business!'
});
```

### Register Payment

```javascript
const result = await mcp.callTool('odoo_register_payment', {
  invoice_id: 123,
  amount: 1500.00,
  payment_date: '2026-01-07',
  reference: 'INV/2026/001'
});
```

### Get Financial Summary

```javascript
const result = await mcp.callTool('odoo_get_financial_summary', {
  period_days: 30
});
```

## Integration with AI Employee

Add to your MCP configuration:

```json
{
  "servers": [
    {
      "name": "odoo",
      "command": "node",
      "args": ["/path/to/skills/mcp-servers/odoo-mcp/index.js"],
      "cwd": "/path/to/skills/mcp-servers/odoo-mcp",
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DATABASE": "odoo",
        "ODOO_API_KEY": "your-api-key",
        "ODOO_USER_ID": "2"
      }
    }
  ]
}
```

## Troubleshooting

### Connection Error

```bash
# Check if Odoo is running
docker ps | grep odoo

# Check Odoo logs
docker compose logs web
```

### Authentication Error

- Verify API key is correct
- Check user ID is numeric
- Ensure database name matches

### Tool Not Found

- Ensure server is running: `npm start`
- Check MCP client configuration
- Verify server is registered in Claude Code

## Development

```bash
# Run in development mode (auto-reload)
npm run dev

# Run tests
npm test
```

## Resources

- [Odoo JSON-RPC API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Odoo Accounting Documentation](https://www.odoo.com/documentation/19.0/applications/finance/accounting.html)
- [MCP SDK Documentation](https://modelcontextprotocol.io/)
