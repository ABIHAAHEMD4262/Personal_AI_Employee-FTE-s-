#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo MCP Client - Communicates with Odoo MCP Server

Usage:
    python odoo_mcp_client.py create_invoice --partner-id 1 --amount 1500 --description "Services"
    python odoo_mcp_client.py register_payment --invoice-id 123 --amount 1500
    python odoo_mcp_client.py get_invoices --limit 10
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / '../../mcp-servers/odoo-mcp/.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DATABASE = os.getenv('ODOO_DATABASE')
ODOO_API_KEY = os.getenv('ODOO_API_KEY')
ODOO_USER_ID = os.getenv('ODOO_USER_ID')


class OdooClient:
    """Direct Odoo JSON-RPC client (bypasses MCP for programmatic access)."""
    
    def __init__(self, base_url, db, api_key, user_id):
        self.base_url = f"{base_url}/jsonrpc"
        self.db = db
        self.api_key = api_key
        self.user_id = int(user_id)
    
    def call(self, service, method, args=None):
        """Make JSON-RPC call to Odoo."""
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": service,
                "method": method,
                "args": args or []
            },
            "id": 1
        }
        
        response = requests.post(self.base_url, json=payload)
        result = response.json()
        
        if result.get('error'):
            raise Exception(result['error']['message'])
        
        return result.get('result')
    
    def execute(self, model, method, args=None, kwargs=None):
        """Execute KW method."""
        return self.call('object', 'execute_kw', [
            self.db, self.user_id, self.api_key,
            model, method, args or [], kwargs or {}
        ])
    
    def create_invoice(self, partner_id, invoice_lines, invoice_date=None, due_date=None, narration=''):
        """Create customer invoice."""
        invoice_data = {
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_line_ids': [[0, 0, {
                'name': line['description'],
                'price_unit': line['amount'],
                'quantity': line.get('quantity', 1),
            }] for line in invoice_lines],
        }
        
        if invoice_date:
            invoice_data['invoice_date'] = invoice_date
        if due_date:
            invoice_data['invoice_date_due'] = due_date
        if narration:
            invoice_data['narration'] = narration
        
        invoice_id = self.execute('account.move', 'create', [invoice_data])
        return invoice_id
    
    def post_invoice(self, invoice_id):
        """Post invoice."""
        return self.execute('account.move', 'action_post', [[invoice_id]])
    
    def register_payment(self, invoice_id, amount, payment_date=None, reference=''):
        """Register payment for invoice."""
        # Create payment register
        payment_register_id = self.execute('account.payment.register', 'create', [{
            'payment_type': 'inbound',
            'amount': amount,
            'currency_id': 1,
            'payment_date': payment_date,
            'communication': reference,
        }], {
            'active_model': 'account.move',
            'active_ids': [invoice_id],
        })
        
        # Create payment
        self.execute('account.payment.register', 'create_payments', [[payment_register_id]])
        
        return True
    
    def get_invoices(self, partner_id=None, state=None, limit=10):
        """Get invoices."""
        domain = []
        if partner_id:
            domain.append(['partner_id', '=', partner_id])
        if state:
            domain.append(['state', '=', state])
        
        return self.execute('account.move', 'search_read', [
            domain,
            ['id', 'name', 'partner_id', 'amount_total', 'amount_residual', 'state', 'invoice_date', 'invoice_date_due']
        ], {'limit': limit})
    
    def search_partners(self, query='', limit=10):
        """Search partners."""
        domain = []
        if query:
            domain = ['|', '|', 
                ['name', 'ilike', query],
                ['email', 'ilike', query],
                ['company_name', 'ilike', query]
            ]
        
        return self.execute('res.partner', 'search_read', [
            domain,
            ['id', 'name', 'email', 'phone', 'company_name']
        ], {'limit': limit})


def main():
    parser = argparse.ArgumentParser(description='Odoo MCP Client')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create invoice command
    create_parser = subparsers.add_parser('create_invoice', help='Create invoice')
    create_parser.add_argument('--partner-id', type=int, required=True)
    create_parser.add_argument('--amount', type=float, required=True)
    create_parser.add_argument('--description', type=str, default='Services')
    create_parser.add_argument('--quantity', type=int, default=1)
    create_parser.add_argument('--due-date', type=str, default=None)
    create_parser.add_argument('--narration', type=str, default='')
    
    # Post invoice command
    post_parser = subparsers.add_parser('post_invoice', help='Post invoice')
    post_parser.add_argument('--invoice-id', type=int, required=True)
    
    # Register payment command
    payment_parser = subparsers.add_parser('register_payment', help='Register payment')
    payment_parser.add_argument('--invoice-id', type=int, required=True)
    payment_parser.add_argument('--amount', type=float, required=True)
    payment_parser.add_argument('--payment-date', type=str, default=None)
    payment_parser.add_argument('--reference', type=str, default='')
    
    # Get invoices command
    invoices_parser = subparsers.add_parser('get_invoices', help='Get invoices')
    invoices_parser.add_argument('--partner-id', type=int, default=None)
    invoices_parser.add_argument('--state', type=str, default=None)
    invoices_parser.add_argument('--limit', type=int, default=10)
    
    # Search partners command
    search_parser = subparsers.add_parser('search_partners', help='Search partners')
    search_parser.add_argument('--query', type=str, default='')
    search_parser.add_argument('--limit', type=int, default=10)
    
    args = parser.parse_args()
    
    # Check credentials
    if not all([ODOO_DATABASE, ODOO_API_KEY, ODOO_USER_ID]):
        print("❌ Missing Odoo credentials. Please set up .env file.")
        print("   Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)
    
    client = OdooClient(ODOO_URL, ODOO_DATABASE, ODOO_API_KEY, ODOO_USER_ID)
    
    try:
        if args.command == 'create_invoice':
            invoice_id = client.create_invoice(
                args.partner_id,
                [{
                    'description': args.description,
                    'amount': args.amount,
                    'quantity': args.quantity,
                }],
                due_date=args.due_date,
                narration=args.narration
            )
            print(f"✅ Invoice created: ID {invoice_id}")
        
        elif args.command == 'post_invoice':
            client.post_invoice(args.invoice_id)
            print(f"✅ Invoice {args.invoice_id} posted")
        
        elif args.command == 'register_payment':
            client.register_payment(
                args.invoice_id,
                args.amount,
                payment_date=args.payment_date,
                reference=args.reference
            )
            print(f"✅ Payment registered for invoice {args.invoice_id}")
        
        elif args.command == 'get_invoices':
            invoices = client.get_invoices(
                partner_id=args.partner_id,
                state=args.state,
                limit=args.limit
            )
            print(f"📋 Invoices ({len(invoices)} found):")
            for inv in invoices:
                partner_name = inv.get('partner_id', [None, 'Unknown'])[1]
                print(f"  - {inv['name']}: ${inv['amount_total']} ({inv['state']}) - {partner_name}")
        
        elif args.command == 'search_partners':
            partners = client.search_partners(
                query=args.query,
                limit=args.limit
            )
            print(f"👥 Partners ({len(partners)} found):")
            for p in partners:
                print(f"  - {p['name']} (ID: {p['id']}) - {p.get('email', 'No email')}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
