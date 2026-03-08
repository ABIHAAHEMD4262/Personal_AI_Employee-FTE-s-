#!/usr/bin/env node
/**
 * Simple Gmail OAuth Authentication
 * Alternative to auth_gmail.js if the main one fails
 */

const {google} = require('googleapis');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CREDENTIALS_PATH = path.join(__dirname, '..', '..', '..', 'credentials.json');
const TOKEN_PATH = path.join(__dirname, 'token.json');
const SCOPES = ['https://www.googleapis.com/auth/gmail.send'];

console.log('📧 Gmail OAuth Authentication (Simple Mode)');
console.log('============================================\n');

// Load credentials
if (!fs.existsSync(CREDENTIALS_PATH)) {
    console.error('❌ Credentials file not found!');
    console.error(`Expected at: ${CREDENTIALS_PATH}`);
    console.error('\nDownload from: https://console.cloud.google.com/apis/credentials');
    process.exit(1);
}

const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
const {client_secret, client_id, redirect_uris} = credentials.installed || credentials.web;

if (!client_id || !client_secret) {
    console.error('❌ Invalid credentials format');
    process.exit(1);
}

console.log('✅ Credentials loaded');
console.log(`   Project: ${credentials.project_id || 'Unknown'}`);
console.log(`   Client ID: ${client_id.substring(0, 30)}...`);
console.log('');

const oauth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris[0] || 'http://localhost'
);

// Check if token already exists
if (fs.existsSync(TOKEN_PATH)) {
    console.log('⚠️  Token already exists!');
    console.log(`   Location: ${TOKEN_PATH}`);
    
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    rl.question('Do you want to overwrite it? (y/n): ', (answer) => {
        rl.close();
        if (answer.toLowerCase() !== 'y') {
            console.log('Authentication cancelled.');
            process.exit(0);
        }
        startAuth();
    });
} else {
    startAuth();
}

function startAuth() {
    const authUrl = oauth2Client.generateAuthUrl({
        access_type: 'offline',
        scope: SCOPES,
        prompt: 'consent'
    });

    console.log('📋 Step 1: Open this URL in your browser:');
    console.log('');
    console.log(authUrl);
    console.log('');
    console.log('📋 Step 2: Sign in and grant permissions');
    console.log('📋 Step 3: You will be redirected to a page');
    console.log('📋 Step 4: Copy the ENTIRE URL from your browser');
    console.log('📋 Step 5: Paste it below\n');

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    rl.question('Enter the authorization code URL: ', (codeUrl) => {
        rl.close();
        
        try {
            // Extract code from URL
            const url = new URL(codeUrl);
            const code = url.searchParams.get('code');
            
            if (!code) {
                console.error('❌ No authorization code found in URL');
                process.exit(1);
            }

            console.log('\n⏳ Exchanging code for token...');

            oauth2Client.getToken(code, (err, token) => {
                if (err) {
                    console.error('❌ Error exchanging code:', err.message);
                    console.error('\nPossible issues:');
                    console.error('  1. URL expired (try again)');
                    console.error('  2. Wrong project selected');
                    console.error('  3. Test user not added');
                    process.exit(1);
                }

                // Save token
                fs.writeFileSync(TOKEN_PATH, JSON.stringify(token));
                
                console.log('');
                console.log('✅ Authentication successful!');
                console.log(`📁 Token saved to: ${TOKEN_PATH}`);
                console.log('');
                console.log('🎉 You can now send emails!');
                console.log('');
                console.log('Test with:');
                console.log('  python3 ../../../../skills/actions/send-email/send_email.py AI_Employee_Vault \\');
                console.log('    --send \\');
                console.log('    --to "test@example.com" \\');
                console.log('    --subject "Test" \\');
                console.log('    --content "Testing" \\');
                console.log('    --no-approval');
            });

        } catch (e) {
            console.error('❌ Error parsing URL:', e.message);
            console.error('\nMake sure you copied the ENTIRE URL from the browser.');
            process.exit(1);
        }
    });
}
