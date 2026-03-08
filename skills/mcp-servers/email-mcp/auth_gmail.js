#!/usr/bin/env node
/**
 * Gmail OAuth Authentication for MCP Server
 * 
 * Usage:
 *   node auth_gmail.js
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

async function authenticate() {
  const { google } = await import('googleapis');
  
  // Load credentials
  const credsPath = process.env.GMAIL_CREDENTIALS || 
                    path.join(__dirname, '..', '..', '..', 'credentials.json');
  
  if (!fs.existsSync(credsPath)) {
    console.error('❌ Credentials file not found:', credsPath);
    return false;
  }
  
  const credentials = JSON.parse(fs.readFileSync(credsPath, 'utf8'));
  const { client_secret, client_id, redirect_uris } = credentials.installed;
  
  const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris[0]
  );
  
  // Generate auth URL
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: ['https://www.googleapis.com/auth/gmail.send', 
            'https://www.googleapis.com/auth/gmail.readonly'],
  });
  
  console.log('📧 Gmail OAuth Authentication');
  console.log('=============================\n');
  console.log('1. Open this URL in your browser:');
  console.log(authUrl);
  console.log('\n2. Sign in with your Google account');
  console.log('3. Grant permissions');
  console.log('4. Copy the authorization code');
  console.log('\nEnter the authorization code here:');
  
  return new Promise((resolve, reject) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    
    rl.question('Authorization code: ', (code) => {
      oauth2Client.getToken(code, (err, token) => {
        if (err) {
          console.error('❌ Error retrieving token:', err.message);
          rl.close();
          reject(err);
          return;
        }
        
        // Save token
        const tokenPath = path.join(__dirname, 'token.json');
        fs.writeFileSync(tokenPath, JSON.stringify(token));
        
        console.log('\n✅ Authentication successful!');
        console.log('Token saved to:', tokenPath);
        console.log('\nYou can now use the Gmail MCP server.');
        
        rl.close();
        resolve(true);
      });
    });
  });
}

authenticate()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error('Authentication failed:', err);
    process.exit(1);
  });
