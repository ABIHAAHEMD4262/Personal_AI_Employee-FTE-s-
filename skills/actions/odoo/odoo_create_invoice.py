#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Create Invoice Skill - Gold Tier AI Employee

Creates a new customer invoice in Odoo Accounting.
Requires Odoo MCP server to be running.

Usage:
    python odoo_create_invoice.py /path/to/vault \
        --partner-id 1 \
        --amount 1500.00 \
        --description "Web Development Services"
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create invoice in Odoo'
    )
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--partner-id', type=int, required=True, 
                        help='Customer/Partner ID in Odoo')
    parser.add_argument('--amount', type=float, required=True,
                        help='Invoice amount')
    parser.add_argument('--description', type=str, default='Services Rendered',
                        help='Invoice line description')
    parser.add_argument('--quantity', type=int, default=1,
                        help='Quantity')
    parser.add_argument('--due-days', type=int, default=30,
                        help='Days until due')
    parser.add_argument('--narration', type=str, default='',
                        help='Additional notes')
    parser.add_argument('--create-approval', action='store_true',
                        help='Create approval request (default: True)')
    parser.add_argument('--no-approval', action='store_true',
                        help='Skip approval request')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    
    return parser.parse_args()


def generate_frontmatter(**kwargs):
    """Generate YAML frontmatter."""
    lines = ["---"]
    for key, value in kwargs.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def create_approval_request(vault_path, partner_id, amount, description, due_date, narration):
    """Create approval request file for invoice."""
    pending_folder = Path(vault_path) / 'Pending_Approval'
    pending_folder.mkdir(parents=True, exist_ok=True)
    
    invoice_date = datetime.now().strftime('%Y-%m-%d')
    filename = f"INVOICE_APPROVAL_{partner_id}_{invoice_date}.md"
    
    content = f'''{generate_frontmatter(
        type='approval_request',
        action='odoo_create_invoice',
        partner_id=partner_id,
        amount=amount,
        description=description,
        due_date=due_date,
        created=datetime.now().isoformat(),
        status='pending'
    )}

# Invoice Approval Request

## Details
- **Customer ID**: {partner_id}
- **Amount**: ${amount:,.2f}
- **Description**: {description}
- **Due Date**: {due_date}

## Notes
{narration if narration else 'No additional notes'}

## To Approve
Move this file to `/Approved` folder to create the invoice in Odoo.

## To Reject
Move this file to `/Rejected` folder to cancel.
'''
    
    filepath = pending_folder / filename
    filepath.write_text(content)
    
    return filepath


def create_invoice_in_odoo(partner_id, amount, description, quantity, due_date, narration):
    """Call Odoo MCP server to create invoice."""
    # This would typically call the MCP server
    # For now, we'll simulate with a subprocess call
    
    mcp_script = Path(__file__).parent / 'odoo_mcp_client.py'
    
    if mcp_script.exists():
        result = subprocess.run([
            'python', str(mcp_script),
            'create_invoice',
            '--partner-id', str(partner_id),
            '--amount', str(amount),
            '--description', description,
            '--quantity', str(quantity),
            '--due-date', due_date,
            '--narration', narration if narration else ''
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    else:
        # MCP client not available, create action file for Claude to process
        return False, "MCP client not available - create action file"


def create_action_file(vault_path, partner_id, amount, description, quantity, due_date, narration):
    """Create action file for Claude to process."""
    needs_action = Path(vault_path) / 'Needs_Action'
    needs_action.mkdir(parents=True, exist_ok=True)
    
    invoice_date = datetime.now().strftime('%Y-%m-%d')
    filename = f"ODOO_INVOICE_{partner_id}_{invoice_date}.md"
    
    content = f'''{generate_frontmatter(
        type='odoo_invoice_request',
        partner_id=partner_id,
        amount=amount,
        description=description,
        quantity=quantity,
        due_date=due_date,
        narration=narration,
        created=datetime.now().isoformat(),
        status='pending'
    )}

# Odoo Invoice Request

## Invoice Details
- **Customer ID**: {partner_id}
- **Amount**: ${amount:,.2f}
- **Description**: {description}
- **Quantity**: {quantity}
- **Due Date**: {due_date}

## Notes
{narration if narration else 'No additional notes'}

## Next Steps
1. Verify customer exists in Odoo
2. Create invoice with above details
3. Post invoice
4. Send to customer
'''
    
    filepath = needs_action / filename
    filepath.write_text(content)
    
    return filepath


def main():
    args = parse_args()
    vault_path = Path(args.vault_path).resolve()
    
    print(f"📄 Creating invoice for Partner {args.partner_id}")
    print(f"   Amount: ${args.amount:,.2f}")
    print(f"   Description: {args.description}")
    
    # Calculate due date
    due_date = (datetime.now() + timedelta(days=args.due_days)).strftime('%Y-%m-%d')
    
    # Check if approval is required
    require_approval = not args.no_approval
    
    if require_approval:
        # Create approval request
        filepath = create_approval_request(
            vault_path,
            args.partner_id,
            args.amount,
            args.description,
            due_date,
            args.narration
        )
        print(f"✅ Approval request created: {filepath.name}")
        print(f"   Location: {filepath}")
        print(f"\n💡 Move file to /Approved to create invoice")
    else:
        # Create action file for direct processing
        filepath = create_action_file(
            vault_path,
            args.partner_id,
            args.amount,
            args.description,
            args.quantity,
            due_date,
            args.narration
        )
        print(f"✅ Action file created: {filepath.name}")
        
        # Try to create invoice directly
        success, message = create_invoice_in_odoo(
            args.partner_id,
            args.amount,
            args.description,
            args.quantity,
            due_date,
            args.narration
        )
        
        if success:
            print(f"✅ Invoice created in Odoo")
            print(f"   {message}")
        else:
            print(f"⚠️  {message}")
            print(f"   File waiting in: {filepath}")


if __name__ == "__main__":
    main()
