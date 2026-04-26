#!/usr/bin/env node
/**
 * Odoo MCP Server Test Script
 * 
 * Tests basic connectivity and tool functionality
 */

import fetch from 'node-fetch';
import dotenv from 'dotenv';

dotenv.config();

const ODOO_URL = process.env.ODOO_URL || 'http://localhost:8069';
const ODOO_DATABASE = process.env.ODOO_DATABASE;
const ODOO_API_KEY = process.env.ODOO_API_KEY;
const ODOO_USER_ID = process.env.ODOO_USER_ID;

async function testConnection() {
  console.log('🧪 Testing Odoo Connection...\n');
  
  try {
    const response = await fetch(`${ODOO_URL}/jsonrpc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'common',
          method: 'version',
          args: [],
        },
        id: 1,
      }),
    });

    const result = await response.json();
    
    if (result.result) {
      console.log('✅ Connection successful!');
      console.log(`   Odoo Version: ${JSON.stringify(result.result, null, 2)}`);
      return true;
    } else {
      console.log('❌ Connection failed:', result);
      return false;
    }
  } catch (error) {
    console.log('❌ Connection error:', error.message);
    console.log('\n💡 Is Odoo running? Try: cd ../../odoo && docker compose ps');
    return false;
  }
}

async function testAuthentication() {
  console.log('\n🧪 Testing Authentication...\n');
  
  if (!ODOO_DATABASE || !ODOO_API_KEY || !ODOO_USER_ID) {
    console.log('❌ Missing credentials in .env file');
    console.log('   Please copy .env.example to .env and fill in your credentials');
    return false;
  }

  try {
    const response = await fetch(`${ODOO_URL}/jsonrpc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute_kw',
          args: [
            ODOO_DATABASE,
            parseInt(ODOO_USER_ID),
            ODOO_API_KEY,
            'res.partner',
            'search_count',
            [[]], // Get all partners count
          ],
        },
        id: 2,
      }),
    });

    const result = await response.json();
    
    if (result.result !== undefined) {
      console.log('✅ Authentication successful!');
      console.log(`   Total contacts in database: ${result.result}`);
      return true;
    } else {
      console.log('❌ Authentication failed:', result);
      return false;
    }
  } catch (error) {
    console.log('❌ Authentication error:', error.message);
    console.log('\n💡 Check your credentials in .env file');
    return false;
  }
}

async function testGetInvoices() {
  console.log('\n🧪 Testing Invoice Retrieval...\n');
  
  try {
    const response = await fetch(`${ODOO_URL}/jsonrpc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'call',
        params: {
          service: 'object',
          method: 'execute_kw',
          args: [
            ODOO_DATABASE,
            parseInt(ODOO_USER_ID),
            ODOO_API_KEY,
            'account.move',
            'search_read',
            [[]], // Get all invoices
            ['id', 'name', 'partner_id', 'amount_total', 'state'],
          ],
        },
        id: 3,
      }),
    });

    const result = await response.json();
    
    if (result.result) {
      console.log('✅ Invoice retrieval successful!');
      console.log(`   Total invoices: ${result.result.length}`);
      if (result.result.length > 0) {
        console.log('\n   Sample invoice:');
        const sample = result.result[0];
        console.log(`   - ${sample.name}: $${sample.amount_total} (${sample.state})`);
      }
      return true;
    } else {
      console.log('❌ Invoice retrieval failed:', result);
      return false;
    }
  } catch (error) {
    console.log('❌ Invoice retrieval error:', error.message);
    return false;
  }
}

async function main() {
  console.log('===========================================');
  console.log('Odoo MCP Server Test Suite');
  console.log('===========================================\n');
  
  const connectionOk = await testConnection();
  
  if (!connectionOk) {
    console.log('\n❌ Tests aborted due to connection failure');
    process.exit(1);
  }
  
  const authOk = await testAuthentication();
  
  if (!authOk) {
    console.log('\n❌ Tests aborted due to authentication failure');
    process.exit(1);
  }
  
  await testGetInvoices();
  
  console.log('\n===========================================');
  console.log('✅ All tests passed!');
  console.log('===========================================');
  console.log('\n💡 You can now start the MCP server:');
  console.log('   npm start\n');
}

main().catch(console.error);
