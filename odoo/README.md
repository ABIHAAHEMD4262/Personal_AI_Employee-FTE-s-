# Odoo Integration for Gold Tier AI Employee

This directory contains the Odoo Community Edition setup and integration for the Gold Tier AI Employee.

## Quick Start

### 1. Install Odoo

```bash
# Make the setup script executable
chmod +x setup-odoo.sh

# Run the setup
./setup-odoo.sh
```

This will:
- Start Odoo Community 19.0 with Docker Compose
- Create necessary data directories
- Set up PostgreSQL database

### 2. Initial Odoo Configuration

1. Open http://localhost:8069 in your browser
2. Create a new database:
   - Database name: `odoo`
   - Email: `admin@example.com`
   - Password: `admin`
3. Install these modules:
   - **Accounting** (for financial management)
   - **Invoicing** (for invoice generation)
   - **Contacts** (for customer management)
   - **Sales** (optional, for sales orders)

### 3. Enable Developer Mode

1. Go to Settings
2. Scroll down and click "Activate the developer mode"

### 4. Get API Credentials

1. Go to Settings → Users & Companies → Users
2. Click on your user (admin)
3. Under "API Keys", generate a new API key
4. Note your:
   - Database name
   - User ID
   - API Key

### 5. Configure MCP Server

```bash
cd ../skills/mcp-servers/odoo-mcp
npm install
```

Create `.env` file:
```env
ODOO_URL=http://localhost:8069
ODOO_DATABASE=odoo
ODOO_API_KEY=your-api-key-here
ODOO_USER_ID=2
```

### 6. Start Odoo MCP Server

```bash
npm start
```

## Directory Structure

```
odoo/
├── docker-compose.yml      # Docker Compose configuration
├── odoo.conf              # Odoo server configuration
├── setup-odoo.sh          # Setup script
├── README.md              # This file
├── odoo-data/             # Odoo data (auto-created)
├── odoo-config/           # Odoo configuration (auto-created)
├── odoo-addons/           # Custom addons (auto-created)
└── postgres-data/         # PostgreSQL data (auto-created)
```

## Docker Commands

```bash
# Start Odoo
docker compose up -d

# Stop Odoo
docker compose down

# View logs
docker compose logs -f web

# Restart Odoo
docker compose restart

# Reset everything (WARNING: deletes all data)
docker compose down -v
```

## Odoo JSON-RPC API

The AI Employee uses Odoo's JSON-RPC API for integration. Key endpoints:

- **Base URL**: `http://localhost:8069/jsonrpc`
- **Content-Type**: `application/json`

### Example API Calls

#### Authenticate
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "common",
    "method": "authenticate",
    "args": ["odoo", "admin@example.com", "admin"]
  },
  "id": 1
}
```

#### Create Invoice
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "odoo",
      2,
      "api_key",
      "account.move",
      "create",
      [{
        "move_type": "out_invoice",
        "partner_id": 1,
        "invoice_line_ids": [[0, 0, {
          "name": "Service",
          "price_unit": 100.0,
          "quantity": 1
        }]]
      }]
    ]
  },
  "id": 2
}
```

## Integration with AI Employee

The Odoo MCP server provides these capabilities:

1. **Accounting**: Create invoices, record payments, track receivables
2. **Contacts**: Manage customer information
3. **Products**: Manage products and services
4. **Reporting**: Generate financial reports

## Troubleshooting

### Odoo won't start
```bash
# Check logs
docker compose logs web

# Restart
docker compose restart
```

### Database connection error
```bash
# Check PostgreSQL is running
docker compose ps db

# Restart database
docker compose restart db
```

### Port already in use
Edit `docker-compose.yml` and change the port:
```yaml
ports:
  - "8070:8069"  # Use 8070 instead of 8069
```

## Security Notes

- Change default admin password immediately
- Use strong API keys
- Never commit `.env` files with credentials
- Consider using HTTPS in production

## Resources

- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [Odoo External API Reference](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Odoo JSON-RPC Examples](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html#json-rpc)
